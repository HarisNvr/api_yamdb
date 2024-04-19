# YaMDb

Проект YaMDb представляет собой платформу для сбора отзывов пользователей о различных произведениях и искусстве. В YaMDb не хранится контент произведений, таких как фильмы или музыка, и поэтому нельзя просматривать их на самой платформе. Вместо этого, YaMDb предоставляет API для работы с отзывами и оценками пользователей.

### Создатели:

https://github.com/S0loWay
https://github.com/HarisNvr

### Технологии: 
 
- Python
- Django
- Django REST Framework 
- SQLite
- Djoser

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/S0loWay/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Работа с API:

### Регистрация:

Пользователь отправляет POST-запрос на добавление нового пользователя с параметрами email и username на эндпоинт:

```
/api/v1/auth/signup/
```

YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес email.

Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт

```
/api/v1/auth/token/
```

В ответе на запрос ему приходит token (JWT-токен).


При желании пользователь отправляет PATCH-запрос и заполняет поля в своём профайле:

```
/api/v1/users/me/
```

Доступные поля для заполнения: first_name, last_name, bio

### Для администратов и модераторов:

При создании пользователя админ может указать role(default='user').

Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать отзывы и ставить оценку произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы; может редактировать и удалять свои отзывы и комментарии. Эта роль присваивается по умолчанию каждому новому пользователю.
Модератор (moderator) — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
Суперюзер Django — обладет правами администратора (admin)

Администраторы могут:
Добавлять, удалять и редактировать: аккаунты пользователей, произведения, коментарии, жанры, отзывы, в том числе других авторов

Модераторы могут:
Добавлять, удалять и редактировать коментарии всех пользователей

## Примеры запросов и ответов API:

### Получение жанров:

GET http://127.0.0.1:8000/api/v1/titles/

{
"count": 0,
"next": "string",
"previous": "string",
"results": [
  {
    "id": 0,
    "name": "string",
    "year": 0,
    "rating": 0,
    "description": "string",
    "genre": [],
    "category": {}
  }
  ]
}


### Публикация комментариев:

POST http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/

{
"text": "string"
}

{
"id": 0,
"text": "string",
"author": "string",
"pub_date": "2019-08-24T14:15:22Z"
}

### Удаление категории:

Права доступа: Администратор.

DELETE http://127.0.0.1:8000/api/v1/categories/{slug}/
