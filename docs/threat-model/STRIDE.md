# STRIDE Threat Analysis — Recipe Manager

| Поток/Элемент | Угроза (STRIDE) | Риск | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|------|-----------|---------------|-------------------|
| **F1 /recipes (GET)** | I: Information Disclosure | R1 | Маскирование логов, исключение чувствительных данных в ответах | NFR-04, NFR-08 | e2e тесты + анализ логов |
| **F2 /recipes (POST)** | D: Denial of Service | R2 | Ограничение частоты запросов (rate limiting ≤30 rpm/IP) | NFR-02 | Нагрузочный тест |
| **F2 /recipes (POST)** | T: Tampering | R3 | Валидация и нормализация полей title/description/ingredients | NFR-03 | Unit-тесты FastAPI |
| **F3 SQL → PostgreSQL** | E: Elevation of Privilege | R4 | Минимальные права DB-пользователя, separate user roles | NFR-07 | Конфиг Postgres roles |
| **F4 Neo4j API** | R: Repudiation | R5 | Аудит запросов и логирование действий администратора | NFR-08 | Логи Neo4j + audit trail |
| **F5 CI → Backend** | S: Spoofing | R6 | Доверенные токены GitHub Actions, подпись runner-ов | NFR-06 | CI настройки + лог проверки |
| **F6 POST /login** | S: Spoofing | R7 | Хэширование Argon2id + rate-limit /login | NFR-01, NFR-02 | Unit + e2e тесты |
| **F6 POST /login** | I: Information Disclosure | R8 | Маскирование ошибок логина, возврат 401 без деталей | NFR-04 | Контрактные тесты |
| **F7 Validation Layer** | T: Tampering | R9 | Input sanitization и ограничение длины полей | NFR-03 | Pytest валидации |
| **F8 SQLAlchemy CRUD** | E: Elevation of Privilege | R10 | ORM binding, параметризованные запросы | NFR-03 | Unit-тест + линтер SQLAlchemy |
| **F9 Neo4j driver queries** | T: Tampering | R11 | Ограничение доступных узлов/рёбер через роль | NFR-07 | Integration test Neo4j |
| **F10 recipes table (Postgres)** | I: Information Disclosure | R12 | Защищённый доступ, dump без PII | NFR-07, NFR-08 | CI snapshot check |
| **F11 relations graph (Neo4j)** | T: Tampering | R13 | ACL в Neo4j, только чтение для API-ролей | NFR-07 | Neo4j config policy |
| **F12 CI Reports → Backend** | R: Repudiation | R14 | Подписание артефактов CI и хранение в безопасном S3 | NFR-06 | GitHub artifact logs |
| **Frontend (Vue.js)** | S: Spoofing | R15 | CSP и CORS-политика (allowlist origins) | NFR-05 | HTTP-заголовки в e2e |
| **Backend (FastAPI)** | D: DoS via large JSON | R16 | Лимит размера тела запроса ≤ 1MB | NFR-03 | pytest + нагрузочный тест |
| **Frontend (Vue.js)** | X: Cross-Site Scripting | R17 | Escaping и Content-Security-Policy | NFR-05 | OWASP ZAP baseline scan |
| **Не применимо:** F9–F11 (внутренние связи)** | - | - | Доступ ограничен внутри Core и Data boundary | - | Документированное исключение |
| **Общее (все потоки)** | I: Information Disclosure | R18 | Шифрование каналов связи HTTPS/TLS1.3 | NFR-10 | SSL scan + конфиг Nginx |
| **Общее (все потоки)** | D: Denial of Service | R19 | Мониторинг p95 latency и error rate | NFR-09 | CI + Grafana dashboard |

---

### Исключения

- **F9–F11 (внутренние связи)**: не анализируются по STRIDE, так как проходят исключительно внутри доверенных границ Core и Data,
  используют сервисные учётные записи и защищены сетевыми ACL.
- **F12 (CI Reports)**: угроза подделки маловероятна, CI запускается с подписанными runner-ами GitHub.
  Проверено настройками Actions (NFR-06).
