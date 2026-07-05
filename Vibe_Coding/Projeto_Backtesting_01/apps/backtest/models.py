from django.db import models
from django.db.models import UniqueConstraint


class Match(models.Model):
    """Historical football match imported from FutPythonTrader API."""

    date = models.DateField(db_index=True)
    time = models.TimeField(null=True, blank=True)
    home = models.CharField(max_length=200)
    away = models.CharField(max_length=200)
    ft_goals_h = models.SmallIntegerField(null=True, blank=True)
    ft_goals_a = models.SmallIntegerField(null=True, blank=True)
    ft_result = models.CharField(max_length=10, blank=True, null=True)  # H/D/A
    ht_goals_h = models.SmallIntegerField(null=True, blank=True)
    ht_goals_a = models.SmallIntegerField(null=True, blank=True)
    ht_result = models.CharField(max_length=10, blank=True, null=True)  # H/D/A
    odd_home = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    odd_draw = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    odd_away = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    odd_over25 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    odd_btts = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    league = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    season = models.CharField(max_length=20, blank=True)
    raw_data = models.JSONField(null=True, blank=True)
    importado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["home"]),
            models.Index(fields=["away"]),
            models.Index(fields=["league"]),
        ]
        constraints = [
            UniqueConstraint(fields=["date", "home", "away"], name="unique_match"),
        ]
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"

    def __str__(self) -> str:
        return f"{self.home} vs {self.away} ({self.date})"


class Strategy(models.Model):
    """User's saved backtesting strategy."""

    TIPO_CHOICES = [
        ("HOME", "Back Home"),
        ("DRAW", "Back Draw"),
        ("AWAY", "Back Away"),
    ]

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="strategies"
    )
    nome = models.CharField(max_length=100)
    tipo_back = models.CharField(max_length=4, choices=TIPO_CHOICES)
    odd_min = models.DecimalField(max_digits=6, decimal_places=2)
    odd_max = models.DecimalField(max_digits=6, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criada_em"]
        constraints = [
            UniqueConstraint(
                fields=["user", "nome"], name="unique_user_strategy"
            ),
        ]
        verbose_name = "Estratégia"
        verbose_name_plural = "Estratégias"

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_tipo_back_display()})"


class BacktestResult(models.Model):
    """Saved result of a backtest run."""

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="backtest_results"
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backtest_results",
    )
    total_jogos = models.IntegerField()
    verdes = models.IntegerField()
    vermelhas = models.IntegerField()
    profit_total = models.DecimalField(max_digits=10, decimal_places=2)
    win_rate = models.DecimalField(max_digits=6, decimal_places=2)
    roi = models.DecimalField(max_digits=8, decimal_places=2)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2)
    odd_min_usada = models.DecimalField(max_digits=6, decimal_places=2)
    odd_max_usada = models.DecimalField(max_digits=6, decimal_places=2)
    TIPO_CHOICES = [
        ("HOME", "Back Home"),
        ("DRAW", "Back Draw"),
        ("AWAY", "Back Away"),
    ]

    tipo_back_usado = models.CharField(max_length=4, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Resultado de Backtest"
        verbose_name_plural = "Resultados de Backtest"

    def __str__(self) -> str:
        return f"Backtest #{self.id} — {self.user} ({self.criado_em:%d/%m/%Y})"
