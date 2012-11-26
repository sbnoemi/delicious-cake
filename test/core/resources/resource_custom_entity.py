from django.db import models

from delicious_cake.response import ResourceResponse

from core.entities import CakeDetailEntity, CakeListEntity
from core.resources import BaseListResource, BaseDetailResource

__all__ = ('CustomEntityDetailResource', 'CustomEntityListResource',)


class CustomEntityDetailResource(BaseDetailResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(
            self._get(request, *args, **kwargs), entity_cls=CakeDetailEntity)

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cake, created = self._post(request, *args, **kwargs)
        return ResourceResponse(cake, entity_cls=CakeDetailEntity), created

    def put(self, request, *args, **kwargs):
        cake, created = self._put(request, *args, **kwargs)
        return ResourceResponse(cake, entity_cls=CakeDetailEntity), created

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = True


class CustomEntityListResource(BaseListResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(
            self._get(request, *args, **kwargs), entity_cls=CakeListEntity)

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return ResourceResponse(
            self.create_obj(
                request, *args, **kwargs), entity_cls=CakeDetailEntity), True

    def put(self, request, *args, **kwargs):
        return ResourceResponse(
            self._put(request, *args, **kwargs), entity_cls=CakeDetailEntity)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    @models.permalink
    def get_resource_uri(self):
        return ('custom-entity-list',)

    class Meta(object):
        include_entity = True
