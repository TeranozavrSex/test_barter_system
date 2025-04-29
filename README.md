Я сделал этот проект за ночь исходя из моего темплейта для джанго проектов, не судите стого.
Я не отключил все ненужные функции но думаю это не будет проблемой, лишний контейнер редиса или функционал для создания дампов бд не повлияет на работу тестового задания.
Так же я использовал языковые модели что можно понять по встречающимся комментариям в коде, не думаю что это плохо так как они удешевляют разработку проектов если уметь ими пользоваться.
Тем более они дают нечестное приимущество по сравнения с разработкой просто руками.  


# Barter System Application

A Django-based platform for exchanging items between users. This application allows users to create listings for items they want to exchange, browse other users' listings, and make exchange proposals.

## Features

- **User Authentication**: Custom token-based authentication system
- **Ad Management**:
  - Create ads with title, description, category, condition
  - Upload images for ads
  - Edit and delete your own ads
  - Browse ads from other users
- **Search & Filtering**:
  - Search by keywords in title and description
  - Filter by category and condition
  - Pagination for better UX
- **Exchange System**:
  - Send exchange proposals
  - Accept or reject proposals
  - Automatic deactivation of ads after successful exchange
  - Automatic cancellation of pending proposals after an exchange is accepted
- **REST API**:
  - Complete API for all functions
  - OpenAPI/Swagger documentation

## Technology Stack

- **Python** 3.8+
- **Django** 4+
- **PostgreSQL** database
- **Django REST Framework** for API
- **drf_spectacular** for API documentation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd test_barter_system
```

2. Configure environment variables (create a `.env` file near `.env.sample`):

3. Up docker containers `docker compose up -d --build`

site: http://localhost:8000/
swagger: http://localhost:8000/swagger/
admin: http://localhost:8000/admin/


## Project Structure

- `src/` - Main project directory
  - `settings/` - Project settings
  - `user/` - Custom user model and authentication
  - `barter/` - Main application with ad and proposal functionality
    - `models.py` - Database models
    - `views.py` - Views for web interface and API
    - `urls.py` - URL routing
    - `serializers.py` - API serializers
    - `templates/` - HTML templates
    - `tests.py` - Test suite

## Usage

### Web Interface

1. Register or log in to your account
2. Create ads for items you want to exchange
3. Browse other users' ads
4. Send exchange proposals
5. Manage your proposals (accept/reject)
6. View your active ads and exchange history

### API Endpoints

The REST API provides endpoints for:

- Ad management (CRUD operations)
- Proposal creation and management
- User authentication
- Search and filtering

API documentation is available at `/api/schema/swagger-ui/` when the server is running.

## Implementation Details

This project implements:
- User registration and authentication
- JWT tokens
- Custom user model
- Dual authentication via cookies and bearer tokens (bearer tokens checked first when both are enabled)
- Complete ad management system
- Exchange proposal workflow with status updates
- Advanced filtering and search functionality

## Testing

Run the test suite with:

```bash
python src/manage.py test
```

The project includes comprehensive tests for:
- Model validation
- View functionality
- API endpoints
- Authentication
- Business logic (exchange process)


# А это описание моего темплейта с которого я писал этот проект, я подумал а почему бы его тут не оставить)
## В этом примере реализованы:
 - Регистрация, jwt токены, кастомная модель юзера, авторизация через cookie и bearer (Если в конфиге включены оба то bearer проверяется первый)
 - Регистрация и авторизация через телеграмм приложение с проверкой тг хэша
 - Само приложение, база данных и автохил в докере
 - Бэкапы базы данных и медиафайлов через крон
 - gunicorn
 - redis
 - Логи в одном месте
 - Отключен csrf, настроено хранение статики
 - Реализован абоба сваггер для быстрой документации ручек на бэкэнде
 - dozzle в отдельном компоузе (Если поднимаешь обязятельно ставь в nginx base auth)
 - django-defender защита от брутфорса админки, запись всех логинов и айпишников с которых они были произведены
 - pre-commit

## При использовании проекта как темплейта
  - Найди barter по всему проекту и замени в нужных местах на название совего проекта
  - Создай `./.env` по примеру `./.env.sample`
  - `docker compose up -d`
  - Создай суперюзер для джанги, зайди в контейнер бэкенда и `poetry run python src/manage.py createsuperuser`

## Run pre-commit
  `sudo pre-commit run --all -c ./.pre-commit-config.yaml`

## Деплой
  - Установи ngixn, certbot и docker compose
    ```shell
      echo "################## DOCKER ##################"
      sudo apt update
      sudo apt install apt-transport-https ca-certificates curl software-properties-common
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
      sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" -y
      sudo apt install docker-ce -y
      echo "################## DOCKER COMPOSE ##################"
      sudo curl -L "https://github.com/docker/compose/releases/download/2.32.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
      echo "################## NGINX ##################"
      sudo apt install nginx -y
      echo "################## CERTBOT ##################"
      sudo apt install certbot python3-certbot-nginx -y
    ```
  - Создай файл с названием твоего проекта по пути `/etc/nginx/sites-enabled/`
  - Скопируй в этот файл содержимое `./nginx_sample.conf`, замени все barter на нужные адреса
  - Проверь не подавится ли nginx твоим конфигом `nginx -t`
  - Перезапусти nginx `service nginx restart`
  - Настройка ssl с certbot
    ```shell
      sudo certbot --nginx -d [your_domen] --register-unsafely-without-email
    ```
