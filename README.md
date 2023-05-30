## *Готовый проект: [aliceyaroslavtseva.pythonanywhere.com]*
---

## 1. [Описание](#1)
## 2. [Запуск проекта](#2)
## 4. [Техническая информация](#3)
## 5. [Об авторе](#4)

---
## 1. Описание <a id=1></a>

Yatube- социальная сеть для публикации личных дневников. 
Сайт, на котором можно создать личную страницу. Если на нее зайти, то можно посмотреть все записи автора.
Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. 
Автор может выбрать имя и уникальный адрес для своей страницы. 
Есть возможность модерировать записи.
Записи можно отправить в сообщество и посмотреть там записи разных авторов.

---
## 2. Запуск проекта <a id=2></a>

### Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:AliceYaroslavtseva/yatube_final.git
```
### Cоздать и активировать виртуальное окружение:
```
python -m venv venv # Для Windows
python3 -m venv venv # Для Linux и macOS
```
```
source venv/Scripts/activate # Для Windows
source venv/bin/activate # Для Linux и macOS
```
### Установить зависимости из файла requirements.txt:
```
python.exe -m pip install --upgrade pip # Для Windows
python3 -m pip install --upgrade pip # Для Linux и macOS
```
```
pip install -r requirements.txt
```
### Выполнить миграции:
```
python manage.py migrate # Для Windows
python3 manage.py migrate # Для Linux и macOS
```
### Запустить проект:
```
python manage.py runserver # Для Windows
python3 manage.py runserver # Для Linux и macOS
```

---
## 3. Техническая информация <a id=3></a>

  - Python
  - Django
  - HTML
  - CSS
  - Bootstrap

---
## 4. Об авторе <a id=4></a>

Алиса Ярославцева:
```
Telegram: t.me/hellfoxalice
GitHub: github.com/AliceYaroslavtseva
```
