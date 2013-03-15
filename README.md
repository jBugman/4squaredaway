## Поиск

Все типы venues:

    /search/{запрос}

Без private home:

    /filter/{запрос}

Дополнительные GET-параметры:

* `format=json|csv`
* `iterations=n` — количество запросов в батче

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
