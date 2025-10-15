Feature: Производительность списка рецептов
  Scenario: p95 для GET /recipes держится под порогом
    Given сервис развернут на stage и есть ≥ 100 рецептов
    When запускается нагрузочный тест на 50 RPS в течение 5 минут
    Then p95 времени ответа для GET /recipes ≤ 150 мс

Feature: Валидация входных данных
  Scenario: Слишком длинное поле title отклоняется
    Given пользователь отправляет POST /recipes с title длиной более 120 символов
    When запрос обрабатывается API
    Then ответ имеет статус 422
    And тело ошибки не содержит внутренних деталей

Feature: Ограничение частоты запросов
  Scenario: Превышение лимита POST /recipes возвращает 429
    Given лимит запросов установлен на 30 в минуту на IP
    When пользователь отправляет 35 POST /recipes за минуту
    Then как минимум 5 ответов должны иметь код 429 Too Many Requests

Feature: Формат ошибок RFC7807
  Scenario: Все ошибки возвращаются в формате RFC7807
    Given сервис обрабатывает любые исключения
    When возникает ошибка валидации или серверная ошибка
    Then тело ответа содержит поля type, title, status и correlation_id

Feature: CORS-политика
  Scenario: Блокировка недоверенных доменов
    Given разрешённый origin "https://app.recipes.io"
    When браузер отправляет preflight-запрос из "https://evil.com"
    Then ответ не содержит заголовок Access-Control-Allow-Origin

Feature: Rate limiting (negative)
  Scenario: API остаётся доступным после временного ограничения
    Given лимит запросов 30 в минуту на IP
    When клиент превышает лимит и получает 429
    Then через 60 секунд лимит должен сбрасываться
    And следующие запросы снова возвращают 200 OK

Feature: Validation fallback (negative)
  Scenario: Неверный JSON формат обрабатывается корректно
    Given пользователь отправляет некорректный JSON в POST /recipes
    When API получает запрос
    Then ответ имеет код 400
    And ошибка в формате RFC7807
