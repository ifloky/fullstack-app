from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class MonthsForm(forms.Form):
    months = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'),
              ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
              ('10', 'October'), ('11', 'November'), ('12', 'December'), ]
    month = forms.ChoiceField(choices=months, label='')

    def __init__(self, *args, **kwargs):
        super(MonthsForm, self).__init__(*args, **kwargs)
        self.fields['month'].initial = '08'
        self.fields['month'].widget.attrs['class'] = 'form-control'
        self.fields['month'].widget.attrs['label'] = 'Month:'
        self.fields['month'].widget.attrs['id'] = 'month'
        self.fields['month'].widget.attrs['name'] = 'month'


class YearsForm(forms.Form):
    years = [('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ]
    year = forms.ChoiceField(choices=years, label='')

    def __init__(self, *args, **kwargs):
        super(YearsForm, self).__init__(*args, **kwargs)
        self.fields['year'].initial = '2022'
        self.fields['year'].widget.attrs['class'] = 'form-control'
        self.fields['year'].widget.attrs['label'] = 'Year:'
        self.fields['year'].widget.attrs['id'] = 'year'
        self.fields['year'].widget.attrs['name'] = 'year'
