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

All columns are non-null. UUIDs are supplied by Python; timestamps default to
`SYSUTCDATETIME()` (UTC). SQL Server `timestamp` is a row version, so actual times
use `datetime2`. Updating a settlement must explicitly update `updated_at`.

- Names/usernames/category names: `nvarchar(100)`; email: `nvarchar(254)`;
  expense description: `nvarchar(500)`; password hash: `varchar(255)`;
  split method: `varchar(20)`.
- Amounts use `decimal(19,2)`. Expense totals and settlements must be positive;
  individual shares may be zero (rounding very small expenses).
- Membership has a composite `(group_id, user_id)` primary key. A split is unique
  per `(expense_id, debtor_id)`. Settlements must have different sender/receiver.
- Category IDs are explicit reference keys, not identity-generated values:
  `1 = Jedzenie`, `2 = Transport`, `3 = Inne`.
- Foreign keys use SQL Server's default no-action behavior. Cross-row rules,
  including group membership and shares summing to the total, belong to future
  application functionality. `split_method` and settlement `status` have no
  database enumeration yet; the demo uses `equal` and status `0`.

This task implements the existing seven-table design from issue #8/#15.
Correction records, authentication, balance calculation, and HTTP database access
remain separate application tasks; this schema does not claim to implement all
proposed requirements in issue #11.
