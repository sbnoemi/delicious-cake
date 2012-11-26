from delicious_cake.test import ResourceTestCase

from core.models import Cake

__all__ = ('SimpleResourceTestCase',)


BIRTHDAY_MESSAGE = u"You're another year closer to death!"


class SimpleResourceTestCase(ResourceTestCase):
    fixtures = ['test_data.json']

    simple_detail_get_entity = {
        'resource_uri': u'/simple/1/',
        'message': u'Cake 1',
        'cake_type': u'Birthday Cake',
        'resource_id': 1}

    def _test_detail_resource(self, resource):
        # Test GET
        response = self.api_client.get('/%s/1/' % resource)
        self.assertHttpOK(response)

        self.assertEqual(
            self.simple_detail_get_entity, self.deserialize(response))

        # Test GET 404
        response = self.api_client.get('/%s/404/' % resource)
        self.assertHttpNotFound(response)

        # Test HEAD
        response = self.api_client.head('/%s/1/' % resource)
        self.assertHttpOK(response)

        #### POST ####
        response = self.api_client.post('/%s/2/' % resource, data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})
        self.assertHttpCreated(response)

        entity = self.deserialize(response)

        self.assertEqual(BIRTHDAY_MESSAGE, entity['message'])

        self.assertTrue(
            response['Location'].endswith(entity['resource_uri']))

        # Test Bad POST
        response = self.api_client.post('/%s/2/' % resource, data={
            'ct': Cake.CAKE_TYPE_BIRTHDAY, 'm': BIRTHDAY_MESSAGE})
        self.assertHttpBadRequest(response)

        # Test PUT update
        cake = Cake.objects.get(pk=3)
        self.assertEquals(cake.message, u'Cake 3')

        response = self.api_client.put('/%s/3/' % resource, data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})

        cake = Cake.objects.get(pk=3)

        self.assertEquals(cake.message, BIRTHDAY_MESSAGE)

        # Test PUT create
        response = self.api_client.put('/%s/100000/' % resource, data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})

        self.assertHttpCreated(response)

        response = self.api_client.get('/%s/100000/' % resource)
        self.assertHttpOK(response)

        # Test Bad PUT
        response = self.api_client.post('/%s/2/' % resource, data={
            'ct': Cake.CAKE_TYPE_BIRTHDAY, 'm': BIRTHDAY_MESSAGE})
        self.assertHttpBadRequest(response)

        # Test DELETE
        response = self.api_client.delete('/%s/100000/' % resource)
        self.assertHttpNoContent(response)

        # Test DELETE with 404
        response = self.api_client.delete('/%s/100000/' % resource)
        self.assertHttpNotFound(response)

        # Test DELETE with entity in response

    def _test_list_resource(self, resource):
        # Test GET
        response = self.api_client.get('/%s/' % resource)

        self.assertHttpOK(response)
        self.assertEqual(20, len(self.deserialize(response)['objects']))

        # Test HEAD
        response = self.api_client.head('/%s/' % resource)
        self.assertHttpOK(response)

        # Test POST
        response = self.api_client.post('/%s/' % resource, data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})

        self.assertHttpCreated(response)

        # Test PUT
        data = [
            {'cake_type': Cake.CAKE_TYPE_BIRTHDAY,
                'message': BIRTHDAY_MESSAGE},
            {'cake_type': Cake.CAKE_TYPE_GRADUATION,
                'message': BIRTHDAY_MESSAGE},
            {'cake_type': Cake.CAKE_TYPE_SCHADENFREUDE,
                'message': BIRTHDAY_MESSAGE}]

        response = self.api_client.put('/%s/' % resource, data=data)

        self.assertHttpOK(response)

        response = self.api_client.get('/%s/' % resource)

        self.assertHttpOK(response)
        self.assertEqual(3, len(self.deserialize(response)['objects']))

        # Test Delete
        response = self.api_client.delete('/%s/' % resource)
        self.assertHttpNoContent(response)

        response = self.api_client.get('/%s/' % resource)

        self.assertHttpOK(response)
        self.assertEqual(0, len(self.deserialize(response)['objects']))

    def test_simple_detail_resource(self):
        self._test_detail_resource('simple')

    def test_simple_list_resource(self):
        self._test_list_resource('simple')

    def test_forced_simple_detail_resource(self):
        self._test_detail_resource('forced/simple')

    def test_forced_simple_list_resource(self):
        self._test_list_resource('forced/simple')

    def test_bare_simple_detail_resource(self):
        self._test_detail_resource('bare/simple')

    def test_bare_simple_list_resource(self):
        self._test_list_resource('bare/simple')

    def test_custom_simple_detail_resource(self):
        self._test_detail_resource('custom/simple')

    def test_custom_simple_list_resource(self):
        self._test_list_resource('custom/simple')
