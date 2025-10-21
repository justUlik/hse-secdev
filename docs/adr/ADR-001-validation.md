# ADR-001: Input Validation and Upload Limits
Дата: 2025-10-21
Статус: Accepted

## Context
В API `/recipes` пользователи передают названия, описания и списки ингредиентов.
Без ограничений на размер и тип данных возможно DoS или повреждение данных.

## Decision
- Ограничить размер тела запроса `max_body_size = 1 MB` (FastAPI middleware).
- Добавить проверку типов и пустых полей (pydantic validation).
- Для загрузок — проверка `magic bytes` и расширений файлов.
- Все имена файлов сохраняются как UUID для предотвращения коллизий.

## Consequences
- Повышение безопасности и надёжности API.
- Возможные отказы при загрузке больших файлов.
- Улучшена трассировка ошибок для тестов валидации.

## Links
- NFR-03 (валидация данных)
- STRIDE: F2 (Tampering), F7 (Validation Layer)
- Risk R4 (внедрение вредных данных)
- tests/test_recipes_validation.py::test_invalid_payload
