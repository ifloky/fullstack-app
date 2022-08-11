from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from .forms import NewUserForm, MonthsForm, YearsForm

import requests
import credentials
import datetime


def homepage(request):
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')

    return render(request=request, template_name="main/home.html",
                  context={"support": support_users, "risks": risks_users})


def reports(request):
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')

    return render(request=request, template_name="main/reports.html",
                  context={"support": support_users, "risks": risks_users})


def message_count_from_s_and_r(start_date, end_date):
    """
    Calculates the number of messages in the inbox.
    """
    headers = {
        'X-Auth-Token': credentials.token,
        'X-User-Id': credentials.user_id,
        'Content-Type': 'application/json; charset=utf-8',
        }

    url = credentials.site_url + '/api/v1/channels.history?roomName'
    count = 0
    room_name = 'z2Nj4upxRReMRe8wY'

    rc_msg = requests.get(f'{url}={room_name}&count={count}&latest={end_date}&oldest={start_date}', headers=headers)

    return len(rc_msg.json()['messages'])


def message_count_from_crm(start_date, end_date):
    """
    Calculates the number of messages in the inbox.
    """
    headers = {
        'X-Auth-Token': credentials.token,
        'X-User-Id': credentials.user_id,
        'Content-Type': 'application/json; charset=utf-8',
        }

    url = credentials.site_url + '/api/v1/channels.history?roomName'
    count = 0
    room_name = 'CRM_RISK_SUPPORT'

    rc_msg = requests.get(f'{url}={room_name}&count={count}&latest={end_date}&oldest={start_date}', headers=headers)

    return len(rc_msg.json()['messages'])


def message_count_from_ver(start_date, end_date):
    """
    Calculates the number of messages in the inbox.
    """
    headers = {
        'X-Auth-Token': credentials.token,
        'X-User-Id': credentials.user_id,
        'Content-Type': 'application/json; charset=utf-8',
        }

    url = credentials.site_url + '/api/v1/channels.history?roomName'
    count = 0
    room_name = 'VERIFICATION'

    rc_msg = requests.get(f'{url}={room_name}&count={count}&latest={end_date}&oldest={start_date}', headers=headers)

    return len(rc_msg.json()['messages'])


def rocket(request):
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')

    now_date = datetime.datetime.now() - relativedelta(months=1)
    last_month = now_date.month, now_date.year

    month_id = request.GET.get('month', None)
    if month_id is None:
        month_id = f'0{last_month[0]}'

    year_id = request.GET.get('year', None)
    if year_id is None:
        year_id = last_month[1]

    if len(month_id) > 2:
        month_id = month_id[1:]

    start_date = f'{year_id}-{month_id}-01T03:00:00.000Z'
    end_date = f'{year_id}-{month_id}-31T20:59:59.999Z'

    message_count_s_and_r = message_count_from_s_and_r(start_date, end_date)
    message_count_crm = message_count_from_crm(start_date, end_date)
    message_count_ver = message_count_from_ver(start_date, end_date)
    months = MonthsForm()
    years = YearsForm()

    m = int(month_id)
    a = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
         'Декабрь']
    month_name = a[m - 1 % 12]

    return render(request, 'main/rocket.html',
                  {'title': 'Rocket Chat', 'message_count_s_and_r': message_count_s_and_r,
                   'message_count_crm': message_count_crm, 'message_count_ver': message_count_ver,
                   'months': months, 'years': years, 'month_id': month_name, 'year_id': year_id,
                   'support': support_users, 'risks': risks_users})


def payment(request):
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')

    tracking_id = request.GET.get('tracking', None)
    if tracking_id == '' or tracking_id is None:
        status = 0
        tracking_id = 'Нет номера отслеживания'
        payment_status = 'Нет статуса платежа'
        payment_url = '/payment'
        holder_name = 'Нет имени'
        card_number = 'Нет номера карты'
    else:
        status = 1
        auth = (credentials.bepaid_shop_id, credentials.bepaid_secret_key)
        url = 'https://gateway.bepaid.by/v2/transactions/tracking_id/'
        tracking_url = f'{url}{tracking_id}'
        rc_msg_tracking = requests.get(url=tracking_url, auth=auth)
        try:
            payment_status = rc_msg_tracking.json()['transactions'][0]['status']
        except IndexError:
            status = 2
            tracking_id = 'Неверный номер отслеживания'
            payment_status = 'Нет статуса платежа'
        try:
            payment_url = rc_msg_tracking.json()['transactions'][0]['receipt_url']
        except IndexError:
            payment_url = '/payment'
        try:
            holder_name = rc_msg_tracking.json()['transactions'][0]['credit_card']['holder']
        except IndexError:
            holder_name = 'Нет имени'
        try:
            card_number = rc_msg_tracking.json()['transactions'][0]['credit_card']['bin'] + ' XXXX ' + \
                          rc_msg_tracking.json()['transactions'][0]['credit_card']['last_4']
        except IndexError:
            card_number = 'Нет номера карты'

    return render(request, 'main/payment.html', {'tracking_id': tracking_id, 'payment_status': payment_status,
                                                 'payment_url': payment_url, 'holder_name': holder_name,
                                                 'card_number': card_number, 'status': status,
                                                 'support': support_users, 'risks': risks_users})


def info_by_ip(request):
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')

    ip_address = request.GET.get('object').replace(",", ".")

    if ip_address == '' or ip_address is None:
        status = 0
        get_ip = None,
        get_int_prov = None,
        get_org = None,
        get_country = None,
        get_region_name = None,
        get_city = None,
        get_zip_code = None,
        get_lat = None,
        get_lon = None,
    else:
        status = 1
        ip_info = requests.get(url=f'http://ip-api.com/json/{ip_address}')
        get_ip = ip_info.json()['query']
        try:
            get_int_prov = ip_info.json()['isp']
        except KeyError:
            get_int_prov = 'Это локальный адрес'
        try:
            get_org = ip_info.json()['org']
        except KeyError:
            get_org = 'Нет информации'
        try:
            get_country = ip_info.json()['country']
        except KeyError:
            get_country = 'Нет информации'
        try:
            get_region_name = ip_info.json()['regionName']
        except KeyError:
            get_region_name = 'Нет информации'
        try:
            get_city = ip_info.json()['city']
        except KeyError:
            get_city = 'Нет информации'
        try:
            get_zip_code = ip_info.json()['zip']
        except KeyError:
            get_zip_code = 'Нет информации'
        try:
            get_lat = str(ip_info.json()['lat']).replace(",", ".")
            get_lon = str(ip_info.json()['lon']).replace(",", ".")
        except KeyError:
            get_lat = 'Нет информации'
            get_lon = 'Нет информации'

    return render(request, 'main/ip_info.html', {'status': status,
                                                 'IP': get_ip, 'Int_prov': get_int_prov, 'Org': get_org,
                                                 'Country': get_country, 'Region_Name': get_region_name,
                                                 'City': get_city, 'ZIP': get_zip_code, 'Lat': get_lat, 'Lon': get_lon,
                                                 'support': support_users, 'risks': risks_users})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("main:homepage")
    else:
        messages.error(request, "Unsuccessful registration. Invalid information.")
        form = NewUserForm()

    return render(request=request, template_name="main/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("main:reports")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("main:homepage")


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "main/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:

                        return HttpResponse('Invalid header found.')

                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                    return redirect("main:homepage")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="main/password/password_reset.html",
                  context={"password_reset_form": password_reset_form})
