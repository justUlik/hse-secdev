# ADR-003: Secrets Management via Environment Variables
Дата: 2025-10-21
Статус: Accepted

## Context
Сервис использует базы данных PostgreSQL и Neo4j.
Неправильное хранение секретов в коде или логах повышает риск компрометации.

## Decision
- Все секреты (DB_URL, JWT_SECRET, API_KEYS) берутся из переменных окружения.
- .env исключён из репозитория (через `.gitignore`).
- Секреты ротируются каждые 30 дней (Vault policy).
- В тестах — использование mock-секретов, не продакшн-ключей.

## Consequences
- Соответствие политикам NFR-07, безопасная ротация.
- Требуется дополнительная настройка CI/CD для секретов.
- Возможность централизованного управления через Vault/KMS.

## Links
- NFR-07 (секреты и ротация)
- STRIDE: F3 (Elevation of Privilege)
- Risk R10 (неправильная ротация секретов)
- tests/test_env_vars.py::test_env_not_in_repo
