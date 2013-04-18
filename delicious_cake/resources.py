import sys
import logging
import traceback
import collections

import django
from django.conf import settings

from django.db import models
from django.views.generic import View
from django import http as django_http
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from delicious_cake import http as cake_http
from delicious_cake.response import ResourceResponse
from delicious_cake.utils import (
    determine_format, build_content_type, is_valid_jsonp_callback_value,)
from delicious_cake.options import DetailResourceOptions, ListResourceOptions

from delicious_cake.exceptions import (
    ImmediateHttpResponse, BadRequest,
    UnsupportedSerializationFormat, UnsupportedDeserializationFormat,
    WrongNumberOfValues, ResourceEntityError, ValidationError,)

__all__ = ('Resource', 'DetailResource', 'ListResource', 'MultipartResource',)


log = logging.getLogger('django.request.delicious_cake')

NOT_FOUND_EXCEPTIONS = (ObjectDoesNotExist, django_http.Http404,)


class BaseResourceMetaClass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(BaseResourceMetaClass, cls).__new__(
            cls, name, bases, attrs)

        opts = getattr(new_class, 'Meta', None)
        new_class._meta = cls.options_cls(name, opts)

        return new_class


class DetailResourceMetaClass(BaseResourceMetaClass):
    options_cls = DetailResourceOptions


class ListResourceMetaClass(BaseResourceMetaClass):
    options_cls = ListResourceOptions


class Resource(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            method = request.method.lower()

            if method in self.http_method_names and hasattr(self, method):
                handler = getattr(
                    self, 'dispatch_%s' % method, self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            self.is_authenticated(request)
            self.is_authorized(request)
            self.throttle_check(request)

            self.request = request
            self.args = args
            self.kwargs = kwargs

            try:
                response = self.dispatch_any(request, handler, *args, **kwargs)
            except ValidationError, e:
                # Catch ValidationError here for non-resources can throw them.
                self.raise_validation_error(request, e.form_errors)

        except ImmediateHttpResponse, e:
            if e.response is not None:
                response = e.response
            else:
                desired_format = self.determine_format(request)

                response_kwargs = e.response_kwargs
                response_kwargs['content_type'] = response_kwargs.get(
                    'content_type', build_content_type(desired_format))

                response = e.response_cls(**response_kwargs)
        except Exception, e:
            response = self.handle_exception(request, e)

        self.log_throttled_access(request)

        if not isinstance(response, cake_http.HttpResponse):
            return cake_http.HttpNoContent()

        return response

    def is_authenticated(self, request):
        auth_result = self._meta.authentication.is_authenticated(request)

        if isinstance(auth_result, cake_http.HttpResponse):
            raise ImmediateHttpResponse(response=auth_result)

        if auth_result is False:
            self.raise_authorization_error()

    def is_authorized(self, request, obj=None):
        auth_result = self._meta.authorization.is_authorized(request, obj)

        if isinstance(auth_result, cake_http.HttpResponse):
            raise ImmediateHttpResponse(response=auth_result)

        if auth_result is False:
            self.raise_authorization_error()

    def throttle_check(self, request):
        identifier = self._meta.authentication.get_identifier(request)

        if self._meta.throttle.should_be_throttled(identifier):
            raise ImmediateHttpResponse(
                response_cls=cake_http.HttpTooManyRequests)

    def log_throttled_access(self, request):
        request_method = request.method.lower()
        self._meta.throttle.accessed(
            self._meta.authentication.get_identifier(request),
            url=request.get_full_path(), request_method=request_method)
            
    def dispatch_any(self, request, handler, *args, **kwargs):
        """
        Hook for custom exception handling
        """
        return handler(request, *args, **kwargs)

    def dispatch_get(self, request, *args, **kwargs):
        raise NotImplementedError

    def dispatch_head(self, request, *args, **kwargs):
        raise NotImplementedError

    def dispatch_post(self, request, *args, **kwargs):
        return self.dispatch_creation(self.post, request, *args, **kwargs)

    def dispatch_put(self, request, *args, **kwargs):
        raise NotImplementedError

    def dispatch_delete(self, request, *args, **kwargs):
        raise NotImplementedError

    def dispatch_options(self, request, *args, **kwargs):
        return self.options(request, *args, **kwargs)

    def dispatch_method(self, method, request,
                        wrap_response=True, *args, **kwargs):
        self.process_body(request)
        resource_resp = method(request, *args, **kwargs)

        self.raise_if_http_response(resource_resp)

        if wrap_response and resource_resp is not None and \
                not isinstance(resource_resp, ResourceResponse):
            resource_resp = ResourceResponse(resource_resp)

        return resource_resp

    def dispatch_creation(self, method, request, *args, **kwargs):
        # Expected to be in the form of one of the following:
        # 0.  None
        # 1.  ResourceResponse
        # 2.  ResourceResponse, created (bool)
        # 3.  Object
        # 4.  Object, created (bool)
        ret = self.dispatch_method(
            method, request, wrap_response=False, *args, **kwargs)
        created = False

        if isinstance(ret, ResourceResponse):
            resp = ret
        elif isinstance(ret, collections.Iterable):
            if len(ret) == 2:
                resp = ret[0]

                if resp is not None:
                    created = ret[1]
                    if not isinstance(resp, ResourceResponse):
                        resp = ResourceResponse(resp)
            else:
                raise WrongNumberOfValues('Must return 1 or 2 values')
        elif ret is not None:
            resp = ResourceResponse(ret)
        else:
            resp = None

        if resp is not None:
            return self.create_http_response(request, resp, created=created)

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = cake_http.HttpResponse()
        response['Allow'] = ', '.join(self.allowed_methods)
        response['Content-Length'] = '0'
        return response

    @property
    def allowed_methods(self):
        return [m for m in self.http_method_names if hasattr(self, m)]

    def raise_if_http_response(self, potential_response):
        if isinstance(potential_response, cake_http.HttpResponse):
            raise ImmediateHttpResponse(response=potential_response)

    def handle_exception(self, request, exception):
        desired_format = self.determine_format(request)
        content_type = build_content_type(desired_format)

        if isinstance(exception, NOT_FOUND_EXCEPTIONS):
            response = cake_http.HttpNotFound(content_type=content_type)
        elif isinstance(exception, UnsupportedSerializationFormat):
            response = cake_http.HttpNotAcceptable(content_type=content_type)
        elif isinstance(exception, UnsupportedDeserializationFormat):
            response = cake_http.HttpUnsupportedMediaType(
                content_type=content_type)
        elif isinstance(exception, MultipleObjectsReturned):
            response = cake_http.HttpMultipleChoices(content_type=content_type)
        elif isinstance(exception, BadRequest):
            response = cake_http.HttpBadRequest(exception.message)
        else:
            if settings.DEBUG:
                data = {
                    'error_message': unicode(exception),
                    'traceback': '\n'.join(
                        traceback.format_exception(*(sys.exc_info())))}
            else:
                data = {
                    'error_message': getattr(
                        settings, 'DELICIOUS_CAKE_CANNED_ERROR',
                        'Sorry, this request could not be processed.  ' \
                        'Please try again later.')}

            response = cake_http.HttpApplicationError(
                content=self.serialize(request, data, desired_format),
                content_type=content_type, status=500)

        if settings.DEBUG or response.status_code == 500:
            log.error('Server Error: %s' % request.path,
                exc_info=sys.exc_info(), extra={'request': request})

            # SEND ERROR NOTIFICATIONS HERE!

        return response

    def process_body(self, request):
        # Deprecated, use request.body going forward
        if request.raw_post_data:
            request.DATA = self.deserialize(
                request, request.raw_post_data,
                format=request.META.get('CONTENT_TYPE', 'application/json'))
        else:
            request.DATA = {}

    def determine_format(self, request):
        return determine_format(
            request, self._meta.serializer,
            default_format=self._meta.default_format)

    def serialize(self, request, data, format, options={}):
        options = options or {}

        if 'text/javascript' in format:
            # get JSONP callback name. default to "callback"
            callback = request.GET.get('callback', 'callback')

            if not is_valid_jsonp_callback_value(callback):
                raise BadRequest('JSONP callback name is invalid.')

            options['callback'] = callback
        return self._meta.serializer.serialize(data, format, options)

    def deserialize(self, request, data, format):
        return self._meta.serializer.deserialize(data, format)

    def raise_validation_error(self, request, errors):
        self.raise_coded_error(request, 'VALIDATION_ERROR', errors)

    def raise_coded_error(self, request, code, errors, errors_extra=None,
                          response_cls=cake_http.HttpBadRequest):
        errors = {'code': code, 'errors': errors}

        if errors_extra is not None:
            errors.update(errors_extra)

        self.raise_http_error(request, errors, response_cls=response_cls)

    def raise_http_error(self, request, error,
                         response_cls=cake_http.HttpBadRequest):
        if request:
            desired_format = self.determine_format(request)
        else:
            desired_format = self._meta.default_format

        response = response_cls(
            content_type=build_content_type(desired_format),
            content=self.serialize(request, error, desired_format))

        raise ImmediateHttpResponse(response=response)

    def raise_authorization_error(self):
        raise ImmediateHttpResponse(response_cls=cake_http.HttpUnauthorized)

    def _get_include_entity(self, resource_response, force_include_entity):
        if force_include_entity:
            return True
        elif resource_response.include_entity is not None:
            return resource_response.include_entity

        return self._meta.include_entity

    def get_http_response_details(self, resource_response, entity,
                                  include_entity, default_response_cls,
                                  default_response_kwargs):
        response_cls = resource_response.get_response_cls()

        if response_cls is not None:
            response_kwargs = resource_response.get_response_kwargs(entity)
        else:
            if default_response_cls is not None:
                response_cls = default_response_cls
                response_kwargs = default_response_kwargs
            else:
                response_kwargs = {}
                response_cls = cake_http.HttpResponse \
                    if include_entity else cake_http.HttpNoContent

        return response_cls, response_kwargs

    def _process_http_response(self, request, http_response, obj):
        if hasattr(self, 'process_http_response'):
            self.process_http_response(http_response, obj)

        method_response_processor = getattr(
            self, 'process_http_response_%s' % request.method.lower(), None)

        if method_response_processor is not None:
            method_response_processor(http_response, obj)

    def create_http_response(self, request, resource_response,
                             created=False, force_include_entity=None,
                             default_response_cls=None,
                             **default_response_kwargs):
        if resource_response is None:
            return

        include_entity = self._get_include_entity(
            resource_response, force_include_entity)

        entity_cls = resource_response.get_entity_cls(
            self._meta.get_detail_entity_cls())

        if resource_response.obj is None:
            if created or include_entity:
                raise ResourceEntityError(
                    "'ResourceResponse.obj' must not be None if 'created'" \
                    " or 'include_entity' is True")
            entity = None
        else:
            if entity_cls is None:
                raise ResourceEntityError(
                    "Must specify 'entity_cls' or 'detail_entity_cls' if" \
                    " 'created' or 'include_entity' is True")

            entity = entity_cls(resource_response.obj)

        if created:
            http_response_cls = cake_http.HttpCreated
            http_response_kwargs = {'location': entity.get_resource_uri()}
        else:
            http_response_cls, http_response_kwargs = \
                self.get_http_response_details(
                    resource_response, entity, include_entity,
                    default_response_cls, default_response_kwargs)

        desired_format = self.determine_format(request)

        content = '' if entity is None or include_entity is False else \
            self.serialize(request, entity.full_process(), desired_format)

        http_response = http_response_cls(
            content=content, content_type=build_content_type(desired_format),
            **http_response_kwargs)

        self._process_http_response(request, http_response, entity)

        return http_response

    def head_impl(self, request, *args, **kwargs):
        if hasattr(self, 'get'):
            return self.get(request, *args, **kwargs)


class DetailResource(Resource):
    __metaclass__ = DetailResourceMetaClass

    def dispatch_get(self, request, *args, **kwargs):
        return self.create_http_response(request,
            self.dispatch_method(self.get, request, *args, **kwargs),
            force_include_entity=True)

    def dispatch_head(self, request, *args, **kwargs):
        return self.create_http_response(request,
            self.dispatch_method(self.head, request, *args, **kwargs),
            default_response_cls=cake_http.HttpResponse,
            force_include_entity=False)

    def dispatch_put(self, request, *args, **kwargs):
        return self.dispatch_creation(self.put, request, *args, **kwargs)

    def dispatch_delete(self, request, *args, **kwargs):
        return self.create_http_response(request,
            self.dispatch_method(self.delete, request, *args, **kwargs))


class ListResource(Resource):
    __metaclass__ = ListResourceMetaClass

    def dispatch_get(self, request, *args, **kwargs):
        return self.create_http_list_response(
            request, self.dispatch_method(self.get, request, *args, **kwargs),
            paginated=True, force_include_entity=True)

    def dispatch_head(self, request, *args, **kwargs):
        return self.create_http_list_response(request,
            self.dispatch_method(self.head, request, *args, **kwargs),
            paginated=True, force_include_entity=False,
            default_response_cls=cake_http.HttpResponse)

    def dispatch_put(self, request, *args, **kwargs):
        return self.create_http_list_response(request,
            self.dispatch_method(self.put, request, *args, **kwargs))

    def dispatch_delete(self, request, *args, **kwargs):
        return self.create_http_list_response(request,
            self.dispatch_method(self.delete, request, *args, **kwargs))

    def create_http_list_response(self, request, resource_response,
                                  paginated=False, force_include_entity=None,
                                  default_response_cls=None,
                                  **default_response_kwargs):
        if resource_response is None:
            return

        include_entity = self._get_include_entity(
            resource_response, force_include_entity)

        entity_cls = resource_response.get_entity_cls(
            self._meta.get_detail_entity_cls())

        if entity_cls is None and include_entity:
            raise ResourceEntityError(
                "Must specify 'entity_cls', 'list_entity_cls', or " \
                "'detail_entity_cls' if 'include_entity' is True")

        obj = resource_response.obj

        if obj is None:
            entities = []
        elif not isinstance(obj, collections.Iterable):
            entities = [obj]
        else:
            entities = obj

        if paginated:
            paginator = self._meta.paginator_cls(
                request.GET, entities, resource_uri=self.get_resource_uri(),
                limit=self._meta.limit, max_limit=self._meta.max_limit,
                collection_name=self._meta.collection_name)

            page = paginator.page()
            entities = page[self._meta.collection_name]
        else:
            page = {}
            page[self._meta.collection_name] = entities

        http_response_cls, http_response_kwargs = \
            self.get_http_response_details(
                resource_response, entities, include_entity,
                default_response_cls, default_response_kwargs)

        desired_format = self.determine_format(request)

        if include_entity:
            entities = [entity_cls(obj).full_process() for obj in entities]
            page[self._meta.collection_name] = entities
            content = self.serialize(request, page, desired_format)
        else:
            content = ''
            entities = None

        http_response = http_response_cls(
            content=content, content_type=build_content_type(desired_format),
            **http_response_kwargs)

        self._process_http_response(request, http_response, entities)

        return http_response

    def get_resource_uri(self):
        raise NotImplementedError


class MultipartResource(DetailResource):
    def convert_post_to_VERB(self, request, verb):
        if request.method == verb:
            if hasattr(request, '_post'):
                del(request._post)
                del(request._files)

            try:
                request.method = 'POST'
                request._load_post_and_files()
                request.method = verb
            except AttributeError:
                request.META['REQUEST_METHOD'] = 'POST'
                request._load_post_and_files()
                request.META['REQUEST_METHOD'] = verb

            setattr(request, verb, request.POST)

    def convert_post_to_put(self, request):
        return self.convert_post_to_VERB(request, verb='PUT')

    def deserialize(self, request, data, format=None):
        self.convert_post_to_put(request)

        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(MultipartResource, self).deserialize(
            request, data, format)
