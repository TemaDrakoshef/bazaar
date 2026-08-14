# BAZAAR — техническая выжимка для разработки (v2 с отдельным Auth Service)

## 1. Цель проекта

Создать open-source интернет-магазин (микросервисная архитектура) для портфолио. Универсальный каталог с гибкими атрибутами (EAV/JSONB), возможность продажи любых товаров. Освобождение продавцов от маркетплейсов.
Референс репозиторий - https://github.com/DimaKrylovDev/microservice-dating-app

## 2. Архитектура

- Микросервисы (+ API Gateway как единая точка входа).
- Синхронное: REST (frontend ↔ Gateway) и gRPC (между сервисами, опционально).
- Асинхронное: события через Kafka (или Redis Pub/Sub).
- Database per service (у каждого своя БД PostgreSQL).
- Паттерн Saga для транзакций (заказы).

## 3. Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, gRPC (опционально), Kafka/Redis, pytest.
- **Frontend**: React 18, TypeScript, Tailwind CSS, React Router, Axios.
- **Infrastructure**: Docker, Docker Compose, Nginx/Traefik (Gateway).
- **Базы данных**: PostgreSQL 15+.
- **Кэш**: Redis (сессии, кэширование).
- **Лицензия**: MIT.
- **Документация и код**: на английском (README.md + README.ru.md опционально).

## 4. Микросервисы (обновлённый список)

| Сервис                   | Ответственность                                                                                                                                                                                                                                                                                 | Хранит ли данные?            |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **Auth Service**         | Аутентификация (login), выдача JWT (access + refresh), валидация токенов (для Gateway), выход (logout), обновление токенов. Не хранит пользователей, только refresh-токены (в своей БД) или в Redis. | Да (refresh-токены)                |
| **User Service**         | Управление профилями: регистрация, CRUD пользователей, роли, профиль.                                                                                                                                                                                    | Да (пользователи)            |
| **Product Service**      | Каталог товаров, категории, динамические атрибуты (EAV), остатки.                                                                                                                                                                                            | Да                                       |
| **Order Service**        | Корзина, заказы, статусы, история.                                                                                                                                                                                                                                                  | Да                                       |
| **Payment Service**      | Платежи (тестовый режим, Stripe/заглушка).                                                                                                                                                                                                                                         | Да                                       |
| **Notification Service** | Email-уведомления (приветствие, статусы заказа, оплата).                                                                                                                                                                                                              | Нет (или своя для логов) |
| **API Gateway**          | Единый вход, проверка JWT (обращается к Auth Service для валидации), маршрутизация запросов к нужным сервисам.                                                                                                                    | Нет                                     |

## 5. Основные сущности (модели данных)

- **User** (в User Service): id, email, hashed_password, full_name, role, created_at, updated_at.
- **RefreshToken** (в Auth Service): id, user_id (внешний ключ к User), token_hash, expires_at, revoked.
- **Product**: id, name, description, price, category_id, attributes (JSONB или отдельная таблица ProductAttribute с key/value), stock_quantity, created_at, updated_at.
- **Category**: id, name, parent_id (иерархия), slug.
- **Cart**: id, user_id, created_at.
- **CartItem**: id, cart_id, product_id, quantity.
- **Order**: id, user_id, total_amount, status (pending, paid, shipped, delivered, cancelled), shipping_address, created_at, updated_at.
- **OrderItem**: id, order_id, product_id, quantity, price_at_time.
- **Payment**: id, order_id, amount, status (pending, succeeded, failed), payment_method, external_id (из платежной системы), created_at.

## 6. События (event-driven)

- `user.registered` (публикует User Service) → Auth (создать запись о refresh‑токене? нет, не надо), Notification (приветствие).
- `order.created` (Order Service) → Payment (инициировать оплату), Inventory (если есть).
- `payment.succeeded` (Payment Service) → Order (обновить статус), Notification.
- `payment.failed` → Order (отмена), Notification.
- `order.status_changed` → Notification.

## 7. План разработки (обновлённый порядок)

0. **Проектирование** (диаграммы, контракты, схемы БД, структура).
1. **Инфраструктура** – docker-compose, общая библиотека (логирование, exceptions, клиенты для gRPC/REST), настройка Kafka.
2. **Auth Service** (первый) – эндпоинты /login, /refresh, /logout, /validate (для Gateway). JWT генерация, хранение refresh-токенов.
3. **User Service** – регистрация (принимает запрос от Auth), CRUD пользователей. Реализовать синхронный gRPC-вызов от Auth к User для проверки пароля при логине.
4. **API Gateway** – проверка JWT через Auth Service, прокси на сервисы.
5. **Product Service** – каталог с EAV.
6. **Order Service** – корзина, заказы.
7. **Payment Service** – интеграция с платежами.
8. **Notification Service** – подписка на события.
9. **Frontend** – React (каталог, корзина, заказ, личный кабинет, админка).
10. **Тестирование, документация, деплой**.

## 8. Требования к коду

- Имена переменных, функций, классов – на английском.
- Комментарии и docstrings – на английском.
- Использовать async/await.
- Alembic для миграций.
- Покрытие тестами (pytest) ключевых сценариев.
- PEP8, black/isort (опционально).
- Структурированное логирование (JSON).
- Настройки через переменные окружения (pydantic-settings).

## 9. Структура репозитория (обновлённая)

bazaar/
├── services/
│ ├── auth-service/ # новый сервис
│ │ ├── app/
│ │ │ ├── api/ # /login, /refresh, /logout, /validate
│ │ │ ├── core/ # config, security (JWT)
│ │ │ ├── models/ # RefreshToken (SQLAlchemy)
│ │ │ ├── schemas/ # Pydantic для запросов/ответов
│ │ │ └── services/ # логика генерации токенов, валидации
│ │ ├── tests/
│ │ ├── Dockerfile
│ │ ├── requirements.txt
│ │ └── .env.example
│ ├── user-service/
│ │ ├── app/
│ │ │ ├── api/ # регистрация, профиль, роли
│ │ │ ├── core/ # config, db
│ │ │ ├── models/ # User
│ │ │ ├── schemas/
│ │ │ └── services/ # бизнес-логика
│ │ └── ...
│ ├── product-service/
│ ├── order-service/
│ ├── payment-service/
│ ├── notification-service/
│ └── api-gateway/ # прокси + проверка JWT через Auth Service
├── frontend/
├── protos/ # для gRPC (например, UserService для Auth)
├── scripts/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md

## 10. Взаимодействие Auth ↔ User

- **Логин**: Auth принимает email/password, вызывает User Service (gRPC или REST) для проверки пароля, получает user_id и роль, генерирует JWT и сохраняет refresh-токен в своей БД.
- **Регистрация**: Auth → User Service создаёт пользователя
- **Валидация токена**: Gateway отправляет токен в Auth Service на эндпоинт /validate, получает user_id и роль, затем проксирует запрос.

## 11. Текущий статус

- Проект инициализирован, нет кода.
- Первая задача: написать Auth Service (генерация JWT, хранение refresh-токенов в PostgreSQL) и User Service (CRUD пользователей, проверка пароля).
- Затем связать их через gRPC.

## 12. Ближайшие действия

1. Создать структуру папок.
2. Написать docker-compose.yml с PostgreSQL для Auth, User, Product, Order, Payment; Kafka/Redis.
3. Реализовать общую библиотеку (shared) для JWT, настроек, логов.
4. Разработать Auth Service: модели RefreshToken, эндпоинты /login, /refresh, /logout, /validate (с использованием User Service gRPC-клиента для проверки пароля).
5. Разработать User Service: модели User, эндпоинты регистрации, получения профиля, обновления, CRUD (только для админа).
6. Реализовать API Gateway: проверка JWT через Auth Service, прокси.
7. Далее Product Service и т.д.
