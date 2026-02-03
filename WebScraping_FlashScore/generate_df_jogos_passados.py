#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de DataFrame para Jogos Passados (All Seasons)
Converte JSON de jogos históricos em DataFrame tabular

Baseado no gerador de jogos futuros, mas adiciona:
- Placar final (Home_Score, Away_Score)
- Minutos dos gols (Min_Goals_Home, Min_Goals_Away)
- Estatísticas FT, HT e 2T

Regras de Odds:
- Bookie preferencial: Bet365 > Betfair > Primeiro disponível
- Um jogo por linha
- Odds: 1X2 HT/FT, O/U HT (0.5, 1.5, 2.5), O/U FT (0.5-4.5), BTTS, DC
"""

import json
import os
import pandas as pd
from pathlib import Path
from league_mapping import standardize_league_name


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


def extract_correct_score(cs_data, score, prefer=['bet365', 'betfair']):
    """
    Extrai odd de um placar específico (ex: "1-0", "2-1")
    Retorna (bookmaker, odd)
    """
    if not cs_data or not isinstance(cs_data, dict):
        return None, None
    
    if score not in cs_data:
        return None, None
    
    odds_list = cs_data[score]
    if not odds_list or not isinstance(odds_list, list):
        return None, None
    
    best_odd = find_best_bookmaker(odds_list, prefer)
    
    if best_odd:
        return best_odd.get('Bookmaker'), best_odd.get('Odd')
    
    return None, None


def extract_asian_handicap_line(ah_data, line, prefer=['bet365', 'betfair']):
    """
    Extrai odds Asian Handicap de uma linha específica (ex: -1.5, 0.0, +1.5)
    Retorna (bookmaker, home, away)
    """
    if not ah_data or not isinstance(ah_data, dict):
        return None, None, None
    
    # O JSON salva com prefixo "AH_"
    key = f"AH_{line}"
    if key not in ah_data:
        return None, None, None
    
    odds_list = ah_data[key]
    if not odds_list or not isinstance(odds_list, list):
        return None, None, None
    
    best_odd = find_best_bookmaker(odds_list, prefer)
    
    if best_odd:
        return (
            best_odd.get('Bookmaker'),
            best_odd.get('Home'),
            best_odd.get('Away')
        )
    
    return None, None, None


def extract_european_handicap_line(eh_data, line, prefer=['bet365', 'betfair']):
    """
    Extrai odds European Handicap de uma linha específica (ex: -2, 0, +2)
    Retorna (bookmaker, home, draw, away)
    """
    if not eh_data or not isinstance(eh_data, dict):
        return None, None, None, None
    
    # O JSON salva com prefixo "EH_"
    key = f"EH_{line}"
    if key not in eh_data:
        return None, None, None, None
    
    odds_list = eh_data[key]
    if not odds_list or not isinstance(odds_list, list):
        return None, None, None, None
    
    best_odd = find_best_bookmaker(odds_list, prefer)
    
    if best_odd:
        return (
            best_odd.get('Bookmaker'),
            best_odd.get('Home'),
            best_odd.get('Draw'),
            best_odd.get('Away')
        )
    
    return None, None, None, None


def process_match_to_row(match_data, league_name, country, season, prefer_bookmakers=['bet365', 'betfair']):
    """
    Converte dados de um jogo em uma linha de DataFrame
    """
    row = {}
    
    # Informações básicas
    row['Match_ID'] = match_data.get('Match_ID', match_data.get('Id'))
    row['Country'] = country
    row['Season'] = season
    
    # Div = nome original da liga (ex: "Torneo Betano 2024")
    row['Div'] = league_name
    
    # League = nome padronizado (ex: "ARGENTINA 1")
    row['League'] = standardize_league_name(country=country, league=league_name)
    
    row['Date'] = match_data.get('Date')
    row['Time'] = match_data.get('Time')
    row['Round'] = match_data.get('Round')
    row['Home'] = match_data.get('Home')
    row['Away'] = match_data.get('Away')
    
    # === PLACAR FINAL (NOVO!) ===
    row['Home_Score'] = match_data.get('Home_Score')
    row['Away_Score'] = match_data.get('Away_Score')
    
    # === MINUTOS DOS GOLS (NOVO!) ===
    min_goals_home = match_data.get('Min_Goals_Home', [])
    min_goals_away = match_data.get('Min_Goals_Away', [])
    
    # Mantém como lista (será salvo como string no CSV mas pode ser parseado de volta)
    row['Min_Goals_Home'] = min_goals_home if isinstance(min_goals_home, list) else []
    row['Min_Goals_Away'] = min_goals_away if isinstance(min_goals_away, list) else []
    
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
    
    # === CORRECT SCORE (Placares mais comuns) ===
    cs_ft = match_data.get('Odds_CS_FT', {})
    
    # Placares mais populares para apostas (formato do JSON usa ':' não '-')
    common_scores = ['0:0', '1:0', '0:1', '1:1', '2:0', '0:2', '2:1', '1:2', 
                     '2:2', '3:0', '0:3', '3:1', '1:3', '3:2', '2:3']
    
    for score in common_scores:
        bookie, odd = extract_correct_score(cs_ft, score, prefer_bookmakers)
        score_key = score.replace(':', '_')  # Muda de : para _
        row[f'Bookie_CS_{score_key}'] = bookie
        row[f'CS_{score_key}'] = odd if odd is not None else 0
    
    # === ASIAN HANDICAP (Linhas mais comuns) ===
    ah_ft = match_data.get('Odds_AH_FT', {})
    
    # Linhas mais populares de AH (JSON salva no formato -1.5, +0.5, etc)
    # Nota: AH_0 não existe no JSON (só AH_0,-0.5 e AH_0,+0.5)
    # Handicaps inteiros no JSON não têm .0 (ex: AH_-2, não AH_-2.0)
    ah_lines = ['-2.5', '-2', '-1.5', '-1', '-0.5', '+0.5', '+1', '+1.5', '+2', '+2.5']
    
    for line in ah_lines:
        bookie, home, away = extract_asian_handicap_line(ah_ft, line, prefer_bookmakers)
        # Normaliza chave para formato do CSV
        line_key = line.replace('-', 'neg_').replace('+', 'pos_').replace('.', '_')
        row[f'Bookie_AH_{line_key}'] = bookie
        row[f'AH_Home_{line_key}'] = home if home is not None else 0
        row[f'AH_Away_{line_key}'] = away if away is not None else 0
    
    # === EUROPEAN HANDICAP (Linhas mais comuns) ===
    eh_ft = match_data.get('Odds_EH_FT', {})
    
    # Linhas mais populares de EH (JSON salva no formato -2, 1, etc)
    # Nota: EH_0 não existe no JSON (não há European Handicap 0)
    # Handicaps positivos não têm sinal + no JSON (ex: EH_1, não EH_+1)
    eh_lines = ['-3', '-2', '-1', '1', '2', '3']
    
    for line in eh_lines:
        bookie, home, draw, away = extract_european_handicap_line(eh_ft, line, prefer_bookmakers)
        line_key = line.replace('-', 'neg_').replace('+', 'pos_')
        row[f'Bookie_EH_{line_key}'] = bookie
        row[f'EH_Home_{line_key}'] = home if home is not None else 0
        row[f'EH_Draw_{line_key}'] = draw if draw is not None else 0
        row[f'EH_Away_{line_key}'] = away if away is not None else 0
    
    # === ESTATÍSTICAS FULL TIME (34 campos!) ===
    stats_ft = match_data.get('Statistics_FT', {})
    
    # Função auxiliar para extrair estatística (evita repetição)
    def extract_stat(stat_dict, key):
        data = stat_dict.get(key, {})
        if isinstance(data, dict):
            return data.get('Home'), data.get('Away')
        return None, None
    
    if stats_ft:
        # xG e métricas avançadas
        row['xG_Home_FT'], row['xG_Away_FT'] = extract_stat(stats_ft, 'Expected goals (xG)')
        row['xGOT_Home_FT'], row['xGOT_Away_FT'] = extract_stat(stats_ft, 'xG on target (xGOT)')
        row['xA_Home_FT'], row['xA_Away_FT'] = extract_stat(stats_ft, 'Expected assists (xA)')
        row['xGOT_Faced_Home_FT'], row['xGOT_Faced_Away_FT'] = extract_stat(stats_ft, 'xGOT faced')
        row['Goals_Prevented_Home_FT'], row['Goals_Prevented_Away_FT'] = extract_stat(stats_ft, 'Goals prevented')
        
        # Posse e passes
        row['Possession_Home_FT'], row['Possession_Away_FT'] = extract_stat(stats_ft, 'Ball possession')
        row['Passes_Pct_Home_FT'], row['Passes_Pct_Away_FT'] = extract_stat(stats_ft, 'Passes')
        row['Long_Passes_Pct_Home_FT'], row['Long_Passes_Pct_Away_FT'] = extract_stat(stats_ft, 'Long passes')
        row['Passes_Final_Third_Pct_Home_FT'], row['Passes_Final_Third_Pct_Away_FT'] = extract_stat(stats_ft, 'Passes in final third')
        row['Through_Passes_Home_FT'], row['Through_Passes_Away_FT'] = extract_stat(stats_ft, 'Accurate through passes')
        row['Crosses_Pct_Home_FT'], row['Crosses_Pct_Away_FT'] = extract_stat(stats_ft, 'Crosses')
        
        # Chutes
        row['Total_Shots_Home_FT'], row['Total_Shots_Away_FT'] = extract_stat(stats_ft, 'Total shots')
        row['Shots_On_Target_Home_FT'], row['Shots_On_Target_Away_FT'] = extract_stat(stats_ft, 'Shots on target')
        row['Shots_Off_Target_Home_FT'], row['Shots_Off_Target_Away_FT'] = extract_stat(stats_ft, 'Shots off target')
        row['Blocked_Shots_Home_FT'], row['Blocked_Shots_Away_FT'] = extract_stat(stats_ft, 'Blocked shots')
        row['Shots_Inside_Box_Home_FT'], row['Shots_Inside_Box_Away_FT'] = extract_stat(stats_ft, 'Shots inside the box')
        row['Shots_Outside_Box_Home_FT'], row['Shots_Outside_Box_Away_FT'] = extract_stat(stats_ft, 'Shots outside the box')
        row['Big_Chances_Home_FT'], row['Big_Chances_Away_FT'] = extract_stat(stats_ft, 'Big chances')
        row['Hit_Woodwork_Home_FT'], row['Hit_Woodwork_Away_FT'] = extract_stat(stats_ft, 'Hit the woodwork')
        
        # Área e toques
        row['Touches_Box_Home_FT'], row['Touches_Box_Away_FT'] = extract_stat(stats_ft, 'Touches in opposition box')
        
        # Escanteios e bolas paradas
        row['Corners_Home_FT'], row['Corners_Away_FT'] = extract_stat(stats_ft, 'Corner kicks')
        row['Free_Kicks_Home_FT'], row['Free_Kicks_Away_FT'] = extract_stat(stats_ft, 'Free kicks')
        row['Throw_Ins_Home_FT'], row['Throw_Ins_Away_FT'] = extract_stat(stats_ft, 'Throw ins')
        
        # Disciplina
        row['Fouls_Home_FT'], row['Fouls_Away_FT'] = extract_stat(stats_ft, 'Fouls')
        row['Yellow_Cards_Home_FT'], row['Yellow_Cards_Away_FT'] = extract_stat(stats_ft, 'Yellow cards')
        row['Red_Cards_Home_FT'], row['Red_Cards_Away_FT'] = extract_stat(stats_ft, 'Red cards')
        
        # Impedimentos
        row['Offsides_Home_FT'], row['Offsides_Away_FT'] = extract_stat(stats_ft, 'Offsides')
        
        # Defesa
        row['Goalkeeper_Saves_Home_FT'], row['Goalkeeper_Saves_Away_FT'] = extract_stat(stats_ft, 'Goalkeeper saves')
        row['Tackles_Pct_Home_FT'], row['Tackles_Pct_Away_FT'] = extract_stat(stats_ft, 'Tackles')
        row['Duels_Won_Home_FT'], row['Duels_Won_Away_FT'] = extract_stat(stats_ft, 'Duels won')
        row['Clearances_Home_FT'], row['Clearances_Away_FT'] = extract_stat(stats_ft, 'Clearances')
        row['Interceptions_Home_FT'], row['Interceptions_Away_FT'] = extract_stat(stats_ft, 'Interceptions')
        
        # Erros
        row['Errors_Shot_Home_FT'], row['Errors_Shot_Away_FT'] = extract_stat(stats_ft, 'Errors leading to shot')
        row['Errors_Goal_Home_FT'], row['Errors_Goal_Away_FT'] = extract_stat(stats_ft, 'Errors leading to goal')
    else:
        # Preenche com None se não houver estatísticas (34 campos × 2 times = 68 colunas)
        stat_fields = ['xG', 'xGOT', 'xA', 'xGOT_Faced', 'Goals_Prevented',
                      'Possession', 'Passes_Pct', 'Long_Passes_Pct', 'Passes_Final_Third_Pct', 
                      'Through_Passes', 'Crosses_Pct',
                      'Total_Shots', 'Shots_On_Target', 'Shots_Off_Target', 'Blocked_Shots',
                      'Shots_Inside_Box', 'Shots_Outside_Box', 'Big_Chances', 'Hit_Woodwork',
                      'Touches_Box', 'Corners', 'Free_Kicks', 'Throw_Ins',
                      'Fouls', 'Yellow_Cards', 'Red_Cards', 'Offsides',
                      'Goalkeeper_Saves', 'Tackles_Pct', 'Duels_Won', 'Clearances', 'Interceptions',
                      'Errors_Shot', 'Errors_Goal']
        for stat in stat_fields:
            row[f'{stat}_Home_FT'] = None
            row[f'{stat}_Away_FT'] = None
    
    # === ESTATÍSTICAS HALF TIME (principais campos) ===
    stats_ht = match_data.get('Statistics_HT', {})
    
    if stats_ht:
        row['xG_Home_HT'], row['xG_Away_HT'] = extract_stat(stats_ht, 'Expected goals (xG)')
        row['xGOT_Home_HT'], row['xGOT_Away_HT'] = extract_stat(stats_ht, 'xG on target (xGOT)')
        row['xA_Home_HT'], row['xA_Away_HT'] = extract_stat(stats_ht, 'Expected assists (xA)')
        row['Possession_Home_HT'], row['Possession_Away_HT'] = extract_stat(stats_ht, 'Ball possession')
        row['Total_Shots_Home_HT'], row['Total_Shots_Away_HT'] = extract_stat(stats_ht, 'Total shots')
        row['Shots_On_Target_Home_HT'], row['Shots_On_Target_Away_HT'] = extract_stat(stats_ht, 'Shots on target')
        row['Shots_Off_Target_Home_HT'], row['Shots_Off_Target_Away_HT'] = extract_stat(stats_ht, 'Shots off target')
        row['Big_Chances_Home_HT'], row['Big_Chances_Away_HT'] = extract_stat(stats_ht, 'Big chances')
        row['Corners_Home_HT'], row['Corners_Away_HT'] = extract_stat(stats_ht, 'Corner kicks')
        row['Yellow_Cards_Home_HT'], row['Yellow_Cards_Away_HT'] = extract_stat(stats_ht, 'Yellow cards')
        row['Fouls_Home_HT'], row['Fouls_Away_HT'] = extract_stat(stats_ht, 'Fouls')
        row['Offsides_Home_HT'], row['Offsides_Away_HT'] = extract_stat(stats_ht, 'Offsides')
        row['Goalkeeper_Saves_Home_HT'], row['Goalkeeper_Saves_Away_HT'] = extract_stat(stats_ht, 'Goalkeeper saves')
    else:
        for stat in ['xG', 'xGOT', 'xA', 'Possession', 'Total_Shots', 'Shots_On_Target', 
                     'Shots_Off_Target', 'Big_Chances', 'Corners', 'Yellow_Cards', 
                     'Fouls', 'Offsides', 'Goalkeeper_Saves']:
            row[f'{stat}_Home_HT'] = None
            row[f'{stat}_Away_HT'] = None
    
    # === ESTATÍSTICAS 2º TEMPO (principais campos) ===
    stats_2t = match_data.get('Statistics_2T', {})
    
    if stats_2t:
        row['xG_Home_2T'], row['xG_Away_2T'] = extract_stat(stats_2t, 'Expected goals (xG)')
        row['xGOT_Home_2T'], row['xGOT_Away_2T'] = extract_stat(stats_2t, 'xG on target (xGOT)')
        row['xA_Home_2T'], row['xA_Away_2T'] = extract_stat(stats_2t, 'Expected assists (xA)')
        row['Possession_Home_2T'], row['Possession_Away_2T'] = extract_stat(stats_2t, 'Ball possession')
        row['Total_Shots_Home_2T'], row['Total_Shots_Away_2T'] = extract_stat(stats_2t, 'Total shots')
        row['Shots_On_Target_Home_2T'], row['Shots_On_Target_Away_2T'] = extract_stat(stats_2t, 'Shots on target')
        row['Shots_Off_Target_Home_2T'], row['Shots_Off_Target_Away_2T'] = extract_stat(stats_2t, 'Shots off target')
        row['Big_Chances_Home_2T'], row['Big_Chances_Away_2T'] = extract_stat(stats_2t, 'Big chances')
        row['Corners_Home_2T'], row['Corners_Away_2T'] = extract_stat(stats_2t, 'Corner kicks')
        row['Yellow_Cards_Home_2T'], row['Yellow_Cards_Away_2T'] = extract_stat(stats_2t, 'Yellow cards')
        row['Red_Cards_Home_2T'], row['Red_Cards_Away_2T'] = extract_stat(stats_2t, 'Red cards')
        row['Fouls_Home_2T'], row['Fouls_Away_2T'] = extract_stat(stats_2t, 'Fouls')
        row['Offsides_Home_2T'], row['Offsides_Away_2T'] = extract_stat(stats_2t, 'Offsides')
        row['Goalkeeper_Saves_Home_2T'], row['Goalkeeper_Saves_Away_2T'] = extract_stat(stats_2t, 'Goalkeeper saves')
    else:
        for stat in ['xG', 'xGOT', 'xA', 'Possession', 'Total_Shots', 'Shots_On_Target',
                     'Shots_Off_Target', 'Big_Chances', 'Corners', 'Yellow_Cards', 'Red_Cards',
                     'Fouls', 'Offsides', 'Goalkeeper_Saves']:
            row[f'{stat}_Home_2T'] = None
            row[f'{stat}_Away_2T'] = None
    
    return row


def generate_dataframe_from_json(json_file, output_csv=None, prefer_bookmakers=['bet365', 'betfair']):
    """
    Gera DataFrame a partir de um arquivo JSON de país/temporada
    
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
    
    country = data.get('country', 'Unknown')
    season = data.get('season', 'Unknown')
    leagues = data.get('leagues', [])
    
    print(f"   País: {country} | Temporada: {season} | Ligas: {len(leagues)}")
    
    if not leagues:
        print("⚠️ Nenhuma liga no arquivo")
        return None
    
    # Processa cada liga e seus jogos
    all_rows = []
    total_matches = 0
    
    for league_data in leagues:
        league_name = league_data.get('name', 'Unknown')
        matches = league_data.get('matches', [])
        
        if not matches:
            continue
        
        print(f"   🔄 {league_name}: {len(matches)} jogos")
        total_matches += len(matches)
        
        for match in matches:
            row = process_match_to_row(match, league_name, country, season, prefer_bookmakers)
            all_rows.append(row)
    
    if not all_rows:
        print("⚠️ Nenhum jogo processado")
        return None
    
    # Cria DataFrame
    df = pd.DataFrame(all_rows)
    
    print(f"✓ DataFrame criado: {len(df)} linhas x {len(df.columns)} colunas")
    
    # Salva CSV se solicitado
    if output_csv:
        df.to_csv(output_csv, index=False, encoding='utf-8')
        file_size_kb = os.path.getsize(output_csv) / 1024
        print(f"✓ Salvo: {output_csv} ({file_size_kb:.1f} KB)")
    
    return df


def process_all_historical_games(input_dir='jogos_passados', output_dir='dataframes_jogos_passados', 
                                  prefer_bookmakers=['bet365', 'betfair']):
    """
    Processa todos os arquivos JSON de jogos históricos (all seasons)
    """
    if not os.path.exists(input_dir):
        print(f"❌ Diretório não encontrado: {input_dir}")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("📊 GERADOR DE DATAFRAMES - JOGOS HISTÓRICOS (ALL SEASONS)")
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
        process_all_historical_games()
