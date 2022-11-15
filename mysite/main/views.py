import psycopg2
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from dateutil.relativedelta import relativedelta
from django.views import View

from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from django.urls.base import reverse_lazy

from .forms import NewUserForm, MonthsForm, YearsForm, RiskReportForm
from .forms import RiskReportDayForm, CallsCheckForm, AddDataFromTextForm, AppealReportForm

from .models import RiskReport, RiskReportDay, CallsCheck, AddDataFromText, AppealReport

import credentials
import requests
import datetime


def homepage(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

    return render(request=request, template_name="main/home.html",
                  context={"support": support_users, "risks": risks_users, 'risk_heads': risk_heads_users,
                           'site_adm': site_adm_users, 'support_heads': support_heads_users, 'heads': heads})


def reports(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')
    support_heads_users = User.objects.filter(groups__name='support_heads')

    return render(request=request, template_name="main/reports.html",
                  context={"support": support_users, "risks": risks_users, 'risk_heads': risk_heads_users,
                           'site_adm': site_adm_users, 'support_heads': support_heads_users, 'heads': heads})


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
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

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
                   'support': support_users, 'risks': risks_users, 'risk_heads': risk_heads_users,
                   'site_adm': site_adm_users, 'support_heads': support_heads_users, 'heads': heads})


def payment(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    support_users = User.objects.filter(groups__name='support')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

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
                                                 'support': support_users, 'risks': risks_users,
                                                 'risk_heads': risk_heads_users, 'site_adm': site_adm_users,
                                                 'support_heads': support_heads_users})


def info_by_ip(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

    ip_address = request.GET.get('object')

    if ip_address == '' or ip_address is None:
        status = 0
        get_ip = None
        get_int_prov = None
        get_org = None
        get_country = None
        get_region_name = None
        get_city = None
        get_zip_code = None
        get_lat = None
        get_lon = None
    else:
        ip_address = ip_address.replace(' ', '')
        ip_address = ip_address.replace(',', '.')
        url = f'http://ip-api.com/json/{ip_address}'
        ip_info = requests.get(url=url)

        if ip_info.json()['status'] == 'fail':
            status = 1
            get_ip = 'Неверный IP или адрес не найден'
            get_int_prov = 'Нет интернет провайдера'
            get_org = 'Нет организации'
            get_country = 'Нет страны'
            get_region_name = 'Нет региона'
            get_city = 'Нет города'
            get_zip_code = 'Нет почтового индекса'
            get_lat = 'Нет координаты'
            get_lon = 'Нет координаты'
        else:
            status = 1
            get_ip = ip_info.json()['query']
            get_int_prov = ip_info.json()['isp']
            get_org = ip_info.json()['org']
            get_country = ip_info.json()['country']
            get_region_name = ip_info.json()['regionName']
            get_city = ip_info.json()['city']
            get_zip_code = ip_info.json()['zip']
            get_lat = str(ip_info.json()['lat']).replace(",", ".")
            get_lon = str(ip_info.json()['lon']).replace(",", ".")

    return render(request, 'main/ip_info.html', {'status': status,
                                                 'IP': get_ip, 'Int_prov': get_int_prov, 'Org': get_org,
                                                 'Country': get_country, 'Region_Name': get_region_name,
                                                 'City': get_city, 'ZIP': get_zip_code, 'Lat': get_lat, 'Lon': get_lon,
                                                 'support': support_users, 'risks': risks_users,
                                                 'risk_heads': risk_heads_users, 'site_adm': site_adm_users,
                                                 'support_heads': support_heads_users, 'heads': heads})


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


def check_db_record(model, date, user):
    if model.objects.filter(shift_date=date, user_name=user).exists():
        return True
    else:
        return False


def add_personal_report(request):
    """Добавление персонального отчета"""
    site_adm_users = User.objects.filter(groups__name='site_adm')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

    error_text = ''

    if request.method == "POST":
        form = RiskReportForm(request.POST)

        if form.is_valid():
            if check_db_record(RiskReport, form.cleaned_data.get('shift_date'), form.cleaned_data.get('user_name')):
                shift_date = form.cleaned_data.get('shift_date')
                user_name = form.cleaned_data.get('user_name')
                error_text = f'Данные смены {user_name} за {shift_date} уже присутствуют в Базе Данных'
            else:
                form.save()
                shift_date = form.cleaned_data.get('shift_date')
                user_name = form.cleaned_data.get('user_name')
                error_text = f'Данные смены {user_name} за {shift_date} успешно записаны в Базу Данных'
        else:
            error_text = form.errors

    form = RiskReportForm()

    data = {
        'form': form,
        'risks': risks_users,
        'risk_heads': risk_heads_users,
        'site_adm': site_adm_users,
        'error_text': error_text,
    }

    return render(request, "main/add_personal_report.html", data)


def add_day_report(request):
    """Добавление дневного отчета"""
    site_adm_users = User.objects.filter(groups__name='site_adm')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

    error_text = ''

    if request.method == "POST":
        form = RiskReportDayForm(request.POST)

        if form.is_valid():
            if check_db_record(RiskReportDay, form.cleaned_data.get('shift_date'), form.cleaned_data.get('user_name')):
                shift_date = form.cleaned_data.get('shift_date')
                error_text = f'Данные за {shift_date} уже присутствуют в Базе Данных'
            else:
                form.save()
                shift_date = form.cleaned_data.get('shift_date')
                error_text = f'Данные за {shift_date} успешно записаны в Базу Данных'

        else:
            error_text = form.errors

    form = RiskReportDayForm()

    data = {
        'form': form,
        'risks': risks_users,
        'risk_heads': risk_heads_users,
        'site_adm': site_adm_users,
        'error_text': error_text,
    }

    return render(request, "main/add_day_report.html", data)


def get_risks_report(start_date, end_date):
    """ This function get data from risk_report db table and return it as list of dicts """
    cursor, connection = None, None

    risks_report_list = []

    sql_query = (f'''
                    SELECT * FROM public.risk_report
                    WHERE shift_date >= '{start_date}' AND shift_date < '{end_date}'
                    ORDER BY shift_date ASC''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        risks_report_list = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return risks_report_list


def get_personal_risks_report(start_date, end_date):
    """ This function get data from risk_report db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT user_name,
                sum(verified_clients) AS verified_clients,
                sum(re_verified_clients) AS re_verified_clients,
                sum(processed_conclusions) AS processed_conclusions,
                sum(processed_support_requests) AS processed_support_requests,
                sum(tacks_help_desk) AS tacks_help_desk,
                sum(oapi_requests) AS oapi_requests,
                sum(schemes_revealed) AS schemes_revealed
            FROM main_riskreport
            WHERE shift_date >= '{start_date}' AND shift_date < '{end_date}'
            GROUP BY user_name
            ORDER BY user_name ASC''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        report_list = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return report_list


def calculate_risks_report(start_date, end_date):
    """ This function calculate risks report data and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                 SELECT
                    SUM (verified_clients) AS verified_clients,
                    SUM (re_verified_clients) AS re_verified_clients,
                    SUM (processed_conclusions) AS processed_conclusions,
                    SUM (processed_support_requests) AS processed_support_requests,
                    SUM (tacks_help_desk) AS tacks_help_desk,
                    SUM (oapi_requests) AS oapi_requests,
                    SUM (schemes_revealed) AS schemes_revealed,
                    SUM (foto_clients) AS foto_clients,
                    SUM (deposits_sum) AS deposits_sum,
                    SUM (withdrawals_sum) AS withdrawals_sum,
                    SUM (ggr_sport) AS ggr_sport,
                    SUM (ggr_casino) AS ggr_casino,
                    SUM (withdrawals_5000) AS withdrawals_5000
                FROM public.risk_report
                WHERE shift_date >= '{start_date}' AND shift_date < '{end_date}'
                ''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        report_list = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return report_list


def risks_rep(request):
    """ This function return risks report page """
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')

    now_date = datetime.datetime.now()
    last_month = now_date.month, now_date.year

    month_id = request.GET.get('month', None)
    if month_id is None:
        month_id = f'0{last_month[0]}'

    year_id = request.GET.get('year', None)
    if year_id is None:
        year_id = last_month[1]

    if len(month_id) > 2:
        month_id = month_id[1:]

    start_date = f'01.{month_id}.{year_id}'
    end_date = f'01.{month_id}.{year_id}'
    end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y') + relativedelta(months=1)
    end_date = str(end_date.date()).replace('-', '.')

    report = get_risks_report(start_date, end_date)
    pers_report = get_personal_risks_report(start_date, end_date)
    calc_report = calculate_risks_report(start_date, end_date)

    months = MonthsForm()
    years = YearsForm()

    m = int(month_id)
    a = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
         'Декабрь']
    month_name = a[m - 1 % 12]

    data = {
        'site_adm': site_adm_users,
        'heads': heads,
        'risks': risks_users,
        'risk_heads': risk_heads_users,
        'risk_reports': report,
        'pers_reports': pers_report,
        'calc_reports': calc_report,
        'months': months,
        'years': years,
        'month_id': month_name,
        'year_id': year_id,
    }
    return render(request, "main/risks_rep.html", data)


class ListRisksReport(ListView):
    """ This class is used to display risks report data in table """
    model = RiskReport
    form_class = RiskReportForm
    template_name = 'main/list_risks_rep.html'
    context_object_name = 'list_reports'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['risks'] = User.objects.filter(groups__name='risks')
        context['risk_heads'] = User.objects.filter(groups__name='risk_heads')
        context['superuser'] = User.objects.filter(is_superuser=True)
        return context

    def get_queryset(self):
        queryset = RiskReport.objects.all().order_by('-id')
        return queryset


class ListRisksReportDay(ListView):
    """ This class view show list of risks report for day """
    model = RiskReportDay
    form_class = RiskReportDayForm
    template_name = 'main/list_risks_rep_day.html'
    context_object_name = 'list_reports_day'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['risks'] = User.objects.filter(groups__name='risks')
        context['risk_heads'] = User.objects.filter(groups__name='risk_heads')
        context['superuser'] = User.objects.filter(is_superuser=True)
        return context

    def get_queryset(self):
        queryset = RiskReportDay.objects.all().order_by('-id')
        return queryset


class UpdateRisksReport(UpdateView):
    """Обновление персонального отчета по рискам"""
    model = RiskReport
    form_class = RiskReportForm
    template_name = 'main/update_risks_rep.html'
    success_url = reverse_lazy('main:list_risks_rep')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['risks'] = User.objects.filter(groups__name='risks')
        context['risk_heads'] = User.objects.filter(groups__name='risk_heads')
        context['superuser'] = User.objects.filter(is_superuser=True)
        return context


class UpdateRisksReportDay(UpdateView):
    """Обновление отчета за день"""
    model = RiskReportDay
    form_class = RiskReportDayForm
    template_name = 'main/update_risks_rep_day.html'
    success_url = reverse_lazy('main:list_risks_rep_day')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['risks'] = User.objects.filter(groups__name='risks')
        context['risk_heads'] = User.objects.filter(groups__name='risk_heads')
        context['superuser'] = User.objects.filter(is_superuser=True)
        return context


class CallsView(ListView):
    """ This class view show list of not verified clients """
    model = CallsCheck
    form_class = CallsCheckForm
    template_name = 'main/calls_rep.html'
    context_object_name = 'list_calls_reports'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['support'] = User.objects.filter(groups__name='support')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        context['months'] = MonthsForm()
        context['years'] = YearsForm()
        return context

    def get_queryset(self):
        month_id = self.request.GET.get('month')
        year_id = self.request.GET.get('year')
        if month_id is None and year_id is None:
            filter_date = None
        else:
            filter_date = month_id + '-' + year_id
        # print(filter_date)
        display_type = self.request.GET.get('display_type')
        phone_number = self.request.GET.get('phone_number')
        if display_type == '1':
            user_name = self.request.user.first_name + ' ' + self.request.user.last_name
            queryset = CallsCheck.objects.all().order_by('-id').filter(Q(user_name=user_name)
                                                                       & Q(upload_date_short=filter_date))
            return queryset
        elif display_type == '2':
            queryset = CallsCheck.objects.all().order_by('-id').filter(Q(user_name=None)
                                                                       & Q(upload_date_short=filter_date))
            return queryset
        elif display_type == '3':
            queryset = CallsCheck.objects.all().order_by('-id'). \
                filter(Q(call_date=None) & ~Q(call_result="есть фото")
                       & ~Q(call_result="номер не РБ") & ~Q(user_name=None)
                       & Q(upload_date_short=filter_date))
            return queryset
        elif phone_number is not None:
            phone_number = phone_number.strip()
            if len(phone_number) < 13:
                phone_number = '+' + phone_number
                queryset = CallsCheck.objects.all().order_by('-id').filter(Q(client_phone=phone_number))
                return queryset
            else:
                queryset = CallsCheck.objects.all().order_by('-id').filter(Q(client_phone=phone_number))
                return queryset
        elif filter_date is not None:
            queryset = CallsCheck.objects.all().order_by('-id').filter(~Q(call_result="есть фото")
                                                                       & ~Q(call_result="номер не РБ")
                                                                       & Q(verified_date=None)
                                                                       & Q(upload_date_short=filter_date))
            return queryset
        else:
            queryset = CallsCheck.objects.all().order_by('-id').filter(~Q(call_result="есть фото")
                                                                       & ~Q(call_result="номер не РБ")
                                                                       & Q(verified_date=None))
            return queryset


class UpdateCallView(UpdateView):
    """ This class view add new call report """
    model = CallsCheck
    form_class = CallsCheckForm
    template_name = 'main/update_calls.html'
    success_url = reverse_lazy('main:calls_rep')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['support'] = User.objects.filter(groups__name='support')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        return context


class AddDataFromTextView(View):
    """ This class view add new data from text area """
    model = AddDataFromText
    form_class = AddDataFromTextForm
    template_name = 'main/add_data.html'
    success_url = reverse_lazy('main:calls_rep')

    def get(self, request):
        site_adm_users = User.objects.filter(groups__name='site_adm')
        support_heads_users = User.objects.filter(groups__name='support_heads')

        data = {
            'site_adm': site_adm_users,
            'support_heads': support_heads_users,
            'superuser': User.objects.filter(is_superuser=True),
            'form': self.form_class,
        }
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            connection = psycopg2.connect(database=credentials.db_name,
                                          user=credentials.db_username,
                                          password=credentials.db_password,
                                          host=credentials.db_host,
                                          port=credentials.db_port,
                                          )

            data = form.cleaned_data.pop('text')
            data = data.split('\n')  # split data by tabulation
            data = [i.split(',') for i in data]  # split data by new line
            data = [i for i in data if i != ['']]  # remove empty list

            for i in data:
                client_data = i  # get client data
                client_data = [i.split('\t') for i in client_data]  # split client data by tabulation
                client_data = [i for i in client_data if i != ['']]  # remove empty list
                client_id = client_data[0][0]  # get client id
                client_phone = '+' + client_data[0][1]  # get client phone
                upload_date = datetime.datetime.now()  # get upload date
                upload_date_short = upload_date.strftime('%m-%Y')  # get upload date short
                """ sql query added client_id and client_phone to sql table main_callscheck """
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO main_callscheck "
                                       "(client_id, client_phone, upload_date, upload_date_short) "
                                       "VALUES (%s, %s, %s, %s)",
                                       [client_id, client_phone, upload_date, upload_date_short])
                        connection.commit()
                    print('Данные клиента:', client_id, client_phone)
                except Exception as e:
                    print('Данные клиента:', client_id, client_phone)
                    print(e)
                    connection.rollback()
            return redirect('main:calls_rep')

        return render(request, self.template_name, {'form': form})


def get_personal_cc_report(start_date, end_date):
    """ This function get data from callscheck db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT user_name AS "user_name", 
                    SUM(case when call_result != 'нет ответа' then 1 else 0 end)  AS "Количество звонков без ответа",
                    SUM(case when call_result != 'нет ответа' then 0 else 1 end ) AS "Количество звонков с ответом",
                    SUM(case when verified_date is not Null then 1 else 0 end) AS "Количество верификаций"
                FROM public.main_callscheck
                WHERE upload_date >= '{start_date}' AND upload_date < '{end_date}' 
                                                    AND user_name != 'null' 
                                                    AND call_result != 'есть фото'
                                                    AND call_result != 'номер не РБ' 
                GROUP BY user_name
                ORDER BY user_name ASC''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        report_list = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return report_list


def get_cc_report(start_date, end_date):
    """ This function get data from callscheck db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT
                    SUM(case when client_phone != '' then 1 else 0 end) AS "Общее количество звонков",
                    SUM(case when call_result != 'нет ответа' then 1 else 0 end)  AS "Количество звонков без ответа",
                    SUM(case when call_result != 'нет ответа' then 0 else 1 end ) AS "Количество звонков с ответом",
                    SUM(case when call_result = 'подумает' then 1 else 0 end ) AS "Подумает",
                    SUM(case when call_result = 'планирует' then 1 else 0 end ) AS "Паланирует",
                    SUM(case when call_result = 'не будет' OR call_result = 'не будет, перезвонил 
                    сам' then 1 else 0 end) AS "Не будет",
                    SUM(case when call_result = 'номер не РБ' then 1 else 0 end ) AS "Номер не РБ",
                    SUM(case when verified_date is not Null then 1 else 0 end) AS "Количество верификаций"
                FROM public.main_callscheck
                WHERE upload_date >= '{start_date}' AND upload_date < '{end_date}' 
                ''')

    try:
        connection = psycopg2.connect(database=credentials.db_name,
                                      user=credentials.db_username,
                                      password=credentials.db_password,
                                      host=credentials.db_host,
                                      port=credentials.db_port,
                                      )

        cursor = connection.cursor()
        cursor.execute(sql_query)

        report_list = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgresSQL", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    return report_list


def cc_report(request):
    """ This function return сс report page """
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_heads_users = User.objects.filter(groups__name='support_heads')

    now_date = datetime.datetime.now()
    last_month = now_date.month, now_date.year

    month_id = request.GET.get('month', None)
    if month_id is None:
        month_id = f'0{last_month[0]}'

    year_id = request.GET.get('year', None)
    if year_id is None:
        year_id = last_month[1]

    if len(month_id) > 2:
        month_id = month_id[1:]

    start_date = f'01.{month_id}.{year_id}'
    end_date = f'01.{month_id}.{year_id}'
    end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y') + relativedelta(months=1)
    end_date = str(end_date.date()).replace('-', '.')

    calls_report = get_personal_cc_report(start_date, end_date)
    calls_sum = get_cc_report(start_date, end_date)

    months = MonthsForm()
    years = YearsForm()

    m = int(month_id)
    a = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь',
         'Декабрь']
    month_name = a[m - 1 % 12]

    data = {
        'site_adm': site_adm_users,
        'heads': heads,
        'support_heads': support_heads_users,
        'calls_report': calls_report,
        'calls_sum': calls_sum,
        'months': months,
        'years': years,
        'month_id': month_name,
        'year_id': year_id,
    }
    return render(request, "main/cc_report.html", data)


def view_log_file(request):
    """ This function read file and render source file to page """
    site_adm_users = User.objects.filter(groups__name='site_adm')

    try:
        with open('./call_check.log', 'r', encoding='UTF-8') as f:
            file = f.read().split('\n')
    except FileNotFoundError:
        with open('/home/pgadmin/reports_site/call_check.log', 'r', encoding='UTF-8') as f:
            file = f.read().split('\n')
    except Exception as e:
        print(e)
        file = 'Файл не найден'

    data = {
        'site_adm': site_adm_users,
        'log_file': file,
    }
    return render(request, "main/log_file.html", data)


class AppealReportView(View):
    """ This class return appeal report page """

    model = AppealReport
    form_class = AppealReportForm
    template_name = 'main/appeal.html'
    success_url = reverse_lazy('main:appeal')

    def get(self, request):
        site_adm_users = User.objects.filter(groups__name='site_adm')
        support_heads_users = User.objects.filter(groups__name='support_heads')
        support_users = User.objects.filter(groups__name='support')

        # user_name = self.request.user.first_name + ' ' + self.request.user.last_name
        user_name = 'Мирончик Дмитрий'

        calls_in_count = AppealReport.objects.filter(appeal_type='Звонок входящий').\
            filter(Q(user_name=user_name)).count()

        calls_out_count = AppealReport.objects.filter(appeal_type='Звонок исходящий').\
            filter(Q(user_name=user_name)).count()

        mail_count = AppealReport.objects.filter(appeal_type='Почта').\
            filter(Q(user_name=user_name)).count()

        chat_count = AppealReport.objects.filter(Q(appeal_type='Чат') & Q(user_name=user_name)).count()
        telegram_count = AppealReport.objects.filter(Q(appeal_type='Телеграм') & Q(user_name=user_name)).count()
        whatsapp_count = AppealReport.objects.filter(Q(appeal_type='Ватсап') & Q(user_name=user_name)).count()

        chats_count = chat_count + telegram_count + whatsapp_count

        data = {
            'site_adm': site_adm_users,
            'support_heads': support_heads_users,
            'support': support_users,
            'superuser': User.objects.filter(is_superuser=True),
            'calls_in_count': calls_in_count,
            'calls_out_count': calls_out_count,
            'mail_count': mail_count,
            'chats_count': chats_count,
            'form': self.form_class,
        }
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:appeal')

        return render(request, self.template_name, {'form': form})


class AppealReportListView(ListView):
    """ This class return appeal report list page """

    model = AppealReport
    template_name = 'main/appeal_rep.html'
    context_object_name = 'appeal_rep'
    # paginate_by = 30

    def get_queryset(self):
        return AppealReport.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AppealReportListView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        context['support'] = User.objects.filter(groups__name='support')
        context['superuser'] = User.objects.filter(is_superuser=True)
        return context
