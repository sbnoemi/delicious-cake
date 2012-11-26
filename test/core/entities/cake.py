import datetime

from django.db import models

from delicious_cake import fields
from delicious_cake.entities import Entity

from core.models import Cake

__all__ = ('CakeListEntity', 'CakeDetailEntity')


class CakeEntity(Entity):
    @models.permalink
    def get_resource_uri(self):
        return ('simple-detail', (self.obj.pk,))


class CakeDeleteEntity(Entity):
    message = fields.CharField(attr='message')

    def process_message(self, processed_data):
        return u'DELETED:  %s' % processed_data['cake']


class CakeListEntity(CakeEntity):
    CAKE_TYPE_CHOICES_LOOKUP = dict(Cake.CAKE_TYPE_CHOICES)

    resource_id = fields.IntegerField(attr='pk')
    cake_type = fields.CharField(attr='cake_type')

    def process_cake_type(self, cake_type):
        return self.CAKE_TYPE_CHOICES_LOOKUP.get(cake_type, 'Unknown')


class CakeDetailEntity(CakeListEntity):
    message = fields.CharField(attr='message')
