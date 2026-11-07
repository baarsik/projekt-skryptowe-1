-- Run as the Microsoft Entra database administrator, connected to rachunki-db.
-- These are public Azure identity display names, never passwords.
IF DB_NAME() <> N'rachunki-db'
    THROW 50000, 'Connect specifically to rachunki-db before granting permissions.', 1;

IF DATABASE_PRINCIPAL_ID(N'id-projekt-skryptowe-1-migrate') IS NULL
    CREATE USER [id-projekt-skryptowe-1-migrate] FROM EXTERNAL PROVIDER;
IF DATABASE_PRINCIPAL_ID(N'projekt-skryptowe-1-api-baarsik') IS NULL
    CREATE USER [projekt-skryptowe-1-api-baarsik] FROM EXTERNAL PROVIDER;

GRANT CREATE TABLE TO [id-projekt-skryptowe-1-migrate];
GRANT ALTER, REFERENCES, SELECT, INSERT, UPDATE, DELETE, VIEW DEFINITION
    ON SCHEMA::dbo TO [id-projekt-skryptowe-1-migrate];
GRANT SELECT, INSERT, UPDATE, DELETE
    ON SCHEMA::dbo TO [projekt-skryptowe-1-api-baarsik];
