"""Tests for the backtest engine service."""

from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.backtest.models import Match
from apps.backtest.services.backtest_engine import run_backtest


class RunBacktestTests(TestCase):
    """Test the pure backtest calculation engine."""

    def setUp(self) -> None:
        """Create sample match data for testing."""
        # Match 1: Home win, odd_home=2.00
        Match.objects.create(
            date=date(2024, 1, 1),
            time="15:00",
            home="Team A",
            away="Team B",
            ft_result="H",
            odd_home=Decimal("2.00"),
            odd_draw=Decimal("3.50"),
            odd_away=Decimal("4.00"),
            odd_over25=Decimal("1.80"),
            odd_btts=Decimal("1.90"),
        )
        # Match 2: Draw, odd_draw=3.20
        Match.objects.create(
            date=date(2024, 1, 2),
            time="16:00",
            home="Team C",
            away="Team D",
            ft_result="D",
            odd_home=Decimal("2.50"),
            odd_draw=Decimal("3.20"),
            odd_away=Decimal("2.80"),
            odd_over25=Decimal("2.10"),
            odd_btts=Decimal("1.70"),
        )
        # Match 3: Away win, odd_away=3.50
        Match.objects.create(
            date=date(2024, 1, 3),
            time="17:00",
            home="Team E",
            away="Team F",
            ft_result="A",
            odd_home=Decimal("1.80"),
            odd_draw=Decimal("3.60"),
            odd_away=Decimal("3.50"),
            odd_over25=Decimal("1.90"),
            odd_btts=Decimal("1.85"),
        )
        # Match 4: Home win, but odd_home=1.20 (BELOW min)
        Match.objects.create(
            date=date(2024, 1, 4),
            time="18:00",
            home="Team G",
            away="Team H",
            ft_result="H",
            odd_home=Decimal("1.20"),
            odd_draw=Decimal("5.00"),
            odd_away=Decimal("10.00"),
            odd_over25=Decimal("1.40"),
            odd_btts=Decimal("2.00"),
        )
        # Match 5: odds are None (should be skipped)
        Match.objects.create(
            date=date(2024, 1, 5),
            time="19:00",
            home="Team I",
            away="Team J",
            ft_result="H",
            odd_home=None,
            odd_draw=None,
            odd_away=None,
            odd_over25=None,
            odd_btts=None,
        )

    # ------------------------------------------------------------------
    # Basic smoke tests
    # ------------------------------------------------------------------

    def test_back_home_basic(self) -> None:
        """Home strategy with odd_home 1.50-3.00 finds 3 matches (1 Green, 2 Red)."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.50"),
            odd_home_max=Decimal("3.00"),
        )
        assert result["total_jogos"] == 3
        assert result["verdes"] == 1
        assert result["vermelhas"] == 2
        assert result["profit_total"] == Decimal("-1.00")
        assert result["win_rate"] == Decimal("33.33")
        assert result["roi"] == Decimal("-33.33")

    def test_back_draw_one_match(self) -> None:
        """Draw strategy finds 3 matches (1 Green, 2 Red)."""
        result = run_backtest(
            tipo_back="DRAW",
            odd_draw_min=Decimal("2.00"),
            odd_draw_max=Decimal("4.00"),
        )
        assert result["total_jogos"] == 3
        assert result["verdes"] == 1
        assert result["vermelhas"] == 2
        assert result["profit_total"] == Decimal("0.20")
        assert result["win_rate"] == Decimal("33.33")
        assert result["roi"] == Decimal("6.67")

    def test_back_away_mixed(self) -> None:
        """Away strategy catches 2 matches (1 Green, 1 Red)."""
        result = run_backtest(
            tipo_back="AWAY",
            odd_away_min=Decimal("3.50"),
            odd_away_max=Decimal("5.00"),
        )
        assert result["total_jogos"] == 2
        assert result["verdes"] == 1
        assert result["vermelhas"] == 1
        assert result["profit_total"] == Decimal("1.50")

    def test_combined_filters(self) -> None:
        """Multiple odds filters act as AND."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.50"),
            odd_home_max=Decimal("3.00"),
            odd_over25_min=Decimal("1.80"),
        )
        # Match 1: odd_home=2.00 OK, odd_over25=1.80 OK -> included (Green)
        # Match 2: odd_home=2.50 OK, odd_over25=2.10 OK -> included (Red)
        # Match 3: odd_home=1.80 OK, odd_over25=1.90 OK -> included (Red)
        assert result["total_jogos"] == 3
        assert result["verdes"] == 1

    def test_over25_filter_excludes(self) -> None:
        """Over 2.5 filter excludes matches with odd outside range."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
            odd_over25_min=Decimal("2.00"),
        )
        # Match 1: odd_over25=1.80 < 2.00 -> excluded
        # Match 2: odd_over25=2.10 -> included (Red)
        # Match 3: odd_over25=1.90 < 2.00 -> excluded
        # Match 4: odd_over25=1.40 -> excluded
        assert result["total_jogos"] == 1
        assert result["matches"][0]["match"].home == "Team C"

    def test_btts_filter_excludes(self) -> None:
        """BTTS filter excludes matches with odd outside range."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
            odd_btts_min=Decimal("1.95"),
        )
        # Match 1: btts=1.90 -> excluded
        # Match 2: btts=1.70 -> excluded
        # Match 3: btts=1.85 -> excluded
        # Match 4: btts=2.00 -> included
        assert result["total_jogos"] == 1
        assert result["matches"][0]["match"].home == "Team G"

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_empty_queryset(self) -> None:
        """Pre-filtered queryset with no matches should return zero results."""
        qs = Match.objects.filter(home="Nonexistent")
        result = run_backtest(
            tipo_back="HOME",
            queryset=qs,
        )
        assert result["total_jogos"] == 0
        assert result["verdes"] == 0
        assert result["profit_total"] == Decimal("0")
        assert result["win_rate"] == Decimal("0")
        assert result["roi"] == Decimal("0")
        assert result["max_drawdown"] == Decimal("0")
        assert result["matches"] == []
        assert result["pl_curve"] == []

    def test_match_with_none_odds_skipped(self) -> None:
        """Matches with None for the relevant odd are skipped."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
        )
        assert result["total_jogos"] == 4

    def test_no_filters_includes_all(self) -> None:
        """With no odds filters, all matches with non-null odds are included."""
        result = run_backtest(
            tipo_back="HOME",
        )
        assert result["total_jogos"] == 4

    # ------------------------------------------------------------------
    # Drawdown calculation
    # ------------------------------------------------------------------

    def test_drawdown_tracks_peak_to_trough(self) -> None:
        """Create a sequence where P&L goes up then down to verify drawdown."""
        Match.objects.all().delete()

        Match.objects.create(
            date=date(2024, 2, 1), home="A", away="B",
            ft_result="H", odd_home=Decimal("1.50"),
        )
        Match.objects.create(
            date=date(2024, 2, 2), home="C", away="D",
            ft_result="H", odd_home=Decimal("2.00"),
        )
        Match.objects.create(
            date=date(2024, 2, 3), home="E", away="F",
            ft_result="D", odd_home=Decimal("1.80"),
        )
        Match.objects.create(
            date=date(2024, 2, 4), home="G", away="H",
            ft_result="A", odd_home=Decimal("3.00"),
        )

        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
        )

        assert result["total_jogos"] == 4
        assert result["verdes"] == 2
        assert result["vermelhas"] == 2
        assert result["profit_total"] == Decimal("-0.50")
        assert result["max_drawdown"] == Decimal("2.00")

    # ------------------------------------------------------------------
    # Curve data
    # ------------------------------------------------------------------

    def test_pl_curve_length_matches_total(self) -> None:
        """pl_curve, drawdown_curve, and labels should have one entry per bet."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
        )
        n = result["total_jogos"]
        assert len(result["pl_curve"]) == n
        assert len(result["drawdown_curve"]) == n
        assert len(result["labels"]) == n
        assert len(result["matches"]) == n

    def test_pl_curve_last_value_equals_profit_total(self) -> None:
        """The last value of pl_curve should equal profit_total."""
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
        )
        if result["pl_curve"]:
            assert Decimal(str(result["pl_curve"][-1])) == result["profit_total"]

    # ------------------------------------------------------------------
    # Queryset pre-filtering
    # ------------------------------------------------------------------

    def test_queryset_param_is_used(self) -> None:
        """When queryset is provided, only those matches are used."""
        qs = Match.objects.filter(home="Team A")
        result = run_backtest(
            tipo_back="HOME",
            odd_home_min=Decimal("1.01"),
            odd_home_max=Decimal("100.00"),
            queryset=qs,
        )
        assert result["total_jogos"] == 1
        assert result["matches"][0]["match"].home == "Team A"
