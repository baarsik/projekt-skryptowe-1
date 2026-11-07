# Initial database schema

Implemented by [Alembic revision 20261107_01](../backend/migrations/versions/20261107_01_initial_schema.py).
The generated SQL Server creation script is [schema.sql](schema.sql).

```mermaid
erDiagram
    users {
        uniqueidentifier id PK
        nvarchar name
        nvarchar username UK
        nvarchar email UK
        varchar password_hash
        datetime2 created_at
    }
    groups {
        uniqueidentifier id PK
        nvarchar name
        datetime2 created_at
    }
    group_members {
        uniqueidentifier group_id PK,FK
        uniqueidentifier user_id PK,FK
        datetime2 joined_at
    }
    categories {
        int id PK
        nvarchar name UK
    }
    expenses {
        uniqueidentifier id PK
        uniqueidentifier group_id FK
        uniqueidentifier payer_id FK
        int category_id FK
        nvarchar description
        decimal total_amount
        varchar split_method
        date occurred_on
        datetime2 created_at
    }
    expense_splits {
        uniqueidentifier id PK
        uniqueidentifier expense_id FK
        uniqueidentifier debtor_id FK
        decimal amount_owed
    }
    settlements {
        uniqueidentifier id PK
        uniqueidentifier group_id FK
        uniqueidentifier sender_id FK
        uniqueidentifier receiver_id FK
        decimal amount
        int status
        date occurred_on
        datetime2 created_at
        datetime2 updated_at
    }

    groups ||--o{ group_members : has
    users ||--o{ group_members : is_member_of
    groups ||--o{ expenses : contains
    users ||--o{ expenses : pays
    categories ||--o{ expenses : categorizes
    expenses ||--o{ expense_splits : is_split_into
    users ||--o{ expense_splits : owes
    groups ||--o{ settlements : contains
    users ||--o{ settlements : sends
    users ||--o{ settlements : receives
```

All columns are non-null. UUIDs come from Python; timestamps default to UTC.
Applications must explicitly update `settlements.updated_at` when changing a row.

- Money uses `decimal(19,2)`: totals/repayments must be positive; shares may be zero.
- Membership is keyed by `(group_id, user_id)`; each expense/debtor split is unique.
  A settlement's sender and receiver must differ.
- Category IDs are fixed reference keys: `1 = Jedzenie`, `2 = Transport`, `3 = Inne`.
- Foreign keys prevent deleting referenced rows. Membership eligibility and shares
  adding up to the total are not enforced by the database.
- `split_method` and settlement `status` have no database enum constraints yet.

See [db/schema.py](../backend/db/schema.py) for exact column definitions.
