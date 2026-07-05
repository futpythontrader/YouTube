import json

from django.http import JsonResponse
from django.shortcuts import render

from .data_processor import (
    aplicar_filtros,
    check_all_tests,
    get_base,
    get_features,
    get_strategies,
    resumo_bloco,
)


def home(request):
    try:
        df = get_base()
    except Exception as e:
        return render(request, "backtester/home.html", {
            "estrategias": [],
            "features": [],
            "total_jogos": 0,
            "strategy": "",
            "filtros_atuais": {},
            "error": str(e),
        })

    estrategias = get_strategies(df)
    features = get_features(df)

    features_data = []
    for f in features:
        serie = df[f].dropna()
        if not serie.empty:
            features_data.append({
                "name": f,
                "min": round(float(serie.min()), 4),
                "max": round(float(serie.max()), 4),
            })

    context = {
        "estrategias": estrategias,
        "features": features_data,
        "total_jogos": len(df),
        "strategy": request.session.get("strategy", ""),
        "filtros_atuais": request.session.get("filtros_atuais", {}),
    }
    return render(request, "backtester/home.html", context)


def select_strategy(request):
    if request.method == "POST":
        strategy = request.POST.get("strategy", "")
        df = get_base()
        estrategias = get_strategies(df)
        if strategy in estrategias:
            request.session["strategy"] = strategy
            request.session["filtros_atuais"] = {}
    return home(request)


def apply_filters(request):
    if request.method == "POST":
        filtros = {}
        for key in request.POST:
            if key.startswith("feature_min_"):
                feature = key.replace("feature_min_", "")
                min_val = request.POST[key]
                max_val = request.POST.get(f"feature_max_{feature}", "")
                if min_val and max_val:
                    try:
                        filtros[feature] = (float(min_val), float(max_val))
                    except ValueError:
                        pass
        request.session["filtros_atuais"] = {k: list(v) for k, v in filtros.items()}
    return home(request)


def clear_filters(request):
    request.session["filtros_atuais"] = {}
    return home(request)


def run_backtest(request):
    df = get_base()
    strategy = request.session.get("strategy", "")
    filtros_session = request.session.get("filtros_atuais", {})

    if not strategy:
        return JsonResponse({"error": "Selecione uma estrategia primeiro."}, status=400)

    if f"Profit_{strategy}" not in df.columns:
        return JsonResponse({"error": f"Estrategia {strategy} nao encontrada."}, status=400)

    df = df.copy()
    df["Profit"] = df[f"Profit_{strategy}"]

    filtros = {k: tuple(v) for k, v in filtros_session.items()}
    df_filtrado = aplicar_filtros(df, filtros)
    n_total = len(df_filtrado)

    if n_total < 60:
        warning = "Poucos jogos. Testes podem ser frageis."
    else:
        warning = None

    b1_end = int(n_total * 0.25)
    b2_end = int(n_total * 0.50)
    b3_end = int(n_total * 0.75)
    bloco1 = df_filtrado.iloc[:b1_end]
    bloco2 = df_filtrado.iloc[b1_end:b2_end]
    bloco3 = df_filtrado.iloc[b2_end:b3_end]
    bloco4 = df_filtrado.iloc[b3_end:]

    b1 = resumo_bloco(bloco1)
    b2 = resumo_bloco(bloco2)
    b3 = resumo_bloco(bloco3)
    b4 = resumo_bloco(bloco4)
    total_resumo = resumo_bloco(df_filtrado)

    passou, testes = check_all_tests(bloco1, bloco2, bloco3, bloco4)

    passou = bool(passou)
    for k in list(testes.keys()):
        v = testes[k]
        if hasattr(v, 'item'):
            testes[k] = v.item()
        elif isinstance(v, float):
            testes[k] = round(float(v), 4) if k not in ('n',) else int(v)

    def cumsum_data(df_bloco):
        if df_bloco.empty:
            return []
        arr = df_bloco["Profit"].cumsum().tolist()
        return [round(float(x), 4) for x in arr]

    chart_data = {
        "bloco1": cumsum_data(bloco1),
        "bloco2": cumsum_data(bloco2),
        "bloco3": cumsum_data(bloco3),
        "bloco4": cumsum_data(bloco4),
        "total": cumsum_data(df_filtrado),
    }

    return JsonResponse({
        "strategy": strategy,
        "filtros": {k: list(v) for k, v in filtros.items()},
        "n_total": n_total,
        "warning": warning,
        "blocos": {"b1": b1, "b2": b2, "b3": b3, "b4": b4},
        "total": total_resumo,
        "aprovado": passou,
        "testes": testes,
        "chart_data": chart_data,
    })
