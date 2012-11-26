import collections

from django.shortcuts import get_object_or_404

from delicious_cake.resources import (
    ListResource, DetailResource, ResourceResponse,)

from core.models import Cake
from core.forms import CakeForm

__all__ = ('BaseResourceMixin', 'BaseDetailResource', 'BaseListResource',)


class BaseResourceMixin(object):
    def get_obj(self, request, *args, **kwargs):
        return get_object_or_404(Cake, pk=kwargs['pk'])

    def _update_obj(self, obj, data, custom_pk=None):
        if custom_pk is not None:
            obj.pk = custom_pk

        obj.message = data['message']
        obj.cake_type = data['cake_type']

        obj.save()

        return obj

    def update_obj(self, obj, request, custom_pk=None, *args, **kwargs):
        cake_form = CakeForm(request.DATA)

        if cake_form.is_valid():
            return self._update_obj(
                obj, cake_form.cleaned_data, custom_pk=custom_pk)
        else:
            self.raise_validation_error(request, cake_form.errors)

    def _create_obj(self, request, *args, **kwargs):
        cake = Cake()
        self.update_obj(cake, request, *args, **kwargs)

        return cake

    def create_obj(self, request, *args, **kwargs):
        cake = Cake()
        self.update_obj(cake, request, *args, **kwargs)

        return cake


class BaseDetailResource(DetailResource, BaseResourceMixin):
    def _get(self, request, *args, **kwargs):
        return self.get_obj(request, *args, **kwargs)

    def _post(self, request, *args, **kwargs):
        cake = self.create_obj(request, *args, **kwargs)
        return cake, True

    def _put(self, request, *args, **kwargs):
        pk = kwargs['pk']

        try:
            cake = Cake.objects.get(pk=pk)
            self.update_obj(cake, request, *args, **kwargs)
            created = False
        except Cake.DoesNotExist:
            created = True
            cake = self.create_obj(request, custom_pk=pk, *args, **kwargs)

        return cake, created

    def _delete(self, request, *args, **kwargs):
        cake = get_object_or_404(Cake, pk=kwargs['pk'])
        cake.delete()
        return cake

    def _head(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)


class BaseListResource(ListResource, BaseResourceMixin):
    def _get(self, request, *args, **kwargs):
        return Cake.objects.all()

    def _head(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    def _put(self, request, *args, **kwargs):
        data = request.DATA

        if not isinstance(data, list):
            self.raise_http_error(request, 'Must be a list')

        cake_forms = []

        for cake in data:
            cake_form = CakeForm(cake)

            if not cake_form.is_valid():
                self.raise_http_error(request, 'Invalid Cake')

            cake_forms.append(cake_form)

        # Delete Old List
        Cake.objects.all().delete()

        # Create New List
        cakes = [self._update_obj(Cake(), cake_form.cleaned_data) \
                    for cake_form in cake_forms]

        return cakes

    def _post(self, request, *args, **kwargs):
        cake = self.create_obj(request, *args, **kwargs)
        return cake, True

    def _delete(self, request, *args, **kwargs):
        Cake.objects.all().delete()
