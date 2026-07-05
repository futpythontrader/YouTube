import io
import logging
from typing import Any

import pandas as pd
import requests
from django.conf import settings
from django.db import IntegrityError, transaction

from apps.backtest.models import Match

logger = logging.getLogger(__name__)

# CSV column mapping: API column name -> Match model field name
COLUMN_MAPPING: dict[str, str] = {
    "Date": "date",
    "Time": "time",
    "Home": "home",
    "Away": "away",
    "Goals_H_FT": "ft_goals_h",
    "Goals_A_FT": "ft_goals_a",
    "Goals_H_HT": "ht_goals_h",
    "Goals_A_HT": "ht_goals_a",
    "Odd_H_Back": "odd_home",
    "Odd_D_Back": "odd_draw",
    "Odd_A_Back": "odd_away",
    "Odd_Over25_FT_Back": "odd_over25",
    "Odd_BTTS_Yes_Back": "odd_btts",
    "League": "league",
    "Country": "country",
    "Season": "season",
}


def import_from_api() -> dict[str, int]:
    """
    Downloads the full historical CSV from the FutPythonTrader API and
    populates the Match model using bulk_create with ignore_conflicts.

    Deduplication is handled by the unique constraint on (date, home, away).

    Returns:
        dict with keys ``importados`` (created), ``atualizados`` (0 — bulk mode),
        and ``erros`` (rows skipped due to errors).
    """
    token: str = settings.FUTPYTHONTRADER_TOKEN
    base_url: str = settings.FUTPYTHONTRADER_BASE_URL
    url: str = f"{base_url}/betfair/download/"

    headers: dict[str, str] = {"Authorization": f"Token {token}"}

    logger.info("Fetching CSV from FutPythonTrader API...")
    try:
        response = requests.get(url, headers=headers, timeout=120)
    except requests.exceptions.Timeout:
        logger.error("Timeout while fetching FutPythonTrader API")
        return {"importados": 0, "atualizados": 0, "erros": -1}
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while fetching FutPythonTrader API")
        return {"importados": 0, "atualizados": 0, "erros": -2}

    if response.status_code == 401:
        logger.error("FutPythonTrader API returned 401 — token may be invalid")
        return {"importados": 0, "atualizados": 0, "erros": -3}
    if response.status_code != 200:
        logger.error(
            "FutPythonTrader API returned %d — %s",
            response.status_code,
            response.text[:200],
        )
        return {"importados": 0, "atualizados": 0, "erros": -4}

    try:
        df = pd.read_csv(
            io.BytesIO(response.content),
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:
        logger.exception("Failed to parse CSV from FutPythonTrader API")
        return {"importados": 0, "atualizados": 0, "erros": -5}

    if df.empty:
        logger.warning("CSV from FutPythonTrader API is empty")
        return {"importados": 0, "atualizados": 0, "erros": 0}

    # Count existing before import
    existing_before: int = Match.objects.count()

    matches: list[Match] = []
    erros: int = 0

    for _, row in df.iterrows():
        row_dict: dict[str, Any] = row.to_dict()

        try:
            match_data = _build_match_data(row_dict)
        except Exception:
            logger.exception("Failed to build match data for row: %s", row_dict)
            erros += 1
            continue

        match_data["raw_data"] = row_dict
        matches.append(Match(**match_data))

    # Bulk insert in batches — ignore duplicates via unique_constraint
    if matches:
        batch_size = 500
        for i in range(0, len(matches), batch_size):
            batch = matches[i : i + batch_size]
            Match.objects.bulk_create(batch, ignore_conflicts=True)

    existing_after: int = Match.objects.count()
    importados: int = existing_after - existing_before

    logger.info(
        "Import complete — %d created, %d existing, %d errors",
        importados,
        existing_after - importados,
        erros,
    )
    return {"importados": importados, "atualizados": 0, "erros": erros}


def _build_match_data(row: dict[str, Any]) -> dict[str, Any]:
    """
    Converts a raw CSV row dict into a dict suitable for ``Match.objects.create``.
    Handles type conversions, missing values, and derives ft_result/ht_result from goals.
    """
    import pandas as pd

    match_data: dict[str, Any] = {}

    # Date
    date_str = row.get("Date", "")
    match_data["date"] = pd.to_datetime(date_str, errors="coerce").date() if date_str else None

    # Time — keep as string if format is HH:MM, else None
    time_str = row.get("Time", "")
    if time_str and ":" in str(time_str):
        match_data["time"] = str(time_str).strip()
    else:
        match_data["time"] = None

    # String fields
    match_data["home"] = str(row.get("Home", "")).strip()
    match_data["away"] = str(row.get("Away", "")).strip()
    match_data["league"] = str(row.get("League", "")).strip()
    match_data["country"] = str(row.get("Country", "")).strip()
    match_data["season"] = str(row.get("Season", "")).strip()

    # Integer fields (goals)
    ft_h = _safe_int(row.get("Goals_H_FT"))
    ft_a = _safe_int(row.get("Goals_A_FT"))
    ht_h = _safe_int(row.get("Goals_H_HT"))
    ht_a = _safe_int(row.get("Goals_A_HT"))

    match_data["ft_goals_h"] = ft_h
    match_data["ft_goals_a"] = ft_a
    match_data["ht_goals_h"] = ht_h
    match_data["ht_goals_a"] = ht_a

    # Derive ft_result and ht_result from goals
    match_data["ft_result"] = _goals_to_result(ft_h, ft_a)
    match_data["ht_result"] = _goals_to_result(ht_h, ht_a)

    # Decimal fields (odds)
    match_data["odd_home"] = _safe_decimal(row.get("Odd_H_Back"))
    match_data["odd_draw"] = _safe_decimal(row.get("Odd_D_Back"))
    match_data["odd_away"] = _safe_decimal(row.get("Odd_A_Back"))
    match_data["odd_over25"] = _safe_decimal(row.get("Odd_Over25_FT_Back"))
    match_data["odd_btts"] = _safe_decimal(row.get("Odd_BTTS_Yes_Back"))

    # Validate required fields
    if not match_data["date"] or not match_data["home"] or not match_data["away"]:
        raise ValueError(f"Missing required field (date/home/away) in row: {row}")

    return match_data


def _goals_to_result(goals_h: int | None, goals_a: int | None) -> str | None:
    """Derive match result (H/D/A) from goals, or None if incomplete."""
    if goals_h is None or goals_a is None:
        return None
    if goals_h > goals_a:
        return "H"
    if goals_h < goals_a:
        return "A"
    return "D"


def _normalize_result(value: Any) -> str | None:
    """Normalize H/D/A result codes."""
    if not value:
        return None
    val = str(value).strip().upper()
    if val in ("H", "HOME", "1"):
        return "H"
    if val in ("D", "DRAW", "X"):
        return "D"
    if val in ("A", "AWAY", "2"):
        return "A"
    return val if val else None


def _safe_int(value: Any) -> int | None:
    """Safely convert a value to int, returning None on failure."""
    if value is None:
        return None
    try:
        val = int(float(str(value).strip()))
        return val
    except (ValueError, TypeError):
        return None


def _safe_decimal(value: Any) -> Any | None:
    """Safely convert a value to Decimal, returning None on failure."""
    from decimal import Decimal, InvalidOperation

    if value is None:
        return None
    try:
        val = str(value).strip()
        if not val:
            return None
        return Decimal(val)
    except (InvalidOperation, ValueError, TypeError):
        return None
