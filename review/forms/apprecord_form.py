from django.forms import ModelForm
from review.models import AppRecord


class AppRecordForm(ModelForm):

    class Meta:
        model = AppRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AppRecordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
