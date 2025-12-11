import json
import os
import time
import subprocess
from datetime import datetime
from flashscore_scraper import FlashScoreScraper

# ==================== LIGAS 2021 (24 ligas) ====================
LINKS_2021 = [
'https://www.flashscore.com/football/argentina/torneo-betano-2021/results/',
'https://www.flashscore.com/football/bolivia/division-profesional-2021/results/',
'https://www.flashscore.com/football/brazil/serie-a-betano-2021/results/',
'https://www.flashscore.com/football/brazil/serie-b-2021/results/',
'https://www.flashscore.com/football/brazil/copa-betano-do-brasil-2021/results/',
'https://www.flashscore.com/football/chile/liga-de-primera-2021/results/',
'https://www.flashscore.com/football/china/super-league-2021/results/',
'https://www.flashscore.com/football/colombia/primera-a-2021/results/',
'https://www.flashscore.com/football/ecuador/liga-pro-2021/results/',
'https://www.flashscore.com/football/estonia/meistriliiga-2021/results/',
'https://www.flashscore.com/football/finland/veikkausliiga-2021/results/',
'https://www.flashscore.com/football/iceland/besta-deild-karla-2021/results/',
'https://www.flashscore.com/football/ireland/premier-division-2021/results/',
'https://www.flashscore.com/football/japan/j1-league-2021/results/',
'https://www.flashscore.com/football/norway/eliteserien-2021/results/',
'https://www.flashscore.com/football/paraguay/copa-de-primera-2021/results/',
'https://www.flashscore.com/football/peru/liga-1-2021/results/',
'https://www.flashscore.com/football/south-america/copa-libertadores-2021/results/',
'https://www.flashscore.com/football/south-america/copa-sudamericana-2021/results/',
'https://www.flashscore.com/football/south-korea/k-league-1-2021/results/',
'https://www.flashscore.com/football/sweden/allsvenskan-2021/results/',
'https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-2021/results/',
'https://www.flashscore.com/football/usa/mls-2021/results/',
'https://www.flashscore.com/football/venezuela/liga-futve-2021/results/',
]

# ==================== LIGAS 2021-2022 (54 ligas) ====================
LINKS_2021_2022 = [
'https://www.flashscore.com/football/australia/a-league-2021-2022/results/',
'https://www.flashscore.com/football/austria/bundesliga-2021-2022/results/',
'https://www.flashscore.com/football/belgium/jupiler-pro-league-2021-2022/results/',
'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih-2021-2022/results/',
'https://www.flashscore.com/football/bulgaria/efbet-league-2021-2022/results/',
'https://www.flashscore.com/football/croatia/hnl-2021-2022/results/',
'https://www.flashscore.com/football/cyprus/cyprus-league-2021-2022/results/',
'https://www.flashscore.com/football/czech-republic/chance-liga-2021-2022/results/',
'https://www.flashscore.com/football/denmark/superliga-2021-2022/results/',
'https://www.flashscore.com/football/egypt/premier-league-2021-2022/results/',
'https://www.flashscore.com/football/england/championship-2021-2022/results/',
'https://www.flashscore.com/football/england/league-one-2021-2022/results/',
'https://www.flashscore.com/football/england/league-two-2021-2022/results/',
'https://www.flashscore.com/football/england/premier-league-2021-2022/results/',
'https://www.flashscore.com/football/europe/champions-league-2021-2022/results/',
'https://www.flashscore.com/football/europe/europa-conference-league-2021-2022/results/',
'https://www.flashscore.com/football/europe/europa-league-2021-2022/results/',
'https://www.flashscore.com/football/france/ligue-1-2021-2022/results/',
'https://www.flashscore.com/football/france/ligue-2-2021-2022/results/',
'https://www.flashscore.com/football/france/national-2021-2022/results/',
'https://www.flashscore.com/football/germany/2-bundesliga-2021-2022/results/',
'https://www.flashscore.com/football/germany/bundesliga-2021-2022/results/',
'https://www.flashscore.com/football/germany/3-liga-2021-2022/results/',
'https://www.flashscore.com/football/greece/super-league-2021-2022/results/',
'https://www.flashscore.com/football/israel/ligat-ha-al-2021-2022/results/',
'https://www.flashscore.com/football/italy/serie-a-2021-2022/results/',
'https://www.flashscore.com/football/italy/serie-b-2021-2022/results/',
'https://www.flashscore.com/football/italy/serie-c-group-a-2021-2022/results/',
'https://www.flashscore.com/football/italy/serie-c-group-b-2021-2022/results/',
'https://www.flashscore.com/football/italy/serie-c-group-c-2021-2022/results/',
'https://www.flashscore.com/football/mexico/liga-mx-2021-2022/results/',
'https://www.flashscore.com/football/netherlands/eredivisie-2021-2022/results/',
'https://www.flashscore.com/football/netherlands/eerste-divisie-2021-2022/results/',
'https://www.flashscore.com/football/northern-ireland/nifl-premiership-2021-2022/results/',
'https://www.flashscore.com/football/poland/ekstraklasa-2021-2022/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2-2021-2022/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2021-2022/results/',
'https://www.flashscore.com/football/romania/superliga-2021-2022/results/',
'https://www.flashscore.com/football/saudi-arabia/saudi-professional-league-2021-2022/results/',
'https://www.flashscore.com/football/scotland/championship-2021-2022/results/',
'https://www.flashscore.com/football/scotland/premiership-2021-2022/results/',
'https://www.flashscore.com/football/scotland/league-one-2021-2022/results/',
'https://www.flashscore.com/football/scotland/league-two-2021-2022/results/',
'https://www.flashscore.com/football/serbia/mozzart-bet-super-liga-2021-2022/results/',
'https://www.flashscore.com/football/slovakia/nike-liga-2021-2022/results/',
'https://www.flashscore.com/football/slovenia/prva-liga-2021-2022/results/',
'https://www.flashscore.com/football/south-africa/betway-premiership-2021-2022/results/',
'https://www.flashscore.com/football/spain/laliga-2021-2022/results/',
'https://www.flashscore.com/football/spain/laliga2-2021-2022/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-1-2021-2022/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-2-2021-2022/results/',
'https://www.flashscore.com/football/switzerland/super-league-2021-2022/results/',
'https://www.flashscore.com/football/turkey/super-lig-2021-2022/results/',
'https://www.flashscore.com/football/ukraine/premier-league-2021-2022/results/',
'https://www.flashscore.com/football/wales/cymru-premier-2021-2022/results/'
]

# ==================== LIGAS 2022 (24 ligas) ====================
LINKS_2022 = [
'https://www.flashscore.com/football/argentina/torneo-betano-2022/results/',
'https://www.flashscore.com/football/bolivia/division-profesional-2022/results/',
'https://www.flashscore.com/football/brazil/serie-a-betano-2022/results/',
'https://www.flashscore.com/football/brazil/serie-b-2022/results/',
'https://www.flashscore.com/football/brazil/copa-betano-do-brasil-2022/results/',
'https://www.flashscore.com/football/chile/liga-de-primera-2022/results/',
'https://www.flashscore.com/football/china/super-league-2022/results/',
'https://www.flashscore.com/football/colombia/primera-a-2022/results/',
'https://www.flashscore.com/football/ecuador/liga-pro-2022/results/',
'https://www.flashscore.com/football/estonia/meistriliiga-2022/results/',
'https://www.flashscore.com/football/finland/veikkausliiga-2022/results/',
'https://www.flashscore.com/football/iceland/besta-deild-karla-2022/results/',
'https://www.flashscore.com/football/ireland/premier-division-2022/results/',
'https://www.flashscore.com/football/japan/j1-league-2022/results/',
'https://www.flashscore.com/football/norway/eliteserien-2022/results/',
'https://www.flashscore.com/football/paraguay/copa-de-primera-2022/results/',
'https://www.flashscore.com/football/peru/liga-1-2022/results/',
'https://www.flashscore.com/football/south-america/copa-libertadores-2022/results/',
'https://www.flashscore.com/football/south-america/copa-sudamericana-2022/results/',
'https://www.flashscore.com/football/south-korea/k-league-1-2022/results/',
'https://www.flashscore.com/football/sweden/allsvenskan-2022/results/',
'https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-2022/results/',
'https://www.flashscore.com/football/usa/mls-2022/results/',
'https://www.flashscore.com/football/venezuela/liga-futve-2022/results/',
]

# ==================== LIGAS 2022-2023 (54 ligas) ====================
LINKS_2022_2023 = [
'https://www.flashscore.com/football/australia/a-league-2022-2023/results/',
'https://www.flashscore.com/football/austria/bundesliga-2022-2023/results/',
'https://www.flashscore.com/football/belgium/jupiler-pro-league-2022-2023/results/',
'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih-2022-2023/results/',
'https://www.flashscore.com/football/bulgaria/efbet-league-2022-2023/results/',
'https://www.flashscore.com/football/croatia/hnl-2022-2023/results/',
'https://www.flashscore.com/football/cyprus/cyprus-league-2022-2023/results/',
'https://www.flashscore.com/football/czech-republic/chance-liga-2022-2023/results/',
'https://www.flashscore.com/football/denmark/superliga-2022-2023/results/',
'https://www.flashscore.com/football/egypt/premier-league-2022-2023/results/',
'https://www.flashscore.com/football/england/championship-2022-2023/results/',
'https://www.flashscore.com/football/england/league-one-2022-2023/results/',
'https://www.flashscore.com/football/england/league-two-2022-2023/results/',
'https://www.flashscore.com/football/england/premier-league-2022-2023/results/',
'https://www.flashscore.com/football/europe/champions-league-2022-2023/results/',
'https://www.flashscore.com/football/europe/europa-conference-league-2022-2023/results/',
'https://www.flashscore.com/football/europe/europa-league-2022-2023/results/',
'https://www.flashscore.com/football/france/ligue-1-2022-2023/results/',
'https://www.flashscore.com/football/france/ligue-2-2022-2023/results/',
'https://www.flashscore.com/football/france/national-2022-2023/results/',
'https://www.flashscore.com/football/germany/2-bundesliga-2022-2023/results/',
'https://www.flashscore.com/football/germany/bundesliga-2022-2023/results/',
'https://www.flashscore.com/football/germany/3-liga-2022-2023/results/',
'https://www.flashscore.com/football/greece/super-league-2022-2023/results/',
'https://www.flashscore.com/football/israel/ligat-ha-al-2022-2023/results/',
'https://www.flashscore.com/football/italy/serie-a-2022-2023/results/',
'https://www.flashscore.com/football/italy/serie-b-2022-2023/results/',
'https://www.flashscore.com/football/italy/serie-c-group-a-2022-2023/results/',
'https://www.flashscore.com/football/italy/serie-c-group-b-2022-2023/results/',
'https://www.flashscore.com/football/italy/serie-c-group-c-2022-2023/results/',
'https://www.flashscore.com/football/mexico/liga-mx-2022-2023/results/',
'https://www.flashscore.com/football/netherlands/eredivisie-2022-2023/results/',
'https://www.flashscore.com/football/netherlands/eerste-divisie-2022-2023/results/',
'https://www.flashscore.com/football/northern-ireland/nifl-premiership-2022-2023/results/',
'https://www.flashscore.com/football/poland/ekstraklasa-2022-2023/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2-2022-2023/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2022-2023/results/',
'https://www.flashscore.com/football/romania/superliga-2022-2023/results/',
'https://www.flashscore.com/football/saudi-arabia/saudi-professional-league-2022-2023/results/',
'https://www.flashscore.com/football/scotland/championship-2022-2023/results/',
'https://www.flashscore.com/football/scotland/premiership-2022-2023/results/',
'https://www.flashscore.com/football/scotland/league-one-2022-2023/results/',
'https://www.flashscore.com/football/scotland/league-two-2022-2023/results/',
'https://www.flashscore.com/football/serbia/mozzart-bet-super-liga-2022-2023/results/',
'https://www.flashscore.com/football/slovakia/nike-liga-2022-2023/results/',
'https://www.flashscore.com/football/slovenia/prva-liga-2022-2023/results/',
'https://www.flashscore.com/football/south-africa/betway-premiership-2022-2023/results/',
'https://www.flashscore.com/football/spain/laliga-2022-2023/results/',
'https://www.flashscore.com/football/spain/laliga2-2022-2023/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-1-2022-2023/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-2-2022-2023/results/',
'https://www.flashscore.com/football/switzerland/super-league-2022-2023/results/',
'https://www.flashscore.com/football/turkey/super-lig-2022-2023/results/',
'https://www.flashscore.com/football/ukraine/premier-league-2022-2023/results/',
'https://www.flashscore.com/football/wales/cymru-premier-2022-2023/results/'
]

# ==================== LIGAS 2023 (24 ligas) ====================
LINKS_2023 = [
'https://www.flashscore.com/football/argentina/torneo-betano-2023/results/',
'https://www.flashscore.com/football/bolivia/division-profesional-2023/results/',
'https://www.flashscore.com/football/brazil/serie-a-betano-2023/results/',
'https://www.flashscore.com/football/brazil/serie-b-2023/results/',
'https://www.flashscore.com/football/brazil/copa-betano-do-brasil-2023/results/',
'https://www.flashscore.com/football/chile/liga-de-primera-2023/results/',
'https://www.flashscore.com/football/china/super-league-2023/results/',
'https://www.flashscore.com/football/colombia/primera-a-2023/results/',
'https://www.flashscore.com/football/ecuador/liga-pro-2023/results/',
'https://www.flashscore.com/football/estonia/meistriliiga-2023/results/',
'https://www.flashscore.com/football/finland/veikkausliiga-2023/results/',
'https://www.flashscore.com/football/iceland/besta-deild-karla-2023/results/',
'https://www.flashscore.com/football/ireland/premier-division-2023/results/',
'https://www.flashscore.com/football/japan/j1-league-2023/results/',
'https://www.flashscore.com/football/norway/eliteserien-2023/results/',
'https://www.flashscore.com/football/paraguay/copa-de-primera-2023/results/',
'https://www.flashscore.com/football/peru/liga-1-2023/results/',
'https://www.flashscore.com/football/south-america/copa-libertadores-2023/results/',
'https://www.flashscore.com/football/south-america/copa-sudamericana-2023/results/',
'https://www.flashscore.com/football/south-korea/k-league-1-2023/results/',
'https://www.flashscore.com/football/sweden/allsvenskan-2023/results/',
'https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-2023/results/',
'https://www.flashscore.com/football/usa/mls-2023/results/',
'https://www.flashscore.com/football/venezuela/liga-futve-2023/results/',
]

# ==================== LIGAS 2023-2024 (54 ligas) ====================
LINKS_2023_2024 = [
'https://www.flashscore.com/football/australia/a-league-2023-2024/results/',
'https://www.flashscore.com/football/austria/bundesliga-2023-2024/results/',
'https://www.flashscore.com/football/belgium/jupiler-pro-league-2023-2024/results/',
'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih-2023-2024/results/',
'https://www.flashscore.com/football/bulgaria/efbet-league-2023-2024/results/',
'https://www.flashscore.com/football/croatia/hnl-2023-2024/results/',
'https://www.flashscore.com/football/cyprus/cyprus-league-2023-2024/results/',
'https://www.flashscore.com/football/czech-republic/chance-liga-2023-2024/results/',
'https://www.flashscore.com/football/denmark/superliga-2023-2024/results/',
'https://www.flashscore.com/football/egypt/premier-league-2023-2024/results/',
'https://www.flashscore.com/football/england/championship-2023-2024/results/',
'https://www.flashscore.com/football/england/league-one-2023-2024/results/',
'https://www.flashscore.com/football/england/league-two-2023-2024/results/',
'https://www.flashscore.com/football/england/premier-league-2023-2024/results/',
'https://www.flashscore.com/football/europe/champions-league-2023-2024/results/',
'https://www.flashscore.com/football/europe/europa-conference-league-2023-2024/results/',
'https://www.flashscore.com/football/europe/europa-league-2023-2024/results/',
'https://www.flashscore.com/football/france/ligue-1-2023-2024/results/',
'https://www.flashscore.com/football/france/ligue-2-2023-2024/results/',
'https://www.flashscore.com/football/france/national-2023-2024/results/',
'https://www.flashscore.com/football/germany/2-bundesliga-2023-2024/results/',
'https://www.flashscore.com/football/germany/bundesliga-2023-2024/results/',
'https://www.flashscore.com/football/germany/3-liga-2023-2024/results/',
'https://www.flashscore.com/football/greece/super-league-2023-2024/results/',
'https://www.flashscore.com/football/israel/ligat-ha-al-2023-2024/results/',
'https://www.flashscore.com/football/italy/serie-a-2023-2024/results/',
'https://www.flashscore.com/football/italy/serie-b-2023-2024/results/',
'https://www.flashscore.com/football/italy/serie-c-group-a-2023-2024/results/',
'https://www.flashscore.com/football/italy/serie-c-group-b-2023-2024/results/',
'https://www.flashscore.com/football/italy/serie-c-group-c-2023-2024/results/',
'https://www.flashscore.com/football/mexico/liga-mx-2023-2024/results/',
'https://www.flashscore.com/football/netherlands/eredivisie-2023-2024/results/',
'https://www.flashscore.com/football/netherlands/eerste-divisie-2023-2024/results/',
'https://www.flashscore.com/football/northern-ireland/nifl-premiership-2023-2024/results/',
'https://www.flashscore.com/football/poland/ekstraklasa-2023-2024/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2-2023-2024/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2023-2024/results/',
'https://www.flashscore.com/football/romania/superliga-2023-2024/results/',
'https://www.flashscore.com/football/saudi-arabia/saudi-professional-league-2023-2024/results/',
'https://www.flashscore.com/football/scotland/championship-2023-2024/results/',
'https://www.flashscore.com/football/scotland/premiership-2023-2024/results/',
'https://www.flashscore.com/football/scotland/league-one-2023-2024/results/',
'https://www.flashscore.com/football/scotland/league-two-2023-2024/results/',
'https://www.flashscore.com/football/serbia/mozzart-bet-super-liga-2023-2024/results/',
'https://www.flashscore.com/football/slovakia/nike-liga-2023-2024/results/',
'https://www.flashscore.com/football/slovenia/prva-liga-2023-2024/results/',
'https://www.flashscore.com/football/south-africa/betway-premiership-2023-2024/results/',
'https://www.flashscore.com/football/spain/laliga-2023-2024/results/',
'https://www.flashscore.com/football/spain/laliga2-2023-2024/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-1-2023-2024/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-2-2023-2024/results/',
'https://www.flashscore.com/football/switzerland/super-league-2023-2024/results/',
'https://www.flashscore.com/football/turkey/super-lig-2023-2024/results/',
'https://www.flashscore.com/football/ukraine/premier-league-2023-2024/results/',
'https://www.flashscore.com/football/wales/cymru-premier-2023-2024/results/'
]

# ==================== LIGAS 2024 (24 ligas) ====================
LINKS_2024 = [
'https://www.flashscore.com/football/argentina/torneo-betano-2024/results/',
'https://www.flashscore.com/football/bolivia/division-profesional-2024/results/',
'https://www.flashscore.com/football/brazil/serie-a-betano-2024/results/',
'https://www.flashscore.com/football/brazil/serie-b-2024/results/',
'https://www.flashscore.com/football/brazil/copa-betano-do-brasil-2024/results/',
'https://www.flashscore.com/football/chile/liga-de-primera-2024/results/',
'https://www.flashscore.com/football/china/super-league-2024/results/',
'https://www.flashscore.com/football/colombia/primera-a-2024/results/',
'https://www.flashscore.com/football/ecuador/liga-pro-2024/results/',
'https://www.flashscore.com/football/estonia/meistriliiga-2024/results/',
'https://www.flashscore.com/football/finland/veikkausliiga-2024/results/',
'https://www.flashscore.com/football/iceland/besta-deild-karla-2024/results/',
'https://www.flashscore.com/football/ireland/premier-division-2024/results/',
'https://www.flashscore.com/football/japan/j1-league-2024/results/',
'https://www.flashscore.com/football/norway/eliteserien-2024/results/',
'https://www.flashscore.com/football/paraguay/copa-de-primera-2024/results/',
'https://www.flashscore.com/football/peru/liga-1-2024/results/',
'https://www.flashscore.com/football/south-america/copa-libertadores-2024/results/',
'https://www.flashscore.com/football/south-america/copa-sudamericana-2024/results/',
'https://www.flashscore.com/football/south-korea/k-league-1-2024/results/',
'https://www.flashscore.com/football/sweden/allsvenskan-2024/results/',
'https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-2024/results/',
'https://www.flashscore.com/football/usa/mls-2024/results/',
'https://www.flashscore.com/football/venezuela/liga-futve-2024/results/',
]

# ==================== LIGAS 2024-2025 (54 ligas) ====================
LINKS_2024_2025 = [
'https://www.flashscore.com/football/australia/a-league-2024-2025/results/',
'https://www.flashscore.com/football/austria/bundesliga-2024-2025/results/',
'https://www.flashscore.com/football/belgium/jupiler-pro-league-2024-2025/results/',
'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih-2024-2025/results/',
'https://www.flashscore.com/football/bulgaria/efbet-league-2024-2025/results/',
'https://www.flashscore.com/football/croatia/hnl-2024-2025/results/',
'https://www.flashscore.com/football/cyprus/cyprus-league-2024-2025/results/',
'https://www.flashscore.com/football/czech-republic/chance-liga-2024-2025/results/',
'https://www.flashscore.com/football/denmark/superliga-2024-2025/results/',
'https://www.flashscore.com/football/egypt/premier-league-2024-2025/results/',
'https://www.flashscore.com/football/england/championship-2024-2025/results/',
'https://www.flashscore.com/football/england/league-one-2024-2025/results/',
'https://www.flashscore.com/football/england/league-two-2024-2025/results/',
'https://www.flashscore.com/football/england/premier-league-2024-2025/results/',
'https://www.flashscore.com/football/europe/champions-league-2024-2025/results/',
'https://www.flashscore.com/football/europe/europa-conference-league-2024-2025/results/',
'https://www.flashscore.com/football/europe/europa-league-2024-2025/results/',
'https://www.flashscore.com/football/france/ligue-1-2024-2025/results/',
'https://www.flashscore.com/football/france/ligue-2-2024-2025/results/',
'https://www.flashscore.com/football/france/national-2024-2025/results/',
'https://www.flashscore.com/football/germany/2-bundesliga-2024-2025/results/',
'https://www.flashscore.com/football/germany/bundesliga-2024-2025/results/',
'https://www.flashscore.com/football/germany/3-liga-2024-2025/results/',
'https://www.flashscore.com/football/greece/super-league-2024-2025/results/',
'https://www.flashscore.com/football/israel/ligat-ha-al-2024-2025/results/',
'https://www.flashscore.com/football/italy/serie-a-2024-2025/results/',
'https://www.flashscore.com/football/italy/serie-b-2024-2025/results/',
'https://www.flashscore.com/football/italy/serie-c-group-a-2024-2025/results/',
'https://www.flashscore.com/football/italy/serie-c-group-b-2024-2025/results/',
'https://www.flashscore.com/football/italy/serie-c-group-c-2024-2025/results/',
'https://www.flashscore.com/football/mexico/liga-mx-2024-2025/results/',
'https://www.flashscore.com/football/netherlands/eredivisie-2024-2025/results/',
'https://www.flashscore.com/football/netherlands/eerste-divisie-2024-2025/results/',
'https://www.flashscore.com/football/northern-ireland/nifl-premiership-2024-2025/results/',
'https://www.flashscore.com/football/poland/ekstraklasa-2024-2025/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2-2024-2025/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2024-2025/results/',
'https://www.flashscore.com/football/romania/superliga-2024-2025/results/',
'https://www.flashscore.com/football/saudi-arabia/saudi-professional-league-2024-2025/results/',
'https://www.flashscore.com/football/scotland/championship-2024-2025/results/',
'https://www.flashscore.com/football/scotland/premiership-2024-2025/results/',
'https://www.flashscore.com/football/scotland/league-one-2024-2025/results/',
'https://www.flashscore.com/football/scotland/league-two-2024-2025/results/',
'https://www.flashscore.com/football/serbia/mozzart-bet-super-liga-2024-2025/results/',
'https://www.flashscore.com/football/slovakia/nike-liga-2024-2025/results/',
'https://www.flashscore.com/football/slovenia/prva-liga-2024-2025/results/',
'https://www.flashscore.com/football/south-africa/betway-premiership-2024-2025/results/',
'https://www.flashscore.com/football/spain/laliga-2024-2025/results/',
'https://www.flashscore.com/football/spain/laliga2-2024-2025/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-1-2024-2025/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-2-2024-2025/results/',
'https://www.flashscore.com/football/switzerland/super-league-2024-2025/results/',
'https://www.flashscore.com/football/turkey/super-lig-2024-2025/results/',
'https://www.flashscore.com/football/ukraine/premier-league-2024-2025/results/',
'https://www.flashscore.com/football/wales/cymru-premier-2024-2025/results/'
]

LINKS_2025 = [
'https://www.flashscore.com/football/argentina/torneo-betano-2025/results/',
'https://www.flashscore.com/football/bolivia/division-profesional-2025/results/',
'https://www.flashscore.com/football/brazil/serie-a-betano-2025/results/',
'https://www.flashscore.com/football/brazil/serie-b-2025/results/',
'https://www.flashscore.com/football/brazil/copa-betano-do-brasil-2025/results/',
'https://www.flashscore.com/football/chile/liga-de-primera-2025/results/',
'https://www.flashscore.com/football/china/super-league-2025/results/',
'https://www.flashscore.com/football/colombia/primera-a-2025/results/',
'https://www.flashscore.com/football/ecuador/liga-pro-2025/results/',
'https://www.flashscore.com/football/estonia/meistriliiga-2025/results/',
'https://www.flashscore.com/football/finland/veikkausliiga-2025/results/',
'https://www.flashscore.com/football/iceland/besta-deild-karla-2025/results/',
'https://www.flashscore.com/football/ireland/premier-division-2025/results/',
'https://www.flashscore.com/football/japan/j1-league-2025/results/',
'https://www.flashscore.com/football/norway/eliteserien-2025/results/',
'https://www.flashscore.com/football/paraguay/copa-de-primera-2025/results/',
'https://www.flashscore.com/football/peru/liga-1-2025/results/',
'https://www.flashscore.com/football/south-america/copa-libertadores-2025/results/',
'https://www.flashscore.com/football/south-america/copa-sudamericana-2025/results/',
'https://www.flashscore.com/football/south-korea/k-league-1-2025/results/',
'https://www.flashscore.com/football/sweden/allsvenskan-2025/results/',
'https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-2025/results/',
'https://www.flashscore.com/football/usa/mls-2025/results/',
'https://www.flashscore.com/football/venezuela/liga-futve-2025/results/',
]

# ==================== LIGAS 2025-2026 (54 ligas) ====================
LINKS_2025_2026 = [
'https://www.flashscore.com/football/australia/a-league-2025-2026/results/',
'https://www.flashscore.com/football/austria/bundesliga-2025-2026/results/',
'https://www.flashscore.com/football/belgium/jupiler-pro-league-2025-2026/results/',
'https://www.flashscore.com/football/bosnia-and-herzegovina/wwin-liga-bih-2025-2026/results/',
'https://www.flashscore.com/football/bulgaria/efbet-league-2025-2026/results/',
'https://www.flashscore.com/football/croatia/hnl-2025-2026/results/',
'https://www.flashscore.com/football/cyprus/cyprus-league-2025-2026/results/',
'https://www.flashscore.com/football/czech-republic/chance-liga-2025-2026/results/',
'https://www.flashscore.com/football/denmark/superliga-2025-2026/results/',
'https://www.flashscore.com/football/egypt/premier-league-2025-2026/results/',
'https://www.flashscore.com/football/england/championship-2025-2026/results/',
'https://www.flashscore.com/football/england/league-one-2025-2026/results/',
'https://www.flashscore.com/football/england/league-two-2025-2026/results/',
'https://www.flashscore.com/football/england/premier-league-2025-2026/results/',
'https://www.flashscore.com/football/europe/champions-league-2025-2026/results/',
'https://www.flashscore.com/football/europe/europa-conference-league-2025-2026/results/',
'https://www.flashscore.com/football/europe/europa-league-2025-2026/results/',
'https://www.flashscore.com/football/france/ligue-1-2025-2026/results/',
'https://www.flashscore.com/football/france/ligue-2-2025-2026/results/',
'https://www.flashscore.com/football/france/national-2025-2026/results/',
'https://www.flashscore.com/football/germany/2-bundesliga-2025-2026/results/',
'https://www.flashscore.com/football/germany/bundesliga-2025-2026/results/',
'https://www.flashscore.com/football/germany/3-liga-2025-2026/results/',
'https://www.flashscore.com/football/greece/super-league-2025-2026/results/',
'https://www.flashscore.com/football/israel/ligat-ha-al-2025-2026/results/',
'https://www.flashscore.com/football/italy/serie-a-2025-2026/results/',
'https://www.flashscore.com/football/italy/serie-b-2025-2026/results/',
'https://www.flashscore.com/football/italy/serie-c-group-a-2025-2026/results/',
'https://www.flashscore.com/football/italy/serie-c-group-b-2025-2026/results/',
'https://www.flashscore.com/football/italy/serie-c-group-c-2025-2026/results/',
'https://www.flashscore.com/football/mexico/liga-mx-2025-2026/results/',
'https://www.flashscore.com/football/netherlands/eredivisie-2025-2026/results/',
'https://www.flashscore.com/football/netherlands/eerste-divisie-2025-2026/results/',
'https://www.flashscore.com/football/northern-ireland/nifl-premiership-2025-2026/results/',
'https://www.flashscore.com/football/poland/ekstraklasa-2025-2026/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2-2025-2026/results/',
'https://www.flashscore.com/football/portugal/liga-portugal-2025-2026/results/',
'https://www.flashscore.com/football/romania/superliga-2025-2026/results/',
'https://www.flashscore.com/football/saudi-arabia/saudi-professional-league-2025-2026/results/',
'https://www.flashscore.com/football/scotland/championship-2025-2026/results/',
'https://www.flashscore.com/football/scotland/premiership-2025-2026/results/',
'https://www.flashscore.com/football/scotland/league-one-2025-2026/results/',
'https://www.flashscore.com/football/scotland/league-two-2025-2026/results/',
'https://www.flashscore.com/football/serbia/mozzart-bet-super-liga-2025-2026/results/',
'https://www.flashscore.com/football/slovakia/nike-liga-2025-2026/results/',
'https://www.flashscore.com/football/slovenia/prva-liga-2025-2026/results/',
'https://www.flashscore.com/football/south-africa/betway-premiership-2025-2026/results/',
'https://www.flashscore.com/football/spain/laliga-2025-2026/results/',
'https://www.flashscore.com/football/spain/laliga2-2025-2026/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-1-2025-2026/results/',
'https://www.flashscore.com/football/spain/primera-rfef-group-2-2025-2026/results/',
'https://www.flashscore.com/football/switzerland/super-league-2025-2026/results/',
'https://www.flashscore.com/football/turkey/super-lig-2025-2026/results/',
'https://www.flashscore.com/football/ukraine/premier-league-2025-2026/results/',
'https://www.flashscore.com/football/wales/cymru-premier-2025-2026/results/'
]

def extract_country_from_url(url):
    """Extrai o país da URL"""
    parts = url.split('/football/')
    if len(parts) > 1:
        country = parts[1].split('/')[0]
        return country.lower()
    return 'unknown'


def extract_league_name_from_url(url):
    """Extrai o nome da liga da URL"""
    parts = url.split('/football/')
    if len(parts) > 1:
        league = parts[1].split('/')[1]
        return league.replace('-', ' ').title()
    return 'Unknown League'


def extract_season_from_url(url):
    """Extrai a temporada da URL"""
    if '2024-2025' in url:
        return '2024-2025'
    elif '2024' in url:
        return '2024'
    return 'unknown'


def get_match_ids_from_league(scraper, league_url):
    """Extrai todos os IDs de partidas de uma página de liga"""
    print(f"\n🔍 Carregando: {league_url.split('/football/')[1]}")
    
    # Verifica e recria driver se necessário
    recreate_driver_if_needed(scraper)
    
    scraper.driver.get(league_url)
    
    try:
        time.sleep(3)
        
        # PRIMEIRO: Aceitar cookies se aparecer banner
        try:
            cookie_button = scraper.driver.find_element("css selector", "button#onetrust-accept-btn-handler")
            if cookie_button.is_displayed():
                cookie_button.click()
                print(f"  ✓ Cookies aceitos")
                time.sleep(2)
        except:
            # Se não encontrar botão de cookies, continua normalmente
            pass
        
        # SEGUNDO: Clica em "Show more matches" para expandir TODOS os jogos
        max_clicks = 200  # Aumentado para 200 cliques (mais que suficiente para qualquer liga)
        clicks = 0
        consecutive_fails = 0
        
        print(f"  ⏬ Expandindo todos os jogos...")
        
        while clicks < max_clicks and consecutive_fails < 3:
            try:
                # Procura o botão "Show more matches" pelo novo seletor do FlashScore
                # O botão é um <span> com data-testid="wcl-scores-caption-05"
                show_more_buttons = scraper.driver.find_elements("css selector", "span[data-testid='wcl-scores-caption-05']")
                clicked_this_round = False
                
                for button in show_more_buttons:
                    if button.is_displayed() and 'Show more' in button.text:
                        # Clica no elemento pai (o link) ao invés do span
                        parent = button.find_element("xpath", "..")
                        scraper.driver.execute_script("arguments[0].scrollIntoView(true);", parent)
                        time.sleep(0.3)
                        scraper.driver.execute_script("arguments[0].click();", parent)
                        time.sleep(2)  # Aguarda carregar novos jogos
                        clicks += 1
                        consecutive_fails = 0
                        clicked_this_round = True
                        if clicks % 10 == 0:
                            print(f"     {clicks} cliques...")
                        break
                
                if not clicked_this_round:
                    consecutive_fails += 1
                    time.sleep(0.5)
                    
            except Exception as e:
                consecutive_fails += 1
                time.sleep(0.5)
        
        # Aguarda carregar tudo após os cliques
        time.sleep(3)
        
        if clicks > 0:
            print(f"  ✓ Expandiu com {clicks} cliques")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        
        match_ids = []
        match_divs = soup.select("div.event__match")
        
        for div in match_divs:
            match_id = div.get('id')
            if match_id and match_id.startswith('g_1_'):
                match_id = match_id.replace('g_1_', '')
                match_ids.append(match_id)
        
        print(f"  ✓ {len(match_ids)} jogos encontrados")
        return match_ids
    
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return []


def recreate_driver_if_needed(scraper):
    """
    Verifica se o driver está ativo e recria se necessário
    Retorna True se teve que recriar, False caso contrário
    """
    try:
        # Tenta uma operação simples para verificar se o driver está vivo
        _ = scraper.driver.current_url
        return False
    except Exception as e:
        print(f"\n  ⚠️ Sessão perdida: {str(e)[:50]}...")
        print(f"  🔄 Recriando driver...")
        try:
            scraper.driver.quit()
        except:
            pass
        
        # Recria o driver
        scraper.driver = scraper.setup_driver(headless=True)
        print(f"  ✓ Driver recriado")
        return True


def load_existing_data(filename):
    """Carrega dados existentes de um arquivo JSON se ele existir"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def get_processed_match_ids(country_data):
    """Extrai todos os IDs de jogos já processados de um país"""
    processed_ids = set()
    if country_data and 'leagues' in country_data:
        for league in country_data['leagues']:
            if 'matches' in league:
                for match in league['matches']:
                    # Tenta extrair ID de diferentes campos possíveis
                    match_id = match.get('Match_ID') or match.get('match_id')
                    if match_id:
                        processed_ids.add(match_id)
    return processed_ids


def save_country_data(filename, country_data):
    """Salva dados do país em arquivo JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(country_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"  ❌ Erro ao salvar: {e}")
        return False


def process_season(scraper, league_urls, season_name, output_dir):
    """Processa todas as ligas de uma temporada específica"""
    print(f"\n{'=' * 100}")
    print(f"📅 TEMPORADA {season_name}")
    print(f"{'=' * 100}")
    print(f"Total de ligas: {len(league_urls)}")
    
    # Agrupa por país
    leagues_by_country = {}
    for url in league_urls:
        country = extract_country_from_url(url)
        league_name = extract_league_name_from_url(url)
        
        if country not in leagues_by_country:
            leagues_by_country[country] = []
        
        leagues_by_country[country].append({'url': url, 'name': league_name})
    
    print(f"\n📂 {len(leagues_by_country)} país(es) para processar:")
    for country, leagues in leagues_by_country.items():
        print(f"  • {country.upper()}: {len(leagues)} liga(s)")
    
    # Processa cada país
    for idx, (country, leagues) in enumerate(leagues_by_country.items(), 1):
        print(f"\n{'=' * 100}")
        print(f"🌎 [{idx}/{len(leagues_by_country)}] {country.upper()} - {season_name}")
        print(f"{'=' * 100}")
        
        filename = f"{output_dir}/{country}_{season_name.replace('/', '-')}.json"
        
        # Tenta carregar dados existentes
        existing_data = load_existing_data(filename)
        processed_ids = set()
        
        if existing_data:
            processed_ids = get_processed_match_ids(existing_data)
            print(f"📄 Arquivo existente encontrado: {len(processed_ids)} jogos já processados")
            print(f"   Continuando de onde parou...")
            country_data = existing_data
        else:
            print(f"📄 Iniciando novo arquivo...")
            country_data = {
                'country': country.upper(),
                'season': season_name,
                'scrape_date': datetime.now().isoformat(),
                'total_leagues': len(leagues),
                'leagues': []
            }
        
        # Processa cada liga do país
        for league in leagues:
            league_url = league['url']
            league_name = league['name']
            
            print(f"\n📂 {league_name}")
            
            # Busca se a liga já existe nos dados
            existing_league = None
            for lg in country_data['leagues']:
                if lg['name'] == league_name:
                    existing_league = lg
                    break
            
            # Se não existe, cria nova entrada
            if not existing_league:
                existing_league = {
                    'name': league_name,
                    'url': league_url,
                    'total_matches': 0,
                    'scraped_matches': 0,
                    'matches': []
                }
                country_data['leagues'].append(existing_league)
            
            # Extrai IDs já processados DESTA LIGA específica
            league_processed_ids = set()
            for match in existing_league['matches']:
                match_id = match.get('Match_ID') or match.get('match_id') or match.get('Id')
                if match_id:
                    league_processed_ids.add(match_id)
            
            if league_processed_ids:
                print(f"  📄 {len(league_processed_ids)} jogos já processados nesta liga")
            
            match_ids = get_match_ids_from_league(scraper, league_url)
            
            if not match_ids:
                print(f"  ⚠️  Nenhum jogo encontrado, pulando...")
                continue
            
            # Atualiza total de jogos da liga
            existing_league['total_matches'] = len(match_ids)
            
            # Filtra apenas IDs que ainda não foram processados NESTA LIGA
            new_match_ids = [mid for mid in match_ids if mid not in league_processed_ids]
            
            if not new_match_ids:
                print(f"  ✅ Liga já completa ({len(match_ids)} jogos)")
                continue
            
            print(f"  🔄 {len(new_match_ids)} novos jogos para processar (de {len(match_ids)} totais)")
            
            # Processa apenas jogos novos
            for i, match_id in enumerate(new_match_ids, 1):
                try:
                    # Verifica e recria driver se necessário
                    recreate_driver_if_needed(scraper)
                    
                    # Calcula posição atual (quantos já estão salvos + 1)
                    current_position = len(existing_league['matches']) + 1
                    print(f"  [{current_position:3d}/{len(match_ids)}] {match_id}...", end=" ", flush=True)
                    
                    match_data = scraper.scrape_match(match_id)
                    
                    if match_data:
                        # Valida se tem dados mínimos necessários
                        if not match_data.get('Home') or not match_data.get('Away'):
                            print(f"✗ Erro no jogo {match_id}")
                            continue
                        
                        # Adiciona o ID ao match_data para facilitar verificação futura
                        match_data['Match_ID'] = match_id
                        
                        # Adiciona à lista de jogos da liga
                        existing_league['matches'].append(match_data)
                        existing_league['scraped_matches'] = len(existing_league['matches'])
                        
                        # Salva progresso a cada jogo
                        if save_country_data(filename, country_data):
                            print("✓💾")
                        else:
                            print("✓⚠️")
                        
                        # Adiciona aos IDs processados
                        processed_ids.add(match_id)
                    else:
                        print(f"✗ Erro no jogo {match_id}")
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrompido pelo usuário!")
                    print(f"   Progresso salvo: {len(existing_league['matches'])} jogos de {league_name}")
                    raise
                except Exception as e:
                    print(f"✗ Erro no jogo {match_id}")
                
                time.sleep(1)  # Pausa entre jogos
            
            total_scraped = len(existing_league['matches'])
            print(f"  ✅ {total_scraped}/{len(match_ids)} jogos extraídos nesta liga")
            
            
        # Salva final do país
        save_country_data(filename, country_data)
        
        total_matches = sum(lg['scraped_matches'] for lg in country_data['leagues'])
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"\n✅ {country.upper()} ({season_name}) completo: {total_matches} jogos → {filename} ({size_mb:.1f} MB)")


def scrape_complete_all_seasons():
    """Função principal para scraping completo de todas as temporadas"""
    print("=" * 100)
    print("🚀 FLASHSCORE SCRAPER - COMPLETO")
    print("=" * 100)
    print(f"\n📊 ESCOPO TOTAL:")
    print(f"  • Temporada 2021: {len(LINKS_2021)} ligas")
    print(f"  • Temporada 2021-2022: {len(LINKS_2021_2022)} ligas")
    print(f"  • Temporada 2022: {len(LINKS_2022)} ligas")
    print(f"  • Temporada 2022-2023: {len(LINKS_2022_2023)} ligas")
    print(f"  • Temporada 2023: {len(LINKS_2023)} ligas")
    print(f"  • Temporada 2023-2024: {len(LINKS_2023_2024)} ligas")
    print(f"  • Temporada 2024: {len(LINKS_2024)} ligas")
    print(f"  • Temporada 2024-2025: {len(LINKS_2024_2025)} ligas")
    print(f"  • Temporada 2025: {len(LINKS_2025)} ligas")
    print(f"  • Temporada 2025-2026: {len(LINKS_2025_2026)} ligas")
    total = len(LINKS_2021) + len(LINKS_2021_2022) + len(LINKS_2022) + len(LINKS_2022_2023) + len(LINKS_2023) + len(LINKS_2023_2024) + len(LINKS_2024) + len(LINKS_2024_2025) + len(LINKS_2025) + len(LINKS_2025_2026)
    print(f"  • TOTAL: {total} ligas")
    print(f"\n⏱️  DURAÇÃO ESTIMADA: Vários dias")
    print(f"⚠️  O progresso será salvo continuamente (por país)")
    print(f"💾 Diretório de saída: jogos_passados/")
    print("\nPressione Ctrl+C a qualquer momento para interromper")
    print("=" * 100)
    
    time.sleep(5)
    
    output_dir = "jogos_passados"
    os.makedirs(output_dir, exist_ok=True)
    
    # Modo headless (sem interface gráfica) - funciona com os seletores corretos e aceitação de cookies
    scraper = FlashScoreScraper(headless=True)
    
    try:
        start_time = datetime.now()
        
        # ========================================
        # 🎯 ESCOLHA QUAIS TEMPORADAS PROCESSAR:
        # ========================================
        # Comente (#) as linhas das temporadas que NÃO quer processar
        # Ordem: 2025 → 2025-2026 → 2024 → 2024-2025 → 2023 → 2023-2024 → 2022 → 2022-2023 → 2021 → 2021-2022
        
        # FASE 1: Temporada 2025 (24 ligas - Sul América, Ásia, etc)
        print("\n\n" + "🟡" * 50)
        print("FASE 1 de 10: TEMPORADA 2025")
        print("🟡" * 50)
        process_season(scraper, LINKS_2025, "2025", output_dir)
        
        # FASE 2: Temporada 2025-2026 (54 ligas - Europa, etc)
        print("\n\n" + "🟠" * 50)
        print("FASE 2 de 10: TEMPORADA 2025-2026")
        print("🟠" * 50)
        process_season(scraper, LINKS_2025_2026, "2025-2026", output_dir)
        
        # FASE 3: Temporada 2024 (24 ligas - Sul América, Ásia, etc)
        print("\n\n" + "🔵" * 50)
        print("FASE 3 de 10: TEMPORADA 2024")
        print("🔵" * 50)
        process_season(scraper, LINKS_2024, "2024", output_dir)
        
        # FASE 4: Temporada 2024-2025 (54 ligas - Europa, etc)
        print("\n\n" + "🟢" * 50)
        print("FASE 4 de 10: TEMPORADA 2024-2025")
        print("🟢" * 50)
        process_season(scraper, LINKS_2024_2025, "2024-2025", output_dir)
        
        # FASE 5: Temporada 2023 (24 ligas - Sul América, Ásia, etc)
        print("\n\n" + "🟣" * 50)
        print("FASE 5 de 10: TEMPORADA 2023")
        print("🟣" * 50)
        process_season(scraper, LINKS_2023, "2023", output_dir)
        
        # FASE 6: Temporada 2023-2024 (54 ligas - Europa, etc)
        print("\n\n" + "🔴" * 50)
        print("FASE 6 de 10: TEMPORADA 2023-2024")
        print("🔴" * 50)
        process_season(scraper, LINKS_2023_2024, "2023-2024", output_dir)
        
        # FASE 7: Temporada 2022 (24 ligas - Sul América, Ásia, etc)
        print("\n\n" + "⚪" * 50)
        print("FASE 7 de 10: TEMPORADA 2022")
        print("⚪" * 50)
        process_season(scraper, LINKS_2022, "2022", output_dir)
        
        # FASE 8: Temporada 2022-2023 (54 ligas - Europa, etc)
        print("\n\n" + "⚫" * 50)
        print("FASE 8 de 10: TEMPORADA 2022-2023")
        print("⚫" * 50)
        process_season(scraper, LINKS_2022_2023, "2022-2023", output_dir)
        
        # FASE 9: Temporada 2021 (24 ligas - Sul América, Ásia, etc)
        print("\n\n" + "🟤" * 50)
        print("FASE 9 de 10: TEMPORADA 2021")
        print("🟤" * 50)
        process_season(scraper, LINKS_2021, "2021", output_dir)
        
        # FASE 10: Temporada 2021-2022 (54 ligas - Europa, etc)
        print("\n\n" + "🟥" * 50)
        print("FASE 10 de 10: TEMPORADA 2021-2022")
        print("🟥" * 50)
        process_season(scraper, LINKS_2021_2022, "2021-2022", output_dir)
        
        # Resumo final
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n\n" + "=" * 100)
        print("🎉 SCRAPING COMPLETO FINALIZADO COM SUCESSO!")
        print("=" * 100)
        print(f"\n⏱️  Duração total: {duration}")
        print(f"📅 Início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Lista todos os arquivos criados
        files = sorted([f for f in os.listdir(output_dir) if f.endswith('.json')])
        print(f"\n📄 Total de arquivos criados: {len(files)}")
        
        total_matches = 0
        total_size_mb = 0
        
        for file in files:
            filepath = os.path.join(output_dir, file)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            total_size_mb += size_mb
            
            with open(filepath, 'r') as f:
                data = json.load(f)
                matches = sum(lg['scraped_matches'] for lg in data['leagues'])
                total_matches += matches
            
            print(f"  • {file}: {matches} jogos ({size_mb:.1f} MB)")
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"  • Total de jogos: {total_matches:,}")
        print(f"  • Tamanho total: {total_size_mb:.1f} MB")
        print(f"  • Média por jogo: {(total_size_mb * 1024) / total_matches:.2f} KB")
        print("=" * 100)
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 100)
        print("⚠️  INTERROMPIDO PELO USUÁRIO (Ctrl+C)")
        print("=" * 100)
        print("\n✅ Progresso foi salvo automaticamente")
        print("💡 Você pode continuar depois executando o script novamente")
        print("   O script verificará os IDs já processados e continuará de onde parou")
        print("   (Não perderá nenhum dado - apenas processará os jogos que faltam)")
        print("=" * 100)
    
    finally:
        scraper.close()


if __name__ == "__main__":
    scrape_complete_all_seasons()
