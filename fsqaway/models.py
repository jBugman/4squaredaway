# -*- coding: UTF-8 -*-


class Venue(object):
    def __init__(self, venue):
        self.name = venue['name']
        self.url = venue['canonicalUrl']
        self.checkins = venue['stats']['checkinsCount']
        self.users = venue['stats']['usersCount']
        self.tips = venue['stats']['tipCount']
        self.likes = venue['likes']['count']
        self.specials = venue['specials']['count']
        self.city = venue['location'].get('city', '')
        self.address = venue['location'].get('address', '')
        self.id = venue['id']

        photos = venue.get('photos', None)
        self.photos = photos.get('count', 0) if photos else 0

        _, icon, categories = self._get_categories(venue)
        self.icon = (icon['prefix'], icon['suffix'])
        self.categories = ', '.join(categories)

        self.relevance = 0

    def _get_categories(self, venue):
        primary = None
        icon = None
        categories = []
        for cat in venue['categories']:
            if 'primary' in cat and cat['primary']:
                primary = cat['name']
                icon = cat['icon']
            else:
                categories.append(cat['name'])
        return primary, icon, [primary] + categories


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
