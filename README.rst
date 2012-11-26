===============
Delicious Cake
===============

Delicious Cake is a flexible, Tastypie derived, REST framework for Django.

Over the years I've used both Tastypie and Piston to create RESTful APIs.  While they both have their advantages neither is as flexible as plain old Django views.  


Why Delicious Cake?
===================

Delicious Cake is a framework that removes much of the pain of creating RESTful APIs, without imposing many constraints. 


How is this different from Tastypie?
====================================

Tastypie makes taking your models and quickly exposing them in a RESTful manner extremely easy.  Unfortunately, that's not often the best way to expose an api.  Some functionality is simply difficult to express within Tastypie's constraints.

Tastypie resources tightly couple several features:  List views, detail views, data hydration/dehydration, url construction, and pre-serialization processing of objects.  For simple APIs this can reduce the amount of code necessary to get your project off the ground.  As your project evolves it can become increasingly difficult to express your ideal API with Tastypie.

Delicious Cake is an attempt to take the best of Tastypie and present it in a more flexible form.


This is an experiment 
=====================

I want to get this out quickly to see if there is any interest in this model of API development.  

Both tests and documentation are sparse.  If there's enough interest, test coverage and documentation will become a priority.

Let me know what you think!

mike@theitemshoppe.com
