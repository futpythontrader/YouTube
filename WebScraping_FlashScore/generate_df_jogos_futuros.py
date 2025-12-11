import json
import os
import pandas as pd
from pathlib import Path


def find_best_bookmaker(odds_list, prefer=['bet365', 'betfair']):
    """
    Procura pela casa de apostas preferencial na lista
    Retorna o dict da casa encontrada ou o primeiro da lista
    """
    if not odds_list or not isinstance(odds_list, list):
        return None
    
    # Procura pelas casas preferenciais em ordem
    for preferred in prefer:
        for odd_data in odds_list:
            if isinstance(odd_data, dict):
                bookmaker = odd_data.get('Bookmaker', '').lower()
                if preferred in bookmaker:
                    return odd_data
    
    # Se não encontrou nenhuma preferencial, retorna a primeira
    if len(odds_list) > 0 and isinstance(odds_list[0], dict):
        return odds_list[0]
    
    return None


def extract_ou_line(ou_data, line, prefer=['bet365', 'betfair']):
    """
    Extrai odds Over/Under de uma linha específica
    Retorna (bookmaker, over, under)
    """
    if not ou_data or not isinstance(ou_data, dict):
        return None, None, None
    
    key = f"OU_{line}"
    if key not in ou_data:
        return None, None, None
    
    odds_list = ou_data[key]
    if not odds_list or not isinstance(odds_list, list):
        return None, None, None
    
    # Procura pela casa preferencial
    best_odd = find_best_bookmaker(odds_list, prefer)
    
    if best_odd:
        return (
            best_odd.get('Bookmaker'),
            best_odd.get('Over'),
            best_odd.get('Under')
        )
    
    return None, None, None


def process_match_to_row(match_data, prefer_bookmakers=['bet365', 'betfair']):
    """
    Converte dados de um jogo em uma linha de DataFrame
    """
    row = {}
    
    # Informações básicas
    row['Match_ID'] = match_data.get('Match_ID', match_data.get('Id'))
    row['Date'] = match_data.get('Date')
    row['Time'] = match_data.get('Time')
    row['League'] = match_data.get('League')
    row['Round'] = match_data.get('Round')
    row['Home'] = match_data.get('Home')
    row['Away'] = match_data.get('Away')
    
    # === MATCH ODDS HALF TIME (1X2 HT) ===
    odds_1x2_ht = match_data.get('Odds_1X2_HT', [])
    best_ht = find_best_bookmaker(odds_1x2_ht, prefer_bookmakers)
    
    if best_ht:
        row['Bookie_1X2_HT'] = best_ht.get('Bookmaker')
        row['Odd_1_HT'] = best_ht.get('Odd_1', 0)
        row['Odd_X_HT'] = best_ht.get('Odd_X', 0)
        row['Odd_2_HT'] = best_ht.get('Odd_2', 0)
    else:
        row['Bookie_1X2_HT'] = None
        row['Odd_1_HT'] = 0
        row['Odd_X_HT'] = 0
        row['Odd_2_HT'] = 0
    
    # === MATCH ODDS FULL TIME (1X2 FT) ===
    odds_1x2_ft = match_data.get('Odds_1X2_FT', [])
    best_ft = find_best_bookmaker(odds_1x2_ft, prefer_bookmakers)
    
    if best_ft:
        row['Bookie_1X2_FT'] = best_ft.get('Bookmaker')
        row['Odd_1_FT'] = best_ft.get('Odd_1', 0)
        row['Odd_X_FT'] = best_ft.get('Odd_X', 0)
        row['Odd_2_FT'] = best_ft.get('Odd_2', 0)
    else:
        row['Bookie_1X2_FT'] = None
        row['Odd_1_FT'] = 0
        row['Odd_X_FT'] = 0
        row['Odd_2_FT'] = 0
    
    # === OVER/UNDER HALF TIME (0.5, 1.5, 2.5) ===
    ou_ht = match_data.get('Odds_OU_HT', {})
    
    for line in [0.5, 1.5, 2.5]:
        bookie, over, under = extract_ou_line(ou_ht, line, prefer_bookmakers)
        line_str = str(line).replace('.', '_')
        row[f'Bookie_OU_HT_{line_str}'] = bookie
        row[f'Over_HT_{line_str}'] = over if over is not None else 0
        row[f'Under_HT_{line_str}'] = under if under is not None else 0
    
    # === OVER/UNDER FULL TIME (0.5, 1.5, 2.5, 3.5, 4.5) ===
    ou_ft = match_data.get('Odds_OU_FT', {})
    
    for line in [0.5, 1.5, 2.5, 3.5, 4.5]:
        bookie, over, under = extract_ou_line(ou_ft, line, prefer_bookmakers)
        line_str = str(line).replace('.', '_')
        row[f'Bookie_OU_FT_{line_str}'] = bookie
        row[f'Over_FT_{line_str}'] = over if over is not None else 0
        row[f'Under_FT_{line_str}'] = under if under is not None else 0
    
    # === BOTH TEAMS TO SCORE (BTTS) ===
    btts = match_data.get('Odds_BTTS_FT', [])
    best_btts = find_best_bookmaker(btts, prefer_bookmakers)
    
    if best_btts:
        row['Bookie_BTTS'] = best_btts.get('Bookmaker')
        row['BTTS_Yes'] = best_btts.get('Yes', 0)
        row['BTTS_No'] = best_btts.get('No', 0)
    else:
        row['Bookie_BTTS'] = None
        row['BTTS_Yes'] = 0
        row['BTTS_No'] = 0
    
    # === DOUBLE CHANCE ===
    dc = match_data.get('Odds_DC_FT', [])
    best_dc = find_best_bookmaker(dc, prefer_bookmakers)
    
    if best_dc:
        row['Bookie_DC'] = best_dc.get('Bookmaker')
        row['DC_1X'] = best_dc.get('Odd_1X', 0)
        row['DC_12'] = best_dc.get('Odd_12', 0)
        row['DC_X2'] = best_dc.get('Odd_X2', 0)
    else:
        row['Bookie_DC'] = None
        row['DC_1X'] = 0
        row['DC_12'] = 0
        row['DC_X2'] = 0
    
    return row


def generate_dataframe_from_json(json_file, output_csv=None, prefer_bookmakers=['bet365', 'betfair']):
    """
    Gera DataFrame a partir de um arquivo JSON de jogos futuros
    
    Args:
        json_file: Caminho para o arquivo JSON
        output_csv: Caminho para salvar CSV (opcional)
        prefer_bookmakers: Lista de bookmakers preferenciais em ordem
    
    Returns:
        DataFrame pandas
    """
    print(f"\n📂 Lendo: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data.get('matches', [])
    print(f"✓ {len(matches)} jogos encontrados")
    
    if not matches:
        print("⚠️ Nenhum jogo no arquivo")
        return None
    
    # Processa cada jogo
    rows = []
    for match in matches:
        row = process_match_to_row(match, prefer_bookmakers)
        rows.append(row)
    
    # Cria DataFrame
    df = pd.DataFrame(rows)
    
    print(f"✓ DataFrame criado: {len(df)} linhas x {len(df.columns)} colunas")
    
    # Salva CSV se solicitado
    if output_csv:
        df.to_csv(output_csv, index=False, encoding='utf-8')
        file_size_kb = os.path.getsize(output_csv) / 1024
        print(f"✓ Salvo: {output_csv} ({file_size_kb:.1f} KB)")
    
    return df


def process_all_future_games(input_dir='jogos_futuros', output_dir='dataframes_jogos_futuros', 
                             prefer_bookmakers=['bet365', 'betfair']):
    """
    Processa todos os arquivos JSON de jogos futuros
    """
    if not os.path.exists(input_dir):
        print(f"❌ Diretório não encontrado: {input_dir}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("📊 GERADOR DE DATAFRAMES - JOGOS FUTUROS")
    print("=" * 80)
    print(f"📂 Entrada: {input_dir}/")
    print(f"💾 Saída: {output_dir}/")
    print(f"🎯 Bookmakers preferenciais: {', '.join(prefer_bookmakers)}")
    print("=" * 80)
    
    # Lista arquivos JSON
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"\n❌ Nenhum arquivo JSON encontrado em {input_dir}/")
        return
    
    print(f"\n✓ {len(json_files)} arquivo(s) encontrado(s)")
    
    total_games = 0
    
    # Processa cada arquivo
    for json_file in sorted(json_files):
        input_path = os.path.join(input_dir, json_file)
        output_csv = os.path.join(output_dir, json_file.replace('.json', '.csv'))
        
        df = generate_dataframe_from_json(input_path, output_csv, prefer_bookmakers)
        
        if df is not None:
            total_games += len(df)
    
    print("\n" + "=" * 80)
    print("✅ PROCESSAMENTO CONCLUÍDO")
    print("=" * 80)
    print(f"📊 Total de jogos processados: {total_games}")
    print(f"💾 CSVs salvos em: {output_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Modo específico: processa um arquivo
        json_file = sys.argv[1]
        output_csv = sys.argv[2] if len(sys.argv) > 2 else json_file.replace('.json', '.csv')
        
        df = generate_dataframe_from_json(json_file, output_csv)
        
        if df is not None:
            print("\n📋 Primeiras linhas:")
            print(df.head())
            
            print("\n📊 Colunas disponíveis:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i:2d}. {col}")
    else:
        # Modo padrão: processa todos os arquivos
        process_all_future_games()
