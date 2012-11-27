import re
import datetime
from decimal import Decimal
from dateutil.parser import parse

from django.utils import datetime_safe
from django.utils.timezone import make_aware

from delicious_cake.utils import make_aware
from delicious_cake.exceptions import ApiFieldError


DATE_REGEX = re.compile('^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}).*?$')
DATETIME_REGEX = re.compile(
    '^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})(T|\s+)(?P<hour>\d{2})' \
        ':(?P<minute>\d{2}):(?P<second>\d{2}).*?$')


class ApiField(object):
    """The base implementation of an entity field."""
    processed_type = 'string'
    help_text = ''

    def __init__(self, attr=None, default=None, help_text=None):
        """
        Optionally accepts an ``attr``, which should be a string of
        either an instance attribute or callable off the object during
        ``process``. Defaults to ``None``, meaning data will be manually
        accessed.

        Optionally accepts a ``default``, which provides default data when the
        object being ``processed`` has no data on the field.
        Defaults to ``None``.

        Optionally accepts ``help_text``, which lets you provide a
        human-readable description of the field exposed at the schema level.
        Defaults to the per-Field definition.
        """

        self._attribute = attr
        self._field_name = None
        self._default = default

        if help_text:
            self.help_text = help_text

    def contribute_to_class(self, cls, name):
        pass

    def has_default(self):
        """Returns a boolean of whether this field has a default value."""
        return self._default is not None

    @property
    def default(self):
        """Returns the default value for the field."""
        if callable(self._default):
            return self._default()

        return self._default

    @property
    def attribute(self):
        return self._attribute

    @property
    def field_name(self):
        return self._field_name

    @field_name.setter
    def field_name(self, value):
        self._field_name = value

    def convert(self, value):
        """
        Handles conversion between the data found and the type of the field.

        Extending classes should override this method and provide correct
        data coercion.
        """
        return value

    def process(self, obj):
        """
        Takes data from the provided object and prepares it for the
        resource.
        """
        if self._attribute is not None:
            # Check for `__` in the field for looking through the relation.
            attrs = self._attribute.split('__')
            current_object = obj

            if isinstance(obj, dict):
                for attr in attrs:
                    current_object = current_object.get(attr, None)

                    if callable(current_object):
                        current_object = current_object()
            else:
                for attr in attrs:
                    current_object = getattr(current_object, attr, None)

                    if callable(current_object):
                        current_object = current_object()

            return current_object


class CharField(ApiField):
    """
    A text field of arbitrary length.
    """
    processed_type = 'string'
    help_text = 'Unicode string data. Ex: "Hello World"'

    def convert(self, value):
        if value is None:
            return None

        return unicode(value)


class FileField(ApiField):
    """
    A file-related field.
    """
    processed_type = 'string'
    help_text = 'A file URL as a string. Ex: ' \
        '"http://media.example.com/media/photos/my_photo.jpg"'

    def convert(self, value):
        if value is None:
            return None

        try:
            # Try to return the URL if it's a ``File``, falling back to the 
            # string itself if it's been overridden or is a default.
            return getattr(value, 'url', value)
        except ValueError:
            return None


class IntegerField(ApiField):
    """
    An integer field.
    """
    processed_type = 'integer'
    help_text = 'Integer data. Ex: 2673'

    def convert(self, value):
        if value is None:
            return None

        return int(value)


class FloatField(ApiField):
    """
    A floating point field.
    """
    processed_type = 'float'
    help_text = 'Floating point numeric data. Ex: 26.73'

    def convert(self, value):
        if value is None:
            return None

        return float(value)


class DecimalField(ApiField):
    """
    A decimal field.
    """
    processed_type = 'decimal'
    help_text = 'Fixed precision numeric data. Ex: 26.73'

    def convert(self, value):
        if value is None:
            return None

        return Decimal(value)


class BooleanField(ApiField):
    """
    A boolean field.
    """
    processed_type = 'boolean'
    help_text = 'Boolean data. Ex: True'

    def convert(self, value):
        if value is None:
            return None

        return bool(value)


class ListField(ApiField):
    """
    A list field.
    """
    processed_type = 'list'
    help_text = "A list of data. Ex: ['abc', 26.73, 8]"

    def convert(self, value):
        if value is None:
            return None

        return list(value)


class DictField(ApiField):
    """
    A dictionary field.
    """
    processed_type = 'dict'
    help_text = "A dictionary of data. Ex: {'price': 26.73, 'name': 'Daniel'}"

    def convert(self, value):
        if value is None:
            return None

        return dict(value)


class DateField(ApiField):
    """
    A date field.
    """
    processed_type = 'date'
    help_text = 'A date as a string. Ex: "2010-11-10"'

    def convert(self, value):
        if isinstance(value, basestring):
            match = DATE_REGEX.search(value)

            if match:
                data = match.groupdict()
                return datetime_safe.date(
                    int(data['year']), int(data['month']), int(data['day']))
            else:
                raise ApiFieldError(
                    "Date provided to '%s' field doesn't appear to be a " \
                    "valid date string: '%s'" % (self._field_name, value))

        return datetime_safe.date(value.year, value.month, value.day)


class TimeField(ApiField):
    processed_type = 'time'
    help_text = 'A time as string. Ex: "20:05:23"'

    def convert(self, dt):
        try:
            if isinstance(dt, basestring):
                dt = parse(dt)
        except ValueError:
            raise ApiFieldError(
                    "Time provided to '%s' field doesn't appear to be a " \
                    "valid time string: '%s'" % (self._field_name, dt))
        else:
            return datetime.time(dt.hour, dt.minute, dt.second)


class DateTimeField(ApiField):
    processed_type = 'datetime'
    help_text = 'A date & time as a string. Ex: "2010-11-10T03:07:43"'

    def convert(self, value):
        if isinstance(value, basestring):
            match = DATETIME_REGEX.search(value)

            if match:
                data = match.groupdict()
                return make_aware(datetime_safe.datetime(
                    int(data['year']), int(data['month']),
                    int(data['day']), int(data['hour']),
                    int(data['minute']), int(data['second'])))
            else:
                raise ApiFieldError(
                    "Datetime provided to '%s' field doesn't appear to be a " \
                    "valid datetime string: '%s'" % (
                        self._field_name, value))

        return make_aware(datetime_safe.datetime(
            value.year, value.month, value.day,
            value.hour, value.minute, value.second))


class EntityField(ApiField):
    processed_type = 'dict'

    def __init__(self, *args, **kwargs):
        self.entity_cls = kwargs.pop('entity_cls')
        super(EntityField, self).__init__(*args, **kwargs)

    def convert(self, value):
        if value is not None:
            return self.entity_cls(value).full_process()
