from collections import namedtuple

from django.db import models
from django.utils.timezone import now


__all__ = ('Cake',)


Point = namedtuple('Point', ['x', 'y', 'parrot'])


class Cake(models.Model):
    CAKE_TYPE_BIRTHDAY = 1
    CAKE_TYPE_GRADUATION = 2
    CAKE_TYPE_SCHADENFREUDE = 3

    CAKE_TYPE_CHOICES = (
        (CAKE_TYPE_BIRTHDAY, u'Birthday Cake',),
        (CAKE_TYPE_GRADUATION, u'Graduation Cake',),
        (CAKE_TYPE_SCHADENFREUDE, u'Shameful Pride Cake',),)

    point = Point(x=42, y=7, parrot=u'Norwegian Blue')

    message = models.CharField(max_length=128)
    cake_type = models.PositiveSmallIntegerField(db_index=True)
