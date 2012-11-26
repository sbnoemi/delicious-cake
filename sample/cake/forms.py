from django import forms

from cake.models import Cake


class CakeForm(forms.ModelForm):
    id = forms.IntegerField(required=False)
    message = forms.CharField(max_length=128)
    cake_type = forms.TypedChoiceField(
        choices=Cake.CAKE_TYPE_CHOICES, coerce=int)

    class Meta(object):
        model = Cake
