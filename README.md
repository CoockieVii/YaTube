## Стэк технологий:
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

# Социальная сеть YaTube

В проекте реализованы следующие функции:

- добавление/удаление постов авторизованными пользователями
- редактирование постов только его автором
- возможность авторизованным пользователям оставлять комментарии к постам
- подписка/отписка на понравившихся авторов
- создание отдельной ленты с постами авторов, на которых подписан пользователь
- создание отдельной ленты постов по группам(тематикам)


Подключены пагинация, кеширование, авторизация пользователя, возможна смена пароля через почту.
Неавторизованному пользователю доступно только чтение.
Покрытие тестами.


# Запуск:
    Клонировать репозиторий:
        git clone https://github.com/CoockieVii/hw05_final.git
    
    перейти в него в командной строке:
        cd api_yamdb

    Cоздать и активировать виртуальное окружение:
        python -m venv venv
        source venv/Scripts/activate
    
    Обновить менеджер пакетов:
        python -m pip install --upgrade pip

    Установить зависимости из файла requirements.txt:
        pip install -r requirements.txt

    Выполнить миграции:
        python manage.py migrate

    Запустить проект:
        python manage.py runserver
