# -*- coding: UTF-8 -*-


class Category(object):
    def __init__(self, category):
        self.name = category['name']
        self.id = category['id']
        self.categories = [Category(x) for x in category.get('categories', [])]

    @classmethod
    def list_from_json(cls, source):
        return cls._filter(cls._cleanup(source['categories']))

    @classmethod
    def _cleanup(cls, categories):
        for c in categories:
            c.pop('pluralName', None)
            c.pop('shortName', None)
            icon = c.pop('icon', None)
            if icon:
                c['icon'] = icon['prefix'] + 'bg_32' + icon['suffix']
            if 'categories' in c:
                cls._cleanup(c['categories'])
                if not c['categories']:
                    c.pop('categories', None)
        return categories

    @classmethod
    def _filter(cls, categories):
        result = []
        for c in categories:
            if c['id'] != '4e67e38e036454776db1fb3a':
                # Is not 'Residence'
                c.pop('categories', None)
                result.append(c)
            else:
                for sub_c in c['categories']:
                    if sub_c['id'] != '4bf58dd8d48988d103941735':
                        # Is not 'Home (private)'
                        sub_c.pop('categories', None)
                        result.append(sub_c)
        return result
