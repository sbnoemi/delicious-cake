from django.conf import settings

from delicious_cake.paginators import Paginator
from delicious_cake.throttle import BaseThrottle
from delicious_cake.serializers import Serializer
from delicious_cake.authorization import Authorization
from delicious_cake.authentication import Authentication

__all__ = ('DetailResourceOptions', 'ListResourceOptions',)


class DetailResourceOptions(object):
    include_entity = True

    entity_cls = None
    detail_entity_cls = None

    serializer = Serializer()
    default_format = 'application/json'

    authorization = Authorization()
    authentication = Authentication()

    throttle = BaseThrottle()

    def __new__(cls, name, meta=None):
        overrides = {}

        if meta is not None:
            for override_name in dir(meta):
                if not override_name.startswith('_'):
                    overrides[override_name] = getattr(meta, override_name)

        return object.__new__(type(name, (cls,), overrides))

    def _get_entity_cls(self, *entity_classes):
        entity_cls = None

        for entity_cls in entity_classes:
            if entity_cls is not None:
                break

        return entity_cls

    def get_detail_entity_cls(self):
        return self._get_entity_cls(self.entity_cls, self.detail_entity_cls)


class ListResourceOptions(DetailResourceOptions):
    collection_name = 'objects'

    list_entity_cls = None
    paginator_cls = Paginator

    max_limit = 100
    limit = getattr(settings, 'API_LIMIT_PER_PAGE', 20)

    def get_list_entity_cls(self):
        return self._get_entity_cls(
            self.entity_cls, self.list_entity_cls, self.detail_entity_cls)
