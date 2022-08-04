from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

import datetime


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


now_date = datetime.datetime.now()
last_month = now_date.month, now_date.year


class MonthsForm(forms.Form):
    months = [('01', 'Январь'), ('02', 'Февраль'), ('03', 'Март'), ('04', 'Апрель'), ('05', 'Май'),
              ('06', 'Июнь'), ('07', 'Июль'), ('08', 'Август'), ('09', 'Сентябрь'),
              ('10', 'Октябрь'), ('11', 'Ноябрь'), ('12', 'Декабрь'), ]
    month = forms.ChoiceField(choices=months, label='')

    def __init__(self, *args, **kwargs):
        month_id = f'0{last_month[0]}'

        if len(month_id) > 2:
            month_id = month_id[1:]

        super(MonthsForm, self).__init__(*args, **kwargs)
        self.fields['month'].initial = month_id
        self.fields['month'].widget.attrs['class'] = 'form-control'
        self.fields['month'].widget.attrs['label'] = 'Month:'
        self.fields['month'].widget.attrs['id'] = 'month'
        self.fields['month'].widget.attrs['name'] = 'month'


class YearsForm(forms.Form):
    years = [('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ]
    year = forms.ChoiceField(choices=years, label='')

    def __init__(self, *args, **kwargs):
        year_id = last_month[1]

        super(YearsForm, self).__init__(*args, **kwargs)
        self.fields['year'].initial = year_id
        self.fields['year'].widget.attrs['class'] = 'form-control'
        self.fields['year'].widget.attrs['label'] = 'Year:'
        self.fields['year'].widget.attrs['id'] = 'year'
        self.fields['year'].widget.attrs['name'] = 'year'
