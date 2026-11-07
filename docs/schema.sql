BEGIN TRANSACTION;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

GO

-- Running upgrade  -> 20261107_01

CREATE TABLE users (
    id UNIQUEIDENTIFIER NOT NULL, 
    name NVARCHAR(100) NOT NULL, 
    username NVARCHAR(100) NOT NULL, 
    email NVARCHAR(254) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    CONSTRAINT pk_users PRIMARY KEY (id), 
    CONSTRAINT uq_users_username UNIQUE (username), 
    CONSTRAINT uq_users_email UNIQUE (email)
);

GO

CREATE TABLE groups (
    id UNIQUEIDENTIFIER NOT NULL, 
    name NVARCHAR(100) NOT NULL, 
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    CONSTRAINT pk_groups PRIMARY KEY (id)
);

GO

CREATE TABLE categories (
    id INTEGER NOT NULL, 
    name NVARCHAR(100) NOT NULL, 
    CONSTRAINT pk_categories PRIMARY KEY (id), 
    CONSTRAINT uq_categories_name UNIQUE (name)
);

GO

CREATE TABLE group_members (
    group_id UNIQUEIDENTIFIER NOT NULL, 
    user_id UNIQUEIDENTIFIER NOT NULL, 
    joined_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    CONSTRAINT pk_group_members PRIMARY KEY (group_id, user_id), 
    CONSTRAINT fk_group_members_group_id_groups FOREIGN KEY(group_id) REFERENCES groups (id), 
    CONSTRAINT fk_group_members_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);

GO

CREATE TABLE expenses (
    id UNIQUEIDENTIFIER NOT NULL, 
    group_id UNIQUEIDENTIFIER NOT NULL, 
    payer_id UNIQUEIDENTIFIER NOT NULL, 
    category_id INTEGER NOT NULL, 
    description NVARCHAR(500) NOT NULL, 
    total_amount NUMERIC(19, 2) NOT NULL, 
    split_method VARCHAR(20) NOT NULL, 
    occurred_on DATE NOT NULL, 
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    CONSTRAINT pk_expenses PRIMARY KEY (id), 
    CONSTRAINT fk_expenses_group_id_groups FOREIGN KEY(group_id) REFERENCES groups (id), 
    CONSTRAINT fk_expenses_payer_id_users FOREIGN KEY(payer_id) REFERENCES users (id), 
    CONSTRAINT fk_expenses_category_id_categories FOREIGN KEY(category_id) REFERENCES categories (id), 
    CONSTRAINT ck_expenses_positive_total CHECK (total_amount > 0)
);

GO

CREATE TABLE expense_splits (
    id UNIQUEIDENTIFIER NOT NULL, 
    expense_id UNIQUEIDENTIFIER NOT NULL, 
    debtor_id UNIQUEIDENTIFIER NOT NULL, 
    amount_owed NUMERIC(19, 2) NOT NULL, 
    CONSTRAINT pk_expense_splits PRIMARY KEY (id), 
    CONSTRAINT fk_expense_splits_expense_id_expenses FOREIGN KEY(expense_id) REFERENCES expenses (id), 
    CONSTRAINT fk_expense_splits_debtor_id_users FOREIGN KEY(debtor_id) REFERENCES users (id), 
    CONSTRAINT uq_expense_splits_expense_id UNIQUE (expense_id, debtor_id), 
    CONSTRAINT ck_expense_splits_nonnegative_share CHECK (amount_owed >= 0)
);

GO

CREATE TABLE settlements (
    id UNIQUEIDENTIFIER NOT NULL, 
    group_id UNIQUEIDENTIFIER NOT NULL, 
    sender_id UNIQUEIDENTIFIER NOT NULL, 
    receiver_id UNIQUEIDENTIFIER NOT NULL, 
    amount NUMERIC(19, 2) NOT NULL, 
    status INTEGER NOT NULL, 
    occurred_on DATE NOT NULL, 
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(), 
    CONSTRAINT pk_settlements PRIMARY KEY (id), 
    CONSTRAINT fk_settlements_group_id_groups FOREIGN KEY(group_id) REFERENCES groups (id), 
    CONSTRAINT fk_settlements_sender_id_users FOREIGN KEY(sender_id) REFERENCES users (id), 
    CONSTRAINT fk_settlements_receiver_id_users FOREIGN KEY(receiver_id) REFERENCES users (id), 
    CONSTRAINT ck_settlements_positive_amount CHECK (amount > 0), 
    CONSTRAINT ck_settlements_different_participants CHECK (sender_id <> receiver_id)
);

GO

INSERT INTO alembic_version (version_num) OUTPUT inserted.version_num VALUES ('20261107_01');

GO

COMMIT;

GO

