from delicious_cake.test import ResourceTestCase

from core.models import Cake

__all__ = ('EmptyResourceTestCase',)


BIRTHDAY_MESSAGE = u"You're another year closer to death!"


class EmptyResourceTestCase(ResourceTestCase):
    fixtures = ['test_data.json']

    def test_empty_detail_resource(self):
        # Test GET
        response = self.api_client.get('/empty/1/')
        self.assertHttpNoContent(response)

        # Test GET 404
        response = self.api_client.get('/empty/404/')
        self.assertHttpNotFound(response)

        # Test HEAD
        response = self.api_client.head('/empty/1/')
        self.assertHttpNoContent(response)

        #### POST ####
        response = self.api_client.post('/empty/2/', data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})
        self.assertHttpNoContent(response)

        # Test Bad POST
        response = self.api_client.post('/empty/2/', data={
            'ct': Cake.CAKE_TYPE_BIRTHDAY, 'm': BIRTHDAY_MESSAGE})
        self.assertHttpBadRequest(response)

        # Test PUT update
        cake = Cake.objects.get(pk=3)
        self.assertEquals(cake.message, u'Cake 3')

        response = self.api_client.put('/empty/3/', data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})

        cake = Cake.objects.get(pk=3)

        self.assertEquals(cake.message, BIRTHDAY_MESSAGE)

        # Test PUT create
        response = self.api_client.put('/empty/100000/', data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})
        self.assertHttpNoContent(response)

        response = self.api_client.get('/empty/100000/')
        self.assertHttpNoContent(response)

        # Test Bad PUT
        response = self.api_client.post('/empty/2/', data={
            'ct': Cake.CAKE_TYPE_BIRTHDAY, 'm': BIRTHDAY_MESSAGE})
        self.assertHttpBadRequest(response)

        # Test DELETE
        response = self.api_client.delete('/empty/100000/')
        self.assertHttpNoContent(response)

        # Test DELETE with 404
        response = self.api_client.delete('/empty/100000/')
        self.assertHttpNotFound(response)

    def test_empty_list_resource(self):
        # Test GET
        response = self.api_client.get('/empty/')
        self.assertHttpNoContent(response)

        # Test HEAD
        response = self.api_client.head('/empty/')
        self.assertHttpNoContent(response)

        # Test POST
        response = self.api_client.post('/empty/', data={
            'cake_type': Cake.CAKE_TYPE_BIRTHDAY, 'message': BIRTHDAY_MESSAGE})

        self.assertHttpNoContent(response)
        self.assertEqual(51, Cake.objects.all().count())

        # Test PUT
        data = [
            {'cake_type': Cake.CAKE_TYPE_BIRTHDAY,
                'message': BIRTHDAY_MESSAGE},
            {'cake_type': Cake.CAKE_TYPE_GRADUATION,
                'message': BIRTHDAY_MESSAGE},
            {'cake_type': Cake.CAKE_TYPE_SCHADENFREUDE,
                'message': BIRTHDAY_MESSAGE}]

        response = self.api_client.put('/empty/', data=data)

        self.assertHttpNoContent(response)
        self.assertEqual(3, Cake.objects.all().count())

        # Test Delete
        response = self.api_client.delete('/empty/')

        self.assertHttpNoContent(response)
        self.assertEqual(0, Cake.objects.all().count())
