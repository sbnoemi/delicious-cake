try:
    from django.utils.copycompat import deepcopy
except ImportError:
    from copy import deepcopy

from delicious_cake import fields

__all__ = ('EntityMetaclass', 'Entity',)


class EntityMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = {}
        declared_fields = {}

        try:
            parents = [b for b in bases if issubclass(b, Entity)]
            parents.reverse()

            for p in parents:
                parent_fields = getattr(p, 'base_fields', {})

                for field_name, field_object in parent_fields.items():
                    attrs['base_fields'][field_name] = deepcopy(field_object)
        except NameError:
            pass

        for field_name, obj in attrs.items():
            if isinstance(obj, fields.ApiField) and \
                    not field_name.startswith('_'):
                field = attrs.pop(field_name)
                field.field_name = field_name
                declared_fields[field_name] = field

        attrs['base_fields'].update(declared_fields)
        attrs['declared_fields'] = declared_fields

        new_class = super(
            EntityMetaclass, cls).__new__(cls, name, bases, attrs)

        for field_name, field_object in new_class.base_fields.items():
            if hasattr(field_object, 'contribute_to_class'):
                field_object.contribute_to_class(new_class, field_name)

        return new_class


class Entity(object):
    __metaclass__ = EntityMetaclass

    def __init__(self, obj):
        self.obj = obj
        self.fields = deepcopy(self.base_fields)

    def process(self, data):
        return data

    def full_process(self):
        processed_data = {}

        for field_name, field_object in self.fields.items():
            processed_field_data = field_object.process(self.obj)

            method = getattr(self, 'process_%s' % field_name, None)

            if method:
                if field_object.attribute is None:
                    processed_field_data = method(self.obj)
                else:
                    processed_field_data = method(processed_field_data)

            if processed_field_data is None and field_object.has_default:
                processed_field_data = field_object.default

            if processed_field_data is not None:
                processed_field_data = \
                    field_object.convert(processed_field_data)

            processed_data[field_name] = processed_field_data

        try:
            if 'resource_uri' not in processed_data:
                processed_data['resource_uri'] = self.get_resource_uri()
        except NotImplementedError:
            pass

        return self.process(processed_data)

    def get_resource_uri(self):
        raise NotImplementedError()
