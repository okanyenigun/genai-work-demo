from django import forms
from django.forms import ModelForm
from review.models import AiModels


class AiModelForm(ModelForm):

    class Meta:
        model = AiModels
        fields = ["name", "source", "language_support"]

    def __init__(self, *args, **kwargs):
        super(AiModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
