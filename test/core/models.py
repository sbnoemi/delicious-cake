from django.db import models
from django.utils.timezone import now

class TimeClass(object):
    @property
    def time(self):
        return now()


class Cake(models.Model):
    CAKE_TYPE_BIRTHDAY = 1
    CAKE_TYPE_GRADUATION = 2
    CAKE_TYPE_SCHADENFREUDE = 3

    CAKE_TYPE_CHOICES = (
        (CAKE_TYPE_BIRTHDAY, u'Birthday Cake',),
        (CAKE_TYPE_GRADUATION, u'Graduation Cake',),
        (CAKE_TYPE_SCHADENFREUDE, u'Shameful Pride Cake',),)

    message = models.CharField(max_length=128)
    cake_type = models.PositiveSmallIntegerField(db_index=True)

    def __init__(self, *args, **kwargs):
        self.nested_time = TimeClass()
        super(Cake, self).__init__(*args, **kwargs)
