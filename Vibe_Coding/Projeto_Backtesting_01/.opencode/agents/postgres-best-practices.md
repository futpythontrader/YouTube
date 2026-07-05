---
description: "Boas práticas PostgreSQL para Django — indexes, EXPLAIN, RLS, pooling, particionamento. Foco em VPS remoto."
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

# Postgres Best Practices

> Para PostgreSQL 16+ rodando em VPS remota com Django.

---

## 📊 Categorias por Impacto

| # | Categoria | Impacto |
|---|---|---|
| 1 | Query Performance & Indexes | CRITICAL |
| 2 | Connection Pooling | CRITICAL |
| 3 | Schema Design | HIGH |
| 4 | Concorrência & Locks | MEDIUM |
| 5 | Monitoring | MEDIUM |

---

## 1️⃣ Query Performance

### Use EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 'uuid' AND status = 'paid';
```

Procure:
- **Seq Scan** em tabelas grandes → adicionar index
- **Sort** custoso → considerar index ordenado
- **Nested Loop** com loops grandes → revisar joins

### Indexes Compostos — ordem importa

```sql
-- Para WHERE status='active' AND expires_at > NOW()
CREATE INDEX idx_sub_status_expires ON subscriptions(status, expires_at);

-- Para WHERE user_id=? ORDER BY created_at DESC
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
```

### Partial Indexes

```sql
-- Indexa só assinaturas ativas (menor, mais rápido)
CREATE INDEX idx_active_subs ON subscriptions(expires_at)
WHERE status = 'active';
```

No Django:
```python
class Meta:
    indexes = [
        models.Index(
            fields=["expires_at"],
            condition=Q(status="active"),
            name="idx_active_subs",
        ),
    ]
```

---

## 2️⃣ Connection Pooling

VPS remoto = latência. **Sempre** use pooling.

```python
# config/settings/base.py
DATABASES = {
    "default": dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,        # mantém conexão viva 10 min
        conn_health_checks=True, # checa antes de usar
    )
}
```

Para Django 5.x + PgBouncer (recomendado em produção):
- Modo **transaction** no PgBouncer
- `DISABLE_SERVER_SIDE_CURSORS = True` se usar PgBouncer transaction mode

---

## 3️⃣ Schema Design

| Princípio | Detalhe |
|---|---|
| **UUIDs em PKs públicas** | `uuid_generate_v4()` ou `gen_random_uuid()` |
| **TIMESTAMPTZ** | Sempre com timezone, nunca `timestamp` puro |
| **JSONB > JSON** | JSONB é indexável e mais rápido |
| **NOT NULL por padrão** | Use `NULL` apenas quando ausência tem significado |
| **CHECK constraints** | Validações no banco, não só na app |

```python
# Django 5.x
class Meta:
    constraints = [
        CheckConstraint(check=Q(amount__gte=0), name="amount_positive"),
        UniqueConstraint(fields=["email"], condition=Q(is_active=True), name="unique_active_email"),
    ]
```

---

## 4️⃣ Concorrência

```python
# Lock pessimista
from django.db import transaction

@transaction.atomic
def transfer(from_user, to_user, amount):
    a = Account.objects.select_for_update().get(user=from_user)
    b = Account.objects.select_for_update().get(user=to_user)
    a.balance -= amount
    b.balance += amount
    a.save(); b.save()
```

```sql
-- Atualizações idempotentes via UPSERT
INSERT INTO settings (user_id, key, value)
VALUES (%s, %s, %s)
ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;
```

No Django:
```python
Setting.objects.update_or_create(
    user=user, key="theme",
    defaults={"value": "dark"},
)
```

---

## 5️⃣ Monitoring

```sql
-- Top 10 queries mais lentas (extension pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;

-- Indexes não usados
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Tamanho das tabelas
SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
FROM pg_class WHERE relkind = 'r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 20;
```

---

## ✅ Checklist por Tabela

- [ ] PK é UUID se exposta publicamente
- [ ] FKs têm index (Django cria automaticamente)
- [ ] Campos de filtro frequente têm index
- [ ] Campos `boolean` raros usam partial index
- [ ] `CHECK` constraints declaradas
- [ ] `created_at`/`updated_at` com TIMESTAMPTZ
- [ ] Sem `SELECT *` em hot paths

---

## 🚫 Não Fazer

- ❌ Postgres local em vez do remoto da VPS
- ❌ Conexão sem `conn_max_age`
- ❌ Index em toda coluna (custa write performance)
- ❌ `timestamp` sem timezone
- ❌ JSON quando JSONB serve
- ❌ Migrations destrutivas sem backup
