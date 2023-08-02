Foodgram
Продуктовый помощник - проект курса Backend-разработки Яндекс.Практикум.
Проект представляет собой онлайн-сервис и API для него.
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект реализован на Django и DjangoRestFramework.
Доступ к данным реализован через API-интерфейс.
Документация к API написана с использованием Redoc.

Развертывание проекта
Развертывание на локальном сервере
- Установите на сервере docker и docker-compose.
- Создайте файл /infra/.env.
- Выполните команду docker-compose up -d --buld.
- Выполните миграции docker-compose exec backend python manage.py migrate.
- Создайте суперюзера docker-compose exec backend python manage.py createsuperuser.
- Соберите статику docker-compose exec backend python manage.py collectstatic --no-input.
Документация к API находится по адресу: http://localhost/api/docs/redoc.html.

Автор:

Небыков Артем https://github.com/NBKRTM