---
description: "Especialista PostgreSQL remoto + Django ORM — models, migrations, queries otimizadas. Banco SEMPRE na VPS, nunca local."
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

# Database Django

> **Regra absoluta:** Banco PostgreSQL **da VPS**, nunca local. Mesma instância em dev e prod (databases separados).

---

## 🌐 Conexão — `DATABASE_URL`

```python
# config/settings/base.py
import dj_database_url
import os

DATABASES = {
    "default": dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,  # exige SSL no Postgres da VPS
    )
}
```

```env
# .env (dev)
DATABASE_URL=postgres://user:pass@vps.exemplo.com:5432/myapp_dev?sslmode=require

# .env (prod)
DATABASE_URL=postgres://user:pass@vps.exemplo.com:5432/myapp_prod?sslmode=require
```

> **Nunca** rode Postgres em container local. Crie 2 databases na mesma VPS: `<app>_dev` e `<app>_prod`.

---

## 🧱 Modelo Base Obrigatório

```python
# apps/core/models.py
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Base para todos os models. UUID + timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
```

> Use UUID em todas as PKs públicas para evitar enumeração (IDOR).

---

## ⚡ Comandos Essenciais

```bash
# Ciclo de migrations
python manage.py makemigrations --name "describe_change"
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate app 0001    # ver SQL antes de aplicar

# Inspeção
python manage.py shell_plus --print-sql # django-extensions
python manage.py dbshell                # psql direto

# Manutenção
python manage.py squashmigrations app 0001 0010
```

---

## 🔍 Queries Otimizadas — Receita

| Problema | Solução |
|---|---|
| `.user.name` em loop | `select_related("user")` |
| `.tags.all()` em loop | `prefetch_related("tags")` |
| Contagem com filtro | `annotate(Count("items", filter=Q(...)))` |
| Update em massa | `Model.objects.filter(...).update(...)` |
| Insert em massa | `Model.objects.bulk_create([...], batch_size=1000)` |
| Lock pessimista | `select_for_update()` dentro de `transaction.atomic()` |

```python
# ❌ N+1
orders = Order.objects.all()
for o in orders:
    print(o.user.email, o.items.count())

# ✅ Otimizado
from django.db.models import Count
orders = (
    Order.objects
    .select_related("user")
    .prefetch_related("items")
    .annotate(items_count=Count("items"))
)
```

---

## 🔐 Constraints Modernas (Django 5.x)

```python
from django.db import models
from django.db.models import Q, F, CheckConstraint, UniqueConstraint


class Subscription(TimeStampedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=[("monthly", "Mensal"), ...])
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, default="active")

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(expires_at__gt=F("started_at")),
                name="subscription_valid_period",
            ),
            UniqueConstraint(
                fields=["user"],
                condition=Q(status="active"),
                name="one_active_subscription_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["user", "-started_at"]),
        ]
```

---

## 🌱 Seeds via Management Command

```python
# apps/core/management/commands/seed.py
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Popula o banco com dados de teste."

    @transaction.atomic
    def handle(self, *args, **options):
        from apps.accounts.models import User
        User.objects.get_or_create(
            email="admin@example.com",
            defaults={"is_staff": True, "is_superuser": True},
        )
        self.stdout.write(self.style.SUCCESS("Seed concluído."))
```

```bash
python manage.py seed
```

---

## 🔒 Transações

```python
from django.db import transaction


@transaction.atomic
def transfer_credits(from_user, to_user, amount: int) -> None:
    from_acc = Account.objects.select_for_update().get(user=from_user)
    to_acc = Account.objects.select_for_update().get(user=to_user)
    from_acc.balance -= amount
    to_acc.balance += amount
    from_acc.save(update_fields=["balance"])
    to_acc.save(update_fields=["balance"])
```

---

## ✅ Checklist Antes do Migrate

- [ ] Migration tem nome descritivo (`--name`)
- [ ] Não há perda de dados não documentada
- [ ] `RunPython` tem função `reverse`
- [ ] Indexes adicionados em FK e campos de filtro frequente
- [ ] Constraints declaradas no `Meta`
- [ ] `select_related`/`prefetch_related` nas queries de uso comum
- [ ] Backup do banco prod feito antes de aplicar (em prod)

---

## 🚫 Anti-padrões

- ❌ Postgres local em Docker
- ❌ PK auto-incremento exposto em URL pública
- ❌ `Model.objects.all()` sem paginação em listagem
- ❌ `.count()` quando `.exists()` resolve
- ❌ Loop salvando 1 a 1 (use `bulk_create`/`bulk_update`)
- ❌ Migration sem `--name` descritivo
