from delicious_cake.response import ResourceResponse

from core.entities import CakeListEntity, CakeDetailEntity
from core.resources import BaseDetailResource, BaseListResource

__all__ = ('EmptyDetailResource', 'EmptyListResource',)


class EmptyDetailResource(BaseDetailResource):
    def get(self, request, *args, **kwargs):
        self._get(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        self._head(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self._put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = False


class EmptyListResource(BaseListResource):
    def get(self, request, *args, **kwargs):
        self._get(request, *args, **kwargs)

    def head(self, request, *args, **kwargs):
        self._head(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self._put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self._delete(request, *args, **kwargs)

    class Meta(object):
        include_entity = False
