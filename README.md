# Foodgram - приложение "Продуктовый помощник"

## Описание проекта

Учебный проект от Яндекс.Практикума. 
Сайт, на котором пользователи могут публиковать и редактировать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Задеплоенный проект [Foodgram](https://https://nebykov.ddns.net/) доступен по адресу: https://nebykov.ddns.net/

## Технологии

 - python==3.9;
 - django==3.2.3;
 - djangorestframework==3.12.4;
 - nginx==1.18.0;
 - gunicorn==20.1.0;
 - djoser==2.1.0;

## Запуск проекта
Для запуска проекта необходимо выполнить следующие действия.

- Склонировать репозиторий и перейти в него в командной строке:

```bash
git https://github.com/NBKRTM/foodgram-project-react
cd foodgram-project-react
```

- Cоздать и активировать виртуальное окружение, установить зависимости:

```bash
python3 -m venv venv && \ 
    source venv/scripts/activate && \
    python -m pip install --upgrade pip && \
    pip install -r backend/requirements.txt
```

- Создать файл `.env` файл в директории в корневой папке проекта, в котором должны содержаться следующие переменные:
	>POSTGRES_DB=foodgram_db\
    >DB_NAME= # название БД\ 
    >POSTGRES_USER= # ваше имя пользователя\
    >POSTGRES_PASSWORD= # пароль для доступа к БД\
    >DB_HOST=db\
    >DB_PORT=5432\
	>SECRET_KEY= # секретный ключ\
	
Далее необходимо собрать образы для фронтенда, бэкенда и nginx и загрузить их на dockerhub.  
- Из папки "./backend/" выполнить команды:
```bash
docker build -t nbkrtm/foodgram_backend .
docker push nbkrtm/backend
```

- Из папки "./frontend/" выполнить команду:
```bash
docker build -t nbkrtm/foodgram_frontend .
docker push nbkrtm/foodgram_frontend
```

- Из папки "./nginx/" выполнить команду:
```bash
docker build -t nbkrtm/foodgram_gateway .
docker push nbkrtm/foodgram_gateway 
```

После отправки образов на сервере создать и запустить контейнеры.  
- На сервере из папки "foodgram" выполнить команду:
```bash
sudo docker compose -f docker-compose.production.yml pull
sudo docker compose -f docker-compose.production.yml up -d
```

- После успешного запуска контейнеров выполнить миграции:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

- Создать суперпользователя (пример: email: admin@admin.com password: admin):
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

```

- Собрать статику:
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

- Заполнить базу данных ингредиентами:
```
sudo docker compose -f docker-compose.production.ymlexec backend python manage.py load_ingredients
```

- Добавить теги в админ. зоне проекта: https://nebykov.ddns.net/admin/recipes/tag/


## Автор
Nebykov Artem
GitHub:	https://github.com/nbkrtm
E-mail: nbkrtm2000@icloud.com