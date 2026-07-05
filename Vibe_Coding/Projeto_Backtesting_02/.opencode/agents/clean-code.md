---
description: "Princípios de Clean Code (Uncle Bob) aplicados a Python/Django — nomes, funções, comentários, refatoração, code smells."
mode: subagent
permission:
  read: allow
  edit: allow
  glob: allow
  grep: allow
  list: allow
  bash: deny
  webfetch: deny
  task: allow
---

# Clean Code

> "Código limpo é aquele que outro dev consegue ler e melhorar." — Grady Booch

---

## 🎯 Use Quando

- Refatorando código legado
- Revisando PRs
- Antes de marcar "pronto"
- Após implementar uma feature (passada de polimento)

---

## 1️⃣ Nomes

| Princípio | Ruim | Bom |
|---|---|---|
| Revele intenção | `d` | `elapsed_days` |
| Evite desinformação | `account_list` (é dict) | `accounts_by_id` |
| Distinções reais | `Product`, `ProductData` | `Product`, `ProductSummary` |
| Pronunciável | `genymdhms` | `generation_timestamp` |
| Classes: substantivos | `Manager`, `Processor` | `Customer`, `Invoice` |
| Funções: verbos | `data()` | `fetch_user()` |

---

## 2️⃣ Funções

- **Pequenas.** Caber em 1 tela.
- **Uma coisa só.** Se você consegue extrair uma função com nome significativo, deveria.
- **Mesmo nível de abstração** dentro da função.
- **Argumentos:** 0 ideal, 1-2 ok, 3+ requer justificativa forte. Use dataclass se precisar de mais.
- **Sem efeitos colaterais ocultos.**

```python
# ❌ Faz 3 coisas
def process_order(order_id: int) -> None:
    order = Order.objects.get(pk=order_id)
    order.status = "processed"
    order.save()
    send_mail("Pedido processado", ..., [order.user.email])
    inventory.deduct(order.items)

# ✅ Cada função uma responsabilidade
def process_order(order_id: int) -> Order:
    order = _mark_processed(order_id)
    _notify_customer(order)
    _deduct_inventory(order)
    return order
```

---

## 3️⃣ Comentários

- **Não comente código ruim — reescreva.**
- Explique-se em código (extraia uma função com nome significativo).
- Comentários válidos: legais (licenças), TODO, alertas de consequências, esclarecimento de domínio.

```python
# ❌
# Verifica se o user pode receber benefício
if user.flags & PREMIUM and user.age > 18:

# ✅
if user.is_eligible_for_benefit():
```

---

## 4️⃣ Estrutura — Django

### Fat models, thin views

```python
# ✅ Lógica no model/manager, não na view
class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user).select_related("user")

    def pending_payment(self):
        return self.filter(status="pending")


class Order(models.Model):
    objects = OrderQuerySet.as_manager()

    def mark_paid(self) -> None:
        self.status = "paid"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])
```

### Service layer para regras de negócio complexas

```python
# apps/orders/services.py
def checkout(*, user, items: list[Item]) -> Order:
    """Cria order, reserva estoque e gera link de pagamento."""
    with transaction.atomic():
        order = Order.objects.create(user=user)
        order.items.set(items)
        Inventory.reserve(items)
        link = create_payment_link(order)
    return order
```

---

## 5️⃣ Code Smells Comuns

| Smell | Ação |
|---|---|
| Função com 50+ linhas | Extrair sub-funções |
| 4+ argumentos | Agrupar em dataclass |
| `if`/`elif` longo | Polimorfismo ou dict-dispatch |
| Variáveis com escopo enorme | Reduzir escopo |
| Comentário explicando "o quê" | Renomear/extrair |
| Código duplicado | Extrair função |
| Classe com 10+ métodos | Dividir responsabilidades |
| Loop dentro de loop sobre ORM | N+1 → `prefetch_related` |

---

## 6️⃣ Type Hints — Obrigatório

```python
# ✅
def get_active_users(role: str, since: datetime) -> list[User]:
    return list(User.objects.filter(role=role, last_login__gte=since))

# ❌ sem hints
def get_active_users(role, since):
    ...
```

Use `mypy` ou `pyright` no CI.

---

## 7️⃣ Tests

- Nome do teste descreve o cenário: `test_user_cannot_access_other_users_order()`
- Arrange-Act-Assert visível
- Um conceito por teste
- Use `pytest` fixtures, não `setUp` herdado

```python
def test_subscription_expires_when_passed_due_date(active_subscription):
    active_subscription.expires_at = timezone.now() - timedelta(days=1)
    active_subscription.save()

    expired_count = expire_subscriptions()

    active_subscription.refresh_from_db()
    assert expired_count == 1
    assert active_subscription.status == "expired"
```

---

## ✅ Checklist Antes do PR

- [ ] Funções pequenas e com 1 responsabilidade
- [ ] Nomes revelam intenção
- [ ] Sem código comentado
- [ ] Sem `print` esquecido (use `logging`)
- [ ] Type hints completos
- [ ] Sem `# noqa` sem justificativa
- [ ] Tests cobrindo caminho feliz e erros
- [ ] Sem duplicação óbvia
- [ ] `pre-commit run --all-files` limpo
