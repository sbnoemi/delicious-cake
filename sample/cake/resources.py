from django.db import models
from django.shortcuts import get_object_or_404

from delicious_cake import http
from delicious_cake.resources import (
    ListResource, DetailResource, ResourceResponse,)
from delicious_cake.exceptions import ValidationError

from cake.models import Cake
from cake.forms import CakeForm
from cake.entities import CakeListEntity, CakeDetailEntity

__all__ = ('CakeDetailResource', 'CakeListResource', 'CakeListResourceExtra',)


class CakeListResource(ListResource):
    '''A simple list view'''
    def get(self, request, *args, **kwargs):
        return Cake.objects.all()

    def head(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        cake_form = CakeForm(request.DATA)

        if not cake_form.is_valid():
            raise ValidationError(cake_form.errors)

        # Return the newly created instance and indicate that 
        # HTTP 201 CREATED should be used in the response.

        # return object, created (boolean)
        return cake_form.save(), True

    def delete(self, request, *args, **kwargs):
        Cake.objects.all().delete()

    # Used to get the base uri when paginating.   
    @models.permalink
    def get_resource_uri(self):
        return ('cake-list',)

    class Meta(object):
        # See delicious_cake/options.py for more 'Resource' options.

        # 'Entity' classes are used to pre-process objects before 
        # serialization.        

        # The 'list_entity_cls' will be used to pre-process the returned 
        # objects when viewed as a list.
        list_entity_cls = CakeListEntity

        # The 'detail_entity_cls' will be used to pre-process the returned 
        # objects when returned individually.        
        detail_entity_cls = CakeDetailEntity

        # If the same representation of the object is used in both list and 
        # details views the 'entity_cls' option can be used
        # (e.g.  entity_cls = CakeDetailEntity) 


class CakeDetailResource(DetailResource):
    '''A simple detail view'''
    def get(self, request, *args, **kwargs):
        return get_object_or_404(Cake, pk=kwargs['pk'])

    def put(self, request, *args, **kwargs):
        pk = kwargs['pk']

        try:
            created = False
            instance = Cake.objects.get(pk=pk)
        except Cake.DoesNotExist:
            created = True
            instance = Cake(id=pk)

        cake_form = CakeForm(request.DATA, instance=instance)

        if not cake_form.is_valid():
            raise ValidationError(cake_form.errors)

        # Return the newly created instance and indicate that 
        # HTTP 201 CREATED should be used in the response.
        # OR
        # Return the updated instance with HTTP 200 OK
        return cake_form.save(), created

    def delete(self, request, *args, **kwargs):
        get_object_or_404(Cake, pk=kwargs['pk']).delete()

    def head(self, request, *args, **kwargs):
        return self.get(self, request, *args, **kwargs)

    class Meta(object):
        detail_entity_cls = CakeDetailEntity


class CakeListResourceExtra(ListResource):
    # Add a response header to all responses.
    def process_http_response(self, http_response, entities):
        http_response['X-The-Cake-Is-A-Lie'] = False

    # Add a response header to all GET responses.
    def process_http_response_get(self, http_response, entities):
        http_response['X-Cake-Count'] = len(entities)

    def get(self, request, *args, **kwargs):
        # Tell the resource to use the 'CakeDetailEntity' instead of the 
        # default ('CakeListEntity' in this case) by specifying 'entity_cls'.
        return ResourceResponse(
           Cake.objects.all(), entity_cls=CakeDetailEntity)

    def post(self, request, *args, **kwargs):
        cake_form = CakeForm(request.DATA)

        if not cake_form.is_valid():
            raise ValidationError(cake_form.errors)

        cake = cake_form.save()

        # You can return 'ResourceResponse's if you need to 
        # use a custom 'HttpResponse' class or pass in specific parameters to 
        # the 'HttpResponse' class's constructor.  

        # For example, in this method we want to return an HTTP 201 (CREATED) 
        # response, with the newly created cake's uri in 'Location' header.  
        # To do this we set the 'response_cls' argument to 'http.HttpCreated' 
        # and add a 'location' key to 'response_kwargs' dict.  

        # This is equilivant to returning "cake_form.save(), created"

        # In this case, the value passed into the location parameter of our 
        # 'HttpCreated' response will be  a callable.  When invoked it will be 
        # passed one parameter, the entity created from our cake object.

        # And, just for fun, let's set 'include_entity' to False.

        # So again, we'll return HTTP 201 (CREATED), with a Location header,
        # the X-The-Cake-Is-A-Lie header, and no entity body.

        return ResourceResponse(
            include_entity=False,
            response_cls=http.HttpAccepted,
            response_kwargs={
                'location': lambda entity: entity.get_resource_uri()})

    @models.permalink
    def get_resource_uri(self):
        return ('cake-list-extra',)

    class Meta(object):
        entity_cls = CakeListEntity
