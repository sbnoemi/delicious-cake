from django.db import models

from delicious_cake import fields
from delicious_cake.entities import Entity

from cake.models import Cake

__all__ = ('CakeListEntity', 'CakeDetailEntity', 'CakePointListEntity',)


class CakeEntity(Entity):
    @models.permalink
    def get_resource_uri(self):
        return ('cake-detail', (self.obj.pk,))


class CakeListEntity(CakeEntity):
    CAKE_TYPE_CHOICES_LOOKUP = dict(Cake.CAKE_TYPE_CHOICES)

    resource_id = fields.IntegerField(attr='pk')
    cake_type = fields.CharField(attr='cake_type')

    def process_cake_type(self, cake_type):
        return self.CAKE_TYPE_CHOICES_LOOKUP.get(cake_type, 'Unknown')

class PointEntity(Entity):
    x = fields.IntegerField(attr='x')
    y = fields.IntegerField(attr='y')


class CakePointListEntity(CakeListEntity):
    point = fields.EntityField(attr='point', entity_cls=PointEntity)


class CakeDetailEntity(CakeListEntity):
    message = fields.CharField(attr='message')

