from django.conf.urls import patterns, include, url

from .resources import *


urlpatterns = patterns('',
    url(r'^simple/(?P<pk>\d+)/$', SimpleDetailResource.as_view(),
        name='simple-detail'),
    url(r'^simple/$', SimpleListResource.as_view(),
        name='simple-list'),

    url(r'^forced/simple/(?P<pk>\d+)/$', ForcedSimpleDetailResource.as_view(),
        name='forced-simple-detail'),
    url(r'^forced/simple/$', ForcedSimpleListResource.as_view(),
        name='forced-simple-list'),

    url(r'^bare/simple/(?P<pk>\d+)/$', ForcedSimpleDetailResource.as_view(),
        name='bare-simple-detail'),
    url(r'^bare/simple/$', ForcedSimpleListResource.as_view(),
        name='bare-simple-list'),

    url(r'^custom/simple/(?P<pk>\d+)/$',
        CustomEntityDetailResource.as_view(),
        name='custom-entity-detail'),
    url(r'^custom/simple/$', CustomEntityListResource.as_view(),
        name='custom-entity-list'),

    url(r'^unimplemented/(?P<pk>\d+)/$', UnimplementedDetailResource.as_view(),
        name='unimplemented-detail'),
    url(r'^unimplemented/$', UnimplementedListResource.as_view(),
        name='unimplemented-list'),

    url(r'^empty/(?P<pk>\d+)/$', EmptyDetailResource.as_view(),
        name='empty-detail'),
    url(r'^empty/$', EmptyListResource.as_view(), name='empty-list'),

    url(r'^custom/create/$', CustomCreateListResource.as_view(),
        name='custom-create-detail'),

    url(r'^upload/$', CakeUploadResource.as_view(),
        name='upload-resource'),)
