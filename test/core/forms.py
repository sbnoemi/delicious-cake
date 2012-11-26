from django import forms

from core.models import Cake


class CakeForm(forms.Form):
    message = forms.CharField(max_length=128)
    cake_type = forms.TypedChoiceField(
        choices=Cake.CAKE_TYPE_CHOICES, coerce=int)


class CakeUploadForm(forms.Form):
    cake_pattern = forms.FileField()
