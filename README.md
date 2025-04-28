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
