from core.entities import CakeListEntity, CakeDetailEntity
from core.resources import BaseDetailResource, BaseListResource

__all__ = ('UnimplementedDetailResource', 'UnimplementedListResource',)


class UnimplementedDetailResource(BaseDetailResource):
    class Meta(object):
        include_entity = False
        entity_cls = CakeDetailEntity


class UnimplementedListResource(BaseListResource):
    class Meta(object):
        include_entity = False
        entity_cls = CakeListEntity
