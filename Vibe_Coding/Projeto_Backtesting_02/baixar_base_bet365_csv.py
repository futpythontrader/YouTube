import io
import time
import requests
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

TOKEN = "7256fbc57d1ee9df52ab707e1f8f0c02932161d4"
DIA = "2026-06-01"
FONTE = "bet365"
CSV_SAIDA = "base_bet365.csv"
MAX_TENTATIVAS = 5
TIMEOUT_CONEXAO = 15
TIMEOUT_LEITURA = 300

HEADERS = {"Authorization": f"Token {TOKEN}"}
BASE_URL_DOWNLOAD = f"https://api.futpythontrader.com/api/dados/{FONTE}/download/"


def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def get_dataframe(params=None):
    print(f"Baixando dados da fonte '{FONTE}'.")
    ultimo_erro = None

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            response = requests.get(
                BASE_URL_DOWNLOAD,
                headers=HEADERS,
                params=params,
                timeout=(TIMEOUT_CONEXAO, TIMEOUT_LEITURA),
            )

            if response.status_code == 200:
                df = pd.read_csv(io.BytesIO(response.content))
                print(f"Sucesso! DataFrame criado com {len(df)} linhas.")
                return df

            print(f"Erro na requisição (tentativa {tentativa}/{MAX_TENTATIVAS}): {response.status_code}")
            print(response.text)

        except requests.exceptions.RequestException as exc:
            ultimo_erro = exc
            print(f"Falha de conexão (tentativa {tentativa}/{MAX_TENTATIVAS}): {exc}")

        if tentativa < MAX_TENTATIVAS:
            espera = tentativa * 2
            print(f"Aguardando {espera}s para nova tentativa...")
            time.sleep(espera)

    if ultimo_erro is not None:
        print(f"Erro final ao baixar base: {ultimo_erro}")

    return pd.DataFrame()


if __name__ == "__main__":
    base = get_dataframe(params={})

    if base.empty:
        raise ValueError("Nenhum dado retornado da API apos retentativas. Verifique TOKEN/DIA e tente novamente.")

    df = base.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Date" in df.columns and "Time" in df.columns:
        df = df.sort_values(by=["Date", "Time"], ascending=[True, True])
    elif "Date" in df.columns:
        df = df.sort_values(by=["Date"], ascending=[True])

    df = drop_reset_index(df)
    df.to_csv(CSV_SAIDA, index=False)

    print(f"CSV salvo em: {CSV_SAIDA}")
    print(df.tail())
