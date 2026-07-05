# Deploy no EasyPanel — BacktestBet

## Pré-requisitos

- VPS com **EasyPanel** instalado
- **PostgreSQL** rodando na VPS (ou em outra VPS acessível)
- **Domínio** configurado apontando para o IP da VPS (ex: `backtestbet.com`)
- Conta **Gmail** com [App Password](https://myaccount.google.com/apppasswords) gerado (para envio de emails)

---

## 1. Preparar o Banco de Dados (PostgreSQL)

Conecte-se ao PostgreSQL da VPS e crie o banco de produção:

```sql
CREATE DATABASE backtestbet_prod;
CREATE USER backtestbet_user WITH PASSWORD 'senha_muito_segura';
GRANT ALL PRIVILEGES ON DATABASE backtestbet_prod TO backtestbet_user;
ALTER DATABASE backtestbet_prod OWNER TO backtestbet_user;
```

---

## 2. Gerar o Arquivo `.env`

No terminal local (não precisa da VPS):

```bash
python generate_env.py
```

Edite o `.env` gerado e preencha **todas** as variáveis. As essenciais são:

| Variável | Valor |
|---|---|
| `SECRET_KEY` | Já gerada automaticamente |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `backtestbet.com,www.backtestbet.com` |
| `DATABASE_URL` | `postgres://backtestbet_user:senha@vps-ip:5432/backtestbet_prod?sslmode=require` |
| `EMAIL_HOST_USER` | Seu email Gmail |
| `EMAIL_HOST_PASSWORD` | App Password do Gmail (16 caracteres) |
| `FUTPYTHONTRADER_TOKEN` | Seu token da API |

---

## 3. Criar o Projeto no EasyPanel

1. Acesse o painel do EasyPanel na sua VPS (`https://seu-vps.com:3000`)
2. Vá em **Projects** → **Create Project**
3. Escolha **App** como tipo
4. Selecione **Docker Compose**
5. Cole o conteúdo do `docker-compose.yml` do projeto
6. Ou, se preferir deploy via Git:
   - Conecte seu repositório GitHub
   - Selecione a branch `main`
   - EasyPanel detecta o `docker-compose.yml` automaticamente

---

## 4. Configurar Variáveis de Ambiente

No EasyPanel, após criar o serviço:

1. Vá até a aba **Environment** do serviço `web`
2. Cole **todas** as variáveis do seu arquivo `.env`
3. Clique **Save**

**Atenção:** Não use o `.env` de desenvolvimento. As variáveis de produção são diferentes.

---

## 5. Configurar o Domínio e SSL

1. No EasyPanel, vá em **Domains**
2. Adicione `backtestbet.com` apontando para:
   - **Service:** `web`
   - **Port:** `8000`
3. Marque a opção **Enable SSL** (Let's Encrypt)
4. Clique **Save**

O EasyPanel emitirá o certificado SSL automaticamente em 1-2 minutos.

---

## 6. Deploy

1. Clique em **Deploy**
2. Acompanhe os logs em tempo real
3. O deploy estará completo quando aparecer:
   ```
   → Aplicando migrations...
   → Iniciando Gunicorn em :8000
   Listening at http://0.0.0.0:8000
   ```

---

## 7. Criar Superusuário

Após o primeiro deploy, acesse o terminal do container:

1. No EasyPanel, vá até o serviço `web` → **Terminal**
2. Execute:

```bash
python manage.py createsuperuser
```

Preencha email e senha quando solicitado.

---

## 8. Validar o Deploy

- **Healthcheck:** `https://backtestbet.com/healthz/` → `{"status":"ok"}`
- **Admin:** `https://backtestbet.com/painel-admin/` → login com superusuário
- **Signup:** `https://backtestbet.com/accounts/signup/` → deve enviar email de verificação
- **Landing:** `https://backtestbet.com/` → página inicial

---

## 9. Atualizações Futuras

Para atualizar o projeto após mudanças no código:

1. Faça push para a branch `main` (se usando Git)
2. No EasyPanel, clique em **Deploy** novamente
3. O novo build será feito com `docker compose build --no-cache`

Ou, se estiver usando Docker Compose manualmente:

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Estrutura de Arquivos no Servidor

```
/app/
├── start.sh          # Script de boot (migrations + gunicorn)
├── manage.py
├── config/           # Django settings (production.py ativo)
├── apps/             # Aplicações Django
├── templates/        # Templates HTML
├── static/           # Arquivos estáticos fonte
└── staticfiles/      # Coletados pelo collectstatic (servidos pelo Whitenoise)
```

---

## Troubleshooting

| Problema | Solução |
|---|---|
| `502 Bad Gateway` | Verifique se o container está rodando: `docker compose ps` |
| `healthz` retorna 503 | Banco de dados inacessível. Verifique `DATABASE_URL` e se o PostgreSQL aceita conexões externas |
| Email não chega | Confira o App Password do Gmail. Verifique logs com `docker compose logs web` |
| Arquivos estáticos quebrados | Execute `python manage.py collectstatic --noinput` no terminal do container |
| Erro `ALLOWED_HOSTS` | Adicione o domínio em `ALLOWED_HOSTS` no `.env` e faça redeploy |
