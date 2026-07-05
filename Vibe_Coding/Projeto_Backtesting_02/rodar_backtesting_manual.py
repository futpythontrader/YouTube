# -*- coding: utf-8 -*-
"""
Backtesting Manual Bet365
=========================

Fluxo:
  1. Le o CSV local gerado por baixar_base_bet365_csv.py
  2. Calcula colunas de lucro (Profit_*) para todas as estrategias
  3. Usuario escolhe a estrategia
  4. Lista todas as features numericas com o min/max real dos dados
  5. Usuario escolhe quais filtrar e digita min/max (Enter = padrao)
  6. Aplica filtros, divide em 4 blocos cronologicos de 25% cada
  7. Exibe testes estatisticos e resultado APROVADO / REPROVADO
  8. Plota grafico de lucro acumulado
  9. Pergunta se quer ajustar filtros, trocar estrategia ou sair

Para atualizar a base: python baixar_base_bet365_csv.py
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm, t, ttest_1samp

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

CSV_PATH = "base_bet365.csv"
DEFAULT_STRATEGY = "Under25_FT"


# =============================================================================
# Utilidades
# =============================================================================

def drop_reset_index(df):
    df = df.dropna().reset_index(drop=True)
    df.index += 1
    return df


# =============================================================================
# Testes Estatisticos
# =============================================================================

def runs_test(profits):
    signs = [1 if x > 0 else 0 for x in profits]
    n = len(signs)
    if n < 2:
        return 0, 1.0
    n1 = sum(signs)
    n2 = n - n1
    if n1 == 0 or n2 == 0:
        return 0, 1.0
    runs = 1
    for i in range(1, n):
        if signs[i] != signs[i - 1]:
            runs += 1
    mean_runs = 1 + (2 * n1 * n2) / float(n)
    var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (float(n) ** 2 * (n - 1))
    if var_runs <= 0:
        return 0, 1.0
    z = (runs - mean_runs) / np.sqrt(var_runs)
    p = 2 * (1 - norm.cdf(abs(z)))
    return z, p


def max_drawdown(profits):
    arr = np.asarray(profits)
    if len(arr) == 0:
        return 0.0
    cumsum = np.cumsum(arr)
    runmax = np.maximum.accumulate(cumsum)
    return float(np.max(runmax - cumsum))


def bootstrap_mean_ci(data, n_bootstrap=2000, alpha=0.05):
    rng = np.random.default_rng(seed=42)
    arr = np.asarray(data)
    n_data = len(arr)
    if n_data < 2:
        v = float(np.mean(arr)) if n_data > 0 else 0.0
        return v, v, v
    boot_means = np.sort([
        np.mean(rng.choice(arr, size=n_data, replace=True))
        for _ in range(n_bootstrap)
    ])
    lo = int((alpha / 2) * n_bootstrap)
    hi = int((1 - alpha / 2) * n_bootstrap)
    return float(np.mean(boot_means)), float(boot_means[lo]), float(boot_means[hi])


def monte_carlo_simulation_test(profits, n_simulations=2000):
    rng = np.random.default_rng(seed=42)
    arr = np.asarray(profits)
    if len(arr) == 0:
        return 0.0, 0.0
    sim_final = np.array([
        rng.choice(arr, size=len(arr), replace=True).sum()
        for _ in range(n_simulations)
    ])
    return float(np.mean(sim_final)), float(np.mean(sim_final > 0))


def check_all_tests(*blocos, verbose=True):
    df_all = pd.concat(list(blocos), ignore_index=True)
    arr = df_all["Profit"].values
    n = len(arr)

    if n < 20:
        if verbose:
            print("\n  POUCOS DADOS (N < 20) - testes nao aplicaveis.")
        return False, {}

    alpha_ = 0.05

    _, p_t = ttest_1samp(arr, 0, alternative="greater")
    mean_p = np.mean(arr)
    std_p  = np.std(arr, ddof=1)
    ci_lower = -np.inf
    if n > 1 and std_p > 0:
        ci_lower = mean_p - t.ppf(1 - alpha_, n - 1) * std_p / np.sqrt(n)
    pass_t = (p_t < alpha_) and (ci_lower > 0)

    _, p_runs = runs_test(arr)
    pass_runs = p_runs >= alpha_

    _, bs_low, _ = bootstrap_mean_ci(arr)
    pass_bs = bs_low > 0

    _, prob_plus = monte_carlo_simulation_test(arr)
    pass_mc = prob_plus >= 0.8

    dd    = max_drawdown(arr)
    total = float(arr.sum())
    dd_lim = 0.5 * abs(total) if total != 0 else np.inf
    pass_dd = dd < dd_lim

    passou = pass_t and pass_runs and pass_bs and pass_mc and pass_dd

    if verbose:
        def lbl(ok):
            return "APROVADO " if ok else "REPROVADO"
        linha = "=" * 57
        print("\n" + linha)
        print("  TESTES ESTATISTICOS")
        print(linha)
        print(f"  Teste T        : {lbl(pass_t)}  (p={p_t:.4f}  IC_inf={ci_lower:.4f})")
        print(f"  Runs Test      : {lbl(pass_runs)}  (p={p_runs:.4f})")
        print(f"  Bootstrap 95%  : {lbl(pass_bs)}  (IC_inf={bs_low:.4f})")
        print(f"  Monte Carlo    : {lbl(pass_mc)}  (Prob>0={prob_plus:.2f})")
        print(f"  Max Drawdown   : {lbl(pass_dd)}  (DD={dd:.2f}  limite={dd_lim:.2f})")
        print("-" * 57)
        res_txt = ">>>  APROVADO  <<<" if passou else ">>>  REPROVADO  <<<"
        print(f"  RESULTADO FINAL: {res_txt}")
        print(linha)

    return passou, {
        "pass_t": pass_t, "pass_runs": pass_runs,
        "pass_bs": pass_bs, "pass_mc": pass_mc, "pass_dd": pass_dd,
        "n": n, "lucro": total,
    }


# =============================================================================
# Plotagem
# =============================================================================

def plot_results(df_dict, title):
    fig, ax = plt.subplots(figsize=(15, 7))
    for name, df in df_dict.items():
        if not df.empty:
            df_p   = df.reset_index(drop=True)
            profit = df_p["Profit"].sum()
            n      = len(df_p)
            roi    = profit / n * 100 if n > 0 else 0
            label  = f"{name}  |  N={n}  Profit={profit:.2f}  ROI={roi:.2f}%"
            ax.plot(df_p["Profit"].cumsum(), label=label)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Numero de Entradas")
    ax.set_ylabel("Lucro Acumulado (Stakes)")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.45)
    plt.tight_layout()
    plt.show()


# =============================================================================
# Preparar base: lê CSV, calcula variáveis derivadas e colunas Profit_*
# =============================================================================

def _rolling_mean_std(df, group_col, val_col, n_win, n_per, prefix):
    """Calcula média e desvio padrão rolling por grupo, com shift(1) para evitar leakage."""
    df[f"Media_{prefix}"]   = (df.groupby(group_col)[val_col]
                                 .rolling(window=n_win, min_periods=n_per).mean()
                                 .reset_index(0, drop=True))
    df[f"DesvPad_{prefix}"] = (df.groupby(group_col)[val_col]
                                 .rolling(window=n_win, min_periods=n_per).std()
                                 .reset_index(0, drop=True))
    df[f"Media_{prefix}"]   = df.groupby(group_col)[f"Media_{prefix}"].shift(1)
    df[f"DesvPad_{prefix}"] = df.groupby(group_col)[f"DesvPad_{prefix}"].shift(1)
    df[f"CV_{prefix}"]      = np.where(df[f"Media_{prefix}"] == 0, 0,
                                        df[f"DesvPad_{prefix}"] / df[f"Media_{prefix}"])
    return df


def prepare_base(csv_path=CSV_PATH):
    print(f"\nLendo base: {csv_path}")
    df = pd.read_csv(csv_path)
    df.fillna(0, inplace=True)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    sort_cols = [c for c in ["Date", "Time"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols).reset_index(drop=True)
        df.index += 1

    n_win = 5
    n_per = 5

    # ------------------------------------------------------------------
    # Probabilidades implícitas
    # ------------------------------------------------------------------
    df["p_H"] = 1 / df["Odd_H_FT"]
    df["p_D"] = 1 / df["Odd_D_FT"]
    df["p_A"] = 1 / df["Odd_A_FT"]

    # ------------------------------------------------------------------
    # Coeficiente de Variação das Odds Match Odds
    # ------------------------------------------------------------------
    odds_mo = df[["Odd_H_FT", "Odd_D_FT", "Odd_A_FT"]]
    df["CV_Odds"] = odds_mo.std(axis=1) / odds_mo.mean(axis=1)

    # ------------------------------------------------------------------
    # Proporções entre odds
    # ------------------------------------------------------------------
    df["H_D"] = df["Odd_H_FT"] / df["Odd_D_FT"]
    df["H_A"] = df["Odd_H_FT"] / df["Odd_A_FT"]
    df["D_H"] = df["Odd_D_FT"] / df["Odd_H_FT"]
    df["D_A"] = df["Odd_D_FT"] / df["Odd_A_FT"]
    df["A_H"] = df["Odd_A_FT"] / df["Odd_H_FT"]
    df["A_D"] = df["Odd_A_FT"] / df["Odd_D_FT"]

    # ------------------------------------------------------------------
    # Diferenças absolutas entre odds
    # ------------------------------------------------------------------
    df["DifAbs_HomeAway"] = np.abs(df["Odd_H_FT"] - df["Odd_A_FT"])
    df["DifAbs_HomeDraw"] = np.abs(df["Odd_H_FT"] - df["Odd_D_FT"])
    df["DifAbs_DrawAway"] = np.abs(df["Odd_D_FT"] - df["Odd_A_FT"])

    # ------------------------------------------------------------------
    # Ângulo de disparidade entre odds
    # ------------------------------------------------------------------
    df["Angle_HomeAway"] = np.degrees(np.arctan((df["Odd_A_FT"] - df["Odd_H_FT"]) / 2))
    df["Angle_HomeDraw"] = np.degrees(np.arctan((df["Odd_D_FT"] - df["Odd_H_FT"]) / 2))
    df["Angle_DrawAway"] = np.degrees(np.arctan((df["Odd_A_FT"] - df["Odd_D_FT"]) / 2))

    # ------------------------------------------------------------------
    # Diferenças percentuais entre odds
    # ------------------------------------------------------------------
    df["DifPer_HomeAway"] = np.abs(df["Odd_H_FT"] - df["Odd_A_FT"]) / df["Odd_A_FT"]
    df["DifPer_HomeDraw"] = np.abs(df["Odd_H_FT"] - df["Odd_D_FT"]) / df["Odd_D_FT"]
    df["DifPer_DrawAway"] = np.abs(df["Odd_D_FT"] - df["Odd_A_FT"]) / df["Odd_A_FT"]

    # ------------------------------------------------------------------
    # Pontos (PPG) rolling
    # ------------------------------------------------------------------
    df["Ptos_H"] = np.where(df["Goals_H_FT"] > df["Goals_A_FT"], 3,
                   np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 0))
    df["Ptos_A"] = np.where(df["Goals_H_FT"] > df["Goals_A_FT"], 0,
                   np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 3))
    df = _rolling_mean_std(df, "Home", "Ptos_H", n_win, n_per, "Ptos_H")
    df = _rolling_mean_std(df, "Away", "Ptos_A", n_win, n_per, "Ptos_A")

    # ------------------------------------------------------------------
    # Gols marcados rolling
    # ------------------------------------------------------------------
    df = _rolling_mean_std(df, "Home", "Goals_H_FT", n_win, n_per, "GM_H")
    df = _rolling_mean_std(df, "Away", "Goals_A_FT",  n_win, n_per, "GM_A")

    # ------------------------------------------------------------------
    # Gols sofridos rolling
    # ------------------------------------------------------------------
    df = _rolling_mean_std(df, "Home", "Goals_A_FT", n_win, n_per, "GS_H")
    df = _rolling_mean_std(df, "Away", "Goals_H_FT",  n_win, n_per, "GS_A")

    # ------------------------------------------------------------------
    # Saldo de gols rolling
    # ------------------------------------------------------------------
    df["SG_H"] = df["Goals_H_FT"] - df["Goals_A_FT"]
    df["SG_A"] = df["Goals_A_FT"] - df["Goals_H_FT"]
    df = _rolling_mean_std(df, "Home", "SG_H", n_win, n_per, "SG_H")
    df = _rolling_mean_std(df, "Away", "SG_A", n_win, n_per, "SG_A")

    # ------------------------------------------------------------------
    # SG ponderado pela prob do próprio time (SG_01)
    # ------------------------------------------------------------------
    df["SG_H_01"] = (df["Goals_H_FT"] - df["Goals_A_FT"]) / df["p_H"]
    df["SG_A_01"] = (df["Goals_A_FT"] - df["Goals_H_FT"]) / df["p_A"]
    df = _rolling_mean_std(df, "Home", "SG_H_01", n_win, n_per, "SG_H_01")
    df = _rolling_mean_std(df, "Away", "SG_A_01", n_win, n_per, "SG_A_01")

    # ------------------------------------------------------------------
    # SG ponderado pela prob do adversário (SG_02)
    # ------------------------------------------------------------------
    df["SG_H_02"] = (df["Goals_H_FT"] - df["Goals_A_FT"]) / df["p_A"]
    df["SG_A_02"] = (df["Goals_A_FT"] - df["Goals_H_FT"]) / df["p_H"]
    df = _rolling_mean_std(df, "Home", "SG_H_02", n_win, n_per, "SG_H_02")
    df = _rolling_mean_std(df, "Away", "SG_A_02", n_win, n_per, "SG_A_02")

    # ------------------------------------------------------------------
    # Valor do Gol (VG)
    # ------------------------------------------------------------------
    df["VG_H"] = df["Goals_H_FT"] * df["p_A"]
    df["VG_A"] = df["Goals_A_FT"] * df["p_H"]
    df = _rolling_mean_std(df, "Home", "VG_H", n_win, n_per, "VG_H")
    df = _rolling_mean_std(df, "Away", "VG_A", n_win, n_per, "VG_A")

    # ------------------------------------------------------------------
    # Custo do Gol — versão 00 (p / gols)
    # ------------------------------------------------------------------
    df["CG_H_00"] = df["p_H"] / df["Goals_H_FT"]
    df["CG_A_00"] = df["p_A"] / df["Goals_A_FT"]
    df.replace(np.inf, 1, inplace=True)
    df = _rolling_mean_std(df, "Home", "CG_H_00", n_win, n_per, "CG_H_00")
    df = _rolling_mean_std(df, "Away", "CG_A_00", n_win, n_per, "CG_A_00")

    # ------------------------------------------------------------------
    # Custo do Gol — versão 01 (gols / p)
    # ------------------------------------------------------------------
    df["CG_H_01"] = df["Goals_H_FT"] / df["p_H"]
    df["CG_A_01"] = df["Goals_A_FT"] / df["p_A"]
    df = _rolling_mean_std(df, "Home", "CG_H_01", n_win, n_per, "CG_H_01")
    df = _rolling_mean_std(df, "Away", "CG_A_01", n_win, n_per, "CG_A_01")

    # ------------------------------------------------------------------
    # Custo do Gol — versão 02 (média de gols e p)
    # ------------------------------------------------------------------
    df["CG_H_02"] = (df["Goals_H_FT"] / 2) + (df["p_H"] / 2)
    df["CG_A_02"] = (df["Goals_A_FT"] / 2) + (df["p_A"] / 2)
    df = _rolling_mean_std(df, "Home", "CG_H_02", n_win, n_per, "CG_H_02")
    df = _rolling_mean_std(df, "Away", "CG_A_02", n_win, n_per, "CG_A_02")

    # ------------------------------------------------------------------
    # Remove colunas intermediárias (desvio-padrão e valores brutos)
    # ------------------------------------------------------------------
    drop_cols = [c for c in df.columns if c.startswith("DesvPad_")
                 or c in {"Ptos_H", "Ptos_A",
                          "SG_H", "SG_A",
                          "SG_H_01", "SG_A_01", "SG_H_02", "SG_A_02",
                          "VG_H", "VG_A",
                          "CG_H_00", "CG_A_00", "CG_H_01", "CG_A_01",
                          "CG_H_02", "CG_A_02"}]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    df = drop_reset_index(df)

    # ------------------------------------------------------------------
    # Mercados HT — 1X2
    # ------------------------------------------------------------------
    if "Goals_H_HT" in df.columns:
        df["Back_Home_HT"] = np.where(df["Goals_H_HT"] >  df["Goals_A_HT"], 1, 0)
        df["Back_Draw_HT"] = np.where(df["Goals_H_HT"] == df["Goals_A_HT"], 1, 0)
        df["Back_Away_HT"] = np.where(df["Goals_H_HT"] <  df["Goals_A_HT"], 1, 0)
        if "Odd_H_HT" in df.columns:
            df["Profit_Back_Home_HT"] = np.where(df["Back_Home_HT"] == 1, df["Odd_H_HT"] - 1, -1)
        if "Odd_D_HT" in df.columns:
            df["Profit_Back_Draw_HT"] = np.where(df["Back_Draw_HT"] == 1, df["Odd_D_HT"] - 1, -1)
        if "Odd_A_HT" in df.columns:
            df["Profit_Back_Away_HT"] = np.where(df["Back_Away_HT"] == 1, df["Odd_A_HT"] - 1, -1)

        goals_ht = df["Goals_H_HT"] + df["Goals_A_HT"]
        for line, tag in [(0, "05"), (1, "15"), (2, "25")]:
            over  = (goals_ht > line).astype(int)
            col_o = f"Odd_Over{tag}_HT"
            col_u = f"Odd_Under{tag}_HT"
            if col_o in df.columns:
                df[f"Profit_Over{tag}_HT"]  = np.where(over == 1, df[col_o] - 1, -1)
            if col_u in df.columns:
                df[f"Profit_Under{tag}_HT"] = np.where(over == 0, df[col_u] - 1, -1)

    # ------------------------------------------------------------------
    # Mercados FT — 1X2 Back + Lay (via Double Chance)
    # ------------------------------------------------------------------
    df["Back_Home_FT"] = np.where(df["Goals_H_FT"] >  df["Goals_A_FT"], 1, 0)
    df["Back_Draw_FT"] = np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 0)
    df["Back_Away_FT"] = np.where(df["Goals_H_FT"] <  df["Goals_A_FT"], 1, 0)

    df["Profit_Back_Home_FT"] = np.where(df["Back_Home_FT"] == 1, df["Odd_H_FT"] - 1, -1)
    df["Profit_Back_Draw_FT"] = np.where(df["Back_Draw_FT"] == 1, df["Odd_D_FT"] - 1, -1)
    df["Profit_Back_Away_FT"] = np.where(df["Back_Away_FT"] == 1, df["Odd_A_FT"] - 1, -1)

    if "Odd_DC_X2" in df.columns:
        df["Profit_Lay_Home_FT"] = np.where(df["Back_Home_FT"] == 0, df["Odd_DC_X2"] - 1, -1)
    if "Odd_DC_12" in df.columns:
        df["Profit_Lay_Draw_FT"] = np.where(df["Back_Draw_FT"] == 0, df["Odd_DC_12"] - 1, -1)
    if "Odd_DC_1X" in df.columns:
        df["Profit_Lay_Away_FT"] = np.where(df["Back_Away_FT"] == 0, df["Odd_DC_1X"] - 1, -1)

    # ------------------------------------------------------------------
    # Over / Under FT
    # ------------------------------------------------------------------
    goals_ft = df["Goals_H_FT"] + df["Goals_A_FT"]
    for line, tag in [(0, "05"), (1, "15"), (2, "25"), (3, "35"), (4, "45")]:
        over  = (goals_ft > line).astype(int)
        col_o = f"Odd_Over{tag}_FT"
        col_u = f"Odd_Under{tag}_FT"
        if col_o in df.columns:
            df[f"Profit_Over{tag}_FT"]  = np.where(over == 1, df[col_o] - 1, -1)
        if col_u in df.columns:
            df[f"Profit_Under{tag}_FT"] = np.where(over == 0, df[col_u] - 1, -1)

    # ------------------------------------------------------------------
    # BTTS
    # ------------------------------------------------------------------
    btts = ((df["Goals_H_FT"] > 0) & (df["Goals_A_FT"] > 0)).astype(int)
    if "Odd_BTTS_Yes" in df.columns:
        df["Profit_BTTS_Yes"] = np.where(btts == 1, df["Odd_BTTS_Yes"] - 1, -1)
    if "Odd_BTTS_No" in df.columns:
        df["Profit_BTTS_No"]  = np.where(btts == 0, df["Odd_BTTS_No"]  - 1, -1)

    df = drop_reset_index(df)

    n_mercados = len([c for c in df.columns if c.startswith("Profit_")])
    print(f"Base pronta: {len(df)} jogos  |  {n_mercados} mercados  |  {len(df.columns)} colunas totais.")
    return df


# =============================================================================
# Interface com o usuario
# =============================================================================

_EXCLUIR_FILTRO = {
    "Profit", "Date", "Time",
    # Variáveis calculadas PÓS-jogo — não usar como filtro (data leakage)
    "Back_Home_FT", "Back_Draw_FT", "Back_Away_FT",
    "Back_Home_HT", "Back_Draw_HT", "Back_Away_HT",
    "OverUnder05_HT", "OverUnder15_HT", "OverUnder25_HT",
    "OverUnder05_FT", "OverUnder15_FT", "OverUnder25_FT",
    "OverUnder35_FT", "OverUnder45_FT",
    "BTTS",
    "Goals_H_FT", "Goals_A_FT", "Goals_H_HT", "Goals_A_HT",
}


def _features_numericas(df):
    return sorted([
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in _EXCLUIR_FILTRO and not c.startswith("Profit_")
    ])


def escolher_estrategia(df):
    estrategias = sorted([c.replace("Profit_", "") for c in df.columns if c.startswith("Profit_")])
    if not estrategias:
        raise ValueError("Nenhuma coluna Profit_* encontrada na base.")

    linha = "=" * 57
    print("\n" + linha)
    print("  ESTRATEGIAS DISPONIVEIS")
    print(linha)
    for s in estrategias:
        print(f"  {s}")
    print(linha)

    sugestao = DEFAULT_STRATEGY if DEFAULT_STRATEGY in estrategias else estrategias[0]
    escolha  = input(f"\nDigite a estrategia  [Enter = {sugestao}]: ").strip()
    strategy = escolha if escolha in estrategias else sugestao
    print(f"  Selecionada: {strategy}")
    return strategy


def mostrar_features(features):
    linha = "=" * 70
    print("\n" + linha)
    print("  FEATURES DISPONIVEIS PARA FILTRO")
    print(linha)
    metade = (len(features) + 1) // 2
    for i in range(metade):
        esq = f"  {i+1:03d}  {features[i]}"
        j   = i + metade
        if j < len(features):
            print(f"{esq:<40}  {j+1:03d}  {features[j]}")
        else:
            print(esq)
    print(linha)


def escolher_features(features):
    entrada = input(
        "\nNumeros ou nomes das features (virgula). Enter = sem filtro: "
    ).strip()
    if not entrada:
        return []
    mapa = {str(i + 1): f for i, f in enumerate(features)}
    escolhidas = []
    for token in [tk.strip() for tk in entrada.split(",") if tk.strip()]:
        if token in mapa:
            escolhidas.append(mapa[token])
        elif token in features:
            escolhidas.append(token)
        else:
            print(f"  Ignorado: {token}")
    return list(dict.fromkeys(escolhidas))


def coletar_filtros(df, features_escolhidas):
    filtros = {}
    for feature in features_escolhidas:
        serie = df[feature].dropna()
        if serie.empty:
            continue
        vmin = float(serie.min())
        vmax = float(serie.max())
        print(f"\n  {feature}   (min={vmin:.4f}  max={vmax:.4f})")
        min_in = input(f"    Minimo  [Enter = {vmin:.4f}]: ").strip()
        max_in = input(f"    Maximo  [Enter = {vmax:.4f}]: ").strip()
        try:
            valor_min = float(min_in) if min_in else vmin
            valor_max = float(max_in) if max_in else vmax
        except ValueError:
            print("    Valor invalido. Usando padrao.")
            valor_min, valor_max = vmin, vmax
        if valor_min > valor_max:
            valor_min, valor_max = valor_max, valor_min
        filtros[feature] = (valor_min, valor_max)
    return filtros


def aplicar_filtros(df, filtros):
    if not filtros:
        return df.copy()
    mask = pd.Series(True, index=df.index)
    for feature, (vmin, vmax) in filtros.items():
        mask &= df[feature].between(vmin, vmax, inclusive="both")
    return df.loc[mask].copy()


def _resumo_linha(df, label):
    n     = len(df)
    lucro = df["Profit"].sum() if n > 0 else 0.0
    roi   = lucro / n * 100 if n > 0 else 0.0
    print(f"  {label:<18}  N={n:>6}  Profit={lucro:>9.2f}  ROI={roi:>7.2f}%")


# =============================================================================
# Loop principal
# =============================================================================

def main():
    df_base  = prepare_base(CSV_PATH)
    strategy = escolher_estrategia(df_base)
    df_base["Profit"] = df_base[f"Profit_{strategy}"]

    features       = _features_numericas(df_base)
    filtros_atuais = {}

    while True:
        mostrar_features(features)

        if filtros_atuais:
            print("  Filtros ativos:", ", ".join(
                f"{k}=[{v[0]:.4f},{v[1]:.4f}]" for k, v in filtros_atuais.items()
            ))

        features_escolhidas = escolher_features(features)
        if features_escolhidas:
            filtros_atuais = coletar_filtros(df_base, features_escolhidas)
        else:
            filtros_atuais = {}

        df_filtrado = aplicar_filtros(df_base, filtros_atuais)
        n_total     = len(df_filtrado)
        print(f"\n  Jogos apos filtros: {n_total}")

        if n_total < 60:
            print("  Aviso: poucos jogos. Testes podem ser frageis.")
            if input("  Continuar mesmo assim? (s/n): ").strip().lower() != "s":
                continue

        b1_end = int(n_total * 0.25)
        b2_end = int(n_total * 0.50)
        b3_end = int(n_total * 0.75)
        bloco1 = df_filtrado.iloc[:b1_end].copy()
        bloco2 = df_filtrado.iloc[b1_end:b2_end].copy()
        bloco3 = df_filtrado.iloc[b2_end:b3_end].copy()
        bloco4 = df_filtrado.iloc[b3_end:].copy()

        print("\n  Resumo por bloco:")
        _resumo_linha(bloco1,       "Bloco 1 (25%)")
        _resumo_linha(bloco2,       "Bloco 2 (25%)")
        _resumo_linha(bloco3,       "Bloco 3 (25%)")
        _resumo_linha(bloco4,       "Bloco 4 (25%)")
        _resumo_linha(df_filtrado,  "TOTAL")

        check_all_tests(bloco1, bloco2, bloco3, bloco4, verbose=True)

        titulo = f"{strategy}  [{', '.join(filtros_atuais.keys()) or 'sem filtro'}]"
        plot_results(
            {"Bloco 1": bloco1, "Bloco 2": bloco2, "Bloco 3": bloco3, "Bloco 4": bloco4},
            f"Backtesting Manual — {titulo}",
        )
        plot_results(
            {"Total": df_filtrado},
            f"Resultado Consolidado — {titulo}",
        )

        print("\n  O que deseja fazer?")
        print("    [1] Ajustar filtros e rodar novamente")
        print("    [2] Trocar estrategia / mercado")
        print("    [3] Sair")
        opcao = input("  Opcao: ").strip()

        if opcao == "2":
            strategy = escolher_estrategia(df_base)
            df_base["Profit"] = df_base[f"Profit_{strategy}"]
            filtros_atuais = {}
        elif opcao == "3":
            print("  Encerrando.")
            break


if __name__ == "__main__":
    main()
