from delicious_cake.test import ResourceTestCase

__all__ = ('UnimplementedResourceTestCase',)


HTTP_METHODS = ['get', 'head', 'post', 'put', 'delete', 'options']


class UnimplementedResourceTestCase(ResourceTestCase):
    def _test_unimplemented_resource(self, uri):
        for method in HTTP_METHODS:
            method_attr = getattr(self.client, method)
            response = method_attr(uri)

            if method is not 'options':
                self.assertHttpMethodNotAllowed(response)
            else:
                self.assertHttpOK(response)

    def test_unimplemented_list_resource(self):
        self._test_unimplemented_resource('/unimplemented/')

    def test_unimplemented_detail_resource(self):
        self._test_unimplemented_resource('/unimplemented/1/')
