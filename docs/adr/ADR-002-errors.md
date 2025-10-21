# ADR-002: Standardized Error Responses (RFC 7807)
Дата: 2025-10-21
Статус: Accepted

## Context
Ошибки ранее возвращались в произвольном формате, что затрудняло логирование и маскирование деталей.
Требуется единообразный формат ответов об ошибках без утечки PII.

## Decision
- Все ошибки форматируются по RFC7807:
  `{ "error": { "code": <string>, "message": <string>, "correlation_id": <uuid> } }`
- Включён глобальный exception handler в FastAPI (`api_error_handler`).
- Маскирование PII: stack trace и детали исключений скрываются.
- Добавлен `correlation_id` в заголовках ответов.

## Consequences
- Единообразие логов и интеграции с мониторингом.
- Потеря некоторых деталей при отладке.
- Совместимость с внешними клиентами и e2e тестами.

## Links
- NFR-04 (ошибки RFC7807)
- STRIDE: F1 (Information Disclosure)
- Risk R2 (утечка подробностей ошибок)
- tests/test_errors.py::test_rfc7807_contract
