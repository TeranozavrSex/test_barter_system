FROM python:3.12-slim
USER root

RUN apt-get update && apt-get install -y \
    python3-dev \
    netcat-traditional \
    postgresql-client-common \
    postgresql-client \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --user-group -ms /bin/bash app

ENV PYTHONUNBUFFERED=1
ENV HOME=/home/app
ENV PUBLIC_DIR=/home/app/public

WORKDIR $HOME

COPY --chown=app:app ./pyproject.toml $HOME

RUN pip install --upgrade pip
RUN pip install poetry

COPY --chown=app:app . $HOME

RUN chown -R app:app $HOME

EXPOSE 8000

ENTRYPOINT $HOME/docker-entrypoint.sh
