import re
from django import forms
from django.core.exceptions import ValidationError


def validate_degrees(value):
    pattern = '^\d\d? \d\d?\.\d\d?$'
    regex = re.compile(pattern)
    if regex.match(value) is None:
        raise ValidationError('Degrees input is wrong')

class NeoSubmitForm(forms.Form):
    
    name = forms.CharField()
    discovery_date = forms.DateField()
    right_ascension = forms.CharField(validators=[validate_degrees])
    declination = forms.CharField(validators=[validate_degrees])
    magnitude = forms.FloatField()
    arc = forms.FloatField()
    nominal_h = forms.FloatField()
    media = forms.FileField()