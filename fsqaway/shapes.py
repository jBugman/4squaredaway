# -*- coding: UTF-8 -*-


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect(object):
    def __init__(self, origin, width, height):
        self.origin = origin  # Point(x, y)
        self.width = width
        self.height = height
