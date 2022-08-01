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

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class MonthForm(forms.Form):
    months = [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'),
              ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
              ('10', 'October'), ('11', 'November'), ('12', 'December'), ]
    month = forms.ChoiceField(choices=months, widget=forms.Select(attrs={'class': 'form-control'}))
