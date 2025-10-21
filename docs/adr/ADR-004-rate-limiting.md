# ADR-004: Rate Limiting on /login Endpoint
Дата: 2025-10-21
Статус: Accepted

## Context
Повторные попытки входа могут привести к атаке перебора паролей (Bruteforce).
Это отмечено как риск R1 в модели угроз.

## Decision
- Добавлен rate limiting на `/login`: 30 запросов/мин на IP.
- Используется middleware `slowapi.Limiter`.
- При превышении лимита возвращается HTTP 429.

## Consequences
- Снижен риск брутфорса, улучшена устойчивость сервиса.
- Возможные ложные срабатывания при тестах.
- Можно масштабировать через Redis backend.

## Links
- NFR-02 (rate limiting)
- STRIDE: F6 (Spoofing)
- Risk R1 (брутфорс логина)
- tests/test_login_rate_limit.py::test_rate_limit
