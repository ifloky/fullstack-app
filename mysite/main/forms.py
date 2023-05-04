from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import RiskReport, RiskReportDay, CallsCheck, AppealReport, GameListFromSkks, GameListFromSkksTest
from .models import GameListFromSite, GameDisableList
from .models import CRMCheck

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

        labels = {
            'shift_date': 'Дата смены',
            'shift_type': 'Смена',
            'verified_clients': 'Верифицировано клиентов',
            're_verified_clients': 'Повторно верифицировано клиентов',
            'processed_conclusions': 'Обработанных заключений',
            'processed_support_requests': 'Обработанных запросов поддержки',
            'tacks_help_desk': 'Заявок в Help Desk',
            'oapi_requests': 'Заявок в ОАПИ',
            'schemes_revealed': 'Выявлено схем',
            'user_name': 'Оператор'
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

        results_chooses = [('', ''), ('бросил трубку', 'бросил трубку'),
                           ('верифицирован до звонка', 'верифицирован до звонка'),
                           ('есть фото', 'есть фото'), ('играет не клиент', 'играет не клиент'),
                           ('не будет', 'не будет'), ('нет 21 года', 'нет 21 года'),
                           ('нет ответа', 'нет ответа'), ('номер не РБ', 'номер не РБ'), ('планирует', 'планирует'),
                           ('подумает', 'подумает'), ('чужой номер', 'чужой номер')]

        fields = ['client_id', 'client_name', 'client_phone', 'call_result', 'call_date', 'user_name']

        widgets = {
            'client_id':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'client_id', 'readonly': 'readonly',
                                         'placeholder': 'Тут пишем ID клиента', 'label': 'ID клиента'}),

            'client_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_name',
                                       'placeholder': 'Тут пишем имя клиента', 'label': 'Имя клиента'}),

            'client_phone':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_phone', 'readonly': 'readonly',
                                       'placeholder': 'Тут пишем номер телефона клиента',
                                       'label': 'Номер телефона клиента'}),

            'call_result':
                forms.widgets.Select(attrs={'class': 'form-control', 'id': 'call_result'}, choices=results_chooses),

            'call_date':
                forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'call_date',
                                           'placeholder': '01.01.2021', 'label': 'Дата звонка',
                                           'readonly': 'readonly'}),

            'verified_date':
                forms.DateInput(attrs={'class': 'form-control', 'id': 'verified_date',
                                       'placeholder': '01.01.2022', 'label': 'Дата верификации',
                                       'blank': True, 'null': True, 'required': False}),

            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly',
                                       'label': 'Имя оператора'}),
        }

        labels = {
            'client_id': 'ID клиента',
            'client_name': 'Имя клиента',
            'client_phone': 'Номер телефона клиента',
            'call_result': 'Результат звонка',
            'call_date': 'Дата звонка',
            'verified_date': 'Дата верификации',
            'user_name': 'Имя оператора',
        }

        blank = {
            'client_name': True,
            'call_date': True,
            'verified_date': True,
        }

        required = {
            'client_name': False,
            'verified_date': False,
        }


class CRMCheckForm(ModelForm):
    class Meta:
        model = CRMCheck

        results_chooses = [('', ''), ('бросил трубку', 'бросил трубку'),
                           ('есть депозит', 'есть депозит'), ('играет не клиент', 'играет не клиент'),
                           ('не будет', 'не будет'), ('нет 21 года', 'нет 21 года'),
                           ('нет ответа', 'нет ответа'), ('номер не РБ', 'номер не РБ'), ('планирует', 'планирует'),
                           ('подумает', 'подумает'), ('чужой номер', 'чужой номер')]

        fields = ['client_id', 'client_name', 'client_phone', 'call_result', 'call_date', 'user_name']

        widgets = {
            'client_id':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'client_id', 'readonly': 'readonly',
                                         'placeholder': 'Тут пишем ID клиента', 'label': 'ID клиента'}),

            'client_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_name',
                                       'placeholder': 'Тут пишем имя клиента', 'label': 'Имя клиента'}),

            'client_phone':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'client_phone', 'readonly': 'readonly',
                                       'placeholder': 'Тут пишем номер телефона клиента',
                                       'label': 'Номер телефона клиента'}),

            'call_result':
                forms.widgets.Select(attrs={'class': 'form-control', 'id': 'call_result'}, choices=results_chooses),

            'call_date':
                forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'call_date',
                                           'placeholder': '01.01.2021', 'label': 'Дата звонка',
                                           'readonly': 'readonly'}),

            'first_deposit_date':
                forms.DateInput(attrs={'class': 'form-control', 'id': 'first_deposit_date',
                                       'placeholder': '01.01.2022', 'label': 'Дата первого депозита',
                                       'blank': True, 'null': True, 'required': False}),

            'first_deposit_amount':
                forms.NumberInput(attrs={'class': 'form-control', 'id': 'first_deposit_amount',
                                         'placeholder': 'Тут пишем сумму первого депозита',
                                         'label': 'Сумма первого депозита', 'blank': True, 'null': True,
                                         'required': False}),

            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly',
                                       'label': 'Имя оператора'}),
        }

        labels = {
            'client_id': 'ID клиента',
            'client_name': 'Имя клиента',
            'client_phone': 'Номер телефона клиента',
            'call_result': 'Результат звонка',
            'call_date': 'Дата звонка',
            'first_deposit_date': 'Дата первого депозита',
            'first_deposit_amount': 'Сумма первого депозита',
            'user_name': 'Имя оператора',
        }

        blank = {
            'client_name': True,
            'call_date': True,
            'first_deposit_date': True,
        }

        required = {
            'client_name': False,
            'first_deposit_date': False,
        }


class AddDataFromTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'text',
                                                        'placeholder': 'Сюда вставляем текст'}))
    label = {
        'text': 'Текст',
    }

    def clean_text(self):
        text = self.cleaned_data['text']
        if not text:
            raise forms.ValidationError('Вы не ввели текст')
        return text

    def save(self):
        text = self.cleaned_data['text']
        return text


class AppealReportForm(ModelForm):
    class Meta:
        model = AppealReport

        fields = ['appeal_type', 'appeal_result', 'user_name']

        type_chooses = [('', ''),
                        ('Чат', 'Чат'),
                        ('Почта', 'Почта'),
                        ('Телеграмм', 'Телеграмм'),
                        ('Ватсап', 'Ватсап'),
                        ('Звонок входящий', 'Звонок входящий'),
                        ('Звонок исходящий', 'Звонок исходящий')]

        result_chooses = [('', ''),
                          ('Пояснение ввода логина', 'Пояснение ввода логина'),
                          ('Активировать бонус', 'Активировать бонус'),
                          ('Провести клиента по сайту, где, что найти', 'Провести клиента по сайту, где, что найти'),
                          ('Общая информация', 'Общая информация'),
                          ('Орг.вопросы (ком.предл, претензии, лицензии и т.д',
                           'Орг.вопросы (ком.предл, претензии, лицензии и т.д'),
                          ('Передано в риски', 'Передано в риски'), ('Передано в CRM', 'Передано в CRM')]

        widgets = {
            'appeal_type':
                forms.widgets.Select(attrs={'class': 'form-control', 'id': 'appeal_type'}, choices=type_chooses),

            'appeal_result':
                forms.widgets.Select(attrs={'class': 'form-control', 'id': 'appeal_result'}, choices=result_chooses),

            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly',
                                       'label': 'Имя оператора'}),
        }

        labels = {
            'appeal_type': 'Тип обращения',
            'appeal_result': 'Результат обращения',
            'user_name': 'Имя оператора',
        }


class GameListFromSkksForm(ModelForm):
    class Meta:
        model = GameListFromSkks

        fields = ['game_id', 'game_name', 'game_type', 'game_provider', 'game_permitted_date']

        widgets = {
            'game_id':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_id', 'readonly': 'readonly',
                                       'label': 'ID игры'}),

            'game_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_name', 'readonly': 'readonly',
                                       'label': 'Название игры'}),

            'game_type':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_type', 'readonly': 'readonly',
                                       'label': 'Тип игры'}),

            'game_provider':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_provider', 'readonly': 'readonly',
                                       'label': 'Провайдер игры'}),

            'game_permitted_date':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_permitted_date', 'readonly': 'readonly',
                                       'label': 'Дата разрешения'}),
        }

        labels = {
            'game_id': 'ID игры',
            'game_name': 'Название игры',
            'game_type': 'Тип игры',
            'game_provider': 'Провайдер игры',
            'game_permitted_date': 'Дата разрешения',
        }


class GameListFromSkksTestForm(ModelForm):
    class Meta:
        model = GameListFromSkksTest

        fields = ['game_id', 'game_name', 'game_type', 'game_provider', 'game_permitted_date']

        widgets = {
            'game_id':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_id', 'readonly': 'readonly',
                                       'label': 'ID игры'}),

            'game_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_name', 'readonly': 'readonly',
                                       'label': 'Название игры'}),

            'game_type':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_type', 'readonly': 'readonly',
                                       'label': 'Тип игры'}),

            'game_provider':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_provider', 'readonly': 'readonly',
                                       'label': 'Провайдер игры'}),

            'game_permitted_date':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_permitted_date', 'readonly': 'readonly',
                                       'label': 'Дата разрешения'}),
        }

        labels = {
            'game_id': 'ID игры',
            'game_name': 'Название игры',
            'game_type': 'Тип игры',
            'game_provider': 'Провайдер игры',
            'game_permitted_date': 'Дата разрешения',
        }


class GameListFromSiteForm(ModelForm):
    class Meta:
        model = GameListFromSite

        fields = ['game_name', 'game_provider', 'game_status']

        widgets = {
            'game_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_id', 'readonly': 'readonly',
                                       'label': 'Название игры'}),

            'game_provider':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_name', 'readonly': 'readonly',
                                       'label': 'Провайдер игры'}),

            'game_status':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_type', 'readonly': 'readonly',
                                       'label': 'Статус игры'}),
        }

        labels = {
            'game_name': 'Название игры',
            'game_provider': 'Провайдер игры',
            'game_status': 'Статус игры',
        }


class GameDisableListForm(ModelForm):
    class Meta:
        model = GameDisableList

        fields = ['game_name', 'game_provider', 'game_disable_date', 'user_name']

        queryset = GameListFromSkks.objects.values_list('game_provider', flat=True).order_by('game_provider').distinct()
        providers_list = [(provider, provider) for provider in queryset]

        widgets = {
            'game_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_name', 'label': 'Название игры'}),

            'game_provider':
                forms.widgets.Select(attrs={'class': 'form-control', 'id': 'game_provider', 'label': 'Провайдер игры'},
                                     choices=providers_list),

            'game_disable_date':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'game_disable_date', 'readonly': 'readonly',
                                       'label': 'Дата отключения'}),

            'user_name':
                forms.TextInput(attrs={'class': 'form-control', 'id': 'user_name', 'readonly': 'readonly',
                                       'label': 'Пользователь'}),
        }

        labels = {
            'game_name': 'Название игры',
            'game_provider': 'Провайдер игры',
            'game_disable_date': 'Дата отключения',
            'user_name': 'Пользователь',
        }


class CloseHoldRoundForm(forms.Form):
    accounts_chooses = [603031708, 1268338164]

    accounts_list = [(account, account) for account in accounts_chooses]

    account_id = forms.ChoiceField(choices=accounts_list, required=True)
    round_id = forms.CharField(max_length=12, required=True)
    transaction_id = forms.CharField(max_length=12, required=True)
    amount = forms.CharField(max_length=10, required=True)

    def __init__(self, *args, **kwargs):
        super(CloseHoldRoundForm, self).__init__(*args, **kwargs)
        self.fields['account_id'].widget.attrs.update({'class': 'form-control', 'id': 'account_id'})
        self.fields['round_id'].widget.attrs.update({'class': 'form-control', 'id': 'round_id'})
        self.fields['transaction_id'].widget.attrs.update({'class': 'form-control', 'id': 'transaction_id'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control', 'id': 'amount'})

    def clean(self):
        cleaned_data = super(CloseHoldRoundForm, self).clean()
        account_id = cleaned_data.get('account_id')
        round_id = cleaned_data.get('round_id')
        transaction_id = cleaned_data.get('transaction_id')
        amount = cleaned_data.get('amount')

        if account_id and round_id and transaction_id and amount:
            if not account_id.isdigit() or not round_id.isdigit() \
                    or not transaction_id.isdigit() or not amount.isdigit():
                raise forms.ValidationError('Поля должны содержать только цифры')

        return cleaned_data


class TransactionCancelForm(forms.Form):
    transaction_id = forms.CharField(max_length=12, required=True)

    def __init__(self, *args, **kwargs):
        super(TransactionCancelForm, self).__init__(*args, **kwargs)
        self.fields['transaction_id'].widget.attrs.update({'class': 'form-control', 'id': 'transaction_id'})

    def clean(self):
        cleaned_data = super(TransactionCancelForm, self).clean()
        transaction_id = cleaned_data.get('transaction_id')

        if transaction_id:
            if not transaction_id.isdigit():
                raise forms.ValidationError('Поля должны содержать только цифры')

        return cleaned_data


class CreatePayoutRequestForm(forms.Form):
    money_type_chooses = [('1', 'Наличные деньги'), ('2', 'Безналичные деньги'), ('3', 'Электронные деньги')]
    terminal_id_chooses = [('2', 'ВЫВОД bePaid'), ('7', 'ВЫВОД ОПЛАТИ')]
    document_type_chooses = [('1', 'Паспорт'),
                             ('2', 'Вид на жительство'),
                             ('3', 'Удостоверение беженца'),
                             ('7', 'Идентификационная карта гражданина РБ'),
                             ('8', 'Биометрический вид на жительство в РБ иностранного гражданина'),
                             ('9', 'Биометрический вид на жительство в РБ лица без гражданства')]

    account_id = forms.CharField(max_length=12, required=True, label='ID Игрока')
    terminal_id = forms.ChoiceField(choices=terminal_id_chooses, required=True, label='ID Терминал')
    money_type = forms.ChoiceField(choices=money_type_chooses, required=True, label='Тип денег', initial=2)
    amount = forms.CharField(max_length=6, required=True, label='Сумма, в копейках')
    document_country = forms.CharField(max_length=3, required=True, label='Страна документа')
    document_type = forms.ChoiceField(choices=document_type_chooses, required=True, label='Тип документа')
    document_number = forms.CharField(max_length=20, required=True, label='Номер документа')
    personal_number = forms.CharField(max_length=20, required=False, label='Личный номер')
    last_name = forms.CharField(max_length=50, required=True, label='Фамилия')
    first_name = forms.CharField(max_length=50, required=True, label='Имя')
    middle_name = forms.CharField(max_length=50, required=True, label='Отчество')
    document_issue_agency = forms.CharField(max_length=150, required=True, label='Кем выдан документ')
    document_issue_date = forms.DateField(required=True, label='Дата выдачи документа')

    def __init__(self, *args, **kwargs):
        super(CreatePayoutRequestForm, self).__init__(*args, **kwargs)
        self.fields['account_id'].widget.attrs.update({'class': 'form-control', 'id': 'account_id'})
        self.fields['terminal_id'].widget.attrs.update({'class': 'form-control', 'id': 'terminal_id'})
        self.fields['money_type'].widget.attrs.update({'class': 'form-control', 'id': 'money_type'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control', 'id': 'amount',
                                                   'placeholder': 'Сумма в копейках'})
        self.fields['document_country'].widget.attrs.update({'class': 'form-control', 'id': 'document_country',
                                                             'placeholder': 'В формате ISO 3166-1 alpha-3. '
                                                                            'Например "BLR", "RUS", "UKR", "CHN"'})
        self.fields['document_type'].widget.attrs.update({'class': 'form-control', 'id': 'document_type'})
        self.fields['document_number'].widget.attrs.update({'class': 'form-control', 'id': 'document_number'})
        self.fields['personal_number'].widget.attrs.update({'class': 'form-control', 'id': 'personal_number'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'id': 'last_name'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'id': 'first_name'})
        self.fields['middle_name'].widget.attrs.update({'class': 'form-control', 'id': 'middle_name'})
        self.fields['document_issue_agency'].widget.attrs.update(
            {'class': 'form-control', 'id': 'document_issue_agency'})
        self.fields['document_issue_date'].widget.attrs.update({'class': 'form-control', 'id': 'document_issue_date',
                                                                'placeholder': 'В формате YYYY-MM-DD. '
                                                                               'Например 2020-01-01'})

    def clean(self):
        cleaned_data = super(CreatePayoutRequestForm, self).clean()
        payout_request_id = cleaned_data.get('payout_request_id')
        account_id = cleaned_data.get('account_id')
        money_type = cleaned_data.get('money_type')
        amount = cleaned_data.get('amount')
        document_country = cleaned_data.get('document_country')
        document_type = cleaned_data.get('document_type')
        document_number = cleaned_data.get('document_number')
        personal_number = cleaned_data.get('personal_number')
        last_name = cleaned_data.get('last_name')
        first_name = cleaned_data.get('first_name')
        middle_name = cleaned_data.get('middle_name')
        document_issue_agency = cleaned_data.get('document_issue_agency')
        document_issue_date = cleaned_data.get('document_issue_date')

        if payout_request_id and account_id and money_type and amount and document_country and document_type \
                and document_number and personal_number and last_name and first_name and middle_name \
                and document_issue_agency and document_issue_date:
            if not payout_request_id.isdigit() or not account_id.isdigit() or not money_type.isdigit() \
                    or not amount.isdigit() or not document_type.isdigit():
                raise forms.ValidationError('Поля должны содержать только цифры')

        return cleaned_data


class CreateTransactionPlayerInForm(forms.Form):
    money_type_chooses = [('1', 'Наличные деньги'), ('2', 'Безналичные деньги'), ('3', 'Электронные деньги')]
    terminal_id_chooses = [('1', 'ВВОД bePaid'), ('3', 'ВВОД  iPay')]

    account_id = forms.CharField(max_length=12, required=True, label='ID Игрока')
    terminal_id = forms.ChoiceField(choices=terminal_id_chooses, required=True, label='ID Терминал')
    money_type = forms.ChoiceField(choices=money_type_chooses, required=True, label='Тип денег', initial=2)
    amount = forms.CharField(max_length=6, required=True, label='Сумма, в копейках')
    trans_desc = forms.CharField(max_length=255, required=True, label='Описание транзакции')

    def __init__(self, *args, **kwargs):
        super(CreateTransactionPlayerInForm, self).__init__(*args, **kwargs)
        self.fields['account_id'].widget.attrs.update({'class': 'form-control', 'id': 'account_id'})
        self.fields['terminal_id'].widget.attrs.update({'class': 'form-control', 'id': 'terminal_id'})
        self.fields['money_type'].widget.attrs.update({'class': 'form-control', 'id': 'money_type'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control', 'id': 'amount',
                                                   'placeholder': 'Сумма в копейках'})
        self.fields['trans_desc'].widget.attrs.update({'class': 'form-control', 'id': 'trans_desc',
                                                       'placeholder': 'Дата операции: 15.04.2023 5:27:25, '
                                                                      'техническая ошибка программы, '
                                                                      'в СККС не отражена банковская транзакция'})

    def clean(self):
        cleaned_data = super(CreateTransactionPlayerInForm, self).clean()
        account_id = cleaned_data.get('account_id')
        terminal_id = cleaned_data.get('terminal_id')
        money_type = cleaned_data.get('money_type')
        amount = cleaned_data.get('amount')
        trans_desc = cleaned_data.get('trans_desc')

        if account_id and terminal_id and money_type and amount and trans_desc:
            if not account_id.isdigit() or not terminal_id.isdigit() or not money_type.isdigit() \
                    or not amount.isdigit():
                raise forms.ValidationError('Поля должны содержать только цифры')

        return cleaned_data


class AddGameToSKKSHostForm(forms.Form):
    game_type_chooses = [('1', 'Букмекерская игра'), ('2', 'Букмекерская онлайн-игра'), ('3', 'Игра тотализатора'),
                         ('4', 'Онлайн-игра тотализатора'), ('5', 'Игра на игровых автоматах в лайврежиме'),
                         ('6', 'Слот-игра'), ('7', 'Онлайн-игра в карты'), ('8', 'Игра в карты в лайв-режиме'),
                         ('9', 'Игра в кости в лайв-режиме'), ('10', 'Игра бинго'),
                         ('11', 'Цилиндрическая игра (рулетка) в лайврежиме'), ('12', 'Букмекерская онлайн TV-игра')]

    game_type = forms.ChoiceField(choices=game_type_chooses, required=True, label='Тип игры', initial=6)
    game_provider = forms.ChoiceField(required=True, label='Провайдер игры')
    game_version = forms.CharField(max_length=3, required=True, label='Версия игры')
    game_names = forms.CharField(widget=forms.Textarea, required=True, label='Название игры')

    def __init__(self, *args, **kwargs):
        super(AddGameToSKKSHostForm, self).__init__(*args, **kwargs)
        self.fields['game_type'].widget.attrs.update({'class': 'form-control', 'id': 'game_type'})
        self.fields['game_provider'].widget.attrs.update({'class': 'form-control', 'id': 'game_provider'})
        self.fields['game_version'].widget.attrs.update({'class': 'form-control', 'id': 'game_version',
                                                         'placeholder': 'Версия игры'})
        self.fields['game_names'].widget.attrs.update({'class': 'form-control', 'id': 'game_names',
                                                       'placeholder': 'Название игры, '
                                                                      'каждое с новой строки'})

        self.fields['game_provider'].choices = self.get_game_provider()

    @staticmethod
    def get_game_provider():
        providers_name = [(i['game_provider'], i['game_provider'])
                          for i in GameListFromSkksTest.objects.values('game_provider').distinct().order_by('game_provider')]
        return providers_name

    def clean(self):
        cleaned_data = super(AddGameToSKKSHostForm, self).clean()
        game_type = cleaned_data.get('game_type')
        game_provider = cleaned_data.get('game_provider')
        game_version = cleaned_data.get('game_version')
        game_names = cleaned_data.get('game_names')

        if game_type and game_provider and game_version and game_names:
            if not game_type.isdigit() or not game_version.isdigit():
                raise forms.ValidationError('Поля должны содержать только цифры')

        return cleaned_data
