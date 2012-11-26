from django.db import models

from delicious_cake.http import HttpCreated
from delicious_cake.response import ResourceResponse

from core.entities import CakeDetailEntity, CakeListEntity
from core.resources import BaseListResource, BaseDetailResource

__all__ = ('CustomCreateListResource',)


class CustomCreateListResource(BaseDetailResource):
    def post(self, request, *args, **kwargs):
        cake = self.create_obj(request, *args, **kwargs)

        return ResourceResponse(
            cake, response_cls=HttpCreated,
            response_kwargs={
                'location': lambda entity: entity.get_resource_uri()})

    class Meta(object):
        detail_entity_cls = CakeDetailEntity
