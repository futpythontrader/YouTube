from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.backtest.forms import BacktestForm, StrategyForm
from apps.backtest.models import BacktestResult, Match, Strategy
from apps.backtest.services.backtest_engine import run_backtest as run_engine
from apps.backtest.services.import_service import import_from_api


def _is_htmx(request: HttpRequest) -> bool:
    """Check if the request was made by HTMX."""
    return request.headers.get("HX-Request") == "true"


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@login_required
@never_cache
def dashboard(request: HttpRequest) -> HttpResponse:
    """Main dashboard — backtest form, previous results, and strategy management."""
    strategies = Strategy.objects.filter(user=request.user).order_by("-criada_em")
    previous_results = BacktestResult.objects.filter(
        user=request.user
    ).select_related("strategy").order_by("-criado_em")[:10]

    form = BacktestForm(user=request.user)

    context = {
        "form": form,
        "strategies": strategies,
        "previous_results": previous_results,
        "total_matches": Match.objects.count(),
    }
    return render(request, "backtest/dashboard.html", context)


# ---------------------------------------------------------------------------
# Run Backtest
# ---------------------------------------------------------------------------


@login_required
@require_http_methods(["POST"])
def run_backtest(request: HttpRequest) -> HttpResponse:
    """
    Process the backtest form, run the engine, optionally save strategy
    and backtest result, and return the results partial via HTMX.
    """
    form = BacktestForm(request.POST, user=request.user)

    if not form.is_valid():
        # Return form with errors
        context = {"form": form, "errors": True}
        return render(request, "backtest/partials/_backtest_results.html", context)

    cleaned = form.cleaned_data

    tipo_back: str = cleaned["tipo_back"]
    odd_home_min = cleaned.get("odd_home_min")
    odd_home_max = cleaned.get("odd_home_max")
    odd_draw_min = cleaned.get("odd_draw_min")
    odd_draw_max = cleaned.get("odd_draw_max")
    odd_away_min = cleaned.get("odd_away_min")
    odd_away_max = cleaned.get("odd_away_max")
    odd_over25_min = cleaned.get("odd_over25_min")
    odd_over25_max = cleaned.get("odd_over25_max")
    odd_btts_min = cleaned.get("odd_btts_min")
    odd_btts_max = cleaned.get("odd_btts_max")
    data_inicio = cleaned.get("data_inicio")
    data_fim = cleaned.get("data_fim")
    liga: str | None = cleaned.get("liga")
    salvar_estrategia: bool = cleaned.get("salvar_estrategia", False)
    nome_estrategia: str | None = cleaned.get("nome_estrategia")
    selected_strategy = cleaned.get("strategy")

    # If a saved strategy was selected, override tipo_back (keeps simple strategy model)
    if selected_strategy:
        tipo_back = selected_strategy.tipo_back

    # Build filtered queryset
    matches: QuerySet[Match] = Match.objects.all()

    if data_inicio:
        matches = matches.filter(date__gte=data_inicio)
    if data_fim:
        matches = matches.filter(date__lte=data_fim)
    if liga:
        matches = matches.filter(league__icontains=liga)

    # Run the engine
    result = run_engine(
        tipo_back=tipo_back,
        queryset=matches,
        odd_home_min=odd_home_min,
        odd_home_max=odd_home_max,
        odd_draw_min=odd_draw_min,
        odd_draw_max=odd_draw_max,
        odd_away_min=odd_away_min,
        odd_away_max=odd_away_max,
        odd_over25_min=odd_over25_min,
        odd_over25_max=odd_over25_max,
        odd_btts_min=odd_btts_min,
        odd_btts_max=odd_btts_max,
    )

    # Optionally save as a strategy
    strategy_saved = None
    if salvar_estrategia and nome_estrategia:
        # Use the odds filter matched to tipo_back as the strategy's odds
        if tipo_back == "HOME":
            s_odd_min = odd_home_min or Decimal("1.01")
            s_odd_max = odd_home_max or Decimal("100.00")
        elif tipo_back == "DRAW":
            s_odd_min = odd_draw_min or Decimal("1.01")
            s_odd_max = odd_draw_max or Decimal("100.00")
        else:
            s_odd_min = odd_away_min or Decimal("1.01")
            s_odd_max = odd_away_max or Decimal("100.00")

        strategy_saved, _ = Strategy.objects.get_or_create(
            user=request.user,
            nome=nome_estrategia,
            defaults={
                "tipo_back": tipo_back,
                "odd_min": s_odd_min,
                "odd_max": s_odd_max,
            },
        )

    # Save BacktestResult for history
    BacktestResult.objects.create(
        user=request.user,
        strategy=strategy_saved or selected_strategy,
        total_jogos=result["total_jogos"],
        verdes=result["verdes"],
        vermelhas=result["vermelhas"],
        profit_total=result["profit_total"],
        win_rate=result["win_rate"],
        roi=result["roi"],
        max_drawdown=result["max_drawdown"],
        odd_min_usada=Decimal("0"),
        odd_max_usada=Decimal("0"),
        tipo_back_usado=tipo_back,
    )

    # Last 10 matches for the table
    last_matches = result["matches"][-10:] if result["matches"] else []

    context = {
        "result": result,
        "last_matches": last_matches,
        "tipo_back": tipo_back,
    }
    return render(request, "backtest/partials/_backtest_results.html", context)


# ---------------------------------------------------------------------------
# Backtest Detail
# ---------------------------------------------------------------------------


@login_required
def backtest_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """View a saved backtest result (owner only)."""
    backtest = get_object_or_404(
        BacktestResult.objects.select_related("strategy"),
        pk=pk,
        user=request.user,
    )
    context = {"backtest": backtest}
    return render(request, "backtest/backtest_detail.html", context)


# ---------------------------------------------------------------------------
# Strategy CRUD (HTMX)
# ---------------------------------------------------------------------------


@login_required
def strategy_list(request: HttpRequest) -> HttpResponse:
    """Return the strategy list partial."""
    strategies = Strategy.objects.filter(user=request.user).order_by("-criada_em")
    context = {"strategies": strategies}
    return render(request, "backtest/partials/_strategy_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def strategy_create(request: HttpRequest) -> HttpResponse:
    """Create a new strategy via modal form."""
    if request.method == "POST":
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            messages.success(request, f'Estratégia "{strategy.nome}" criada com sucesso!')
            # Return updated strategy list and close modal via OOB
            strategies = Strategy.objects.filter(user=request.user).order_by("-criada_em")
            return render(
                request,
                "backtest/partials/_strategy_list.html",
                {"strategies": strategies},
            )
    else:
        form = StrategyForm()

    context = {"form": form, "action_url": request.path, "is_create": True}
    return render(request, "backtest/partials/_strategy_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def strategy_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit an existing strategy via modal form (owner only)."""
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)

    if request.method == "POST":
        form = StrategyForm(request.POST, instance=strategy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estratégia "{strategy.nome}" atualizada!')
            strategies = Strategy.objects.filter(user=request.user).order_by("-criada_em")
            return render(
                request,
                "backtest/partials/_strategy_list.html",
                {"strategies": strategies},
            )
    else:
        form = StrategyForm(instance=strategy)

    context = {
        "form": form,
        "strategy": strategy,
        "action_url": request.path,
        "is_create": False,
    }
    return render(request, "backtest/partials/_strategy_form.html", context)


@login_required
@require_http_methods(["DELETE"])
def strategy_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a strategy (owner only)."""
    strategy = get_object_or_404(Strategy, pk=pk, user=request.user)
    nome = strategy.nome
    strategy.delete()
    messages.success(request, f'Estratégia "{nome}" excluída.')
    strategies = Strategy.objects.filter(user=request.user).order_by("-criada_em")
    return render(
        request,
        "backtest/partials/_strategy_list.html",
        {"strategies": strategies},
    )


# ---------------------------------------------------------------------------
# Import Base (API FutPythonTrader)
# ---------------------------------------------------------------------------


@login_required
@require_http_methods(["POST"])
def import_base(request: HttpRequest) -> HttpResponse:
    """Trigger the API import and return status."""
    stats = import_from_api()

    if stats["erros"] < 0:
        # Fatal error codes
        error_messages = {
            -1: "Timeout ao conectar na API FutPythonTrader.",
            -2: "Erro de conexão com a API FutPythonTrader.",
            -3: "Token inválido. Verifique suas credenciais.",
            -4: "API retornou um erro inesperado.",
            -5: "Erro ao processar o CSV retornado pela API.",
        }
        msg = error_messages.get(stats["erros"], "Erro desconhecido na importação.")
        messages.error(request, msg)
    else:
        importados = stats["importados"]
        atualizados = stats["atualizados"]
        erros = stats["erros"]
        messages.success(
            request,
            f"Importação concluída! {importados} novos jogos, "
            f"{atualizados} atualizados, {erros} erros.",
        )

    # Return total match count
    total = Match.objects.count()
    return render(
        request,
        "backtest/partials/_import_status.html",
        {"total_matches": total},
    )
