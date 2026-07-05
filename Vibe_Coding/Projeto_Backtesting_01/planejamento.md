# Planejamento - BacktestBet

## 1. Visao Geral

- **Descricao:** Sistema de Backtesting de Futebol para Betfair. O usuario seleciona estrategias de apostas (Back Home, Back Draw, Back Away), define faixas de odds (minima/maxima), e o sistema calcula retrospectivamente P&L, Win Rate, ROI e Drawdown sobre uma base historica de jogos consumida da API FutPythonTrader. A base e armazenada localmente para evitar requisicoes repetidas a API externa.

- **Publico-alvo:** Traders esportivos da Betfair (Brasil).

- **Tipo de SaaS:** A (SEM pagamento) — ferramenta interna/pessoal, sem integracao de pagamento.

- **Mercado alvo:** Brasil.

## 2. Stack Tecnica

| Camada | Tecnologia | Versao |
|---|---|---|
| Backend | Django | 5.x |
| Linguagem | Python | 3.12+ |
| Banco (dev) | SQLite | nativo |
| Banco (prod TODO) | PostgreSQL (VPS remota) | 16+ |
| ORM | Django ORM | nativo |
| Auth | django-allauth | latest |
| Frontend | HTMX + Tailwind CDN + Alpine.js + Chart.js | latest |
| API (consumo externo) | requests + pandas | latest |
| Tasks | Celery + Redis (opcional, para importacao async) | latest |
| Deploy | Docker + EasyPanel | latest |

### Observacoes tecnicas

- **Banco de dados:** SQLite para desenvolvimento local. No `settings.py`, usar `DATABASE_URL` via `dj-database-url` com fallback para SQLite. TODO claro no codigo e no `.env.example` para migrar para PostgreSQL remoto quando a VPS estiver disponivel.
- **Chart.js:** CDN para graficos de P&L acumulado e Drawdown no dashboard.
- **API FutPythonTrader:** Ja existe o arquivo `api_futpythontrader_betfair.py` na raiz do projeto como referencia. O token (`7256fbc57d1ee9df52ab707e1f8f0c02932161d4`) e as URLs base estao definidos la.
- **Importacao da base:** Feita sob demanda via endpoint `/api/importar-base/` que baixa o CSV da API FutPythonTrader e popula o modelo `Match`. A importacao pode ser sincrona (MVP) ou assincrona via Celery (futuro).

## 3. Modelo de Dados (diagrama textual)

### User (accounts, criado pelo auth-system-django)
- UUID id (PK)
- email (unique, not null)
- full_name (string)
- is_active (bool, default=True)
- is_staff (bool, default=False)
- is_superuser (bool, default=False)
- date_joined (datetime)
- last_login (datetime)

### Match (backtest) — Jogo importado da API FutPythonTrader
- **id** (BigAutoField, PK)
- **date** (DateField, db_index=True) — data do jogo
- **time** (TimeField, blank=True, null=True) — horario do jogo
- **home** (CharField, max_length=200) — time mandante
- **away** (CharField, max_length=200) — time visitante
- **ft_goals_h** (SmallIntegerField, null=True, blank=True) — gols mandante
- **ft_goals_a** (SmallIntegerField, null=True, blank=True) — gols visitante
- **ft_result** (CharField, max_length=10, blank=True, null=True) — resultado final (H/D/A)
- **ht_goals_h** (SmallIntegerField, null=True, blank=True) — gols 1o tempo mandante
- **ht_goals_a** (SmallIntegerField, null=True, blank=True) — gols 1o tempo visitante
- **ht_result** (CharField, max_length=10, blank=True, null=True) — resultado 1o tempo
- **odd_home** (DecimalField, max_digits=8, decimal_places=2, null=True, blank=True) — odd Back Home
- **odd_draw** (DecimalField, max_digits=8, decimal_places=2, null=True, blank=True) — odd Back Draw
- **odd_away** (DecimalField, max_digits=8, decimal_places=2, null=True, blank=True) — odd Back Away
- **league** (CharField, max_length=200, blank=True, null=True) — nome da liga/campeonato
- **country** (CharField, max_length=100, blank=True, null=True) — pais da liga
- **season** (CharField, max_length=20, blank=True, null=True) — temporada
- **raw_data** (JSONField, blank=True, null=True) — dados brutos completos da API para consultas futuras
- **importado_em** (DateTimeField, auto_now_add=True) — timestamp de importacao

    **Meta:**
    - ordering: ['-date', '-time']
    - indexes: date, home, away, league
    - constraints: unique_together(date, home, away) — evita duplicatas

### Strategy (backtest) — Estrategia salva pelo usuario
- **id** (BigAutoField, PK)
- **user** (FK → User, on_delete=CASCADE, related_name='strategies')
- **nome** (CharField, max_length=100) — nome da estrategia
- **tipo_back** (CharField, max_length=4, choices=[('HOME', 'Back Home'), ('DRAW', 'Back Draw'), ('AWAY', 'Back Away')])
- **odd_min** (DecimalField, max_digits=6, decimal_places=2) — odd minima para filtrar
- **odd_max** (DecimalField, max_digits=6, decimal_places=2) — odd maxima para filtrar
- **criada_em** (DateTimeField, auto_now_add=True)
- **atualizada_em** (DateTimeField, auto_now=True)

    **Meta:**
    - ordering: ['-criada_em']
    - unique_together: user, nome

### BacktestResult (backtest) — Resultado de uma execucao de backtest (opcional, pode ser calculado on-the-fly)
- **id** (BigAutoField, PK)
- **user** (FK → User, on_delete=CASCADE)
- **strategy** (FK → Strategy, on_delete=SET_NULL, null=True)
- **total_jogos** (IntegerField)
- **verdes** (IntegerField)
- **vermelhas** (IntegerField)
- **profit_total** (DecimalField, max_digits=10, decimal_places=2)
- **win_rate** (DecimalField, max_digits=6, decimal_places=2) — percentual
- **roi** (DecimalField, max_digits=8, decimal_places=2) — percentual
- **max_drawdown** (DecimalField, max_digits=10, decimal_places=2)
- **odd_min_usada** (DecimalField, max_digits=6, decimal_places=2)
- **odd_max_usada** (DecimalField, max_digits=6, decimal_places=2)
- **tipo_back_usado** (CharField, max_length=4)
- **criado_em** (DateTimeField, auto_now_add=True)

    **Meta:**
    - ordering: ['-criado_em']

## 4. Estrutura de Apps

```
apps/
  accounts/     (auth, perfil - auth-system-django)
  core/         (BaseModel, mixins, helpers)
  backtest/     (app principal: models Match, Strategy, BacktestResult; views; services; templates)
```

### Responsabilidades de cada app:

- **accounts:** Signup com verificacao de email, login, logout, reset de senha, perfil do usuario. Criado pelo agente `auth-system-django` usando django-allauth.
- **core:** `BaseModel` com UUID id, `created_at`, `updated_at`. Mixins como `LoginRequiredMixin`, `OwnerRequiredMixin`. Helpers gerais.
- **backtest:** Todos os models de negocio (`Match`, `Strategy`, `BacktestResult`), services de calculo (`backtest_service.py`), service de importacao (`import_service.py`), views com HTMX, templates com Tailwind + Alpine.js + Chart.js.

## 5. URLs Principais

| URL | Metodo | Descricao | Protecao |
|---|---|---|---|
| `/` | GET | Landing page com explicacao do sistema | Publica |
| `/signup/` | GET/POST | Cadastro com verificacao de email | Publica |
| `/login/` | GET/POST | Login (email + senha) | Publica |
| `/logout/` | POST | Logout | Login required |
| `/password-reset/` | GET/POST | Esqueci minha senha + reset por email | Publica |
| `/dashboard/` | GET | Painel principal de backtesting | Login required |
| `/dashboard/backtest/` | POST | Executa o backtest via HTMX | Login required |
| `/dashboard/backtest/resultados/<id>/` | GET | Exibe resultado detalhado de um backtest | Login required (owner) |
| `/dashboard/estrategias/` | GET | Lista estrategias do usuario | Login required |
| `/dashboard/estrategias/nova/` | GET/POST | Criar nova estrategia (modal HTMX) | Login required |
| `/dashboard/estrategias/<id>/editar/` | GET/POST | Editar estrategia (modal HTMX) | Login required (owner) |
| `/dashboard/estrategias/<id>/excluir/` | DELETE | Excluir estrategia | Login required (owner) |
| `/api/importar-base/` | POST | Importa/atualiza a base historica via API externa | Login required |
| `/api/importar-base/status/` | GET | Status da importacao (progresso) | Login required |
| `/painel-admin/` | GET | Django Admin com URL customizada | Staff only |
| `/healthz/` | GET | Healthcheck para monitoramento | Publica |

## 6. Features Obrigatorias (checklist)

- [ ] Cadastro com verificacao de email (django-allauth)
- [ ] Login + logout
- [ ] Esqueci minha senha + reset por email
- [ ] Perfil do usuario editavel
- [ ] Dashboard apos login com KPIs (total jogos, win rate, ROI, P&L, drawdown)
- [ ] Execucao de backtest com filtros de estrategia e odds
- [ ] Tabela com ultimos 10 jogos filtrados (HTMX partial)
- [ ] Grafico de P&L acumulado (Chart.js)
- [ ] Grafico de Drawdown (Chart.js)
- [ ] CRUD completo de Estrategias (HTMX modals)
- [ ] Importacao da base historica via API FutPythonTrader
- [ ] Dedeplicacao de jogos na importacao (unique_together date+home+away)
- [ ] Admin Django customizado com URL nao-obvia (`/painel-admin/`)
- [ ] SMTP Gmail configurado (placeholder ate usuario fornecer credenciais)
- [ ] Healthcheck `/healthz/`
- [ ] Dockerfile + docker-compose.yml
- [ ] DEPLOY.md com instrucoes EasyPanel

## 7. Modelo de Pagamento

**Tipo A — SEM pagamento.** Nao ha integracao com Mercado Pago, webhooks ou modelos de cobranca. Todas as funcionalidades sao gratuitas e acessiveis a qualquer usuario logado.

## 8. Logica de Backtesting (detalhamento tecnico)

### Algoritmo de calculo

```
Para cada jogo na base filtrada (Match):
  1. Selecionar a odd conforme tipo_back:
     - HOME  -> odd_home
     - DRAW  -> odd_draw
     - AWAY  -> odd_away

  2. Verificar se odd esta no intervalo [odd_min, odd_max]
     Se nao estiver, pular o jogo

  3. Determinar resultado:
     - HOME: Green se ft_result == 'H'
     - DRAW: Green se ft_result == 'D'
     - AWAY: Green se ft_result == 'A'

  4. Calcular profit do jogo:
     - Green: profit = odd - 1
     - Red:   profit = -1

  5. Acumular no P&L running total
```

### Metricas calculadas

| Metrica | Formula |
|---|---|
| **Profit Total** | Soma de todos os profits individuais |
| **Total de Jogos** | Count de jogos filtrados |
| **Win Rate (%)** | (Verdes / Total) * 100 |
| **ROI (%)** | (Profit Total / Total de Jogos) * 100 |
| **Drawdown Maximo** | Maior queda do P&L acumulado a partir de um pico anterior |

### Drawdown (algoritmo)

```
peak = 0
max_drawdown = 0
running_pl = 0

Para cada jogo em ordem cronologica:
  running_pl += profit
  peak = max(peak, running_pl)
  drawdown = peak - running_pl
  max_drawdown = max(max_drawdown, drawdown)
```

### Filtros aplicaveis (alem da estrategia)
- **Periodo:** data inicial e data final (opcional)
- **Liga:** filtrar por `league` (opcional)
- **Pais:** filtrar por `country` (opcional)

## 9. Servico de Importacao da API FutPythonTrader

### Fluxo

```
1. Usuario clica em "Importar Base" no dashboard
2. Backend faz GET em https://api.futpythontrader.com/api/dados/betfair/download/
   com header Authorization: Token 7256fbc57d1ee9df52ab707e1f8f0c02932161d4
3. Response e um CSV binario
4. pandas.read_csv() para parse
5. Para cada linha, criar ou atualizar Match (usando get_or_create com unique date+home+away)
6. Armazenar raw_data como JSON para consultas futuras
7. Retornar contagem: { "importados": N, "atualizados": M, "erros": E }
```

### Tratamento de erros
- Timeout na API externa (30s)
- CSV mal formatado
- Token invalido/expirado (401)
- Linhas com dados ausentes (pular e logar)

### Performance
- MVP: processamento sincrono (bloqueia enquanto importa)
- Futuro: migrar para Celery task assincrona com progresso via WebSocket ou polling

## 10. Variaveis de Ambiente (.env.example)

```
# Django
SECRET_KEY=                   # gerado automaticamente por generate_env.py
DEBUG=True                    # True em dev, False em prod
ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de Dados
# TODO: Migrar para PostgreSQL remoto quando a VPS estiver disponivel
# POSTGRES_HOST=
# POSTGRES_PORT=5432
# POSTGRES_DB=
# POSTGRES_USER=
# POSTGRES_PASSWORD=
DATABASE_URL=sqlite:///db.sqlite3

# Email (SMTP Gmail)
# TODO: Configurar quando tiver credenciais Gmail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# API FutPythonTrader
FUTPYTHONTRADER_TOKEN=7256fbc57d1ee9df52ab707e1f8f0c02932161d4
FUTPYTHONTRADER_BASE_URL=https://api.futpythontrader.com/api/dados
```

## 11. Plano de Execucao por Subagentes (Ordem)

### Fase 0 — Sequencial (setup inicial):
1. **database-django** → Models completos (Match, Strategy, BacktestResult + User custom), migrations, admin registrado
2. **auth-system-django** → Signup, login, logout, reset de senha, verificacao de email, perfil, admin override com URL `/painel-admin/`

### Fase 1 — Paralelo (features de negocio):
3. **django-expert** → Views, templates HTMX com Tailwind + Alpine.js, Chart.js CDN, URLs, forms, services de backtesting e importacao

### Fase 2 — Sequencial (deploy):
4. **docker-deploy-python** → Dockerfile multi-stage, docker-compose.yml, `generate_env.py`, DEPLOY.md com instrucoes EasyPanel
5. **security-audit-python** → Auditoria OWASP, hardening pre-deploy, validacao de settings, secrets, headers, CSRF, rate limiting

> **Nota:** Nao ha fase de pagamento pois o SaaS e Tipo A (sem cobranca). O agente `payment-integration-python` nao sera acionado.

## 12. Definition of Done (MVP)

- [ ] Usuario cria conta, recebe email de verificacao, confirma
- [ ] Login e logout funcionam
- [ ] Reset de senha envia email com link funcional
- [ ] Admin acessivel em `/painel-admin/` e protegido (staff only)
- [ ] Importacao da base historica funciona (consome API FutPythonTrader, popula Match)
- [ ] Dashboard exibe KPIs: total de jogos, win rate, ROI, P&L total, drawdown maximo
- [ ] Backtest executa corretamente com filtros de estrategia e odds
- [ ] Tabela HTMX mostra ultimos 10 jogos filtrados com resultado (Green/Red)
- [ ] Grafico Chart.js de P&L acumulado renderiza corretamente
- [ ] CRUD de estrategias funcional (criar, editar, excluir via modais HTMX)
- [ ] Codigo em ingles, type hints (PEP 484) em todos os modulos
- [ ] UI em portugues brasileiro
- [ ] Container sobe com `docker compose up --build`
- [ ] Aplicacao responde em `/healthz/`
- [ ] `planejamento.md` esta na raiz do projeto
