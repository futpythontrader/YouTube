---
description: "Workspace context for python_django - stack, conventions, and available agents"
globs: "**/*"
version: "1.0.0"
alwaysApply: true
---

## OpenCode Agent Orchestration

Este workspace contem **11 agentes especializados** em `.opencode/agents/`. Fluxo recomendado:

```
1. @saas-planner-python  -> planejamento.md (SEMPRE primeiro)
2. @database-django      -> models, migrations, admin
3. @auth-system-django   -> signup, login, reset, SMTP
4. @django-expert        -> views, templates HTMX, URLs
5. @payment-integration-python -> Mercado Pago (se B/C)
6. @docker-deploy-python -> Dockerfile, EasyPanel
7. @security-audit-python -> auditoria pre-deploy
```

Agentes auxiliares: `@django-access-review`, `@django-perf-review`, `@postgres-best-practices`, `@clean-code`

Sempre leia `planejamento.md` antes de implementar. Use `@` para invocar subagentes via Task tool.

---

# Vibe Coding — Python SaaS Workspace

> **Stack moderno e opinionado para construir SaaS Django prontos para produção em dias, não meses.**

---

## Filosofia

> Planeje com clareza. Implemente em paralelo. Faça deploy desde o dia 1.

- **Planejamento primeiro** — nenhuma linha de código antes do `planejamento.md` aprovado
- **Stack único** — Django 5.x + PostgreSQL remoto + Tailwind + HTMX
- **Banco compartilhado** — mesmo PostgreSQL da VPS em dev e produção
- **Deploy via EasyPanel** — Dockerfile + docker-compose prontos no dia 1
- **Auth completo de fábrica** — signup, login, recuperação de senha, verificação de email
- **Pagamentos opcionais** — Mercado Pago em 3 modos (avulso, assinatura, sem pagamento)

---

## Stack Padrão

| Camada | Tecnologia | Versão |
|---|---|---|
| **Backend** | Django | 5.x |
| **Linguagem** | Python | 3.12+ |
| **Banco de dados** | PostgreSQL **remoto (VPS)** | 16+ |
| **ORM** | Django ORM | nativo |
| **Auth** | django-allauth | latest |
| **Frontend (default)** | HTMX + Tailwind CSS (CDN) + Alpine.js | latest |
| **API (quando precisar)** | Django REST Framework | latest |
| **Tasks assíncronas** | Celery + Redis | latest |
| **Pagamentos BR** | Mercado Pago SDK | latest |
| **Email** | SMTP (Gmail App Password) | — |
| **Container** | Docker + Docker Compose | latest |
| **Deploy** | **EasyPanel** (VPS) | — |
| **Tipagem** | Type hints obrigatórios | PEP 484 |
| **Testes** | pytest + pytest-django | latest |

---

## Frontend — Decisão Rápida

| Necessidade | Stack |
|---|---|
| **Simplicidade e Produtividade** | Django + HTMX + Tailwind CSS |
| **Interatividade Complexa (dashboards)** | Django + Alpine.js + Tailwind |
| **App Mobile + Web no mesmo backend** | Django REST Framework + React/Vue |
| **Máxima performance de interface** | Inertia.js (Vue ou React) |

> **Padrão absoluto:** HTMX + Tailwind (CDN) + Alpine.js. Só mudar se o usuário pedir.

---

## Banco de Dados — Regra de Ouro

> **NÃO use PostgreSQL local. Use a mesma instância remota da VPS em dev e produção.**

- O `planejamento.md` deve solicitar:
  - `POSTGRES_HOST` (IP/domínio da VPS)
  - `POSTGRES_PORT` (default 5432)
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
- Tudo via `DATABASE_URL` em `.env`
- Em dev, abrir **schema separado** ou **database separado** na mesma instância (ex: `myapp_dev`, `myapp_prod`)
- **NUNCA** subir `.env` para o git

---

## Email — SMTP Padrão

Todo projeto deve solicitar no setup:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=app_password_de_16_caracteres
DEFAULT_FROM_EMAIL="Nome do App <seu-email@gmail.com>"
```

> Gmail exige **App Password** (não a senha da conta). Documentar no README.

---

## Features Obrigatórias em TODO Projeto

Toda implementação deve incluir, sem exceção:

- [x] Tela de **cadastro** (signup) com verificação de email
- [x] Tela de **login**
- [x] **Esqueci minha senha** + **reset por email**
- [x] **Django Admin** customizado e protegido
- [x] **Dashboard** do usuário autenticado
- [x] **Logout**
- [x] **Perfil do usuário** editável
- [x] Email transacional via SMTP configurado

---

## Tipos de SaaS — Modelo de Pagamento

O `saas-planner-python` SEMPRE pergunta qual tipo:

### Tipo A — Sem Pagamento
SaaS gratuito, ferramenta interna ou freemium sem cobrança automática.
- Sem integração de pagamento
- Foco em onboarding e UX

### Tipo B — Pagamento Avulso (Links Únicos)
Para restaurantes, lava-jato, prestadores de serviço, vendas pontuais.
- Gera **link único de cobrança** por transação
- Valor variável definido pelo dono do SaaS
- Webhook do Mercado Pago confirma pagamento
- Email de confirmação automático

### Tipo C — Assinatura Recorrente
SaaS clássico com planos.
- Períodos: **mensal | trimestral | semestral | anual**
- Usuário **compra acesso** → libera funcionalidade pelo período pago
- Renovação manual ou automática (Mercado Pago Preapproval)
- **Expira automaticamente** ao final do período se não renovar
- Email de aviso antes do vencimento

---

## Deploy — EasyPanel (VPS)

Todo projeto entrega:

- `Dockerfile` multi-stage otimizado
- `docker-compose.yml` para EasyPanel (web + worker + beat)
- `.env.example` documentado
- `DEPLOY.md` com passo-a-passo do EasyPanel
- Healthcheck endpoint `/healthz/`
- `collectstatic` no build, servido por Whitenoise
- Gunicorn como WSGI server

---

## Convenções

- **Código** em inglês (variáveis, funções, classes, docstrings)
- **UI e mensagens ao usuário** em português brasileiro
- **Type hints** obrigatórios
- **Docstrings** em funções públicas
- **Tests** com pytest + pytest-django
- `pyproject.toml` para dependências (uv ou pip)
- Estrutura modular: `apps/` com apps pequenos e coesos
- Settings split: `config/settings/{base,development,production}.py`

---

## Agentes Disponíveis

> **Carregue o agente correspondente com `read_file` antes de implementar.**

| Agente | Caminho | Quando Usar |
|---|---|---|
| **saas-planner-python** | `.github/agents/saas-planner-python.agent.md` | **PRIMEIRO** — gerar `planejamento.md` |
| **django-expert** | `.github/agents/django-expert.agent.md` | Views, models, URLs, templates, HTMX, DRF |
| **auth-system-django** | `.github/agents/auth-system-django.agent.md` | Signup, login, reset de senha, OAuth, RBAC |
| **database-django** | `.github/agents/database-django.agent.md` | Models, migrations, queries Postgres remoto |
| **docker-deploy-python** | `.github/agents/docker-deploy-python.agent.md` | Docker, EasyPanel, CI/CD |
| **payment-integration-python** | `.github/agents/payment-integration-python.agent.md` | Mercado Pago (3 modos) |
| **security-audit-python** | `.github/agents/security-audit-python.agent.md` | Auditoria OWASP, hardening pré-deploy |
| **django-access-review** | `.github/agents/django-access-review.agent.md` | Revisar IDOR e controle de acesso |
| **django-perf-review** | `.github/agents/django-perf-review.agent.md` | Detectar N+1, queries lentas |
| **postgres-best-practices** | `.github/agents/postgres-best-practices.agent.md` | Índices, RLS, otimização Postgres |
| **clean-code** | `.github/agents/clean-code.agent.md` | Refatoração e qualidade |

---

## Regras Absolutas

1. **NUNCA** começar a implementar sem `planejamento.md` aprovado
2. **NUNCA** usar PostgreSQL local — sempre o da VPS via `DATABASE_URL`
3. **SEMPRE** entregar Dockerfile + docker-compose para EasyPanel
4. **SEMPRE** incluir signup + login + reset de senha + admin
5. **SEMPRE** perguntar o tipo de SaaS (A/B/C) antes de planejar pagamento
6. **SEMPRE** usar HTMX + Tailwind (CDN) + Alpine como frontend padrão
7. **NUNCA** commitar `.env`, `db.sqlite3`, `__pycache__`, `media/`

---

## Fluxo Recomendado

```
1. Usuário descreve a ideia
   ↓
2. saas-planner-python pergunta:
   - Stack frontend (default: HTMX+Tailwind+Alpine)
   - Tipo de SaaS (A, B ou C)
   - Credenciais Postgres VPS (host/port/db/user/pass)
   - Credenciais SMTP Gmail (email + app password)
   - Mercado Pago (se B ou C): access token
   ↓
3. Gera planejamento.md
   ↓
4. Usuário aprova
   ↓
5. django-expert + database-django + auth-system-django implementam em paralelo
   ↓
6. payment-integration-python (se aplicável)
   ↓
7. docker-deploy-python prepara EasyPanel
   ↓
8. security-audit-python valida pré-deploy
   ↓
9. Deploy
```

