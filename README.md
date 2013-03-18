## Поиск

Все типы venues:

    /search/{запрос}

Без private home:

    /filter/{запрос}

Дополнительные GET-параметры:

* `format=json|csv`
* `iterations=n` — количество запросов в батче

## Доступ

    Login: 4sq
    Password: dev1-

## Выгрузка данных в CSV

    /search/{запрос}?format=csv

Порядок полей:

* name
* categories, соединенные ';'
* checkinsCount
* usersCount
* tipCount
* likes.count
* specials.count
* location.city
* location.address
* id
* 'relevance'


## Категории

Все:

    /dev/categories
    
Пригодные для фильтрации домов:

    /dev/categories?filter=true


## Deployment

    cd /home/ubuntu/4squaredaway
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

    sudo apt-get install supervisor
    sudo ln -fs /home/ubuntu/4squaredaway/deploy/4sq.conf /etc/supervisor/conf.d/4sq.conf
    sudo supervisorctl reread
    sudo supervisorctl update

Flask-Assets (Stylus) requires `sudo npm install -g stylus` (nodejs package)
