import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, t, ttest_1samp

warnings.filterwarnings("ignore")

CSV_PATH = Path(__file__).resolve().parent.parent / "base_bet365.csv"


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


def check_all_tests(*blocos):
    df_all = pd.concat(list(blocos), ignore_index=True)
    arr = df_all["Profit"].values
    n = len(arr)

    if n < 20:
        return False, {
            "pass_t": False, "pass_runs": False,
            "pass_bs": False, "pass_mc": False, "pass_dd": False,
            "n": n, "lucro": float(arr.sum()) if n > 0 else 0.0,
            "p_t": 0, "ci_lower": 0, "p_runs": 0, "bs_low": 0,
            "prob_plus": 0, "dd": 0, "dd_lim": 0,
            "warning": "POUCOS DADOS (N < 20) - testes nao aplicaveis."
        }

    alpha_ = 0.05

    _, p_t = ttest_1samp(arr, 0, alternative="greater")
    mean_p = np.mean(arr)
    std_p = np.std(arr, ddof=1)
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

    dd = max_drawdown(arr)
    total = float(arr.sum())
    dd_lim = 0.5 * abs(total) if total != 0 else np.inf
    pass_dd = dd < dd_lim

    passou = pass_t and pass_runs and pass_bs and pass_mc and pass_dd

    return passou, {
        "pass_t": pass_t, "pass_runs": pass_runs,
        "pass_bs": pass_bs, "pass_mc": pass_mc, "pass_dd": pass_dd,
        "n": n, "lucro": total,
        "p_t": round(float(p_t), 4), "ci_lower": round(float(ci_lower), 4),
        "p_runs": round(float(p_runs), 4),
        "bs_low": round(float(bs_low), 4),
        "prob_plus": round(float(prob_plus), 2),
        "dd": round(float(dd), 2), "dd_lim": round(float(dd_lim), 2),
    }


# =============================================================================
# Preparar base
# =============================================================================

def _rolling_mean_std(df, group_col, val_col, n_win, n_per, prefix):
    df[f"Media_{prefix}"] = (df.groupby(group_col)[val_col]
                                 .rolling(window=n_win, min_periods=n_per).mean()
                                 .reset_index(0, drop=True))
    df[f"DesvPad_{prefix}"] = (df.groupby(group_col)[val_col]
                                  .rolling(window=n_win, min_periods=n_per).std()
                                  .reset_index(0, drop=True))
    df[f"Media_{prefix}"] = df.groupby(group_col)[f"Media_{prefix}"].shift(1)
    df[f"DesvPad_{prefix}"] = df.groupby(group_col)[f"DesvPad_{prefix}"].shift(1)
    df[f"CV_{prefix}"] = np.where(df[f"Media_{prefix}"] == 0, 0,
                                   df[f"DesvPad_{prefix}"] / df[f"Media_{prefix}"])
    return df


def prepare_base(csv_path=None):
    if csv_path is None:
        csv_path = CSV_PATH

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

    df["p_H"] = 1 / df["Odd_H_FT"]
    df["p_D"] = 1 / df["Odd_D_FT"]
    df["p_A"] = 1 / df["Odd_A_FT"]

    odds_mo = df[["Odd_H_FT", "Odd_D_FT", "Odd_A_FT"]]
    df["CV_Odds"] = odds_mo.std(axis=1) / odds_mo.mean(axis=1)

    df["H_D"] = df["Odd_H_FT"] / df["Odd_D_FT"]
    df["H_A"] = df["Odd_H_FT"] / df["Odd_A_FT"]
    df["D_H"] = df["Odd_D_FT"] / df["Odd_H_FT"]
    df["D_A"] = df["Odd_D_FT"] / df["Odd_A_FT"]
    df["A_H"] = df["Odd_A_FT"] / df["Odd_H_FT"]
    df["A_D"] = df["Odd_A_FT"] / df["Odd_D_FT"]

    df["DifAbs_HomeAway"] = np.abs(df["Odd_H_FT"] - df["Odd_A_FT"])
    df["DifAbs_HomeDraw"] = np.abs(df["Odd_H_FT"] - df["Odd_D_FT"])
    df["DifAbs_DrawAway"] = np.abs(df["Odd_D_FT"] - df["Odd_A_FT"])

    df["Angle_HomeAway"] = np.degrees(np.arctan((df["Odd_A_FT"] - df["Odd_H_FT"]) / 2))
    df["Angle_HomeDraw"] = np.degrees(np.arctan((df["Odd_D_FT"] - df["Odd_H_FT"]) / 2))
    df["Angle_DrawAway"] = np.degrees(np.arctan((df["Odd_A_FT"] - df["Odd_D_FT"]) / 2))

    df["DifPer_HomeAway"] = np.abs(df["Odd_H_FT"] - df["Odd_A_FT"]) / df["Odd_A_FT"]
    df["DifPer_HomeDraw"] = np.abs(df["Odd_H_FT"] - df["Odd_D_FT"]) / df["Odd_D_FT"]
    df["DifPer_DrawAway"] = np.abs(df["Odd_D_FT"] - df["Odd_A_FT"]) / df["Odd_A_FT"]

    df["Ptos_H"] = np.where(df["Goals_H_FT"] > df["Goals_A_FT"], 3,
                   np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 0))
    df["Ptos_A"] = np.where(df["Goals_H_FT"] > df["Goals_A_FT"], 0,
                   np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 3))
    df = _rolling_mean_std(df, "Home", "Ptos_H", n_win, n_per, "Ptos_H")
    df = _rolling_mean_std(df, "Away", "Ptos_A", n_win, n_per, "Ptos_A")

    df = _rolling_mean_std(df, "Home", "Goals_H_FT", n_win, n_per, "GM_H")
    df = _rolling_mean_std(df, "Away", "Goals_A_FT", n_win, n_per, "GM_A")

    df = _rolling_mean_std(df, "Home", "Goals_A_FT", n_win, n_per, "GS_H")
    df = _rolling_mean_std(df, "Away", "Goals_H_FT", n_win, n_per, "GS_A")

    df["SG_H"] = df["Goals_H_FT"] - df["Goals_A_FT"]
    df["SG_A"] = df["Goals_A_FT"] - df["Goals_H_FT"]
    df = _rolling_mean_std(df, "Home", "SG_H", n_win, n_per, "SG_H")
    df = _rolling_mean_std(df, "Away", "SG_A", n_win, n_per, "SG_A")

    df["SG_H_01"] = (df["Goals_H_FT"] - df["Goals_A_FT"]) / df["p_H"]
    df["SG_A_01"] = (df["Goals_A_FT"] - df["Goals_H_FT"]) / df["p_A"]
    df = _rolling_mean_std(df, "Home", "SG_H_01", n_win, n_per, "SG_H_01")
    df = _rolling_mean_std(df, "Away", "SG_A_01", n_win, n_per, "SG_A_01")

    df["SG_H_02"] = (df["Goals_H_FT"] - df["Goals_A_FT"]) / df["p_A"]
    df["SG_A_02"] = (df["Goals_A_FT"] - df["Goals_H_FT"]) / df["p_H"]
    df = _rolling_mean_std(df, "Home", "SG_H_02", n_win, n_per, "SG_H_02")
    df = _rolling_mean_std(df, "Away", "SG_A_02", n_win, n_per, "SG_A_02")

    df["VG_H"] = df["Goals_H_FT"] * df["p_A"]
    df["VG_A"] = df["Goals_A_FT"] * df["p_H"]
    df = _rolling_mean_std(df, "Home", "VG_H", n_win, n_per, "VG_H")
    df = _rolling_mean_std(df, "Away", "VG_A", n_win, n_per, "VG_A")

    df["CG_H_00"] = df["p_H"] / df["Goals_H_FT"]
    df["CG_A_00"] = df["p_A"] / df["Goals_A_FT"]
    df.replace(np.inf, 1, inplace=True)
    df = _rolling_mean_std(df, "Home", "CG_H_00", n_win, n_per, "CG_H_00")
    df = _rolling_mean_std(df, "Away", "CG_A_00", n_win, n_per, "CG_A_00")

    df["CG_H_01"] = df["Goals_H_FT"] / df["p_H"]
    df["CG_A_01"] = df["Goals_A_FT"] / df["p_A"]
    df = _rolling_mean_std(df, "Home", "CG_H_01", n_win, n_per, "CG_H_01")
    df = _rolling_mean_std(df, "Away", "CG_A_01", n_win, n_per, "CG_A_01")

    df["CG_H_02"] = (df["Goals_H_FT"] / 2) + (df["p_H"] / 2)
    df["CG_A_02"] = (df["Goals_A_FT"] / 2) + (df["p_A"] / 2)
    df = _rolling_mean_std(df, "Home", "CG_H_02", n_win, n_per, "CG_H_02")
    df = _rolling_mean_std(df, "Away", "CG_A_02", n_win, n_per, "CG_A_02")

    drop_cols = [c for c in df.columns if c.startswith("DesvPad_")
                 or c in {"Ptos_H", "Ptos_A",
                          "SG_H", "SG_A",
                          "SG_H_01", "SG_A_01", "SG_H_02", "SG_A_02",
                          "VG_H", "VG_A",
                          "CG_H_00", "CG_A_00", "CG_H_01", "CG_A_01",
                          "CG_H_02", "CG_A_02"}]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    df = drop_reset_index(df)

    # Mercados HT
    if "Goals_H_HT" in df.columns:
        df["Back_Home_HT"] = np.where(df["Goals_H_HT"] > df["Goals_A_HT"], 1, 0)
        df["Back_Draw_HT"] = np.where(df["Goals_H_HT"] == df["Goals_A_HT"], 1, 0)
        df["Back_Away_HT"] = np.where(df["Goals_H_HT"] < df["Goals_A_HT"], 1, 0)
        if "Odd_H_HT" in df.columns:
            df["Profit_Back_Home_HT"] = np.where(df["Back_Home_HT"] == 1, df["Odd_H_HT"] - 1, -1)
        if "Odd_D_HT" in df.columns:
            df["Profit_Back_Draw_HT"] = np.where(df["Back_Draw_HT"] == 1, df["Odd_D_HT"] - 1, -1)
        if "Odd_A_HT" in df.columns:
            df["Profit_Back_Away_HT"] = np.where(df["Back_Away_HT"] == 1, df["Odd_A_HT"] - 1, -1)

        goals_ht = df["Goals_H_HT"] + df["Goals_A_HT"]
        for line, tag in [(0, "05"), (1, "15"), (2, "25")]:
            over = (goals_ht > line).astype(int)
            col_o = f"Odd_Over{tag}_HT"
            col_u = f"Odd_Under{tag}_HT"
            if col_o in df.columns:
                df[f"Profit_Over{tag}_HT"] = np.where(over == 1, df[col_o] - 1, -1)
            if col_u in df.columns:
                df[f"Profit_Under{tag}_HT"] = np.where(over == 0, df[col_u] - 1, -1)

    # Mercados FT
    df["Back_Home_FT"] = np.where(df["Goals_H_FT"] > df["Goals_A_FT"], 1, 0)
    df["Back_Draw_FT"] = np.where(df["Goals_H_FT"] == df["Goals_A_FT"], 1, 0)
    df["Back_Away_FT"] = np.where(df["Goals_H_FT"] < df["Goals_A_FT"], 1, 0)

    df["Profit_Back_Home_FT"] = np.where(df["Back_Home_FT"] == 1, df["Odd_H_FT"] - 1, -1)
    df["Profit_Back_Draw_FT"] = np.where(df["Back_Draw_FT"] == 1, df["Odd_D_FT"] - 1, -1)
    df["Profit_Back_Away_FT"] = np.where(df["Back_Away_FT"] == 1, df["Odd_A_FT"] - 1, -1)

    if "Odd_DC_X2" in df.columns:
        df["Profit_Lay_Home_FT"] = np.where(df["Back_Home_FT"] == 0, df["Odd_DC_X2"] - 1, -1)
    if "Odd_DC_12" in df.columns:
        df["Profit_Lay_Draw_FT"] = np.where(df["Back_Draw_FT"] == 0, df["Odd_DC_12"] - 1, -1)
    if "Odd_DC_1X" in df.columns:
        df["Profit_Lay_Away_FT"] = np.where(df["Back_Away_FT"] == 0, df["Odd_DC_1X"] - 1, -1)

    goals_ft = df["Goals_H_FT"] + df["Goals_A_FT"]
    for line, tag in [(0, "05"), (1, "15"), (2, "25"), (3, "35"), (4, "45")]:
        over = (goals_ft > line).astype(int)
        col_o = f"Odd_Over{tag}_FT"
        col_u = f"Odd_Under{tag}_FT"
        if col_o in df.columns:
            df[f"Profit_Over{tag}_FT"] = np.where(over == 1, df[col_o] - 1, -1)
        if col_u in df.columns:
            df[f"Profit_Under{tag}_FT"] = np.where(over == 0, df[col_u] - 1, -1)

    btts = ((df["Goals_H_FT"] > 0) & (df["Goals_A_FT"] > 0)).astype(int)
    if "Odd_BTTS_Yes" in df.columns:
        df["Profit_BTTS_Yes"] = np.where(btts == 1, df["Odd_BTTS_Yes"] - 1, -1)
    if "Odd_BTTS_No" in df.columns:
        df["Profit_BTTS_No"] = np.where(btts == 0, df["Odd_BTTS_No"] - 1, -1)

    df = drop_reset_index(df)

    n_mercados = len([c for c in df.columns if c.startswith("Profit_")])
    print(f"Base pronta: {len(df)} jogos  |  {n_mercados} mercados  |  {len(df.columns)} colunas totais.")
    return df


# =============================================================================
# Cache do DataFrame processado (pickle em disco)
# =============================================================================

CACHE_PICKLE = Path(__file__).resolve().parent.parent / "base_processed.pkl.gz"

_cached_df = None


def get_base(csv_path=None, force_reprocess=False):
    global _cached_df

    if _cached_df is not None:
        return _cached_df

    if not force_reprocess and CACHE_PICKLE.exists():
        print(f"Carregando cache: {CACHE_PICKLE}")
        _cached_df = pd.read_pickle(CACHE_PICKLE)
        print(f"Cache carregado: {len(_cached_df):,} jogos")
        return _cached_df

    _cached_df = prepare_base(csv_path)

    print(f"Salvando cache: {CACHE_PICKLE}")
    _cached_df.to_pickle(CACHE_PICKLE)
    print(f"Cache salvo: {CACHE_PICKLE}")

    return _cached_df


def reset_cache():
    global _cached_df
    _cached_df = None


# =============================================================================
# Features (apenas odds + medias)
# =============================================================================

_EXCLUIR_FILTRO = {
    "Profit", "Date", "Time",
    "Back_Home_FT", "Back_Draw_FT", "Back_Away_FT",
    "Back_Home_HT", "Back_Draw_HT", "Back_Away_HT",
    "OverUnder05_HT", "OverUnder15_HT", "OverUnder25_HT",
    "OverUnder05_FT", "OverUnder15_FT", "OverUnder25_FT",
    "OverUnder35_FT", "OverUnder45_FT",
    "BTTS",
    "Goals_H_FT", "Goals_A_FT", "Goals_H_HT", "Goals_A_HT",
}


def get_features(df):
    features = sorted([
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in _EXCLUIR_FILTRO
        and not c.startswith("Profit_")
    ])
    return features


def get_strategies(df):
    return sorted([c.replace("Profit_", "") for c in df.columns if c.startswith("Profit_")])


def aplicar_filtros(df, filtros):
    if not filtros:
        return df.copy()
    mask = pd.Series(True, index=df.index)
    for feature, (vmin, vmax) in filtros.items():
        mask &= df[feature].between(vmin, vmax, inclusive="both")
    return df.loc[mask].copy()


def resumo_bloco(df):
    n = len(df)
    lucro = df["Profit"].sum() if n > 0 else 0.0
    roi = lucro / n * 100 if n > 0 else 0.0
    return {"n": n, "lucro": round(float(lucro), 2), "roi": round(float(roi), 2)}
