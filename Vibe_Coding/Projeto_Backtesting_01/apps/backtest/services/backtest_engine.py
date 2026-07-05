from decimal import Decimal
from typing import Any, Optional

from django.db.models import QuerySet

from apps.backtest.models import Match


def run_backtest(
    *,
    tipo_back: str,
    queryset: Optional[QuerySet[Match]] = None,
    odd_home_min: Optional[Decimal] = None,
    odd_home_max: Optional[Decimal] = None,
    odd_draw_min: Optional[Decimal] = None,
    odd_draw_max: Optional[Decimal] = None,
    odd_away_min: Optional[Decimal] = None,
    odd_away_max: Optional[Decimal] = None,
    odd_over25_min: Optional[Decimal] = None,
    odd_over25_max: Optional[Decimal] = None,
    odd_btts_min: Optional[Decimal] = None,
    odd_btts_max: Optional[Decimal] = None,
) -> dict[str, Any]:
    """
    Pure calculation engine for backtesting a betting strategy.

    Applies 5 independent odds filters (Home, Draw, Away, Over 2.5, BTTS)
    with AND logic. The ``tipo_back`` determines the bet type and outcome.

    Args:
        tipo_back: Bet type — 'HOME', 'DRAW', or 'AWAY'.
        queryset: Optional pre-filtered Match QuerySet.
        odd_home_min / odd_home_max: Optional Home odds range.
        odd_draw_min / odd_draw_max: Optional Draw odds range.
        odd_away_min / odd_away_max: Optional Away odds range.
        odd_over25_min / odd_over25_max: Optional Over 2.5 odds range.
        odd_btts_min / odd_btts_max: Optional BTTS Yes odds range.

    Returns:
        dict with keys: total_jogos, verdes, vermelhas, profit_total,
        win_rate, roi, max_drawdown, matches, pl_curve, drawdown_curve, labels.
    """
    if queryset is None:
        matches = Match.objects.all().order_by("date", "time")
    else:
        matches = queryset.order_by("date", "time")

    results: list[dict[str, Any]] = []
    running_pl: Decimal = Decimal("0")
    peak: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    verdes: int = 0
    vermelhas: int = 0
    profit_total: Decimal = Decimal("0")

    pl_curve: list[float] = []
    drawdown_curve: list[float] = []
    labels: list[str] = []

    for match in matches:
        # 1. Pick the relevant odd based on tipo_back (for P&L calculation)
        if tipo_back == "HOME":
            odd = match.odd_home
        elif tipo_back == "DRAW":
            odd = match.odd_draw
        else:  # AWAY
            odd = match.odd_away

        if odd is None:
            continue

        # 2a. Home odds filter
        if odd_home_min is not None or odd_home_max is not None:
            val = match.odd_home
            if val is None:
                continue
            if odd_home_min is not None and val < odd_home_min:
                continue
            if odd_home_max is not None and val > odd_home_max:
                continue

        # 2b. Draw odds filter
        if odd_draw_min is not None or odd_draw_max is not None:
            val = match.odd_draw
            if val is None:
                continue
            if odd_draw_min is not None and val < odd_draw_min:
                continue
            if odd_draw_max is not None and val > odd_draw_max:
                continue

        # 2c. Away odds filter
        if odd_away_min is not None or odd_away_max is not None:
            val = match.odd_away
            if val is None:
                continue
            if odd_away_min is not None and val < odd_away_min:
                continue
            if odd_away_max is not None and val > odd_away_max:
                continue

        # 2d. Over 2.5 odds filter
        if odd_over25_min is not None or odd_over25_max is not None:
            val = match.odd_over25
            if val is None:
                continue
            if odd_over25_min is not None and val < odd_over25_min:
                continue
            if odd_over25_max is not None and val > odd_over25_max:
                continue

        # 2e. BTTS odds filter
        if odd_btts_min is not None or odd_btts_max is not None:
            val = match.odd_btts
            if val is None:
                continue
            if odd_btts_min is not None and val < odd_btts_min:
                continue
            if odd_btts_max is not None and val > odd_btts_max:
                continue

        # 3. Determine win/loss
        if tipo_back == "HOME":
            is_green = match.ft_result == "H"
        elif tipo_back == "DRAW":
            is_green = match.ft_result == "D"
        else:  # AWAY
            is_green = match.ft_result == "A"

        # 4. Calculate profit for this match
        if is_green:
            profit = odd - Decimal("1")
            verdes += 1
            result = "Green"
        else:
            profit = Decimal("-1")
            vermelhas += 1
            result = "Red"

        running_pl += profit
        profit_total += profit

        # 5. Track peak and drawdown
        peak = max(peak, running_pl)
        current_drawdown = peak - running_pl
        max_drawdown = max(max_drawdown, current_drawdown)

        results.append(
            {
                "match": match,
                "odd": odd,
                "result": result,
                "profit": profit,
                "running_pl": running_pl,
            }
        )

        pl_curve.append(float(running_pl))
        drawdown_curve.append(float(current_drawdown))
        labels.append(f"{match.home} vs {match.away}")

    total_jogos: int = verdes + vermelhas

    if total_jogos > 0:
        win_rate: Decimal = round(
            Decimal(verdes) / Decimal(total_jogos) * Decimal("100"), 2
        )
        roi: Decimal = round(profit_total / Decimal(total_jogos) * Decimal("100"), 2)
    else:
        win_rate = Decimal("0")
        roi = Decimal("0")

    return {
        "total_jogos": total_jogos,
        "verdes": verdes,
        "vermelhas": vermelhas,
        "profit_total": profit_total,
        "win_rate": win_rate,
        "roi": roi,
        "max_drawdown": max_drawdown,
        "matches": results,
        "pl_curve": pl_curve,
        "drawdown_curve": drawdown_curve,
        "labels": labels,
    }
