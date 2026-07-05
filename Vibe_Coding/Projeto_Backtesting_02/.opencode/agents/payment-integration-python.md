---
description: "Integração Mercado Pago — 3 modos (Sem pagamento / Pagamento avulso por link / Assinatura recorrente). Webhooks seguros, idempotentes, com expiração automática de assinaturas."
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  bash: allow
  webfetch: allow
  task: allow
---

# Payment Integration Python

> Use o modo definido no `planejamento.md` (Tipo A, B ou C). Nunca implemente os 3 ao mesmo tempo.

---

## 🧭 Decisão de Modo

| Tipo | Cenário | O que entrega |
|---|---|---|
| **A — Sem pagamento** | SaaS gratuito/interno | Nada — pular este agente |
| **B — Pagamento avulso** | Restaurante, lava-jato, serviço pontual | Endpoint cria link único + webhook confirma |
| **C — Assinatura recorrente** | SaaS clássico mensal/trimestral/semestral/anual | Compra acesso pelo período, expira automático |

---

## 📦 Setup Comum

```bash
pip install mercadopago
```

```python
# apps/billing/mp_client.py
import os
import mercadopago

mp = mercadopago.SDK(os.environ["MP_ACCESS_TOKEN"])
```

```env
# .env
MP_ACCESS_TOKEN=APP_USR-...        # do app no painel MP
MP_PUBLIC_KEY=APP_USR-...
MP_WEBHOOK_SECRET=__random_secret__ # gere com secrets.token_urlsafe(32)
```

---

## 🔵 MODO B — Pagamento Avulso (Link Único)

### Modelo

```python
# apps/billing/models.py
from django.db import models
from apps.core.models import TimeStampedModel


class Charge(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("approved", "Aprovado"),
        ("rejected", "Rejeitado"),
        ("cancelled", "Cancelado"),
    ]
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="charges")
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payer_email = models.EmailField()
    mp_preference_id = models.CharField(max_length=100, blank=True, db_index=True)
    mp_payment_id = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    init_point = models.URLField(blank=True)  # link para pagar
    paid_at = models.DateTimeField(null=True, blank=True)
```

### Criar link de cobrança

```python
# apps/billing/services.py
from django.conf import settings
from django.urls import reverse
from .mp_client import mp
from .models import Charge


def create_payment_link(*, user, description: str, amount: float, payer_email: str) -> Charge:
    charge = Charge.objects.create(
        user=user,
        description=description,
        amount=amount,
        payer_email=payer_email,
    )

    base = settings.SITE_URL.rstrip("/")
    pref = {
        "items": [{
            "title": description,
            "quantity": 1,
            "unit_price": float(amount),
            "currency_id": "BRL",
        }],
        "payer": {"email": payer_email},
        "external_reference": str(charge.id),
        "back_urls": {
            "success": f"{base}/billing/success/",
            "failure": f"{base}/billing/failure/",
            "pending": f"{base}/billing/pending/",
        },
        "auto_return": "approved",
        "notification_url": f"{base}/webhooks/mercadopago/",
    }
    result = mp.preference().create(pref)
    data = result["response"]
    charge.mp_preference_id = data["id"]
    charge.init_point = data["init_point"]
    charge.save(update_fields=["mp_preference_id", "init_point"])
    return charge
```

---

## 🟣 MODO C — Assinatura Recorrente

### Planos

```python
# apps/billing/plans.py
PLANS = {
    "monthly":   {"label": "Mensal",     "days": 30,  "price": 49.90},
    "quarterly": {"label": "Trimestral", "days": 90,  "price": 129.90},
    "semestral": {"label": "Semestral",  "days": 180, "price": 239.90},
    "annual":    {"label": "Anual",      "days": 365, "price": 399.90},
}
```

### Modelo

```python
# apps/billing/models.py
from datetime import timedelta
from django.utils import timezone
from django.db import models
from apps.core.models import TimeStampedModel


class Subscription(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Aguardando pagamento"),
        ("active", "Ativa"),
        ("expired", "Expirada"),
        ("cancelled", "Cancelada"),
    ]
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.CharField(max_length=20)  # monthly/quarterly/semestral/annual
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    mp_preference_id = models.CharField(max_length=100, blank=True, db_index=True)
    mp_payment_id = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["status", "expires_at"])]

    @property
    def is_active(self) -> bool:
        return (
            self.status == "active"
            and self.expires_at is not None
            and self.expires_at > timezone.now()
        )

    def activate(self, *, plan_days: int) -> None:
        now = timezone.now()
        self.started_at = now
        self.expires_at = now + timedelta(days=plan_days)
        self.status = "active"
        self.save(update_fields=["started_at", "expires_at", "status"])
```

### Criar assinatura (compra pontual de período)

```python
# apps/billing/services.py
from .plans import PLANS
from .mp_client import mp
from .models import Subscription
from django.conf import settings


def create_subscription_checkout(*, user, plan: str) -> Subscription:
    if plan not in PLANS:
        raise ValueError("Plano inválido.")

    sub = Subscription.objects.create(user=user, plan=plan, amount=PLANS[plan]["price"])
    base = settings.SITE_URL.rstrip("/")

    pref = {
        "items": [{
            "title": f"Assinatura {PLANS[plan]['label']}",
            "quantity": 1,
            "unit_price": float(PLANS[plan]["price"]),
            "currency_id": "BRL",
        }],
        "payer": {"email": user.email},
        "external_reference": f"sub:{sub.id}",
        "back_urls": {
            "success": f"{base}/billing/success/",
            "failure": f"{base}/billing/failure/",
            "pending": f"{base}/billing/pending/",
        },
        "auto_return": "approved",
        "notification_url": f"{base}/webhooks/mercadopago/",
    }
    result = mp.preference().create(pref)
    data = result["response"]
    sub.mp_preference_id = data["id"]
    sub.save(update_fields=["mp_preference_id"])
    return sub
```

### Decorator para proteger rotas premium

```python
# apps/billing/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def subscription_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("account_login")
        sub = (
            request.user.subscriptions
            .filter(status="active")
            .order_by("-expires_at")
            .first()
        )
        if not sub or not sub.is_active:
            messages.warning(request, "Sua assinatura está inativa ou expirada.")
            return redirect("billing:plans")
        return view(request, *args, **kwargs)
    return wrapper
```

### Job diário de expiração (Celery beat)

```python
# apps/billing/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Subscription


@shared_task
def expire_subscriptions() -> int:
    """Marca assinaturas vencidas como expiradas."""
    now = timezone.now()
    qs = Subscription.objects.filter(status="active", expires_at__lt=now)
    count = qs.update(status="expired")
    return count
```

```python
# config/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "expire-subscriptions": {
        "task": "apps.billing.tasks.expire_subscriptions",
        "schedule": crontab(minute=0, hour=3),  # 3h da manhã
    },
}
```

---

## 🔔 Webhook Único (B e C)

```python
# apps/billing/webhooks.py
import hmac
import hashlib
import os
import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from .mp_client import mp
from .models import Charge, Subscription
from .plans import PLANS


def _verify_signature(request) -> bool:
    """Valida x-signature do Mercado Pago (HMAC-SHA256)."""
    secret = os.environ.get("MP_WEBHOOK_SECRET", "")
    if not secret:
        return True  # se não configurado, pula (logar warning em prod!)
    sig_header = request.headers.get("x-signature", "")
    request_id = request.headers.get("x-request-id", "")
    parts = dict(p.strip().split("=", 1) for p in sig_header.split(",") if "=" in p)
    ts = parts.get("ts", "")
    received = parts.get("v1", "")
    data_id = request.GET.get("data.id", "")
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received)


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    if not _verify_signature(request):
        return HttpResponseBadRequest("Invalid signature")

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    if body.get("type") != "payment":
        return HttpResponse(status=200)

    payment_id = body.get("data", {}).get("id")
    if not payment_id:
        return HttpResponse(status=200)

    payment = mp.payment().get(payment_id)["response"]
    status = payment.get("status")
    external_ref = payment.get("external_reference", "")

    # === MODO C: Assinatura ===
    if external_ref.startswith("sub:"):
        sub_id = external_ref.split(":", 1)[1]
        sub = Subscription.objects.filter(id=sub_id).first()
        if not sub:
            return HttpResponse(status=200)
        # idempotência
        if sub.mp_payment_id == str(payment_id) and sub.status == "active":
            return HttpResponse(status=200)
        sub.mp_payment_id = str(payment_id)
        if status == "approved":
            sub.activate(plan_days=PLANS[sub.plan]["days"])
        sub.save(update_fields=["mp_payment_id"])
        return HttpResponse(status=200)

    # === MODO B: Cobrança avulsa ===
    charge = Charge.objects.filter(id=external_ref).first()
    if not charge:
        return HttpResponse(status=200)
    if charge.mp_payment_id == str(payment_id) and charge.status == status:
        return HttpResponse(status=200)
    charge.mp_payment_id = str(payment_id)
    charge.status = status if status in dict(Charge.STATUS_CHOICES) else "pending"
    if status == "approved":
        charge.paid_at = timezone.now()
    charge.save()
    return HttpResponse(status=200)
```

```python
# config/urls.py
from apps.billing.webhooks import mercadopago_webhook
urlpatterns += [path("webhooks/mercadopago/", mercadopago_webhook)]
```

---

## ✉️ Emails Transacionais

```python
# apps/billing/emails.py
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_payment_confirmation(*, to: str, amount: float, description: str) -> None:
    body = render_to_string("billing/email/payment_confirmation.txt", {
        "amount": amount, "description": description,
    })
    send_mail(
        subject="✅ Pagamento confirmado",
        message=body,
        from_email=None,
        recipient_list=[to],
    )
```

Dispare via `signal` ou diretamente no webhook após `status == "approved"`.

---

## 🛡️ Segurança & Idempotência — Checklist

- [ ] Webhook valida `x-signature` (HMAC)
- [ ] Webhook é idempotente (não reprocessa mesmo `payment_id`)
- [ ] `external_reference` sempre setado na criação
- [ ] Valores comparados com Decimal, nunca float
- [ ] Webhook responde 200 mesmo para eventos ignorados (não retentar à toa)
- [ ] Logs de webhook em produção
- [ ] `MP_ACCESS_TOKEN` e `MP_WEBHOOK_SECRET` em `.env` (nunca no código)

---

## 🧪 Testar Localmente

```bash
# Use ngrok para expor /webhooks/mercadopago/
ngrok http 8000
# Cole o URL https no painel MP > Webhooks
```

---

## 🚫 Não Fazer

- ❌ Confiar em `back_urls` para confirmar pagamento (use webhook)
- ❌ Atualizar status sem validar assinatura
- ❌ Usar valor enviado pelo cliente (sempre o do banco/Charge)
- ❌ Implementar Modo B + Modo C ao mesmo tempo sem necessidade
