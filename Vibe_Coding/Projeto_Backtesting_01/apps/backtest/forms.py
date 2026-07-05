from decimal import Decimal

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.backtest.models import Strategy


class BacktestForm(forms.Form):
    """Main backtest execution form with 5 individual odds filters."""

    TIPO_BACK_CHOICES = [
        ("HOME", "Back Home"),
        ("DRAW", "Back Draw"),
        ("AWAY", "Back Away"),
    ]

    strategy = forms.ModelChoiceField(
        queryset=Strategy.objects.none(),
        required=False,
        label="Estratégia Salva",
    )
    tipo_back = forms.ChoiceField(
        choices=TIPO_BACK_CHOICES,
        initial="HOME",
        label="Tipo de Back",
    )

    # 5 individual odds filters — all optional
    odd_home_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Home Mín.",
    )
    odd_home_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Home Máx.",
    )
    odd_draw_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Draw Mín.",
    )
    odd_draw_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Draw Máx.",
    )
    odd_away_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Away Mín.",
    )
    odd_away_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Away Máx.",
    )
    odd_over25_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Over 2.5 Mín.",
    )
    odd_over25_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="Over 2.5 Máx.",
    )
    odd_btts_min = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="BTTS Mín.",
    )
    odd_btts_max = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.01")), MaxValueValidator(Decimal("100.00"))],
        label="BTTS Máx.",
    )

    data_inicio = forms.DateField(
        required=False,
        label="Data Início",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_fim = forms.DateField(
        required=False,
        label="Data Fim",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    liga = forms.CharField(
        required=False,
        max_length=200,
        label="Liga",
        widget=forms.TextInput(attrs={"placeholder": "Ex: Premier League"}),
    )
    salvar_estrategia = forms.BooleanField(
        required=False,
        label="Salvar como estratégia",
    )
    nome_estrategia = forms.CharField(
        required=False,
        max_length=100,
        label="Nome da Estratégia",
        widget=forms.TextInput(attrs={"placeholder": "Ex: Home 1.50-3.00"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["strategy"].queryset = Strategy.objects.filter(user=user)

    def clean_nome_estrategia(self) -> str | None:
        salvar = self.cleaned_data.get("salvar_estrategia")
        nome = self.cleaned_data.get("nome_estrategia", "").strip()
        if salvar and not nome:
            raise forms.ValidationError("Informe um nome para a estratégia.")
        return nome if nome else None

    def clean(self):
        cleaned = super().clean()
        pairs = [
            ("odd_home_min", "odd_home_max"),
            ("odd_draw_min", "odd_draw_max"),
            ("odd_away_min", "odd_away_max"),
            ("odd_over25_min", "odd_over25_max"),
            ("odd_btts_min", "odd_btts_max"),
        ]
        for min_key, max_key in pairs:
            mn = cleaned.get(min_key)
            mx = cleaned.get(max_key)
            if mn and mx and mn > mx:
                self.add_error(min_key, "Mín. não pode ser maior que a Máx.")
        return cleaned


class StrategyForm(forms.ModelForm):
    """Form for creating and editing a saved strategy."""

    class Meta:
        model = Strategy
        fields = ["nome", "tipo_back", "odd_min", "odd_max"]
        labels = {
            "nome": "Nome",
            "tipo_back": "Tipo de Back",
            "odd_min": "Odd Mínima",
            "odd_max": "Odd Máxima",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Ex: Home Seguro"}),
            "tipo_back": forms.Select(),
            "odd_min": forms.NumberInput(attrs={"step": "0.01", "min": "1.01"}),
            "odd_max": forms.NumberInput(attrs={"step": "0.01", "min": "1.01"}),
        }

    def clean(self):
        cleaned = super().clean()
        odd_min = cleaned.get("odd_min")
        odd_max = cleaned.get("odd_max")
        if odd_min and odd_max and odd_min > odd_max:
            self.add_error("odd_min", "Odd mínima não pode ser maior que a odd máxima.")
        return cleaned
