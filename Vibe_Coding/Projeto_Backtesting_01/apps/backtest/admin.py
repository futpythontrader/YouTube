from django.contrib import admin

from apps.backtest.models import BacktestResult, Match, Strategy


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "time",
        "home",
        "away",
        "ft_goals_h",
        "ft_goals_a",
        "ft_result",
        "odd_home",
        "odd_draw",
        "odd_away",
        "odd_over25",
        "odd_btts",
        "league",
        "country",
        "season",
        "importado_em",
    ]
    list_filter = [
        "date",
        "league",
        "country",
        "season",
        "ft_result",
    ]
    search_fields = ["home", "away", "league", "country"]
    ordering = ["-date", "-time"]


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "user",
        "tipo_back",
        "odd_min",
        "odd_max",
        "criada_em",
        "atualizada_em",
    ]
    list_filter = [
        "tipo_back",
        "criada_em",
    ]
    search_fields = ["nome", "user__username", "user__email"]
    ordering = ["-criada_em"]


@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "strategy",
        "total_jogos",
        "verdes",
        "vermelhas",
        "profit_total",
        "win_rate",
        "roi",
        "max_drawdown",
        "tipo_back_usado",
        "criado_em",
    ]
    list_filter = [
        "tipo_back_usado",
        "criado_em",
    ]
    search_fields = ["user__username", "user__email", "strategy__nome"]
    ordering = ["-criado_em"]
