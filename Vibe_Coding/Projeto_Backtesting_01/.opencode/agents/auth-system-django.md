---
description: "Sistema completo de auth Django — signup, login, logout, recuperação de senha, verificação de email, perfil, admin. Usa django-allauth + SMTP Gmail."
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  bash: allow
  webfetch: deny
  task: allow
---

# Auth System Django

> Entrega o **kit obrigatório de auth** que TODO projeto precisa ter no dia 1.

---

## 📦 Features Garantidas

- ✅ Cadastro (signup) com **verificação de email obrigatória**
- ✅ Login (email + senha)
- ✅ Logout
- ✅ **Esqueci minha senha** + reset por email
- ✅ Mudança de senha logado
- ✅ Perfil do usuário editável
- ✅ Admin Django protegido (URL custom)
- ✅ SMTP Gmail configurado de fábrica

---

## 🛠️ Setup

```bash
pip install django-allauth dj-database-url
```

```python
# config/settings/base.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Allauth
    "allauth",
    "allauth.account",

    # Apps locais
    "apps.accounts",
    "apps.core",
]

SITE_ID = 1
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# === Allauth — config moderna (>= 0.61) ===
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",
    "signup": "10/h",
    "reset_password": "3/h",
}

LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/accounts/login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# === SMTP — Gmail App Password ===
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    f"App <{EMAIL_HOST_USER}>",
)
```

---

## 👤 Custom User Model

```python
# apps/accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=120, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
```

---

## 🌐 URLs

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("painel-admin/", admin.site.urls),  # URL custom para admin
    path("accounts/", include("allauth.urls")),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("dashboard/", include("apps.accounts.urls")),
    path("healthz/", TemplateView.as_view(template_name="healthz.html")),
]
```

---

## 🎨 Templates Override (Tailwind)

Estrutura:
```
templates/
└── account/
    ├── login.html
    ├── signup.html
    ├── password_reset.html
    ├── password_reset_done.html
    ├── password_reset_from_key.html
    ├── email/
    │   ├── email_confirmation_message.txt
    │   ├── email_confirmation_subject.txt
    │   ├── password_reset_key_message.txt
    │   └── password_reset_key_subject.txt
    └── verification_sent.html
```

Exemplo `login.html`:

```html
{% extends "base.html" %}
{% block title %}Entrar{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white rounded-2xl shadow-lg p-8">
    <h1 class="text-2xl font-bold mb-6 text-center">Entrar</h1>
    <form method="post" class="space-y-4">
        {% csrf_token %}
        <input type="email" name="login" required
               class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
               placeholder="seu@email.com">
        <input type="password" name="password" required
               class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500"
               placeholder="Senha">
        <button class="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg font-semibold">
            Entrar
        </button>
    </form>
    <p class="text-sm text-center mt-4">
        <a href="{% url 'account_reset_password' %}" class="text-indigo-600 hover:underline">
            Esqueci minha senha
        </a>
    </p>
    <p class="text-sm text-center mt-2">
        Não tem conta?
        <a href="{% url 'account_signup' %}" class="text-indigo-600 hover:underline">Cadastre-se</a>
    </p>
</div>
{% endblock %}
```

---

## 🛡️ Admin Customizado

```python
# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "full_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "full_name")
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("full_name",)}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )


admin.site.site_header = "Painel Administrativo"
admin.site.site_title = "Admin"
admin.site.index_title = "Gestão"
```

---

## 🧪 Verificação de Setup

```bash
python manage.py createsuperuser
python manage.py runserver
# Teste:
# 1. Acesse /accounts/signup/  → cria conta
# 2. Verifica email recebido (Gmail)
# 3. Confirma o link
# 4. Login em /accounts/login/
# 5. Esqueci a senha → recebe email
# 6. Acesse /painel-admin/
```

---

## ✅ Checklist Pronto-para-deploy

- [ ] `AUTH_USER_MODEL` configurado antes da primeira migration
- [ ] Allauth instalado e migrations aplicadas
- [ ] SMTP testado (recebe email de verificação real)
- [ ] Templates Tailwind override em `templates/account/`
- [ ] Admin em URL não-óbvia (`/painel-admin/` ou similar)
- [ ] `ACCOUNT_RATE_LIMITS` ativos (anti-bruteforce)
- [ ] `SECURE_*` settings ativos em produção
- [ ] Superuser criado

---

## 🚫 Não Fazer

- ❌ Usar `username` no signup (usar email como identificador)
- ❌ Deixar admin em `/admin/` em produção
- ❌ Esquecer `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`
- ❌ Hardcode de credenciais SMTP no settings
- ❌ Criar custom user DEPOIS da primeira migration
