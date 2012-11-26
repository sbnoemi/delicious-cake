from delicious_cake import http as cake_http

__all__ = ('ResourceResponse',)


class ResourceResponse(object):
    def __init__(self, obj=None, entity_cls=None, include_entity=None,
                 response_cls=None, response_kwargs=None):
        self.obj = obj

        self.entity_cls = entity_cls
        self.include_entity = include_entity

        self.response_cls = response_cls
        self.response_kwargs = response_kwargs

    def get_entity_cls(self, default=None):
        return self.entity_cls if self.entity_cls is not None else default

    def get_response_cls(self, default=None):
        return self.response_cls if self.response_cls is not None else default

    def get_response_kwargs(self, obj):
        ret = {}

        if self.response_kwargs is not None:
            for key in self.response_kwargs.keys():
                val = self.response_kwargs[key]

                if callable(val):
                    val = val(obj)

                ret[key] = val

        return ret
