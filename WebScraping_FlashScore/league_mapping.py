"""
Mapeamento centralizado de ligas de futebol para padronização de nomes
Usado para converter nomes de ligas do FlashScore para formato padrão
"""

# Dicionário de mapeamento de ligas
# Chave: Nome da liga no formato original
# Valor: Nome padronizado
LEAGUE_MAPPING = {
    # NOVAS ENTRADAS
    'World - Club Friendly': "WORLD CLUB FRIENDLY",
    'World - Kings World Cup Nations': "WORLD KINGS WORLD CUP NATIONS",
    'Asia - AFC Asian Cup U23': "ASIA AFC ASIAN CUP U23",
    'Africa - Africa Cup of Nations': "AFRICA CUP OF NATIONS",
    'Botswana - Premier League': "BOTSWANA 1",
    'Lebanon - Lebanese Cup': "LEBANON CUP",
    'Macao - Elite League': "MACAO 1",
    'Malaysia - Malaysia Cup': "MALAYSIA CUP",
    'Philippines - PFL': "PHILIPPINES PFL",
    'World - Friendly International': "WORLD FRIENDLY INTERNATIONAL",
    'Panama - LPF': "PANAMA 1",
    'Chile - Super Cup': "CHILE SUPER CUP",
    'Jordan - Premier League': "JORDAN 1",
    'Spain - Super Cup Women': "SPAIN SUPER CUP WOMEN",
    'Europe - Atlantic Cup': "EUROPA ATLANTIC CUP",
    'Austria - OFB Cup': "AUSTRIA OFB CUP",
    'Asia - ASEAN Club Championship': "ASIA ASEAN CLUB CHAMPIONSHIP",
    'Brazil - Copa Alagoas': "BRAZIL COPA ALAGOAS",
    'Kuwait - Super Cup': "KUWAIT SUPER CUP",
    'Northern Ireland - Irish League Cup': "NORTHERN IRELAND IRISH LEAGUE CUP",
    'World - Club Friendly Women': "WORLD CLUB FRIENDLY WOM",
    "World - FIFA Women's Champions Cup": "WORLD FIFA WOMENS CHAMPIONS CUP",
    'World - Friendly International Women': "WORLD FRIENDLY INTERNATIONAL WOM",
    'Iceland - League Cup': "ICELAND LEAGUE CUP",
    'Bolivia - Torneo Amistoso de Verano': "BOLIVIA TORNEO AMISTOSO DE VERANO",
    'Hungary - NB II.': "HUNGARY 2",
    'United Arab Emirates - Presidents Cup': "UAE PRESIDENTS CUP",
    'Bulgaria - Super Cup': "BULGARIA SUPER CUP",





    # ARGENTINA
    "ARGENTINA - COPA DE LA LIGA PROFESIONAL": "ARGENTINA COPA",
    "ARGENTINA - COPA DIEGO MARADONA": "ARGENTINA COPA",
    "ARGENTINA - COPA ARGENTINA": "ARGENTINA COPA",
    "ARGENTINA - SUPERLIGA": "ARGENTINA 1",
    "ARGENTINA - LIGA PROFESIONAL": "ARGENTINA 1",
    "ARGENTINA - TORNEO BETANO": "ARGENTINA 1",
    "ARGENTINA - PRIMERA NACIONAL": "ARGENTINA 2",
    "ARGENTINA - TORNEO FEDERAL": "ARGENTINA 3",
    "ARGENTINA - TROFEO DE CAMPEONES": "ARGENTINA TROFEO DE CAMPEONES",
    "Argentina - Torneo Betano": "ARGENTINA 1",
    "Argentina - Torneo Federal": "ARGENTINA 3",
    "Argentina - Liga Profesional": "ARGENTINA 1",
    "Argentina - Primera Nacional": "ARGENTINA 2",
    "Argentina - Trofeo de Campeones": "ARGENTINA TROFEO DE CAMPEONES",
    
    # AUSTRALIA
    "AUSTRALIA - A-LEAGUE": "AUSTRALIA 1",
    "AUSTRALIA - A-LEAGUE WOMEN": "AUSTRALIA 1 WOM",
    "AUSTRALIA - AUSTRALIAN CHAMPIONSHIP": "AUSTRALIA U23",
    "Australia - A-League": "AUSTRALIA 1",
    "Australia - A-League Women": "AUSTRALIA 1 WOM",
    "Australia - Australian Championship": "AUSTRALIA U23",
    
    # AUSTRIA
    "AUSTRIA - BUNDESLIGA": "AUSTRIA 1",
    "AUSTRIA - TIPICO BUNDESLIGA": "AUSTRIA 1",
    "AUSTRIA - 2. LIGA": "AUSTRIA 2",
    "Austria - Bundesliga": "AUSTRIA 1",
    "Austria - 2. Liga": "AUSTRIA 2",
    
    # AZERBAIJAN
    "AZERBAIJAN - PREMIER LEAGUE": "AZERBAIJAN 1",
    "Azerbaijan - Premier League": "AZERBAIJAN 1",
    
    # BELGIUM
    "BELGIUM - JUPILER PRO LEAGUE": "BELGIUM 1",
    "BELGIUM - JUPILER LEAGUE": "BELGIUM 1",
    "BELGIUM - PROXIMUS LEAGUE": "BELGIUM 2",
    "BELGIUM - CHALLENGER PRO LEAGUE": "BELGIUM 2",
    "BELGIUM - 1B PRO LEAGUE": "BELGIUM 2",
    "BELGIUM - BELGIAN CUP": "BELGIUM CUP",
    "Belgium - Jupiler Pro League": "BELGIUM 1",
    "Belgium - Challenger Pro League": "BELGIUM 2",
    "Belgium - Belgian Cup": "BELGIUM CUP",
    
    # BOLIVIA
    "BOLIVIA - DIVISION PROFESIONAL": "BOLIVIA 1",
    "BOLIVIA - NACIONAL B": "BOLIVIA 2",
    "BOLIVIA - COPA PACENA": "BOLIVIA CUP",
    "Bolivia - Division Profesional": "BOLIVIA 1",
    "Bolivia - Copa Pacena": "BOLIVIA CUP",
    
    # BOSNIA AND HERZEGOVINA
    "BOSNIA AND HERZEGOVINA - PREMIER LEAGUE": "BOSNIA 1",
    "BOSNIA AND HERZEGOVINA - WWIN LIGA BIH": "BOSNIA 1",
    "BOSNIA AND HERZEGOVINA - PREMIJER LIGA BIH": "BOSNIA 1",
    "BOSNIA AND HERZEGOVINA - PRVA LIGA": "BOSNIA 2",
    "BOSNIA AND HERZEGOVINA - FBIH": "BOSNIA 2",
    "Bosnia and Herzegovina - WWIN Liga BiH": "BOSNIA 1",
    
    # BRAZIL
    "BRAZIL - COPA BETANO DO BRASIL": "BRAZIL COPA",
    "BRAZIL - COPA DO BRASIL": "BRAZIL COPA",
    "BRAZIL - SERIE A": "BRAZIL 1",
    "BRAZIL - SERIE A BETANO": "BRAZIL 1",
    "BRAZIL - SERIE B": "BRAZIL 2",
    "BRAZIL - SERIE B SUPERBET": "BRAZIL 2",
    "BRAZIL - COPINHA": "BRAZIL COPINHA",
    "BRAZIL - CATARINENSE": "BRAZIL CATARINENSE",
    "BRAZIL - GAUCHO": "BRAZIL GAUCHO",
    "BRAZIL - MINEIRO": "BRAZIL MINEIRO",
    "BRAZIL - PAULISTA": "BRAZIL PAULISTA",
    "BRAZIL - CARIOCA": "BRAZIL CARIOCA",
    "Brazil - Serie A Betano": "BRAZIL 1",
    "Brazil - Serie B": "BRAZIL 2",
    "Brazil - Copa Betano do Brasil": "BRAZIL COPA",
    "Brazil - Copinha": "BRAZIL COPINHA",
    "Brazil - Catarinense": "BRAZIL CATARINENSE",
    "Brazil - Gaucho": "BRAZIL GAUCHO",
    "Brazil - Mineiro": "BRAZIL MINEIRO",
    "Brazil - Paulista": "BRAZIL PAULISTA",
    "Brazil - Carioca": "BRAZIL CARIOCA",
    
    # BULGARIA
    "BULGARIA - PARVA LIGA": "BULGARIA 1",
    "BULGARIA - VTORA LIGA": "BULGARIA 2",
    "BULGARIA - BULGARIAN CUP": "BULGARIA CUP",
    "Bulgaria - efbet League": "BULGARIA 1",
    "Bulgaria - Bulgarian Cup": "BULGARIA CUP",
    
    # CHILE
    "CHILE - PRIMERA DIVISION": "CHILE 1",
    "CHILE - PRIMERA B": "CHILE 2",
    "CHILE - LIGA DE PRIMERA": "CHILE 1",
    "CHILE - LIGA DE ASCENSO": "CHILE 2",
    "Chile - Liga de Primera": "CHILE 1",
    
    # CHINA
    "CHINA - SUPER LEAGUE": "CHINA 1",
    "CHINA - JIA LEAGUE": "CHINA 2",
    "CHINA - FA CUP": "CHINA CUP",
    "China - FA Cup": "CHINA CUP",
    
    # COLOMBIA
    "COLOMBIA - PRIMERA A": "COLOMBIA 1",
    "COLOMBIA - LIGA AGUILA": "COLOMBIA 1",
    "COLOMBIA - PRIMERA B": "COLOMBIA 2",
    "COLOMBIA - TORNEO AGUILA": "COLOMBIA 2",
    "COLOMBIA - COPA COLOMBIA": "COLOMBIA CUP",
    "COLOMBIA - SUPER CUP": "COLOMBIA SUPER CUP",
    "Colombia - Primera A": "COLOMBIA 1",
    "Colombia - Copa Colombia": "COLOMBIA CUP",
    "Colombia - Super Cup": "COLOMBIA SUPER CUP",
    
    # CROATIA
    "CROATIA - 1. HNL": "CROATIA 1",
    "CROATIA - 2. HNL": "CROATIA 2",
    "CROATIA - HNL": "CROATIA 1",
    "CROATIA - PRVA NL": "CROATIA 2",
    "Croatia - HNL": "CROATIA 1",
    
    # CYPRUS
    "CYPRUS - CYTA CHAMPIONSHIP": "CYPRUS 1",
    "CYPRUS - CYPRUS LEAGUE": "CYPRUS 1",
    "CYPRUS - DIVISION 2": "CYPRUS 2",
    "CYPRUS - CYPRUS CUP": "CYPRUS CUP",
    "Cyprus - Cyprus League": "CYPRUS 1",
    "Cyprus - Division 2": "CYPRUS 2",
    "Cyprus - Cyprus Cup": "CYPRUS CUP",
    
    # CZECH REPUBLIC
    "CZECH REPUBLIC - FORTUNA:LIGA": "CZECH 1",
    "CZECH REPUBLIC - CHANCE LIGA": "CZECH 1",
    "CZECH REPUBLIC - CHNL": "CZECH 2",
    "CZECH REPUBLIC - FNL": "CZECH 2",
    "CZECH REPUBLIC - TIPSPORT LIGA": "CZECH TIPSORT LIGA",
    "Czech Republic - Chance Liga": "CZECH 2",
    "Czech Republic - Tipsport liga": "CZECH TIPSORT LIGA",
    
    # DENMARK
    "DENMARK - SUPERLIGA": "DENMARK 1",
    "DENMARK - 1ST DIVISION": "DENMARK 2",
    "DENMARK - LANDSPOKAL CUP": "DENMARK CUP",
    "DENMARK - DANISH CUP WOMEN": "DENMARK CUP WOM",
    "Denmark - Superliga": "DENMARK 1",
    "Denmark - Landspokal Cup": "DENMARK CUP",
    "Denmark - Danish Cup Women": "DENMARK CUP WOM",
    
    # ECUADOR
    "ECUADOR - LIGA PRO": "ECUADOR 1",
    "ECUADOR - SERIE B": "ECUADOR 2",
    "ECUADOR - COPA ECUADOR": "ECUADOR CUP",
    "Ecuador - Liga Pro": "ECUADOR 1",
    "Ecuador - Copa Ecuador": "ECUADOR CUP",
    
    # EGYPT
    "EGYPT - PREMIER LEAGUE": "EGYPT 1",
    "EGYPT - DIVISION 2 A": "EGYPT 2",
    "EGYPT - EGYPT CUP": "EGYPT CUP",
    "EGYPT - LEAGUE CUP": "EGYPT LEAGUE CUP",
    "Egypt - Premier League": "EGYPT 1",
    "Egypt - Egypt Cup": "EGYPT CUP",
    "Egypt - League Cup": "EGYPT LEAGUE CUP",
    
    # ENGLAND
    "ENGLAND - PREMIER LEAGUE": "ENGLAND 1",
    "ENGLAND - CHAMPIONSHIP": "ENGLAND 2",
    "ENGLAND - LEAGUE ONE": "ENGLAND 3",
    "ENGLAND - LEAGUE TWO": "ENGLAND 4",
    "ENGLAND - NATIONAL LEAGUE": "ENGLAND 5",
    "ENGLAND - PREMIER LEAGUE 2": "ENGLAND U21",
    "ENGLAND - PREMIER LEAGUE CUP": "ENGLAND U21",
    "ENGLAND - FA CUP": "ENGLAND FA CUP",
    "ENGLAND - EFL CUP": "ENGLAND EFL CUP",
    "ENGLAND - EFL TROPHY": "ENGLAND EFL TROPHY",
    "ENGLAND - FA TROPHY": "ENGLAND FA TROPHY",
    "ENGLAND - WSL": "ENGLAND 1 WOM",
    "England - Premier League": "ENGLAND 1",
    "England - Championship": "ENGLAND 2",
    "England - League One": "ENGLAND 3",
    "England - League Two": "ENGLAND 4",
    "England - FA Cup": "ENGLAND FA CUP",
    "England - EFL Cup": "ENGLAND EFL CUP",
    "England - EFL Trophy": "ENGLAND EFL TROPHY",
    "England - FA Trophy": "ENGLAND FA TROPHY",
    "England - Premier League Cup": "ENGLAND U21",
    "England - WSL": "ENGLAND 1 WOM",
    
    # ESTONIA
    "ESTONIA - MEISTRILIIGA": "ESTONIA 1",
    "ESTONIA - ESILIIGA": "ESTONIA 2",
    
    # EUROPE
    "EUROPE - CHAMPIONS LEAGUE": "EUROPA CHAMPIONS LEAGUE",
    "EUROPE - EUROPA LEAGUE": "EUROPA LEAGUE",
    "EUROPE - CONFERENCE LEAGUE": "EUROPA CONFERENCE LEAGUE",
    "EUROPE - EUROPA CONFERENCE LEAGUE": "EUROPA CONFERENCE LEAGUE",
    "EUROPE - CHAMPIONS LEAGUE WOMEN": "EUROPA CHAMPIONS LEAGUE WOM",
    "EUROPE - UEFA NATIONS LEAGUE WOMEN": "EUROPA NATIONS LEAGUE WOM",
    "EUROPE - PREMIER LEAGUE INTERNATIONAL CUP": "EUROPA U21",
    "EUROPE - EURO U19 WOMEN": "EUROPA U19 WOM",
    "Europe - Champions League": "EUROPA CHAMPIONS LEAGUE",
    "Europe - Champions League Women": "EUROPA CHAMPIONS LEAGUE WOM",
    "Europe - Europa League": "EUROPA LEAGUE",
    "Europe - Conference League": "EUROPA CONFERENCE LEAGUE",
    "Europe - Premier League International Cup": "EUROPA U21",
    "Europe - Euro U19 Women": "EUROPA U19 WOM",
    "Europe - UEFA Nations League Women": "EUROPA NATIONS LEAGUE WOM",
    
    # FINLAND
    "FINLAND - VEIKKAUSLIIGA": "FINLAND 1",
    "FINLAND - YKKOSLIIGA": "FINLAND 2",
    "FINLAND - YKKONEN": "FINLAND 2",
    "Finland - Liiga Cup": "FINLAND LIIGA CUP",
    
    # FRANCE
    "FRANCE - LIGUE 1": "FRANCE 1",
    "FRANCE - LIGUE 2": "FRANCE 2",
    "FRANCE - NATIONAL": "FRANCE 3",
    "FRANCE - NATIONAL 2": "FRANCE 4",
    "FRANCE - COUPE DE FRANCE": "FRANCE CUP",
    "FRANCE - COUPE DE FRANCE WOMEN": "FRANCE CUP WOM",
    "FRANCE - SUPER CUP": "FRANCE SUPER CUP",
    "FRANCE - PREMIERE LIGUE WOMEN": "FRANCE 1 WOM",
    "France - Ligue 1": "FRANCE 1",
    "France - Ligue 2": "FRANCE 2",
    "France - National": "FRANCE 3",
    "France - Coupe de France": "FRANCE CUP",
    "France - Coupe de France Women": "FRANCE CUP WOM",
    "France - Super Cup": "FRANCE SUPER CUP",
    "France - Premiere Ligue Women": "FRANCE 1 WOM",
    
    # GERMANY
    "GERMANY - BUNDESLIGA": "GERMANY 1",
    "GERMANY - 2. BUNDESLIGA": "GERMANY 2",
    "GERMANY - 3. LIGA": "GERMANY 3",
    "GERMANY - DFB POKAL": "GERMANY CUP",
    "GERMANY - BUNDESLIGA WOMEN": "GERMANY 1 WOM",
    "Germany - Bundesliga": "GERMANY 1",
    "Germany - 2. Bundesliga": "GERMANY 2",
    "Germany - 3. Liga": "GERMANY 3",
    "Germany - DFB Pokal": "GERMANY CUP",
    "Germany - Bundesliga Women": "GERMANY 1 WOM",
    
    # GREECE
    "GREECE - SUPER LEAGUE": "GREECE 1",
    "GREECE - SUPER LEAGUE 2": "GREECE 2",
    "GREECE - GREEK CUP": "GREECE CUP",
    "GREECE - SUPER CUP": "GREECE SUPER CUP",
    "Greece - Super League": "GREECE 1",
    "Greece - Super League 2": "GREECE 2",
    "Greece - Greek Cup": "GREECE CUP",
    "Greece - Super Cup": "GREECE SUPER CUP",
    
    # HUNGARY
    "HUNGARY - OTP BANK LIGA": "HUNGARY 1",
    "HUNGARY - NB I.": "HUNGARY 1",
    "Hungary - NB I.": "HUNGARY 1",
    
    # ICELAND
    "ICELAND - BESTA DEILD KARLA": "ICELAND 1",
    "ICELAND - PEPSIDEILD": "ICELAND 1",
    "ICELAND - DIVISION 1": "ICELAND 2",
    "ICELAND - INKASSO-DEILDIN": "ICELAND 2",
    "ICELAND - LENGJUDEILDIN": "ICELAND 2",
    "ICELAND - REYKJAVIK CUP": "ICELAND REYKJAVIK CUP",
    
    # IRELAND
    "IRELAND - PREMIER DIVISION": "IRELAND 1",
    "IRELAND - DIVISION 1": "IRELAND 2",
    
    # ISRAEL
    "ISRAEL - LIGAT HA'AL": "ISRAEL 1",
    "ISRAEL - LEUMIT LEAGUE": "ISRAEL 2",
    "ISRAEL - STATE CUP": "ISRAEL CUP",
    "Israel - Ligat ha'Al": "ISRAEL 1",
    "Israel - Leumit League": "ISRAEL 2",
    
    # ITALY
    "ITALY - SERIE A": "ITALY 1",
    "ITALY - SERIE B": "ITALY 2",
    "ITALY - SERIE C": "ITALY 3",
    "ITALY - SERIE D": "ITALY 4",
    "ITALY - COPPA ITALIA": "ITALY CUP",
    "ITALY - COPPA ITALIA WOMEN": "ITALY CUP WOM",
    "ITALY - COPPA ITALIA SERIE C": "ITALY CUP SERIE C",
    "ITALY - SUPER CUP": "ITALY SUPER CUP",
    "ITALY - SUPER CUP WOMEN": "ITALY SUPER CUP WOMS",
    "ITALY - SERIE A WOMEN": "ITALY 1 WOM",
    "ITALY - PRIMAVERA 1": "ITALY U19",
    "Italy - Serie A": "ITALY 1",
    "Italy - Serie B": "ITALY 2",
    "Italy - Serie C": "ITALY 3",
    "Italy - Coppa Italia": "ITALY CUP",
    
    # JAPAN
    "JAPAN - J1 LEAGUE": "JAPAN 1",
    "JAPAN - J2 LEAGUE": "JAPAN 2",
    "JAPAN - WE LEAGUE WOMEN": "JAPAN WE LEAGUE WOM",
    "Japan - J1 League": "JAPAN 1",
    "Japan - J2 League": "JAPAN 2",
    
    # MEXICO
    "MEXICO - LIGA MX": "MEXICO 1",
    "MEXICO - LIGA DE EXPANSION MX": "MEXICO 2",
    "MEXICO - ASCENSO MX": "MEXICO 2",
    "MEXICO - LIGA MX WOMEN": "MEXICO 1 WOM",
    "Mexico - Liga MX": "MEXICO 1",
    "Mexico - Liga de Expansion MX": "MEXICO 2",
    
    # MOROCCO
    "MOROCCO - BOTOLA PRO": "MOROCCO 1",
    
    # NETHERLANDS
    "NETHERLANDS - EREDIVISIE": "NETHERLANDS 1",
    "NETHERLANDS - EERSTE DIVISIE": "NETHERLANDS 2",
    "NETHERLANDS - TWEEDE DIVISIE": "NETHERLANDS 3",
    "NETHERLANDS - KNVB BEKER": "NETHERLANDS CUP",
    "NETHERLANDS - KNVB BEKER WOMEN": "NETHERLANDS CUP WOM",
    "NETHERLANDS - EREDIVISIE WOMEN": "NETHERLANDS 1 WOM",
    "Netherlands - Eredivisie": "NETHERLANDS 1",
    "Netherlands - Eerste Divisie": "NETHERLANDS 2",
    
    # NORTHERN IRELAND
    "NORTHERN IRELAND - NIFL CHAMPIONSHIP": "NORTHERN IRELAND 1",
    "NORTHERN IRELAND - NIFL PREMIERSHIP": "NORTHERN IRELAND 2",
    "NORTHERN IRELAND - IRISH CUP": "NORTHERN IRELAND CUP",
    
    # NORWAY
    "NORWAY - ELITESERIEN": "NORWAY 1",
    "NORWAY - OBOS-LIGAEN": "NORWAY 2",
    "NORWAY - NM CUP": "NORWAY CUP",
    "Norway - Eliteserien": "NORWAY 1",
    
    # PARAGUAY
    "PARAGUAY - COPA DE PRIMERA": "PARAGUAY 1",
    "PARAGUAY - PRIMERA DIVISION": "PARAGUAY 1",
    "PARAGUAY - DIVISION INTERMEDIA": "PARAGUAY 2",
    "PARAGUAY - SUPER CUP": "PARAGUAY SUPER CUP",
    
    # PERU
    "PERU - LIGA 1": "PERU 1",
    "PERU - LIGA 2": "PERU 2",
    "Peru - Liga 1": "PERU 1",
    
    # POLAND
    "POLAND - EKSTRAKLASA": "POLAND 1",
    "POLAND - DIVISION 1": "POLAND 2",
    "POLAND - POLISH CUP": "POLAND CUP",
    "Poland - Ekstraklasa": "POLAND 1",
    "Poland - Division 1": "POLAND 2",
    
    # PORTUGAL
    "PORTUGAL - LIGA PORTUGAL": "PORTUGAL 1",
    "PORTUGAL - PRIMEIRA LIGA": "PORTUGAL 1",
    "PORTUGAL - LIGA PORTUGAL 2": "PORTUGAL 2",
    "PORTUGAL - LIGAPRO": "PORTUGAL 2",
    "PORTUGAL - LIGA 3": "PORTUGAL 3",
    "PORTUGAL - TAÇA DE PORTUGAL": "PORTUGAL CUP",
    "PORTUGAL - LEAGUE CUP": "PORTUGAL LEAGUE CUP",
    "Portugal - Liga Portugal": "PORTUGAL 1",
    "Portugal - Liga Portugal 2": "PORTUGAL 2",
    "Portugal - Liga 3": "PORTUGAL 3",
    
    # ROMANIA
    "ROMANIA - SUPERLIGA": "ROMANIA 1",
    "ROMANIA - LIGA 1": "ROMANIA 1",
    "ROMANIA - LIGA 2": "ROMANIA 2",
    "ROMANIA - ROMANIAN CUP": "ROMANIA CUP",
    "ROMANIA - SUPERLIGA WOMEN": "ROMANIA 1 WOM",
    "Romania - Superliga": "ROMANIA 1",
    "Romania - Liga 2": "ROMANIA 2",
    "Romania - Romanian Cup": "ROMANIA CUP",
    
    # SAUDI ARABIA
    "SAUDI ARABIA - SAUDI PROFESSIONAL LEAGUE": "SAUDI ARABIA 1",
    "SAUDI ARABIA - DIVISION 1": "SAUDI ARABIA 2",
    "SAUDI ARABIA - PREMIER LEAGUE WOMEN": "SAUDI ARABIA 1 WOM",
    "Saudi Arabia - Saudi Professional League": "SAUDI ARABIA 1",
    "Saudi Arabia - Division 1": "SAUDI ARABIA 2",
    
    # SCOTLAND
    "SCOTLAND - PREMIERSHIP": "SCOTLAND 1",
    "SCOTLAND - CHAMPIONSHIP": "SCOTLAND 2",
    "SCOTLAND - LEAGUE ONE": "SCOTLAND 3",
    "SCOTLAND - LEAGUE TWO": "SCOTLAND 4",
    "SCOTLAND - SCOTTISH CUP": "SCOTLAND CUP",
    "SCOTLAND - SCOTTISH CUP WOMEN": "SCOTLAND CUP WOM",
    "SCOTLAND - LEAGUE CUP": "SCOTLAND LEAGUE CUP",
    "SCOTLAND - CHALLENGE CUP": "SCOTLAND CHALLENGE CUP",
    "SCOTLAND - SWPL 1 WOMEN": "SCOTLAND 1 WOM",
    "Scotland - Premiership": "SCOTLAND 1",
    "Scotland - Championship": "SCOTLAND 2",
    "Scotland - League One": "SCOTLAND 3",
    "Scotland - League Two": "SCOTLAND 4",
    "Scotland - Scottish Cup": "SCOTLAND CUP",
    
    # SERBIA
    "SERBIA - SUPER LIGA": "SERBIA 1",
    "SERBIA - MOZZART BET SUPER LIGA": "SERBIA 1",
    "SERBIA - PRVA LIGA": "SERBIA 2",
    "SERBIA - MOZZART BET PRVA LIGA": "SERBIA 2",
    "Serbia - Mozzart Bet Super Liga": "SERBIA 1",
    
    # SLOVAKIA
    "SLOVAKIA - NIKE LIGA": "SLOVAKIA 1",
    "SLOVAKIA - FORTUNA LIGA": "SLOVAKIA 1",
    "SLOVAKIA - 2. LIGA": "SLOVAKIA 2",
    "Slovakia - Nike liga": "SLOVAKIA 1",
    
    # SLOVENIA
    "SLOVENIA - PRVA LIGA": "SLOVENIA 1",
    "SLOVENIA - SLOVENIAN CUP": "SLOVENIA CUP",
    "Slovenia - Prva liga": "SLOVENIA 1",
    "Slovenia - Slovenian Cup": "SLOVENIA CUP",
    
    # SOUTH AFRICA
    "SOUTH AFRICA - BETWAY PREMIERSHIP": "SOUTH AFRICA 1",
    "SOUTH AFRICA - MOTSEPE FOUNDATION CHAMPIONSHIP": "SOUTH AFRICA 2",
    "SOUTH AFRICA - CARLING KNOCKOUT": "SOUTH AFRICA CUP",
    "South Africa - Betway Premiership": "SOUTH AFRICA 1",
    
    # SOUTH AMERICA
    "SOUTH AMERICA - COPA LIBERTADORES": "COPA LIBERTADORES",
    "SOUTH AMERICA - COPA SUDAMERICANA": "COPA SUDAMERICANA",
    "SOUTH AMERICA - CONMEBOL NATIONS LEAGUE WOMEN": "SOUTH AMERICA CONMEBOL NATIONS LEAGUE WOM",
    "SOUTH AMERICA - SERIE RIO DE LA PLATA": "SOUTH AMERICA SERIE RIO DE LA PLATA",
    
    # SOUTH KOREA
    "SOUTH KOREA - K LEAGUE 1": "SOUTH KOREA 1",
    "SOUTH KOREA - K LEAGUE 2": "SOUTH KOREA 2",
    "SOUTH KOREA - KOREAN CUP": "SOUTH KOREA CUP",
    "South Korea - K League 1": "SOUTH KOREA 1",
    
    # SPAIN
    "SPAIN - LALIGA": "SPAIN 1",
    "SPAIN - LALIGA2": "SPAIN 2",
    "SPAIN - PRIMERA RFEF": "SPAIN 3",
    "SPAIN - SEGUNDA RFEF": "SPAIN 4",
    "SPAIN - COPA DEL REY": "SPAIN CUP",
    "SPAIN - COPA DE LA REINA WOMEN": "SPAIN CUP WOM",
    "SPAIN - SUPER CUP": "SPAIN SUPER CUP",
    "SPAIN - LIGA F WOMEN": "SPAIN 1 WOM",
    "Spain - LaLiga": "SPAIN 1",
    "Spain - LaLiga2": "SPAIN 2",
    "Spain - Primera RFEF": "SPAIN 3",
    "Spain - Copa del Rey": "SPAIN CUP",
    
    # SWEDEN
    "SWEDEN - ALLSVENSKAN": "SWEDEN 1",
    "SWEDEN - SUPERETTAN": "SWEDEN 2",
    
    # SWITZERLAND
    "SWITZERLAND - SUPER LEAGUE": "SWITZERLAND 1",
    "SWITZERLAND - CHALLENGE LEAGUE": "SWITZERLAND 2",
    "SWITZERLAND - SWISS CUP": "SWITZERLAND CUP",
    "SWITZERLAND - SWISS CUP WOMEN": "SWITZERLAND CUP WOM",
    "SWITZERLAND - SUPER LEAGUE WOMEN": "SWITZERLAND 1 WOM",
    "Switzerland - Super League": "SWITZERLAND 1",
    "Switzerland - Challenge League": "SWITZERLAND 2",
    "Switzerland - Swiss Cup": "SWITZERLAND CUP",
    
    # TUNISIA
    "TUNISIA - LIGUE PROFESSIONNELLE 1": "TUNISIA 1",
    "TUNISIA - LIGUE 2": "TUNISIA 2",
    "TUNISIA - TUNISIA CUP": "TUNISIA CUP",
    "Tunisia - Ligue Professionnelle 1": "TUNISIA 1",
    "Tunisia - Ligue 2": "TUNISIA 2",
    
    # TURKEY
    "TURKEY - SUPER LIG": "TURKEY 1",
    "TURKEY - 1. LIG": "TURKEY 2",
    "TURKEY - TURKISH CUP": "TURKEY CUP",
    "TURKEY - SUPER CUP": "TURKEY SUPER CUP",
    "TURKEY - SUPER LIG WOMEN": "TURKEY 1 WOM",
    "Turkey - Super Lig": "TURKEY 1",
    "Turkey - 1. Lig": "TURKEY 2",
    "Turkey - Turkish Cup": "TURKEY CUP",
    
    # UKRAINE
    "UKRAINE - PREMIER LEAGUE": "UKRAINE 1",
    "UKRAINE - PERSHA LIGA": "UKRAINE 2",
    "Ukraine - Premier League": "UKRAINE 1",
    "Ukraine - Persha Liga": "UKRAINE 2",
    
    # URUGUAY
    "URUGUAY - LIGA AUF URUGUAYA": "URUGUAY 1",
    "URUGUAY - PRIMERA DIVISION": "URUGUAY 1",
    "URUGUAY - SEGUNDA DIVISION": "URUGUAY 2",
    "URUGUAY - COPA DE LA LIGA AUF": "URUGUAY CUP",
    
    # USA
    "USA - MLS": "USA 1",
    "USA - USL CHAMPIONSHIP": "USA 2",
    "USA - USL SUPER LEAGUE WOMEN": "USA USL SUPER LEAGUE WOM",
    
    # VENEZUELA
    "VENEZUELA - PRIMERA DIVISION": "VENEZUELA 1",
    "VENEZUELA - LIGA FUTVE": "VENEZUELA 1",
    "VENEZUELA - SEGUNDA DIVISION": "VENEZUELA 2",
    "VENEZUELA - LIGA FUTVE 2": "VENEZUELA 2",
    
    # WALES
    "WALES - CYMRU PREMIER": "WALES 1",
    "WALES - CYMRU NORTH": "WALES 2",
    "WALES - CYMRU SOUTH": "WALES 3",
    "WALES - FA CUP": "WALES FA CUP",
    "WALES - LEAGUE CUP": "WALES LEAGUE CUP",
    "WALES - PREMIER WOMEN": "WALES 1 WOM",
    
    # OUTROS PAÍSES
    "NEW ZEALAND - NATIONAL LEAGUE": "NEW ZEALAND 1",
    "UNITED ARAB EMIRATES - UAE LEAGUE": "UAE 1",
    "UNITED ARAB EMIRATES - LEAGUE CUP": "UAE LEAGUE CUP",
    "UNITED ARAB EMIRATES - SUPER CUP": "UAE SUPER CUP",
    "ALBANIA - ABISSNET SUPERIORE": "ALBANIA 1",
    "ALBANIA - SUPER CUP": "ALBANIA SUPER CUP",
    "ALGERIA - LIGUE 1": "ALGERIA 1",
    "ALGERIA - ALGERIA CUP": "ALGERIA CUP",
    "ANDORRA - PRIMERA DIVISIÓ": "ANDORRA 1",
    "ARMENIA - PREMIER LEAGUE": "ARMENIA 1",
    "ARUBA - DIVISION DI HONOR": "ARUBA 1",
    "AZERBAIJAN - PREMIER LEAGUE": "AZERBAIJAN 1",
    "BAHRAIN - PREMIER LEAGUE": "BAHRAIN 1",
    "BAHRAIN - SUPER CUP": "BAHRAIN CUP",
    "BAHRAIN - KING'S CUP": "BAHRAIN KINGS CUP",
    "BANGLADESH - BFL": "BANGLADESH 1",
    "BANGLADESH - FEDERATION CUP": "BANGLADESH CUP",
    "BARBADOS - PREMIER LEAGUE": "BARBADOS 1",
    "BELARUS - BELARUSIAN CUP": "BELARUS CUP",
    "BENIN - LIGUE 1": "BENIN 1",
    "BURKINA FASO - PREMIER LEAGUE": "BURKINA FASO 1",
    "BURUNDI - PRIMUS LEAGUE": "BURUNDI 1",
    "CAMBODIA - CPL": "CAMBODIA 1",
    "COSTA RICA - PRIMERA DIVISION": "COSTA RICA 1",
    "Costa Rica - Primera Division": "COSTA RICA 1",
    "DOMINICAN REPUBLIC - LDF": "DOMINICAN REPUBLIC 1",
    "Dominican Republic - LDF": "DOMINICAN REPUBLIC 1",
    "DR CONGO - LIGUE 1": "DRC 1",
    "DR Congo - Ligue 1": "DRC 1",
    "EL SALVADOR - PRIMERA DIVISION": "EL SALVADOR 1",
    "El Salvador - Primera Division": "EL SALVADOR 1",
    "ETHIOPIA - PREMIER LEAGUE": "ETHIOPIA 1",
    "GAMBIA - GFA LEAGUE": "GAMBIA 1",
    "GEORGIA - CRYSTALBET EROVNULI LIGA": "GEORGIA 1",
    "GHANA - PREMIER LEAGUE": "GHANA 1",
    "GHANA - DIVISION ONE LEAGUE": "GHANA 2",
    "GIBRALTAR - NATIONAL LEAGUE": "GIBRALTAR 1",
    "GUATEMALA - LIGA NACIONAL": "GUATEMALA 1",
    "GUINEA - LIGUE 1": "GUINEA 1",
    "HONDURAS - LIGA NACIONAL": "HONDURAS 1",
    "HONG KONG - PREMIER LEAGUE": "HONG KONG 1",
    "HONG KONG - FA CUP": "HONG KONG CUP",
    "INDIA - SUPER CUP": "INDIA CUP",
    "INDIA - SANTOSH TROPHY": "INDIA SANTOSH TROPHY",
    "INDIA - IWL WOMEN": "INDIA IWL WOM",
    "INDONESIA - SUPER LEAGUE": "INDONESIA 1",
    "IRAN - PERSIAN GULF PRO LEAGUE": "IRAN 1",
    "IRAN - HAZFI CUP": "IRAN CUP",
    "IRAQ - STARS LEAGUE": "IRAQ 1",
    "IVORY COAST - LIGUE 1": "IVORY COAST 1",
    "JAMAICA - PREMIER LEAGUE": "JAMAICA 1",
    "JORDAN - JORDAN CUP": "JORDAN CUP",
    "JORDAN - SHIELD CUP": "JORDAN CUP",
    "KENYA - PREMIER LEAGUE": "KENYA 1",
    "KOSOVO - SUPERLIGA": "KOSOVO 1",
    "KUWAIT - PREMIER LEAGUE": "KUWAIT 1",
    "KUWAIT - DIVISION 1": "KUWAIT 2",
    "KUWAIT - EMIR CUP": "KUWAIT CUP",
    "KUWAIT - CROWN PRINCE CUP": "KUWAIT CROWN PRINCE CUP",
    "LEBANON - PREMIER LEAGUE": "LEBANON 1",
    "LIBERIA - LFA FIRST DIVISION": "LIBERIA 1",
    "LUXEMBOURG - BGL LIGUE": "LUXEMBOURG 1",
    "MALAWI - SUPER LEAGUE": "MALAWI 1",
    "MALAYSIA - SUPER LEAGUE": "MALAYSIA 1",
    "MALI - PREMIERE DIVISION": "MALI 1",
    "MALTA - PREMIER LEAGUE": "MALTA 1",
    "MALTA - FA TROPHY": "MALTA FA TROPHY",
    "MONTENEGRO - PRVA CRNOGORSKA LIGA": "MONTENEGRO 1",
    "MOZAMBIQUE - MOCAMBOLA": "MOZAMBIQUE 1",
    "MYANMAR - NATIONAL LEAGUE": "MYANMAR 1",
    "NICARAGUA - LIGA PRIMERA": "NICARAGUA 1",
    "NIGER - SUPER LIGUE": "NIGER 1",
    "NIGERIA - NPFL": "NIGERIA 1",
    "NORTH MACEDONIA - 1. MFL": "NORTH MACEDONIA 1",
    "OMAN - PROFESSIONAL LEAGUE": "OMAN 1",
    "OMAN - SULTAN CUP": "OMAN CUP",
    "QATAR - QSL": "QATAR 1",
    "QATAR - QSL CUP": "QATAR CUP",
    "QATAR - EMIR CUP": "QATAR EMIR CUP",
    "RUSSIA - PREMIER LEAGUE": "RUSSIA 1",
    "RUSSIA - FNL": "RUSSIA 2",
    "RWANDA - PREMIER LEAGUE": "RWANDA 1",
    "RWANDA - SUPER CUP": "RWANDA SUPER CUP",
    "SAN MARINO - CAMPIONATO SAMMARINESE": "SAN MARINO 1",
    "SAN MARINO - SUPER CUP": "SAN MARINO CUP",
    "SENEGAL - LIGUE 1": "SENEGAL 1",
    "SEYCHELLES - PREMIER LEAGUE": "SEYCHELLES 1",
    "SIERRA LEONE - PREMIER LEAGUE": "SIERRA LEONE 1",
    "SINGAPORE - PREMIER LEAGUE": "SINGAPORE 1",
    "SINGAPORE - SINGAPORE CUP": "SINGAPORE CUP",
    "SURINAME - SML": "SURINAME 1",
    "SYRIA - PREMIER LEAGUE": "SYRIA 1",
    "TAIWAN - PREMIER LEAGUE": "TAIWAN 1",
    "TAIWAN - MULAN FOOTBALL LEAGUE WOMEN": "TAIWAN MULAN FOOTBALL LEAGUE WOM",
    "TAJIKISTAN - VYSSHAYA LIGA": "TAJIKISTAN 1",
    "TANZANIA - LIGI KUU BARA": "TANZANIA 1",
    "THAILAND - THAI LEAGUE 1": "THAILAND 1",
    "THAILAND - THAI FA CUP": "THAILAND CUP",
    "THAILAND - LEAGUE CUP": "THAILAND LEAGUE CUP",
    "TOGO - CHAMPIONNAT NATIONAL": "TOGO 1",
    "TRINIDAD AND TOBAGO - TT PREMIER LEAGUE": "TRINIDAD AND TOBAGO 1",
    "UGANDA - PREMIER LEAGUE": "UGANDA 1",
    "UGANDA - BIG LEAGUE": "UGANDA 2",
    "UZBEKISTAN - SUPER LEAGUE": "UZBEKISTAN 1",
    "VIETNAM - V.LEAGUE 1": "VIETNAM 1",
    "ZAMBIA - SUPER LEAGUE": "ZAMBIA 1",
    "Zambia - Super League": "ZAMBIA 1",
}

# Mapeamento para combinar Country + League dos jogos passados
# Formato: (Country, League) -> Nome Padronizado
COUNTRY_LEAGUE_MAPPING = {
    # ARGENTINA
    ("ARGENTINA", "Torneo Betano"): "ARGENTINA 1",
    ("ARGENTINA", "Torneo Betano 2024"): "ARGENTINA 1",
    ("ARGENTINA", "Torneo Betano 2025"): "ARGENTINA 1",
    ("ARGENTINA", "Liga Profesional"): "ARGENTINA 1",
    ("ARGENTINA", "Liga Profesional 2024"): "ARGENTINA 1",
    ("ARGENTINA", "Liga Profesional 2025"): "ARGENTINA 1",
    ("ARGENTINA", "Superliga"): "ARGENTINA 1",
    ("ARGENTINA", "Superliga 2024"): "ARGENTINA 1",
    ("ARGENTINA", "Primera Nacional"): "ARGENTINA 2",
    ("ARGENTINA", "Primera Nacional 2024"): "ARGENTINA 2",
    ("ARGENTINA", "Torneo Federal"): "ARGENTINA 3",
    ("ARGENTINA", "Copa de la Liga Profesional"): "ARGENTINA COPA",
    ("ARGENTINA", "Copa Argentina"): "ARGENTINA COPA",
    ("ARGENTINA", "Trofeo de Campeones"): "ARGENTINA TROFEO DE CAMPEONES",
    
    # AUSTRALIA
    ("AUSTRALIA", "A-League"): "AUSTRALIA 1",
    ("AUSTRALIA", "A-League Women"): "AUSTRALIA 1 WOM",
    ("AUSTRALIA", "Australian Championship"): "AUSTRALIA U23",
    
    # AUSTRIA
    ("AUSTRIA", "Bundesliga"): "AUSTRIA 1",
    ("AUSTRIA", "2. Liga"): "AUSTRIA 2",
    
    # AZERBAIJAN
    ("AZERBAIJAN", "Premier League"): "AZERBAIJAN 1",
    
    # ALBANIA
    ("ALBANIA", "Abissnet Superiore"): "ALBANIA 1",
    ("ALBANIA", "Super Cup"): "ALBANIA SUPER CUP",
    
    # ALGERIA
    ("ALGERIA", "Ligue 1"): "ALGERIA 1",
    ("ALGERIA", "Algeria Cup"): "ALGERIA CUP",
    
    # ANDORRA
    ("ANDORRA", "Primera Divisió"): "ANDORRA 1",
    
    # ARMENIA
    ("ARMENIA", "Premier League"): "ARMENIA 1",
    
    # ARUBA
    ("ARUBA", "Division di Honor"): "ARUBA 1",
    
    # ASIA
    ("ASIA", "AFC Champions League"): "ASIA AFC CHAMPIONS LEAGUE",
    ("ASIA", "AFC Champions League 2"): "ASIA AFC CHAMPIONS LEAGUE 2",
    ("ASIA", "AFC Asian Cup U23"): "ASIA AFC ASIAN CUP U23",
    ("ASIA", "Arabian Gulf Cup U23"): "ASIA ARABIAN GULF CUP U23",
    ("ASIA", "ASEAN Club Championship"): "ASIA ASEAN CLUB CHAMPIONSHIP",
    ("ASIA", "Southeast Asian Games"): "ASIA SOUTHEAST ASIAN GAMES",
    ("ASIA", "Southeast Asian Games Women"): "ASIA SOUTHEAST ASIAN GAMES WOM",
    ("ASIA", "Gulf Club Champions League"): "ASIA GULF CLUB CHAMPIONS LEAGUE",
    ("ASIA", "Guangdong"): "ASIA GUANGDONG",
    
    # AFRICA
    ("AFRICA", "Africa Cup of Nations"): "AFRICA AFRICA CUP OF NATIONS",
    
    # BAHRAIN
    ("BAHRAIN", "Premier League"): "BAHRAIN 1",
    ("BAHRAIN", "Super Cup"): "BAHRAIN CUP",
    ("BAHRAIN", "King's Cup"): "BAHRAIN KINGS CUP",
    
    # BANGLADESH
    ("BANGLADESH", "BFL"): "BANGLADESH 1",
    ("BANGLADESH", "Federation Cup"): "BANGLADESH CUP",
    
    # BARBADOS
    ("BARBADOS", "Premier League"): "BARBADOS 1",
    
    # BELARUS
    ("BELARUS", "Belarusian Cup"): "BELARUS CUP",
    
    # BELGIUM
    ("BELGIUM", "Jupiler Pro League"): "BELGIUM 1",
    ("BELGIUM", "Challenger Pro League"): "BELGIUM 2",
    ("BELGIUM", "Belgian Cup"): "BELGIUM CUP",
    
    # BENIN
    ("BENIN", "Ligue 1"): "BENIN 1",
    
    # BOLIVIA
    ("BOLIVIA", "Division Profesional"): "BOLIVIA 1",
    ("BOLIVIA", "Copa Pacena"): "BOLIVIA CUP",
    
    # BOSNIA AND HERZEGOVINA
    ("BOSNIA AND HERZEGOVINA", "WWIN Liga BiH"): "BOSNIA 1",
    
    # BRAZIL
    ("BRAZIL", "Serie A Betano"): "BRAZIL 1",
    ("BRAZIL", "Serie B"): "BRAZIL 2",
    ("BRAZIL", "Copa Betano do Brasil"): "BRAZIL COPA",
    ("BRAZIL", "Copinha"): "BRAZIL COPINHA",
    ("BRAZIL", "Catarinense"): "BRAZIL CATARINENSE",
    ("BRAZIL", "Gaucho"): "BRAZIL GAUCHO",
    ("BRAZIL", "Mineiro"): "BRAZIL MINEIRO",
    ("BRAZIL", "Paulista"): "BRAZIL PAULISTA",
    ("BRAZIL", "Carioca"): "BRAZIL CARIOCA",
    
    # BULGARIA
    ("BULGARIA", "efbet League"): "BULGARIA 1",
    ("BULGARIA", "Bulgarian Cup"): "BULGARIA CUP",
    
    # BURKINA FASO
    ("BURKINA FASO", "Premier League"): "BURKINA FASO 1",
    
    # BURUNDI
    ("BURUNDI", "Primus League"): "BURUNDI 1",
    
    # CAMBODIA
    ("CAMBODIA", "CPL"): "CAMBODIA 1",
    
    # CHILE
    ("CHILE", "Liga de Primera"): "CHILE 1",
    
    # CHINA
    ("CHINA", "FA Cup"): "CHINA CUP",
    
    # COLOMBIA
    ("COLOMBIA", "Primera A"): "COLOMBIA 1",
    ("COLOMBIA", "Copa Colombia"): "COLOMBIA CUP",
    ("COLOMBIA", "Super Cup"): "COLOMBIA SUPER CUP",
    
    # COSTA RICA
    ("COSTA RICA", "Primera Division"): "COSTA RICA 1",
    
    # CROATIA
    ("CROATIA", "HNL"): "CROATIA 1",
    
    # CYPRUS
    ("CYPRUS", "Cyprus League"): "CYPRUS 1",
    ("CYPRUS", "Division 2"): "CYPRUS 2",
    ("CYPRUS", "Cyprus Cup"): "CYPRUS CUP",
    
    # CZECH REPUBLIC
    ("CZECH REPUBLIC", "Chance Liga"): "CZECH 2",
    ("CZECH REPUBLIC", "Tipsport liga"): "CZECH TIPSORT LIGA",
    
    # DENMARK
    ("DENMARK", "Superliga"): "DENMARK 1",
    ("DENMARK", "Landspokal Cup"): "DENMARK CUP",
    ("DENMARK", "Danish Cup Women"): "DENMARK CUP WOM",
    
    # DOMINICAN REPUBLIC
    ("DOMINICAN REPUBLIC", "LDF"): "DOMINICAN REPUBLIC 1",
    
    # DR CONGO
    ("DR CONGO", "Ligue 1"): "DRC 1",
    
    # ECUADOR
    ("ECUADOR", "Liga Pro"): "ECUADOR 1",
    ("ECUADOR", "Copa Ecuador"): "ECUADOR CUP",
    
    # EGYPT
    ("EGYPT", "Premier League"): "EGYPT 1",
    ("EGYPT", "Egypt Cup"): "EGYPT CUP",
    ("EGYPT", "League Cup"): "EGYPT LEAGUE CUP",
    
    # EL SALVADOR
    ("EL SALVADOR", "Primera Division"): "EL SALVADOR 1",
    
    # ENGLAND
    ("ENGLAND", "Premier League"): "ENGLAND 1",
    ("ENGLAND", "Championship"): "ENGLAND 2",
    ("ENGLAND", "League One"): "ENGLAND 3",
    ("ENGLAND", "League Two"): "ENGLAND 4",
    ("ENGLAND", "FA Cup"): "ENGLAND FA CUP",
    ("ENGLAND", "EFL Cup"): "ENGLAND EFL CUP",
    ("ENGLAND", "EFL Trophy"): "ENGLAND EFL TROPHY",
    ("ENGLAND", "FA Trophy"): "ENGLAND FA TROPHY",
    ("ENGLAND", "Premier League Cup"): "ENGLAND U21",
    ("ENGLAND", "WSL"): "ENGLAND 1 WOM",
    
    # ETHIOPIA
    ("ETHIOPIA", "Premier League"): "ETHIOPIA 1",
    
    # EUROPE
    ("EUROPE", "Champions League"): "EUROPA CHAMPIONS LEAGUE",
    ("EUROPE", "Champions League Women"): "EUROPA CHAMPIONS LEAGUE WOM",
    ("EUROPE", "Europa League"): "EUROPA LEAGUE",
    ("EUROPE", "Conference League"): "EUROPA CONFERENCE LEAGUE",
    ("EUROPE", "Premier League International Cup"): "EUROPA U21",
    ("EUROPE", "Euro U19 Women"): "EUROPA U19 WOM",
    ("EUROPE", "UEFA Nations League Women"): "EUROPA NATIONS LEAGUE WOM",
    
    # FINLAND
    ("FINLAND", "Liiga Cup"): "FINLAND LIIGA CUP",
    
    # FRANCE
    ("FRANCE", "Ligue 1"): "FRANCE 1",
    ("FRANCE", "Ligue 2"): "FRANCE 2",
    ("FRANCE", "National"): "FRANCE 3",
    ("FRANCE", "Coupe de France"): "FRANCE CUP",
    ("FRANCE", "Coupe de France Women"): "FRANCE CUP WOM",
    ("FRANCE", "Super Cup"): "FRANCE SUPER CUP",
    ("FRANCE", "Premiere Ligue Women"): "FRANCE 1 WOM",
    
    # GAMBIA
    ("GAMBIA", "GFA League"): "GAMBIA 1",
    
    # GEORGIA
    ("GEORGIA", "Crystalbet Erovnuli Liga"): "GEORGIA 1",
    
    # GERMANY
    ("GERMANY", "Bundesliga"): "GERMANY 1",
    ("GERMANY", "2. Bundesliga"): "GERMANY 2",
    ("GERMANY", "3. Liga"): "GERMANY 3",
    ("GERMANY", "DFB Pokal"): "GERMANY CUP",
    ("GERMANY", "Bundesliga Women"): "GERMANY 1 WOM",
    
    # GHANA
    ("GHANA", "Premier League"): "GHANA 1",
    ("GHANA", "Division One League"): "GHANA 2",
    
    # GIBRALTAR
    ("GIBRALTAR", "National League"): "GIBRALTAR 1",
    
    # GREECE
    ("GREECE", "Super League"): "GREECE 1",
    ("GREECE", "Super League 2"): "GREECE 2",
    ("GREECE", "Greek Cup"): "GREECE CUP",
    ("GREECE", "Super Cup"): "GREECE SUPER CUP",
    
    # GUATEMALA
    ("GUATEMALA", "Liga Nacional"): "GUATEMALA 1",
    
    # GUINEA
    ("GUINEA", "Ligue 1"): "GUINEA 1",
    
    # HONDURAS
    ("HONDURAS", "Liga Nacional"): "HONDURAS 1",
    
    # HONG KONG
    ("HONG KONG", "Premier League"): "HONG KONG 1",
    ("HONG KONG", "FA Cup"): "HONG KONG CUP",
    
    # HUNGARY
    ("HUNGARY", "NB I."): "HUNGARY 1",
    
    # ICELAND
    "Iceland - Reykjavik Cup": "ICELAND REYKJAVIK CUP",
    ("ICELAND", "Reykjavik Cup"): "ICELAND REYKJAVIK CUP",
    
    # INDIA
    "India - Super Cup": "INDIA CUP",
    "India - Santosh Trophy": "INDIA SANTOSH TROPHY",
    "India - IWL Women": "INDIA IWL WOM",
    ("INDIA", "Super Cup"): "INDIA CUP",
    ("INDIA", "Santosh Trophy"): "INDIA SANTOSH TROPHY",
    ("INDIA", "IWL Women"): "INDIA IWL WOM",
    
    # INDONESIA
    "Indonesia - Super League": "INDONESIA 1",
    ("INDONESIA", "Super League"): "INDONESIA 1",
    
    # IRAN
    "Iran - Persian Gulf Pro League": "IRAN 1",
    "Iran - Hazfi Cup": "IRAN CUP",
    ("IRAN", "Persian Gulf Pro League"): "IRAN 1",
    ("IRAN", "Hazfi Cup"): "IRAN CUP",
    
    # IRAQ
    "Iraq - Stars League": "IRAQ 1",
    ("IRAQ", "Stars League"): "IRAQ 1",
    
    # ISRAEL
    "Israel - State Cup": "ISRAEL CUP",
    ("ISRAEL", "Ligat ha'Al"): "ISRAEL 1",
    ("ISRAEL", "Leumit League"): "ISRAEL 2",
    ("ISRAEL", "State Cup"): "ISRAEL CUP",
    
    # ITALY
    "Italy - Serie A Women": "ITALY 1 WOM",
    "Italy - Coppa Italia Women": "ITALY CUP WOM",
    "Italy - Coppa Italia Serie C": "ITALY CUP SERIE C",
    "Italy - Super Cup Women": "ITALY SUPER CUP WOMS",
    "Italy - Primavera 1": "ITALY U19",
    ("ITALY", "Serie A"): "ITALY 1",
    ("ITALY", "Serie B"): "ITALY 2",
    ("ITALY", "Serie C"): "ITALY 3",
    ("ITALY", "Coppa Italia"): "ITALY CUP",
    ("ITALY", "Coppa Italia Women"): "ITALY CUP WOM",
    ("ITALY", "Coppa Italia Serie C"): "ITALY CUP SERIE C",
    ("ITALY", "Super Cup"): "ITALY SUPER CUP",
    ("ITALY", "Super Cup Women"): "ITALY SUPER CUP WOMS",
    ("ITALY", "Serie A Women"): "ITALY 1 WOM",
    ("ITALY", "Primavera 1"): "ITALY U19",
    
    # IVORY COAST
    ("IVORY COAST", "Ligue 1"): "IVORY COAST 1",
    
    # JAMAICA
    ("JAMAICA", "Premier League"): "JAMAICA 1",
    
    # JAPAN
    ("JAPAN", "J1 League"): "JAPAN 1",
    ("JAPAN", "J2 League"): "JAPAN 2",
    ("JAPAN", "WE League Women"): "JAPAN WE LEAGUE WOM",
    
    # JORDAN
    ("JORDAN", "Jordan Cup"): "JORDAN CUP",
    ("JORDAN", "Shield Cup"): "JORDAN CUP",
    
    # KENYA
    ("KENYA", "Premier League"): "KENYA 1",
    
    # KOSOVO
    ("KOSOVO", "Superliga"): "KOSOVO 1",
    
    # KUWAIT
    ("KUWAIT", "Premier League"): "KUWAIT 1",
    ("KUWAIT", "Division 1"): "KUWAIT 2",
    ("KUWAIT", "Emir Cup"): "KUWAIT CUP",
    ("KUWAIT", "Crown Prince Cup"): "KUWAIT CROWN PRINCE CUP",
    
    # LEBANON
    ("LEBANON", "Premier League"): "LEBANON 1",
    
    # LIBERIA
    ("LIBERIA", "LFA First Division"): "LIBERIA 1",
    
    # LUXEMBOURG
    ("LUXEMBOURG", "BGL Ligue"): "LUXEMBOURG 1",
    
    # MALAWI
    ("MALAWI", "Super League"): "MALAWI 1",
    
    # MALAYSIA
    ("MALAYSIA", "Super League"): "MALAYSIA 1",
    
    # MALI
    ("MALI", "Premiere Division"): "MALI 1",
    
    # MALTA
    ("MALTA", "Premier League"): "MALTA 1",
    ("MALTA", "FA Trophy"): "MALTA FA TROPHY",
    
    # MEXICO
    ("MEXICO", "Liga MX"): "MEXICO 1",
    ("MEXICO", "Liga de Expansion MX"): "MEXICO 2",
    ("MEXICO", "Liga MX Women"): "MEXICO 1 WOM",
    
    # MONTENEGRO
    ("MONTENEGRO", "Prva Crnogorska Liga"): "MONTENEGRO 1",
    
    # MOZAMBIQUE
    ("MOZAMBIQUE", "Mocambola"): "MOZAMBIQUE 1",
    
    # MYANMAR
    ("MYANMAR", "National League"): "MYANMAR 1",
    
    # NETHERLANDS
    ("NETHERLANDS", "Eredivisie"): "NETHERLANDS 1",
    ("NETHERLANDS", "Eerste Divisie"): "NETHERLANDS 2",
    ("NETHERLANDS", "Tweede Divisie"): "NETHERLANDS 3",
    ("NETHERLANDS", "KNVB Beker"): "NETHERLANDS CUP",
    ("NETHERLANDS", "KNVB Beker Women"): "NETHERLANDS CUP WOM",
    ("NETHERLANDS", "Eredivisie Women"): "NETHERLANDS 1 WOM",
    
    # NEW ZEALAND
    ("NEW ZEALAND", "National League"): "NEW ZEALAND 1",
    
    # NICARAGUA
    ("NICARAGUA", "Liga Primera"): "NICARAGUA 1",
    
    # NIGER
    ("NIGER", "Super Ligue"): "NIGER 1",
    
    # NIGERIA
    ("NIGERIA", "NPFL"): "NIGERIA 1",
    
    # NORTH & CENTRAL AMERICA
    ("NORTH & CENTRAL AMERICA", "CONCACAF Championship Women"): "NORTH_CENTRAL AMERICA CONCACAF WOM",
    
    # NORTH MACEDONIA
    ("NORTH MACEDONIA", "1. MFL"): "NORTH MACEDONIA 1",
    
    # NORTHERN IRELAND
    ("NORTHERN IRELAND", "NIFL Championship"): "NORTHERN IRELAND 1",
    ("NORTHERN IRELAND", "NIFL Premiership"): "NORTHERN IRELAND 2",
    ("NORTHERN IRELAND", "Irish Cup"): "NORTHERN IRELAND CUP",
    
    # NORWAY
    ("NORWAY", "Eliteserien"): "NORWAY 1",
    ("NORWAY", "NM Cup"): "NORWAY CUP",
    
    # OMAN
    ("OMAN", "Professional League"): "OMAN 1",
    ("OMAN", "Sultan Cup"): "OMAN CUP",
    
    # PARAGUAY
    ("PARAGUAY", "Super Cup"): "PARAGUAY SUPER CUP",
    
    # PERU
    ("PERU", "Liga 1"): "PERU 1",
    
    # POLAND
    ("POLAND", "Ekstraklasa"): "POLAND 1",
    ("POLAND", "Division 1"): "POLAND 2",
    ("POLAND", "Polish Cup"): "POLAND CUP",
    
    # PORTUGAL
    ("PORTUGAL", "Liga Portugal"): "PORTUGAL 1",
    ("PORTUGAL", "Liga Portugal 2"): "PORTUGAL 2",
    ("PORTUGAL", "Liga 3"): "PORTUGAL 3",
    ("PORTUGAL", "Taça de Portugal"): "PORTUGAL CUP",
    ("PORTUGAL", "League Cup"): "PORTUGAL LEAGUE CUP",
    
    # QATAR
    ("QATAR", "QSL"): "QATAR 1",
    ("QATAR", "QSL Cup"): "QATAR CUP",
    ("QATAR", "Emir Cup"): "QATAR EMIR CUP",
    
    # ROMANIA
    ("ROMANIA", "Superliga"): "ROMANIA 1",
    ("ROMANIA", "Liga 2"): "ROMANIA 2",
    ("ROMANIA", "Romanian Cup"): "ROMANIA CUP",
    ("ROMANIA", "Superliga Women"): "ROMANIA 1 WOM",
    
    # RUSSIA
    ("RUSSIA", "Premier League"): "RUSSIA 1",
    ("RUSSIA", "FNL"): "RUSSIA 2",
    
    # RWANDA
    ("RWANDA", "Premier League"): "RWANDA 1",
    ("RWANDA", "Super Cup"): "RWANDA SUPER CUP",
    
    # SAN MARINO
    ("SAN MARINO", "Campionato Sammarinese"): "SAN MARINO 1",
    ("SAN MARINO", "Super Cup"): "SAN MARINO CUP",
    
    # SAUDI ARABIA
    ("SAUDI ARABIA", "Saudi Professional League"): "SAUDI ARABIA 1",
    ("SAUDI ARABIA", "Division 1"): "SAUDI ARABIA 2",
    ("SAUDI ARABIA", "Premier League Women"): "SAUDI ARABIA 1 WOM",
    
    # SCOTLAND
    ("SCOTLAND", "Premiership"): "SCOTLAND 1",
    ("SCOTLAND", "Championship"): "SCOTLAND 2",
    ("SCOTLAND", "League One"): "SCOTLAND 3",
    ("SCOTLAND", "League Two"): "SCOTLAND 4",
    ("SCOTLAND", "Scottish Cup"): "SCOTLAND CUP",
    ("SCOTLAND", "Scottish Cup Women"): "SCOTLAND CUP WOM",
    ("SCOTLAND", "League Cup"): "SCOTLAND LEAGUE CUP",
    ("SCOTLAND", "Challenge Cup"): "SCOTLAND CHALLENGE CUP",
    ("SCOTLAND", "SWPL 1 Women"): "SCOTLAND 1 WOM",
    
    # SENEGAL
    ("SENEGAL", "Ligue 1"): "SENEGAL 1",
    
    # SERBIA
    ("SERBIA", "Mozzart Bet Super Liga"): "SERBIA 1",
    ("SERBIA", "Mozzart Bet Prva Liga"): "SERBIA 2",
    
    # SEYCHELLES
    ("SEYCHELLES", "Premier League"): "SEYCHELLES 1",
    
    # SIERRA LEONE
    ("SIERRA LEONE", "Premier League"): "SIERRA LEONE 1",
    
    # SINGAPORE
    ("SINGAPORE", "Premier League"): "SINGAPORE 1",
    ("SINGAPORE", "Singapore Cup"): "SINGAPORE CUP",
    
    # SLOVAKIA
    ("SLOVAKIA", "Nike liga"): "SLOVAKIA 1",
    
    # SLOVENIA
    ("SLOVENIA", "Prva liga"): "SLOVENIA 1",
    ("SLOVENIA", "Slovenian Cup"): "SLOVENIA CUP",
    
    # SOUTH AFRICA
    ("SOUTH AFRICA", "Betway Premiership"): "SOUTH AFRICA 1",
    ("SOUTH AFRICA", "Motsepe Foundation Championship"): "SOUTH AFRICA 2",
    ("SOUTH AFRICA", "Carling Knockout"): "SOUTH AFRICA CUP",
    
    # SOUTH AMERICA
    ("SOUTH AMERICA", "CONMEBOL Nations League Women"): "SOUTH AMERICA CONMEBOL NATIONS LEAGUE WOM",
    ("SOUTH AMERICA", "Serie Rio de la Plata"): "SOUTH AMERICA SERIE RIO DE LA PLATA",
    
    # SOUTH KOREA
    ("SOUTH KOREA", "K League 1"): "SOUTH KOREA 1",
    ("SOUTH KOREA", "Korean Cup"): "SOUTH KOREA CUP",
    
    # SPAIN
    ("SPAIN", "LaLiga"): "SPAIN 1",
    ("SPAIN", "LaLiga2"): "SPAIN 2",
    ("SPAIN", "Primera RFEF"): "SPAIN 3",
    ("SPAIN", "Copa del Rey"): "SPAIN CUP",
    ("SPAIN", "Copa de la Reina Women"): "SPAIN CUP WOM",
    ("SPAIN", "Super Cup"): "SPAIN SUPER CUP",
    ("SPAIN", "Liga F Women"): "SPAIN 1 WOM",
    
    # SURINAME
    ("SURINAME", "SML"): "SURINAME 1",
    
    # SWITZERLAND
    ("SWITZERLAND", "Super League"): "SWITZERLAND 1",
    ("SWITZERLAND", "Challenge League"): "SWITZERLAND 2",
    ("SWITZERLAND", "Swiss Cup"): "SWITZERLAND CUP",
    ("SWITZERLAND", "Swiss Cup Women"): "SWITZERLAND CUP WOM",
    ("SWITZERLAND", "Super League Women"): "SWITZERLAND 1 WOM",
    
    # SYRIA
    ("SYRIA", "Premier League"): "SYRIA 1",
    
    # TAIWAN
    ("TAIWAN", "Premier League"): "TAIWAN 1",
    ("TAIWAN", "Mulan Football League Women"): "TAIWAN MULAN FOOTBALL LEAGUE WOM",
    
    # TAJIKISTAN
    ("TAJIKISTAN", "Vysshaya Liga"): "TAJIKISTAN 1",
    
    # TANZANIA
    ("TANZANIA", "Ligi Kuu Bara"): "TANZANIA 1",
    
    # THAILAND
    ("THAILAND", "Thai League 1"): "THAILAND 1",
    ("THAILAND", "Thai FA Cup"): "THAILAND CUP",
    ("THAILAND", "League Cup"): "THAILAND LEAGUE CUP",
    
    # TOGO
    ("TOGO", "Championnat National"): "TOGO 1",
    
    # TRINIDAD AND TOBAGO
    ("TRINIDAD AND TOBAGO", "TT Premier League"): "TRINIDAD AND TOBAGO 1",
    
    # TUNISIA
    ("TUNISIA", "Ligue Professionnelle 1"): "TUNISIA 1",
    ("TUNISIA", "Ligue 2"): "TUNISIA 2",
    ("TUNISIA", "Tunisia Cup"): "TUNISIA CUP",
    
    # TURKEY
    ("TURKEY", "Super Lig"): "TURKEY 1",
    ("TURKEY", "1. Lig"): "TURKEY 2",
    ("TURKEY", "Turkish Cup"): "TURKEY CUP",
    ("TURKEY", "Super Cup"): "TURKEY SUPER CUP",
    ("TURKEY", "Super Lig Women"): "TURKEY 1 WOM",
    
    # UGANDA
    ("UGANDA", "Premier League"): "UGANDA 1",
    ("UGANDA", "Big League"): "UGANDA 2",
    
    # UKRAINE
    ("UKRAINE", "Premier League"): "UKRAINE 1",
    ("UKRAINE", "Persha Liga"): "UKRAINE 2",
    
    # UNITED ARAB EMIRATES
    ("UNITED ARAB EMIRATES", "UAE League"): "UAE 1",
    ("UNITED ARAB EMIRATES", "League Cup"): "UAE LEAGUE CUP",
    ("UNITED ARAB EMIRATES", "Super Cup"): "UAE SUPER CUP",
    
    # URUGUAY
    ("URUGUAY", "Copa de la Liga AUF"): "URUGUAY CUP",
    
    # USA
    ("USA", "USL Super League Women"): "USA USL SUPER LEAGUE WOM",
    
    # UZBEKISTAN
    ("UZBEKISTAN", "Super League"): "UZBEKISTAN 1",
    
    # VENEZUELA
    ("VENEZUELA", "Liga FUTVE"): "VENEZUELA 1",
    
    # VIETNAM
    ("VIETNAM", "V.League 1"): "VIETNAM 1",
    
    # WALES
    ("WALES", "Cymru Premier"): "WALES 1",
    ("WALES", "Cymru North"): "WALES 2",
    ("WALES", "Cymru South"): "WALES 3",
    ("WALES", "FA Cup"): "WALES FA CUP",
    ("WALES", "League Cup"): "WALES LEAGUE CUP",
    ("WALES", "Premier Women"): "WALES 1 WOM",
    
    # WORLD
    ("WORLD", "FIFA Arab Cup"): "WORLD FIFA ARAB CUP",
    ("WORLD", "FIFA Intercontinental Cup"): "WORLD FIFA INTERCONTINENTAL CUP",
    ("WORLD", "Friendly International"): "WORLD FRIENDLY",
    ("WORLD", "Friendly International Women"): "WORLD FRIENDLY WOM",
    ("WORLD", "Club Friendly"): "WORLD CLUB FRIENDLY",
    ("WORLD", "Club Friendly Women"): "WORLD CLUB FRIENDLY WOM",
    ("WORLD", "Kings World Cup Nations"): "WORLD KINGS WORLD CUP NATIONS",
    
    # ZAMBIA
    ("ZAMBIA", "Super League"): "ZAMBIA 1",
}


def standardize_league_name(league_name=None, country=None, league=None):
    """
    Padroniza nome de liga de futebol
    
    Args:
        league_name: Nome da liga no formato "Country - League" (para jogos futuros)
        country: Nome do país (para jogos passados)
        league: Nome da liga (para jogos passados)
    
    Returns:
        Nome padronizado da liga
    """
    # Caso 1: Formato "Country - League" (jogos futuros)
    if league_name:
        league_upper = league_name.strip().upper()
        
        # Tenta mapeamento direto
        if league_name in LEAGUE_MAPPING:
            return LEAGUE_MAPPING[league_name]
        
        # Tenta mapeamento case-insensitive
        for key, value in LEAGUE_MAPPING.items():
            if key.upper() == league_upper:
                return value
    
    # Caso 2: Formato Country + League separados (jogos passados)
    if country and league:
        # Tenta mapeamento direto
        key = (country.strip().upper(), league.strip())
        if key in COUNTRY_LEAGUE_MAPPING:
            return COUNTRY_LEAGUE_MAPPING[key]
        
        # Tenta construir o formato "COUNTRY - LEAGUE" e buscar no mapeamento principal
        constructed = f"{country.upper()} - {league.upper()}"
        if constructed in LEAGUE_MAPPING:
            return LEAGUE_MAPPING[constructed]
        
        # Remove sufixos de ano (2024, 2025, etc) e tenta novamente
        import re
        league_no_year = re.sub(r'\s+\d{4}(-\d{4})?$', '', league.strip())
        
        # Tenta com liga sem ano
        key_no_year = (country.strip().upper(), league_no_year)
        if key_no_year in COUNTRY_LEAGUE_MAPPING:
            return COUNTRY_LEAGUE_MAPPING[key_no_year]
        
        constructed_no_year = f"{country.upper()} - {league_no_year.upper()}"
        if constructed_no_year in LEAGUE_MAPPING:
            return LEAGUE_MAPPING[constructed_no_year]
        
        # Retorna formato padrão: "COUNTRY" + número (se houver no nome da liga)
        # Ex: "ARGENTINA" + "Torneo Betano" -> verifica se é primeira divisão
        if any(keyword in league.upper() for keyword in ['PRIMERA', 'PREMIER', 'SUPER', 'LIGA PROFESIONAL', 'TORNEO', 'CHAMPIONSHIP']):
            return f"{country.upper()} 1"
    
    # Se não encontrou mapeamento, retorna o valor original
    return league_name if league_name else f"{country} {league}"


def get_all_standard_leagues():
    """Retorna lista de todas as ligas padronizadas únicas"""
    standard_leagues = set(LEAGUE_MAPPING.values())
    standard_leagues.update(COUNTRY_LEAGUE_MAPPING.values())
    return sorted(list(standard_leagues))
