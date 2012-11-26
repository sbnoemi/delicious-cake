from django.db import models

import delicious_cake.http as cake_http

from delicious_cake.response import ResourceResponse

from delicious_cake.throttle import CacheDBThrottle
from delicious_cake.authentication import (
    BasicAuthentication, MultiAuthentication, ApiKeyAuthentication,)

from core.entities import CakeDetailEntity, CakeListEntity
from core.resources import BaseListResource, BaseDetailResource

__all__ = ('SimpleDetailResource', 'SimpleListResource',
           'BareSimpleListResource', 'BareSimpleDetailResource',
           'ForcedSimpleDetailResource', 'ForcedSimpleListResource',)


class SimpleDetailResource(BaseDetailResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(self._get(request, *args, **kwargs))

    def head(self, request, *args, **kwargs):
        return ResourceResponse(self._head(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        cake, created = self._post(request, *args, **kwargs)
        return ResourceResponse(cake), created

    def put(self, request, *args, **kwargs):
        cake, created = self._put(request, *args, **kwargs)
        return ResourceResponse(cake), created

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = True
        detail_entity_cls = CakeDetailEntity


class SimpleListResource(BaseListResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(self._get(request, *args, **kwargs))

    def head(self, request, *args, **kwargs):
        return ResourceResponse(self._head(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        return ResourceResponse(
            self.create_obj(request, *args, **kwargs)), True

    def put(self, request, *args, **kwargs):
        return ResourceResponse(self._put(request, *args, **kwargs))

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    @models.permalink
    def get_resource_uri(self):
        return ('simple-list',)

    class Meta(object):
        include_entity = True
        list_entity_cls = CakeListEntity
        detail_entity_cls = CakeDetailEntity

#        authentication = MultiAuthentication(
#            BasicAuthentication(), ApiKeyAuthentication())
#        throttle = CacheDBThrottle(throttle_at=1, timeframe=5)

class ForcedSimpleDetailResource(BaseDetailResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(
            self._get(request, *args, **kwargs), include_entity=True)

    def head(self, request, *args, **kwargs):
        return ResourceResponse(
            self._head(request, *args, **kwargs), include_entity=True)

    def post(self, request, *args, **kwargs):
        cake, created = self._post(request, *args, **kwargs)
        return ResourceResponse(cake, include_entity=True), created

    def put(self, request, *args, **kwargs):
        cake, created = self._put(request, *args, **kwargs)
        return ResourceResponse(cake, include_entity=True), created

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = False
        detail_entity_cls = CakeDetailEntity


class ForcedSimpleListResource(BaseListResource):
    def get(self, request, *args, **kwargs):
        return ResourceResponse(
            self._get(request, *args, **kwargs), include_entity=True)

    def head(self, request, *args, **kwargs):
        return ResourceResponse(
            self._head(request, *args, **kwargs), include_entity=True)

    def post(self, request, *args, **kwargs):
        return ResourceResponse(
            self.create_obj(
                request, *args, **kwargs), include_entity=True), True

    def put(self, request, *args, **kwargs):
        return ResourceResponse(
            self._put(request, *args, **kwargs), include_entity=True)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    @models.permalink
    def get_resource_uri(self):
        return ('forced-simple-list',)

    class Meta(object):
        include_entity = False
        list_entity_cls = CakeListEntity
        detail_entity_cls = CakeDetailEntity


class BareSimpleDetailResource(BaseDetailResource):
    def get(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        return self._head(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self._put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = True
        detail_entity_cls = CakeDetailEntity


class BareSimpleListResource(BaseListResource):
    def get(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        return self._head(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create_obj(request, *args, **kwargs), True

    def put(self, request, *args, **kwargs):
        self._put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    @models.permalink
    def get_resource_uri(self):
        return ('bare-simple-list',)

    class Meta(object):
        include_entity = True
        list_entity_cls = CakeListEntity
        detail_entity_cls = CakeDetailEntity
