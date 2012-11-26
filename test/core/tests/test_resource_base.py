from django.http import HttpRequest

from delicious_cake.resources import Resource
from delicious_cake.test import ResourceTestCase

from core.models import Cake
from core.entities import CakeListEntity, CakeDetailEntity

from core.resources import (
    UnimplementedListResource, UnimplementedDetailResource,
    SimpleListResource,)

__all__ = ('BaseResourceTestCase',)


BIRTHDAY_MESSAGE = u"You're another year closer to death!"


class BaseResourceTestCase(ResourceTestCase):
    fixtures = ['test_data.json']

    def test_determine_format(self):
        request = HttpRequest()
        resource = UnimplementedDetailResource()

        # Default.
        self.assertEqual(
            resource.determine_format(request), 'application/json')

        # Test forcing the ``format`` parameter.
        request.GET = {'format': 'json'}
        self.assertEqual(
            resource.determine_format(request), 'application/json')

        request.GET = {'format': 'jsonp'}
        self.assertEqual(resource.determine_format(request), 'text/javascript')

        request.GET = {'format': 'xml'}
        self.assertEqual(resource.determine_format(request), 'application/xml')

        request.GET = {'format': 'yaml'}
        self.assertEqual(resource.determine_format(request), 'text/yaml')

        request.GET = {'format': 'foo'}
        self.assertEqual(
            resource.determine_format(request), 'application/json')

        # Test the ``Accept`` header.
        request.META = {'HTTP_ACCEPT': 'application/json'}
        self.assertEqual(
            resource.determine_format(request), 'application/json')

        request.META = {'HTTP_ACCEPT': 'text/javascript'}
        self.assertEqual(resource.determine_format(request), 'text/javascript')

        request.META = {'HTTP_ACCEPT': 'application/xml'}
        self.assertEqual(resource.determine_format(request), 'application/xml')

        request.META = {'HTTP_ACCEPT': 'text/yaml'}
        self.assertEqual(resource.determine_format(request), 'text/yaml')

        request.META = {'HTTP_ACCEPT': 'text/html'}
        self.assertEqual(resource.determine_format(request), 'text/html')

        request.META = {
            'HTTP_ACCEPT': 'application/json,application/xml;q=0.9,*/*;q=0.8'}
        self.assertEqual(
            resource.determine_format(request), 'application/json')

        request.META = {
            'HTTP_ACCEPT': \
                'text/plain,application/xml,application/json;q=0.9,*/*;q=0.8'}
        self.assertEqual(resource.determine_format(request), 'application/xml')

    def test_jsonp_validation(self):
        resp = self.api_client.get('/simple/1/?format=jsonp&callback=()')

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, 'JSONP callback name is invalid.')

        # valid JSONP callback should work
        resp = self.api_client.get(
            '/simple/1/?format=jsonp&callback=myCallback')

        self.assertEqual(resp.status_code, 200)

    def test_get_entity_cls(self):
        simple_list_resource = SimpleListResource()
        un_list_resource = UnimplementedListResource()
        un_detail_resource = UnimplementedDetailResource()

        self.assertEqual(
            CakeListEntity, simple_list_resource._meta.get_list_entity_cls())
        self.assertEqual(
            CakeDetailEntity,
            simple_list_resource._meta.get_detail_entity_cls())

        self.assertEqual(
            CakeDetailEntity, un_detail_resource._meta.get_detail_entity_cls())

        self.assertEqual(
            CakeListEntity, un_list_resource._meta.get_list_entity_cls())
        self.assertEqual(
            CakeListEntity, un_list_resource._meta.get_detail_entity_cls())

