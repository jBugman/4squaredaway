# -*- coding: UTF-8 -*-


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.x) + ',' + str(self.y)


class Rect(object):
    def __init__(self, origin, width, height):
        self.origin = origin  # Point(x, y)
        self.width = width
        self.height = height

    @classmethod
    def rect_with_center_and_halfsize(cls, center, half_size):
        return cls(
            origin=Point(center.x - half_size, center.y - half_size),
            width=half_size * 2,
            height=half_size * 2
        )

    @property
    def sw(self):
        return str(self.origin)

    @property
    def ne(self):
        return str(Point(
            self.origin.x + self.width,
            self.origin.y + self.height
        ))

    def __str__(self):
        return '{' + self.sw + ' ' + self.ne + '}'
