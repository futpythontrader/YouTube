#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashScore Scraper V2 - Baseado no projeto funcionando
Usa flashscore.com (sem .br) e BeautifulSoup para mais velocidade
"""

import json
import time
import platform
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm


class FlashScoreScraper:
    def __init__(self, headless=True):
        """Inicializa o scraper do FlashScore"""
        self.base_url = "https://www.flashscore.com"  # SEM .br!
        self.driver = self.setup_driver(headless)
        self.results = []
        
    def setup_driver(self, headless=True):
        """Configura o Chrome WebDriver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Detecta o sistema operacional e usa o chromedriver correto
        sistema = platform.system()
        
        try:
            if sistema == 'Windows':
                # Windows usa chromedriver.exe
                service = Service('./chromedriver.exe')
            else:
                # Linux/Mac usa chromedriver
                service = Service('./chromedriver')
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"✓ Usando chromedriver local para {sistema}")
        except Exception as e:
            # Se falhar, usa o webdriver-manager para baixar a versão correta
            print(f"⚠ Chromedriver local falhou, baixando versão compatível...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver
    
    def accept_cookies(self):
        """Aceita cookies do site"""
        try:
            cookie_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            time.sleep(1)
        except:
            pass
    
    def get_match_basic_info(self, match_id):
        """Extrai informações básicas do jogo e slugs dos times"""
        url = f'{self.base_url}/match/{match_id}/#/match-summary/match-summary'
        self.driver.get(url)
        
        data = {'Id': match_id}
        
        try:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'span[data-testid="wcl-scores-overline-03"]'))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Liga e rodada
            overlines = soup.select('span[data-testid="wcl-scores-overline-03"]')
            if len(overlines) >= 3:
                country = overlines[1].text.strip()
                division_round = overlines[2].text.strip()
                league_rodada = f'{country} - {division_round}'
                parts = league_rodada.split(" - ")
                if len(parts) >= 3:
                    data['League'] = " - ".join(parts[:2])
                    data['Round'] = parts[2]
                else:
                    data['League'] = league_rodada
                    data['Round'] = "-"
            
            # Data e hora
            date_time_elem = soup.select_one('div.duelParticipant__startTime')
            if date_time_elem:
                date_time = date_time_elem.text.strip().split(' ')
                data['Date'] = date_time[0].replace('.', '/')
                data['Time'] = date_time[1]
            
            # Times
            home_elem = soup.select_one('div.duelParticipant__home div.participant__participantName')
            away_elem = soup.select_one('div.duelParticipant__away div.participant__participantName')
            if home_elem:
                data['Home'] = home_elem.text.strip()
            if away_elem:
                data['Away'] = away_elem.text.strip()
            
            # Slugs dos times (CRÍTICO para URLs de odds)
            home_link = soup.select_one('div.duelParticipant__home a.participant__participantLink--team')
            away_link = soup.select_one('div.duelParticipant__away a.participant__participantLink--team')
            
            if home_link and 'href' in home_link.attrs:
                home_href = home_link['href'].strip('/')
                segments = home_href.split('/')
                if len(segments) >= 2:
                    home_slug = segments[-2] + '-' + segments[-1]
                    data['Home_Slug'] = home_slug
            
            if away_link and 'href' in away_link.attrs:
                away_href = away_link['href'].strip('/')
                segments = away_href.split('/')
                if len(segments) >= 2:
                    away_slug = segments[-2] + '-' + segments[-1]
                    data['Away_Slug'] = away_slug
            
            # Placar final (somente para jogos passados)
            score_elem = soup.select_one('div.duelParticipant__score div.detailScore__wrapper')
            if score_elem:
                scores = score_elem.select('span')
                if len(scores) >= 3:  # [Home, "-", Away]
                    try:
                        data['Home_Score'] = int(scores[0].text.strip())
                        data['Away_Score'] = int(scores[2].text.strip())
                    except ValueError:
                        pass
            
        except Exception as e:
            print(f"  ✗ Erro ao extrair info básica: {e}")
        
        return data
    
    def extract_goals_and_minutes(self, match_id, data):
        """
        Extrai minutos dos gols (somente para jogos passados)
        Retorna listas de minutos para casa e fora
        """
        # Só extrai se o jogo já aconteceu (tem placar)
        if 'Home_Score' not in data or 'Away_Score' not in data:
            return data
        
        url = f'{self.base_url}/match/{match_id}/#/match-summary/match-summary'
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.smv__participantRow'))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            min_goals_home = []
            min_goals_away = []
            
            # Busca por todos os eventos de gol
            home_rows = soup.select('div.smv__participantRow.smv__homeParticipant')
            away_rows = soup.select('div.smv__participantRow.smv__awayParticipant')
            
            # Processa gols do time da casa
            for row in home_rows:
                # Verifica se tem ícone de gol (soccer icon ou incidentHomeScore)
                goal_icon = row.select_one('svg[data-testid="wcl-icon-soccer"]')
                goal_score = row.select_one('div.smv__incidentHomeScore')
                
                if goal_icon or goal_score:
                    time_box = row.select_one('div.smv__timeBox')
                    if time_box:
                        time_text = time_box.text.strip()
                        # Remove '+' e converte para int (ex: "45+2'" -> 47)
                        try:
                            if '+' in time_text:
                                parts = time_text.replace("'", "").split('+')
                                minute = int(parts[0]) + int(parts[1])
                            else:
                                minute = int(time_text.replace("'", ""))
                            min_goals_home.append(minute)
                        except ValueError:
                            pass
            
            # Processa gols do time visitante
            for row in away_rows:
                # Verifica se tem ícone de gol (soccer icon ou incidentAwayScore)
                goal_icon = row.select_one('svg[data-testid="wcl-icon-soccer"]')
                goal_score = row.select_one('div.smv__incidentAwayScore')
                
                if goal_icon or goal_score:
                    time_box = row.select_one('div.smv__timeBox')
                    if time_box:
                        time_text = time_box.text.strip()
                        # Remove '+' e converte para int (ex: "48'" -> 48)
                        try:
                            if '+' in time_text:
                                parts = time_text.replace("'", "").split('+')
                                minute = int(parts[0]) + int(parts[1])
                            else:
                                minute = int(time_text.replace("'", ""))
                            min_goals_away.append(minute)
                        except ValueError:
                            pass
            
            # Ordena os minutos
            min_goals_home.sort()
            min_goals_away.sort()
            
            data['Min_Goals_Home'] = min_goals_home
            data['Min_Goals_Away'] = min_goals_away
            
        except Exception as e:
            print(f"  ✗ Erro ao extrair gols: {e}")
            data['Min_Goals_Home'] = []
            data['Min_Goals_Away'] = []
        
        return data
    
    def extract_odds_1x2_ft(self, match_id, data):
        """Extrai odds 1X2 Full Time"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/1x2-odds/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table.oddsCell__odds"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table = soup.select_one("div.ui-table.oddsCell__odds")
            
            if not table:
                return data
            
            rows = table.select("div.ui-table__row")
            
            # Pega todas as odds de todas as casas
            odds_data = []
            
            for row in rows:
                # Nome da casa de apostas
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                
                # Odds 1-X-2
                odds_cells = row.select("a.oddsCell__odd")
                if len(odds_cells) < 3:
                    continue
                
                try:
                    odd_1 = None
                    odd_x = None
                    odd_2 = None
                    
                    for i, cell in enumerate(odds_cells[:3]):
                        # Ignora odds canceladas
                        if cell.select("span.oddsCell__lineThrough"):
                            continue
                        
                        odd_span = cell.select_one("span")
                        if odd_span:
                            odd_text = odd_span.text.strip()
                            odd_value = float(odd_text.replace(',', '.'))
                            
                            analytics = cell.get("data-analytics-element", "")
                            if "CELL_1" in analytics or i == 0:
                                odd_1 = odd_value
                            elif "CELL_2" in analytics or i == 1:
                                odd_x = odd_value
                            elif "CELL_3" in analytics or i == 2:
                                odd_2 = odd_value
                    
                    if odd_1 or odd_x or odd_2:
                        odds_data.append({
                            'Bookmaker': bookmaker,
                            'Odd_1': odd_1,
                            'Odd_X': odd_x,
                            'Odd_2': odd_2
                        })
                
                except:
                    continue
            
            # Armazena todas as odds
            data['Odds_1X2_FT'] = odds_data
            
            # Também pega a melhor odd destacada (highlighted)
            for row in rows:
                odds_cells = row.select("a.oddsCell__odd.oddsCell__highlight")
                for cell in odds_cells:
                    if cell.select("span.oddsCell__lineThrough"):
                        continue
                    
                    odd_span = cell.select_one("span")
                    if odd_span:
                        odd_value = float(odd_span.text.strip().replace(',', '.'))
                        analytics = cell.get("data-analytics-element", "")
                        
                        if "CELL_1" in analytics:
                            data['Best_Odd_1_FT'] = odd_value
                        elif "CELL_2" in analytics:
                            data['Best_Odd_X_FT'] = odd_value
                        elif "CELL_3" in analytics:
                            data['Best_Odd_2_FT'] = odd_value
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def extract_odds_ou_ft(self, match_id, data):
        """Extrai odds Over/Under Full Time - TODAS AS LINHAS"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/over-under/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table"))
            )
            
            # Clica em "Show more" se existir
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "a.showMore__text")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Pega TODAS as linhas (span.wcl-oddsValue_jvPMg) e TODAS as tabelas
            line_spans = soup.select("span.wcl-oddsValue_jvPMg")
            tables = soup.select("div.ui-table.oddsCell__odds")
            
            ou_data = {}
            seen_lines = set()
            line_to_table = {}
            table_idx = 0
            
            # Mapeia linhas únicas para suas tabelas
            for line_span in line_spans:
                line_text = line_span.text.strip()
                if line_text and line_text.replace('.', '').replace(',', '').isdigit():
                    try:
                        line_value = float(line_text.replace(',', '.'))
                        
                        # Só processa cada linha uma vez
                        if line_value not in seen_lines:
                            seen_lines.add(line_value)
                            
                            if table_idx < len(tables):
                                line_to_table[line_value] = tables[table_idx]
                                table_idx += 1
                    except:
                        continue
            
            # Processa cada linha única
            for line_value in sorted(seen_lines):
                if line_value not in line_to_table:
                    continue
                    
                table = line_to_table[line_value]
                line_key = f"OU_{line_value}"
                ou_data[line_key] = []
                
                # Extrai odds desta tabela
                rows = table.select("div.ui-table__row")
                for row in rows:
                    bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                    if not bookmaker_elem:
                        continue
                    
                    bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                    odds_cells = row.select("a.oddsCell__odd")
                    
                    if len(odds_cells) >= 2:
                        try:
                            # Ignora odds canceladas
                            if odds_cells[0].select("span.oddsCell__lineThrough"):
                                continue
                            if odds_cells[1].select("span.oddsCell__lineThrough"):
                                continue
                            
                            over_span = odds_cells[0].select_one("span")
                            under_span = odds_cells[1].select_one("span")
                            
                            if over_span and under_span:
                                over = float(over_span.text.strip().replace(',', '.'))
                                under = float(under_span.text.strip().replace(',', '.'))
                                
                                ou_data[line_key].append({
                                    'Bookmaker': bookmaker,
                                    'Over': over,
                                    'Under': under
                                })
                        except:
                            continue
            
            data['Odds_OU_FT'] = ou_data
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def extract_statistics(self, match_id, data, period="overall", period_name="FT"):
        """Extrai estatísticas de um período (overall=FT, 1st-half=HT, 2nd-half=2T)"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/summary/stats/{period}/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='wcl-statistics']"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            estatisticas = soup.select("div[data-testid='wcl-statistics']")
            
            stats_dict = {}
            
            for estatistica in estatisticas:
                # Valor Home: div.wcl-homeValue_3Q-7P > span[data-testid='wcl-scores-simple-text-01']
                home_value_elem = estatistica.select_one("div.wcl-homeValue_3Q-7P span[data-testid='wcl-scores-simple-text-01']")
                
                # Valor Away: div.wcl-awayValue_Y-QR1 > span[data-testid='wcl-scores-simple-text-01']
                away_value_elem = estatistica.select_one("div.wcl-awayValue_Y-QR1 span[data-testid='wcl-scores-simple-text-01']")
                
                # Nome da estatística: div[data-testid='wcl-statistics-category'] > span[data-testid='wcl-scores-simple-text-01']
                nome_estatistica_elem = estatistica.select_one("div[data-testid='wcl-statistics-category'] span[data-testid='wcl-scores-simple-text-01']")
                
                if home_value_elem and away_value_elem and nome_estatistica_elem:
                    valor_home = home_value_elem.text.strip()
                    valor_away = away_value_elem.text.strip()
                    nome_estatistica = nome_estatistica_elem.text.strip()
                    
                    def convert_value(value):
                        # Remove informações extras como "(405/496)" do formato "82% (405/496)"
                        value_clean = value.split('(')[0].strip()
                        
                        try:
                            if value_clean.endswith('%'):
                                return float(value_clean[:-1]) / 100
                            return float(value_clean)
                        except ValueError:
                            try:
                                return int(value_clean)
                            except ValueError:
                                return value_clean
                    
                    stats_dict[nome_estatistica] = {
                        'Home': convert_value(valor_home),
                        'Away': convert_value(valor_away)
                    }
            
            if stats_dict:
                data[f'Statistics_{period_name}'] = stats_dict
        
        except Exception as e:
            print(f"  ✗ Erro stats {period_name}: {e}")
        
        return data
    
    def extract_statistics_ft(self, match_id, data):
        """Extrai estatísticas Full Time"""
        return self.extract_statistics(match_id, data, period="overall", period_name="FT")
    
    def extract_statistics_ht(self, match_id, data):
        """Extrai estatísticas Half Time (1º tempo)"""
        return self.extract_statistics(match_id, data, period="1st-half", period_name="HT")
    
    def extract_statistics_2t(self, match_id, data):
        """Extrai estatísticas 2º Tempo"""
        return self.extract_statistics(match_id, data, period="2nd-half", period_name="2T")
    
    def extract_odds_1x2_ht(self, match_id, data):
        """Extrai odds 1X2 Half Time"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/1x2-odds/1st-half/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table.oddsCell__odds"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table = soup.select_one("div.ui-table.oddsCell__odds")
            
            if not table:
                return data
            
            rows = table.select("div.ui-table__row")
            odds_data = []
            
            for row in rows:
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                odds_cells = row.select("a.oddsCell__odd")
                
                if len(odds_cells) < 3:
                    continue
                
                try:
                    odd_1 = None
                    odd_x = None
                    odd_2 = None
                    
                    for i, cell in enumerate(odds_cells[:3]):
                        if cell.select("span.oddsCell__lineThrough"):
                            continue
                        
                        odd_span = cell.select_one("span")
                        if odd_span:
                            odd_value = float(odd_span.text.strip().replace(',', '.'))
                            
                            if i == 0:
                                odd_1 = odd_value
                            elif i == 1:
                                odd_x = odd_value
                            elif i == 2:
                                odd_2 = odd_value
                    
                    if odd_1 or odd_x or odd_2:
                        odds_data.append({
                            'Bookmaker': bookmaker,
                            'Odd_1': odd_1,
                            'Odd_X': odd_x,
                            'Odd_2': odd_2
                        })
                
                except:
                    continue
            
            data['Odds_1X2_HT'] = odds_data
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def extract_odds_btts_ft(self, match_id, data):
        """Extrai odds Both Teams to Score FT"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/both-teams-to-score/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table.oddsCell__odds"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table = soup.select_one("div.ui-table.oddsCell__odds")
            
            if not table:
                return data
            
            rows = table.select("div.ui-table__row")
            btts_data = []
            
            for row in rows:
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                odds_cells = row.select("a.oddsCell__odd")
                
                if len(odds_cells) >= 2:
                    try:
                        yes_span = odds_cells[0].select_one("span")
                        no_span = odds_cells[1].select_one("span")
                        
                        if yes_span and no_span:
                            yes_odd = float(yes_span.text.strip().replace(',', '.'))
                            no_odd = float(no_span.text.strip().replace(',', '.'))
                            
                            btts_data.append({
                                'Bookmaker': bookmaker,
                                'Yes': yes_odd,
                                'No': no_odd
                            })
                    except:
                        continue
            
            data['Odds_BTTS_FT'] = btts_data
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def extract_odds_dc_ft(self, match_id, data):
        """Extrai odds Double Chance FT"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/double-chance/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table.oddsCell__odds"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table = soup.select_one("div.ui-table.oddsCell__odds")
            
            if not table:
                return data
            
            rows = table.select("div.ui-table__row")
            dc_data = []
            
            for row in rows:
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                odds_cells = row.select("a.oddsCell__odd")
                
                if len(odds_cells) >= 3:
                    try:
                        odd_1x = None
                        odd_12 = None
                        odd_x2 = None
                        
                        for i, cell in enumerate(odds_cells[:3]):
                            if cell.select("span.oddsCell__lineThrough"):
                                continue
                            
                            odd_span = cell.select_one("span")
                            if odd_span:
                                odd_value = float(odd_span.text.strip().replace(',', '.'))
                                
                                if i == 0:
                                    odd_1x = odd_value
                                elif i == 1:
                                    odd_12 = odd_value
                                elif i == 2:
                                    odd_x2 = odd_value
                        
                        if odd_1x or odd_12 or odd_x2:
                            dc_data.append({
                                'Bookmaker': bookmaker,
                                'Odd_1X': odd_1x,
                                'Odd_12': odd_12,
                                'Odd_X2': odd_x2
                            })
                    except:
                        continue
            
            data['Odds_DC_FT'] = dc_data
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def extract_odds_cs_ft(self, match_id, data):
        """Extrai odds Correct Score Full Time - TODOS os placares"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/correct-score/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table"))
            )
            
            # Clica em "Show more" se existir
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "a.showMore__text")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # NOVA ESTRUTURA: pega todas as linhas (ui-table__row)
            rows = soup.select("div.ui-table__row")
            
            cs_data = {}
            
            # Cada linha tem: bookmaker + score + 1 odd
            for row in rows:
                # Bookmaker
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                
                # Score
                score_elem = row.select_one("span.wcl-oddsValue_jvPMg")
                if not score_elem:
                    continue
                
                score = score_elem.text.strip()
                if ':' not in score:
                    continue
                
                # Odd (apenas 1 para CS)
                odds_cells = row.select("a.oddsCell__odd")
                if not odds_cells:
                    continue
                
                try:
                    # Ignora odds canceladas
                    if odds_cells[0].select("span.oddsCell__lineThrough"):
                        continue
                    
                    odd_span = odds_cells[0].select_one("span")
                    if odd_span:
                        odd_value = float(odd_span.text.strip().replace(',', '.'))
                        
                        # Adiciona ao dicionário
                        if score not in cs_data:
                            cs_data[score] = []
                        
                        cs_data[score].append({
                            'Bookmaker': bookmaker,
                            'Odd': odd_value
                        })
                except:
                    continue
            
            data['Odds_CS_FT'] = cs_data
        
        except Exception as e:
            print(f"  ✗ Erro CS FT: {e}")
        
        return data
    
    def extract_odds_asian_handicap_ft(self, match_id, data):
        """Extrai odds Asian Handicap Full Time - TODAS AS LINHAS"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/asian-handicap/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table"))
            )
            
            # Clica em "Show more" se existir
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "a.showMore__text")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # NOVA ESTRUTURA: pega todas as linhas (ui-table__row)
            rows = soup.select("div.ui-table__row")
            
            ah_data = {}
            
            # Cada linha tem: bookmaker + line + 2 odds (Home, Away)
            for row in rows:
                # Bookmaker
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                
                # Line
                line_elem = row.select_one("span.wcl-oddsValue_jvPMg")
                if not line_elem:
                    continue
                
                line = line_elem.text.strip().replace(' ', '')
                if not line or ('+' not in line and '-' not in line and line != '0'):
                    continue
                
                line_key = f"AH_{line}"
                
                # Odds (2 para AH: Home, Away)
                odds_cells = row.select("a.oddsCell__odd")
                if len(odds_cells) < 2:
                    continue
                
                try:
                    home_odd = None
                    away_odd = None
                    
                    # Home odd (primeira célula)
                    if not odds_cells[0].select("span.oddsCell__lineThrough"):
                        home_span = odds_cells[0].select_one("span")
                        if home_span:
                            home_odd = float(home_span.text.strip().replace(',', '.'))
                    
                    # Away odd (segunda célula)
                    if not odds_cells[1].select("span.oddsCell__lineThrough"):
                        away_span = odds_cells[1].select_one("span")
                        if away_span:
                            away_odd = float(away_span.text.strip().replace(',', '.'))
                    
                    if home_odd or away_odd:
                        if line_key not in ah_data:
                            ah_data[line_key] = []
                        
                        ah_data[line_key].append({
                            'Bookmaker': bookmaker,
                            'Home': home_odd,
                            'Away': away_odd
                        })
                except:
                    continue
            
            data['Odds_AH_FT'] = ah_data
        
        except Exception as e:
            print(f"  ✗ Erro AH FT: {e}")
        
        return data
    
    def extract_odds_european_handicap_ft(self, match_id, data):
        """Extrai odds European Handicap Full Time - TODAS AS LINHAS"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/european-handicap/full-time/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table"))
            )
            
            # Clica em "Show more" se existir
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "a.showMore__text")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # NOVA ESTRUTURA: pega todas as linhas (ui-table__row)
            rows = soup.select("div.ui-table__row")
            
            eh_data = {}
            
            # Cada linha tem: bookmaker + line + 3 odds (Home, Draw, Away)
            for row in rows:
                # Bookmaker
                bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                if not bookmaker_elem:
                    continue
                
                bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                
                # Line
                line_elem = row.select_one("span.wcl-oddsValue_jvPMg")
                if not line_elem:
                    continue
                
                line = line_elem.text.strip().replace(' ', '')
                if not line:
                    continue
                
                line_key = f"EH_{line}"
                
                # Odds (3 para EH: Home, Draw, Away)
                odds_cells = row.select("a.oddsCell__odd")
                if len(odds_cells) < 3:
                    continue
                
                try:
                    home_odd = None
                    draw_odd = None
                    away_odd = None
                    
                    # Home odd (primeira célula)
                    if not odds_cells[0].select("span.oddsCell__lineThrough"):
                        home_span = odds_cells[0].select_one("span")
                        if home_span:
                            home_odd = float(home_span.text.strip().replace(',', '.'))
                    
                    # Draw odd (segunda célula)
                    if not odds_cells[1].select("span.oddsCell__lineThrough"):
                        draw_span = odds_cells[1].select_one("span")
                        if draw_span:
                            draw_odd = float(draw_span.text.strip().replace(',', '.'))
                    
                    # Away odd (terceira célula)
                    if not odds_cells[2].select("span.oddsCell__lineThrough"):
                        away_span = odds_cells[2].select_one("span")
                        if away_span:
                            away_odd = float(away_span.text.strip().replace(',', '.'))
                    
                    if home_odd or draw_odd or away_odd:
                        if line_key not in eh_data:
                            eh_data[line_key] = []
                        
                        eh_data[line_key].append({
                            'Bookmaker': bookmaker,
                            'Home': home_odd,
                            'Draw': draw_odd,
                            'Away': away_odd
                        })
                except:
                    continue
            
            data['Odds_EH_FT'] = eh_data
        
        except Exception as e:
            print(f"  ✗ Erro EH FT: {e}")
        
        return data
    
    def extract_odds_ou_ht(self, match_id, data):
        """Extrai odds Over/Under Half Time - TODAS AS LINHAS"""
        home_slug = data.get('Home_Slug', '')
        away_slug = data.get('Away_Slug', '')
        
        if not home_slug or not away_slug:
            return data
        
        url = f"{self.base_url}/match/football/{home_slug}/{away_slug}/odds/over-under/1st-half/?mid={match_id}"
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-table"))
            )
            
            # Clica em "Show more" se existir
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, "a.showMore__text")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Pega TODAS as linhas (span.wcl-oddsValue_jvPMg) e TODAS as tabelas
            line_spans = soup.select("span.wcl-oddsValue_jvPMg")
            tables = soup.select("div.ui-table.oddsCell__odds")
            
            ou_data = {}
            seen_lines = set()
            line_to_table = {}
            table_idx = 0
            
            # Mapeia linhas únicas para suas tabelas
            for line_span in line_spans:
                line_text = line_span.text.strip()
                if line_text and line_text.replace('.', '').replace(',', '').isdigit():
                    try:
                        line_value = float(line_text.replace(',', '.'))
                        
                        # Só processa cada linha uma vez
                        if line_value not in seen_lines:
                            seen_lines.add(line_value)
                            
                            if table_idx < len(tables):
                                line_to_table[line_value] = tables[table_idx]
                                table_idx += 1
                    except:
                        continue
            
            # Processa cada linha única
            for line_value in sorted(seen_lines):
                if line_value not in line_to_table:
                    continue
                    
                table = line_to_table[line_value]
                line_key = f"OU_{line_value}"
                ou_data[line_key] = []
                
                # Extrai odds desta tabela
                rows = table.select("div.ui-table__row")
                for row in rows:
                    bookmaker_elem = row.select_one("div.wcl-bookmakerLogo_4IUU0 a img")
                    if not bookmaker_elem:
                        continue
                    
                    bookmaker = (bookmaker_elem.get('title') or bookmaker_elem.get('alt', '')).strip()
                    odds_cells = row.select("a.oddsCell__odd")
                    
                    if len(odds_cells) >= 2:
                        try:
                            # Ignora odds canceladas
                            if odds_cells[0].select("span.oddsCell__lineThrough"):
                                continue
                            if odds_cells[1].select("span.oddsCell__lineThrough"):
                                continue
                            
                            over_span = odds_cells[0].select_one("span")
                            under_span = odds_cells[1].select_one("span")
                            
                            if over_span and under_span:
                                over = float(over_span.text.strip().replace(',', '.'))
                                under = float(under_span.text.strip().replace(',', '.'))
                                
                                ou_data[line_key].append({
                                    'Bookmaker': bookmaker,
                                    'Over': over,
                                    'Under': under
                                })
                        except:
                            continue
            
            data['Odds_OU_HT'] = ou_data
        
        except Exception as e:
            pass  # Erro tratado no nível superior
        
        return data
    
    def scrape_match(self, match_id):
        """Scraping completo de um jogo"""
        print(f"\n🎯 Processando {match_id}...")
        
        # 1. Info básica + slugs
        data = self.get_match_basic_info(match_id)
        
        if not data.get('Home_Slug') or not data.get('Away_Slug'):
            print(f"  ✗ Slugs não encontrados, pulando...")
            return None
        
        print(f"  ✓ {data.get('Home', '?')} vs {data.get('Away', '?')}")
        
        # 2. Odds 1X2 FT
        data = self.extract_odds_1x2_ft(match_id, data)
        if data.get('Odds_1X2_FT'):
            print(f"  ✓ 1X2 FT: {len(data['Odds_1X2_FT'])} casas")
        
        # 3. Odds 1X2 HT
        data = self.extract_odds_1x2_ht(match_id, data)
        if data.get('Odds_1X2_HT'):
            print(f"  ✓ 1X2 HT: {len(data['Odds_1X2_HT'])} casas")
        
        # 4. Odds Over/Under FT (TODAS as linhas)
        data = self.extract_odds_ou_ft(match_id, data)
        if data.get('Odds_OU_FT'):
            total_lines = len(data['Odds_OU_FT'])
            total_bookmakers = sum(len(odds) for odds in data['Odds_OU_FT'].values())
            print(f"  ✓ O/U FT: {total_lines} linhas, {total_bookmakers} odds")
        
        # 5. Odds Over/Under HT (TODAS as linhas)
        data = self.extract_odds_ou_ht(match_id, data)
        if data.get('Odds_OU_HT'):
            total_lines = len(data['Odds_OU_HT'])
            total_bookmakers = sum(len(odds) for odds in data['Odds_OU_HT'].values())
            print(f"  ✓ O/U HT: {total_lines} linhas, {total_bookmakers} odds")
        
        # 6. Odds BTTS FT
        data = self.extract_odds_btts_ft(match_id, data)
        if data.get('Odds_BTTS_FT'):
            print(f"  ✓ BTTS FT: {len(data['Odds_BTTS_FT'])} casas")
        
        # 7. Odds Double Chance FT
        data = self.extract_odds_dc_ft(match_id, data)
        if data.get('Odds_DC_FT'):
            print(f"  ✓ DC FT: {len(data['Odds_DC_FT'])} casas")
        
        # 8. Odds Correct Score FT
        data = self.extract_odds_cs_ft(match_id, data)
        if data.get('Odds_CS_FT'):
            total_scores = len(data['Odds_CS_FT'])
            total_cs_odds = sum(len(odds) for odds in data['Odds_CS_FT'].values())
            print(f"  ✓ CS FT: {total_scores} placares, {total_cs_odds} odds")
        
        # 9. Odds Asian Handicap FT
        data = self.extract_odds_asian_handicap_ft(match_id, data)
        if data.get('Odds_AH_FT'):
            total_lines = len(data['Odds_AH_FT'])
            total_ah_odds = sum(len(odds) for odds in data['Odds_AH_FT'].values())
            print(f"  ✓ Asian Handicap FT: {total_lines} linhas, {total_ah_odds} odds")
        
        # 10. Odds European Handicap FT
        data = self.extract_odds_european_handicap_ft(match_id, data)
        if data.get('Odds_EH_FT'):
            total_lines = len(data['Odds_EH_FT'])
            total_eh_odds = sum(len(odds) for odds in data['Odds_EH_FT'].values())
            print(f"  ✓ European Handicap FT: {total_lines} linhas, {total_eh_odds} odds")
        
        # 11. Estatísticas FT
        data = self.extract_statistics_ft(match_id, data)
        if data.get('Statistics_FT'):
            print(f"  ✓ Stats FT: {len(data['Statistics_FT'])} métricas")
        
        # 10. Estatísticas HT (1º tempo)
        data = self.extract_statistics_ht(match_id, data)
        if data.get('Statistics_HT'):
            print(f"  ✓ Stats HT: {len(data['Statistics_HT'])} métricas")
        
        # 11. Estatísticas 2T (2º tempo)
        data = self.extract_statistics_2t(match_id, data)
        if data.get('Statistics_2T'):
            print(f"  ✓ Stats 2T: {len(data['Statistics_2T'])} métricas")
        
        # 12. Placar e minutos dos gols (somente jogos passados)
        data = self.extract_goals_and_minutes(match_id, data)
        if data.get('Min_Goals_Home') is not None:
            total_goals = len(data.get('Min_Goals_Home', [])) + len(data.get('Min_Goals_Away', []))
            if total_goals > 0:
                print(f"  ✓ Gols: {len(data['Min_Goals_Home'])}x{len(data['Min_Goals_Away'])} - Minutos: {data['Min_Goals_Home']} x {data['Min_Goals_Away']}")
        
        return data
    
    def scrape_matches(self, match_ids):
        """Scraping de múltiplos jogos com progresso"""
        self.accept_cookies()
        
        for match_id in tqdm(match_ids, desc="Scraping"):
            result = self.scrape_match(match_id)
            if result:
                self.results.append(result)
                
                # Salva incremental
                with open('flashscore_v2_incremental.json', 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return self.results
    
    def save_results(self, filename='flashscore_v2_results'):
        """Salva resultados em JSON e Excel"""
        # JSON
        json_file = f'{filename}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Salvo: {json_file}")
        
        # Excel - versão simples sem explodir listas
        try:
            df_simple = []
            for match in self.results:
                row = {
                    'Id': match.get('Id'),
                    'Date': match.get('Date'),
                    'Time': match.get('Time'),
                    'League': match.get('League'),
                    'Round': match.get('Round'),
                    'Home': match.get('Home'),
                    'Away': match.get('Away'),
                    'Best_Odd_1_FT': match.get('Best_Odd_1_FT'),
                    'Best_Odd_X_FT': match.get('Best_Odd_X_FT'),
                    'Best_Odd_2_FT': match.get('Best_Odd_2_FT'),
                }
                
                # Adiciona estatísticas
                for key, value in match.items():
                    if '_H_FT' in key or '_A_FT' in key:
                        row[key] = value
                
                df_simple.append(row)
            
            df = pd.DataFrame(df_simple)
            excel_file = f'{filename}.xlsx'
            df.to_excel(excel_file, index=False)
            print(f"✅ Salvo: {excel_file}")
        except Exception as e:
            print(f"⚠ Erro ao salvar Excel: {e}")
    
    def close(self):
        """Fecha o driver"""
        self.driver.quit()


if __name__ == "__main__":
    # Exemplo de uso
    scraper = FlashScoreScraper(headless=True)
    
    try:
        # IDs de exemplo (substitua pelos seus)
        match_ids = [
            'tYxjGH7i',  # Exemplo
        ]
        
        results = scraper.scrape_matches(match_ids)
        scraper.save_results()
        
        print(f"\n✅ Total: {len(results)} jogos processados")
        
    finally:
        scraper.close()
