from delicious_cake import fields
from delicious_cake.entities import Entity
from delicious_cake.resources import UploadResource
from delicious_cake.response import ResourceResponse

from core.forms import CakeUploadForm

__all__ = ('CakeUploadResource',)


class CakeUploadResource(UploadResource):
    def _put_post(self, request, *args, **kwargs):
        cake_form = CakeUploadForm(files=request.FILES)

        if not cake_form.is_valid():
            self.raise_validation_error(request, cake_form.errors)

    def post(self, request, *args, **kwargs):
        return self._put_post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self._put_post(request, *args, **kwargs)
