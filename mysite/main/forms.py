from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import RiskReport, RiskReportDay, CallsCheck

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


class RiskReportForm(ModelForm):
    class Meta:
        model = RiskReport

        fields = ['shift_date', 'shift_type', 'verified_clients', 're_verified_clients', 'processed_conclusions',
                  'processed_support_requests', 'tacks_help_desk', 'oapi_requests', 'schemes_revealed', 'user_name']

        widgets = {
            'shift_date':
                forms.DateInput(attrs={'class': 'form-control', 'id': 'shift_date', 'name': 'shift_date',
                                       'placeholder': '01.01.2021'}),
            'shift_type':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'shift_type',
                                       'placeholder': 'День / Ночь'}),
            'verified_clients':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'verified_clients',
                                         'placeholder': 'Тут пишем количество верифицированных клиентов'}),
            're_verified_clients':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 're_verified_clients',
                                         'placeholder': 'Тут пишем количество повторно верифицированных клиентов'}),
            'processed_conclusions':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'processed_conclusions',
                                         'placeholder': 'Тут пишем количество обработанных заключений'}),
            'processed_support_requests':
                forms.NumberInput(attrs={'class': 'form-control',
                                         'id': 'processed_support_requests',
                                         'placeholder': 'Тут пишем количество обработанных запросов поддержки'}),
            'tacks_help_desk':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'tacks_help_desk',
                                         'placeholder': 'Тут пишем количество заявок в помощь дежурному отделу'}),
            'oapi_requests':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'oapi_requests',
                                         'placeholder': 'Тут пишем количество заявок в ОАПИ'}),
            'schemes_revealed':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'schemes_revealed',
                                         'placeholder': 'Тут пишем количество открытых схем'}),
            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly'}),

        }


class RiskReportDayForm(ModelForm):
    class Meta:
        model = RiskReportDay

        fields = ['shift_date', 'foto_clients', 'deposits_sum', 'withdrawals_sum', 'ggr_sport',
                  'ggr_casino', 'withdrawals_5000', 'user_name']

        widgets = {
            'shift_date':
                forms.DateInput(attrs={'class': 'form-control', 'id': 'shift_date',
                                       'placeholder': '01.01.2021'}),
            'foto_clients':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'foto_clients',
                                         'placeholder': 'Тут пишем количество предоставивших фото для верификации'}),
            'deposits_sum':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'deposits_sum',
                                         'placeholder': 'Тут пишем общую сумму депозитов'}),
            'withdrawals_sum':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'withdrawals_sum',
                                         'placeholder': 'Тут пишем общую сумму выводов'}),
            'ggr_sport':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'ggr_sport',
                                         'placeholder': 'Тут пишем общую сумму депозитов в GGR Спорт'}),
            'ggr_casino':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'ggr_casino',
                                         'placeholder': 'Тут пишем общую сумму депозитов в GGR Казино'}),
            'withdrawals_5000':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'withdrawals_5000',
                                         'placeholder': 'Тут пишем количество выводов на сумму более 5000 BYN'}),
            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly'}),
        }


class CallsCheckForm(ModelForm):
    class Meta:
        model = CallsCheck

        fields = ['client_id', 'client_name', 'client_phone', 'call_result', 'verified_date', 'user_name']

        widgets = {
            'client_id':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'client_id',
                                         'placeholder': 'Тут пишем ID клиента', 'label': 'ID клиента'}),
            'client_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_name',
                                       'placeholder': 'Тут пишем имя клиента', 'label': 'Имя клиента'}),
            'client_phone':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_phone',
                                       'placeholder': 'Тут пишем номер телефона клиента', 'label': 'Номер телефона'}),
            'call_result':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'call_result',
                                       'placeholder': 'Тут пишем результат звонка', 'label': 'Результат звонка'}),
            'verified_date':
                forms.DateInput(attrs={'class': 'form-control', 'id': 'verified_date',
                                       'placeholder': '01.01.2022', 'label': 'Дата верификации'}),
            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly',
                                       'label': 'Имя пользователя'}),
        }

