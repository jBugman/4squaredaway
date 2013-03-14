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

Из-за кодирования в cp1251 cтранные символы заменяются на '?'
