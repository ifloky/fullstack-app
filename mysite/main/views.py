import credentials
import requests
import datetime
import psycopg2

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from dateutil.relativedelta import relativedelta
from django.views import View

from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from django.urls.base import reverse_lazy

from .forms import NewUserForm, MonthsForm, YearsForm, RiskReportForm, GameListFromSkksForm, GameListFromSkksTestForm
from .forms import RiskReportDayForm, CallsCheckForm, AddDataFromTextForm, AppealReportForm, GameListFromSiteForm
from .forms import CRMCheckForm, GameDisableListForm

from .models import RiskReport, RiskReportDay, CallsCheck, AppealReport, GameListFromSkks, GameListFromSkksTest
from .models import GameListFromSite, GameDisableList
from .models import CRMCheck


def homepage(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')
    game_control_users = User.objects.filter(groups__name='game_control')
    crm_users = User.objects.filter(groups__name='crm')

    return render(request=request, template_name="main/home.html",
                  context={"support": support_users, "risks": risks_users, 'risk_heads': risk_heads_users,
                           'site_adm': site_adm_users, 'support_heads': support_heads_users, 'heads': heads,
                           'game_control': game_control_users, 'crm': crm_users})


def reports(request):
    site_adm_users = User.objects.filter(groups__name='site_adm')
    heads = User.objects.filter(groups__name='heads')
    support_users = User.objects.filter(groups__name='support')
    risks_users = User.objects.filter(groups__name='risks')
    risk_heads_users = User.objects.filter(groups__name='risk_heads')
    support_heads_users = User.objects.filter(groups__name='support_heads')
    game_control_users = User.objects.filter(groups__name='game_control')
    crm_users = User.objects.filter(groups__name='crm')

    return render(request=request, template_name="main/reports.html",
                  context={"support": support_users, "risks": risks_users, 'risk_heads': risk_heads_users,
                           'site_adm': site_adm_users, 'support_heads': support_heads_users, 'heads': heads,
                           'game_control': game_control_users, 'crm': crm_users})


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
    game_control_users = User.objects.filter(groups__name='game_control')
    crm_users = User.objects.filter(groups__name='crm')

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
                                                 'support_heads': support_heads_users, 'heads': heads,
                                                 'game_control': game_control_users, 'crm': crm_users})


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

        now_date = datetime.datetime.now()
        last_month = str(now_date.month) + '-' + str(now_date.year)

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
                                                                       & Q(verified_date=None)
                                                                       & Q(upload_date_short=last_month))
            return queryset


class CRMView(ListView):
    """ This class view show list of not verified clients """
    model = CRMCheck
    form_class = CRMCheckForm
    template_name = 'main/crm_rep.html'
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

        now_date = datetime.datetime.now()
        last_month = str(now_date.month) + '-' + str(now_date.year)

        if display_type == '1':
            user_name = self.request.user.first_name + ' ' + self.request.user.last_name
            queryset = CRMCheck.objects.all().order_by('-id').filter(Q(user_name=user_name)
                                                                     & Q(upload_date_short=filter_date))
            return queryset
        elif display_type == '2':
            queryset = CRMCheck.objects.all().order_by('-id').filter(Q(user_name=None)
                                                                     & Q(upload_date_short=filter_date))
            return queryset
        elif display_type == '3':
            queryset = CRMCheck.objects.all().order_by('-id'). \
                filter(Q(call_date=None) & ~Q(call_result="есть фото")
                       & ~Q(call_result="номер не РБ") & ~Q(user_name=None)
                       & Q(upload_date_short=filter_date))
            return queryset
        elif phone_number is not None:
            phone_number = phone_number.strip()
            if len(phone_number) < 13:
                phone_number = '+' + phone_number
                queryset = CRMCheck.objects.all().order_by('-id').filter(Q(client_phone=phone_number))
                return queryset
            else:
                queryset = CRMCheck.objects.all().order_by('-id').filter(Q(client_phone=phone_number))
                return queryset
        elif filter_date is not None:
            queryset = CRMCheck.objects.all().order_by('-id').filter(~Q(call_result="есть фото")
                                                                     & ~Q(call_result="номер не РБ")
                                                                     & Q(first_deposit_date=None)
                                                                     & Q(upload_date_short=filter_date))
            return queryset
        else:
            queryset = CRMCheck.objects.all().order_by('-id').filter(~Q(call_result="есть фото")
                                                                     & ~Q(call_result="номер не РБ")
                                                                     & Q(first_deposit_date=None)
                                                                     & Q(upload_date_short=last_month))
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


class UpdateCRMView(UpdateView):
    """ This class view add new call report """
    model = CRMCheck
    form_class = CRMCheckForm
    template_name = 'main/update_crm.html'
    success_url = reverse_lazy('main:crm_rep')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['support'] = User.objects.filter(groups__name='support')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        return context


class AddDataFromTextView(View):
    """ This class view add new data from text area """
    # model = AddDataFromText
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
            data = list(filter(None, data))  # remove empty spaces

            for i in data:
                if i != ['\t\r']:
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
                else:
                    continue
            return redirect('main:calls_rep')

        return render(request, self.template_name, {'form': form})


class AddDataFromCRMView(View):
    """ This class view add new data from text area """
    # model = AddDataFromText
    form_class = AddDataFromTextForm
    template_name = 'main/add_crm_data.html'
    success_url = reverse_lazy('main:crm_rep')

    def get(self, request):
        site_adm_users = User.objects.filter(groups__name='site_adm')
        crm_users = User.objects.filter(groups__name='crm')

        data = {
            'site_adm': site_adm_users,
            'crm': crm_users,
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
            data = list(filter(None, data))  # remove empty spaces

            for i in data:
                if i != ['\t\r']:
                    client_data = i  # get client data
                    client_data = [i.split('\t') for i in client_data]  # split client data by tabulation
                    client_data = [i for i in client_data if i != ['']]  # remove empty list
                    client_id = client_data[0][0]  # get client id
                    client_name = client_data[0][1]  # get client name
                    client_phone = '+' + client_data[0][2]  # get client phone
                    upload_date = datetime.datetime.now()  # get upload date
                    upload_date_short = upload_date.strftime('%m-%Y')  # get upload date short
                    """ sql query added client_id and client_phone to sql table main_crmcheck """
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("INSERT INTO main_crmcheck "
                                           "(client_id, client_name, client_phone, upload_date, upload_date_short) "
                                           "VALUES (%s, %s, %s, %s, %s)",
                                           [client_id, client_name, client_phone, upload_date, upload_date_short])
                            connection.commit()
                        print('Данные клиента:', client_id, client_name, client_phone)
                    except Exception as e:
                        print('Данные клиента:', client_id, client_name, client_phone)
                        print(e)
                        connection.rollback()
                else:
                    continue
            return redirect('main:crm_rep')

        return render(request, self.template_name, {'form': form})


def get_personal_cc_report(filter_date):

    get_uniq_users = CallsCheck.objects\
        .filter(upload_date_short__icontains=filter_date)\
        .filter(~Q(user_name='Tamara Rozganova'))\
        .filter(~Q(user_name='Величко Оксана'))\
        .filter(~Q(user_name=None))\
        .values('user_name')\
        .distinct()

    user_report = []

    for user in get_uniq_users:
        user_name = user['user_name']

        answered_calls = CallsCheck.objects\
            .filter(upload_date_short__icontains=filter_date)\
            .filter(user_name=user_name)\
            .filter(~Q(call_result='нет ответа'))\
            .filter(~Q(call_result='верифицирован до звонка'))\
            .filter(~Q(call_result='есть фото'))\
            .filter(~Q(call_result='номер не РБ'))\
            .count()

        unanswered_calls = CallsCheck.objects\
            .filter(upload_date_short__icontains=filter_date)\
            .filter(user_name=user_name)\
            .filter(Q(call_result='нет ответа')) \
            .filter(~Q(call_result='верифицирован до звонка')) \
            .filter(~Q(call_result='есть фото')) \
            .filter(~Q(call_result='номер не РБ')) \
            .count()

        verifications = CallsCheck.objects\
            .filter(upload_date_short__icontains=filter_date)\
            .filter(user_name=user_name)\
            .filter(~Q(verified_date=None))\
            .count()

        deposit_count = CRMCheck.objects\
            .filter(upload_date_short__icontains=filter_date)\
            .filter(user_name=user_name)\
            .filter(~Q(first_deposit_date=None))\
            .count()

        deposit_sum = CRMCheck.objects\
            .filter(upload_date_short__icontains=filter_date)\
            .filter(user_name=user_name)\
            .filter(~Q(first_deposit_amount=None))\
            .aggregate(Sum('first_deposit_amount'))['first_deposit_amount__sum']

        if deposit_sum is None:
            deposit_sum = 0

        user_report.append({
            'user_name': user_name,
            'answered_calls': answered_calls,
            'unanswered_calls': unanswered_calls,
            'verifications': verifications,
            'deposit_count': deposit_count,
            'deposit_sum': deposit_sum,
        })

    return user_report


def get_personal_crm_report(short_date):
    """ This function get data from callscheck db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT user_name AS "user_name", 
                    SUM(case when first_deposit_date is not Null then 1 else 0 end) AS "Количество первых депозитов"
                FROM public.main_crmcheck
                WHERE upload_date_short = '{short_date}'
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


def get_personal_appeal_report(date_short):
    """ This function get data from callscheck db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT user_name AS "user_name", 
                    SUM(case when appeal_type = 'Звонок входящий' then 1 else 0 end)  AS "Входящие вызовы",
                    SUM(case when appeal_type = 'Звонок исходящий' then 1 else 0 end ) AS "Исходящие вызовы",
                    SUM(case when appeal_type = 'Почта' then 1 else 0 end ) AS "Почтовые обращаения",
                    SUM(case when appeal_type = 'Чат' then 1 else 0 end + 
                    case when appeal_type = 'Телеграмм' then 1 else 0 end + 
                    case when appeal_type = 'Ватсап' then 1 else 0 end) AS "Чаты"
                FROM public.main_appealreport
                WHERE appeal_date_short = '{date_short}' 
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


def get_cc_report(filter_date):

    data = []

    calls_count = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(~Q(call_date=None)) \
        .count()

    no_answer_calls = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(Q(call_result='нет ответа')) \
        .count()

    answer_call = calls_count - no_answer_calls

    think_about_it = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(Q(call_result='подумает')) \
        .count()

    plans_to_game = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(Q(call_result='планирует')) \
        .count()

    will_not_game = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(Q(call_result='не будет')) \
        .count()

    no_rb_number = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(Q(call_result='номер не РБ')) \
        .count()

    verification = CallsCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(~Q(verified_date=None)) \
        .count()

    deposit_count = CRMCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(~Q(first_deposit_date=None)) \
        .count()

    deposit_sum = CRMCheck.objects \
        .filter(upload_date_short__icontains=filter_date) \
        .filter(~Q(first_deposit_amount=None)) \
        .aggregate(Sum('first_deposit_amount'))['first_deposit_amount__sum']

    data.append({
        'calls_count': calls_count,
        'no_answer_calls': no_answer_calls,
        'answer_call': answer_call,
        'think_about_it': think_about_it,
        'plans_to_game': plans_to_game,
        'will_not_game': will_not_game,
        'no_rb_number': no_rb_number,
        'verification': verification,
        'deposit_count': deposit_count,
        'deposit_sum': deposit_sum,
    })

    return data


def get_appeal_report(date_short):
    """ This function get data from appealreport db table and return it as list of dicts """
    cursor, connection = None, None

    report_list = []

    sql_query = (f'''
                SELECT
                    SUM(case when appeal_type = 'Звонок входящий' then 1 else 0 end) AS "Входящие вызовы",
                    SUM(case when appeal_type = 'Звонок исходящий' then 1 else 0 end) AS "Исходящие вызовы",
                    SUM(case when appeal_type = 'Почта' then 1 else 0 end) AS "Почтовые обращаения",
                    SUM(case when appeal_type = 'Чат' then 1 else 0 end) + 
                    SUM(case when appeal_type = 'Телеграмм' then 1 else 0 end) + 
                    SUM(case when appeal_type = 'Ватсап' then 1 else 0 end) AS "Чаты"
                FROM public.main_appealreport
                WHERE appeal_date_short = '{date_short}' 
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

    date_short = str(month_id) + '-' + str(year_id)

    calls_report = get_personal_cc_report(date_short)
    crm_report = get_personal_crm_report(date_short)
    appeal_report = get_personal_appeal_report(date_short)
    calls_sum = get_cc_report(date_short)
    appeal_sum = get_appeal_report(date_short)

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
        'crm_report': crm_report,
        'appeal_report': appeal_report,
        'calls_sum': calls_sum,
        'appeal_sum': appeal_sum,
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

    try:
        with open('./skks_check.log', 'r', encoding='UTF-8') as f:
            skks_file = f.read().split('\n')
    except FileNotFoundError:
        with open('/home/pgadmin/reports_site/skks_check.log', 'r', encoding='UTF-8') as f:
            skks_file = f.read().split('\n')
    except Exception as e:
        print(e)
        skks_file = 'Файл не найден'

    try:
        with open('./site_check.log', 'r', encoding='UTF-8') as f:
            site_file = f.read().split('\n')
    except FileNotFoundError:
        with open('/home/pgadmin/reports_site/site_check.log', 'r', encoding='UTF-8') as f:
            site_file = f.read().split('\n')
    except Exception as e:
        print(e)
        site_file = 'Файл не найден'

    data = {
        'site_adm': site_adm_users,
        'log_file': file,
        'skks_file': skks_file,
        'site_file': site_file,
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

        user_name = self.request.user.first_name + ' ' + self.request.user.last_name
        # user_name = 'Екатерина Данилюк'

        shift_start = None
        shift_end = None

        if 8 <= datetime.datetime.now().hour < 20:
            shift_start = datetime.datetime.now().strftime('%Y-%m-%d 07:50:00+03')
            shift_end = datetime.datetime.now().strftime('%Y-%m-%d 20:10:00+03')
            print('\n')
            print(datetime.datetime.now())
            print(shift_start, shift_end, user_name, '\n')
        elif 20 <= datetime.datetime.now().hour < 24:
            shift_start = datetime.datetime.now().strftime('%Y-%m-%d 19:50:00+03')
            shift_end = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d 08:10:00+03')
            print('\n')
            print(datetime.datetime.now())
            print(shift_start, shift_end, user_name, '\n')
        elif 0 <= datetime.datetime.now().hour < 8:
            shift_start = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d 19:50:00+03')
            shift_end = datetime.datetime.now().strftime('%Y-%m-%d 08:10:00+03')
            print('\n')
            print(datetime.datetime.now())
            print(shift_start, shift_end, user_name, '\n')

        calls_in_count = AppealReport.objects.filter(appeal_type='Звонок входящий'). \
            filter(Q(user_name=user_name)).filter(Q(appeal_date__range=(shift_start, shift_end))).count()

        calls_out_count = AppealReport.objects.filter(appeal_type='Звонок исходящий'). \
            filter(Q(user_name=user_name)).filter(Q(appeal_date__range=(shift_start, shift_end))).count()

        mail_count = AppealReport.objects.filter(appeal_type='Почта'). \
            filter(Q(user_name=user_name)).filter(Q(appeal_date__range=(shift_start, shift_end))).count()

        chat_count = AppealReport.objects.filter(Q(appeal_type='Чат') & Q(user_name=user_name)). \
            filter(Q(appeal_date__range=(shift_start, shift_end))).count()

        telegram_count = AppealReport.objects.filter(Q(appeal_type='Телеграмм') & Q(user_name=user_name)). \
            filter(Q(appeal_date__range=(shift_start, shift_end))).count()

        whatsapp_count = AppealReport.objects.filter(Q(appeal_type='Ватсап') & Q(user_name=user_name)). \
            filter(Q(appeal_date__range=(shift_start, shift_end))).count()

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
    form_class = AppealReportForm
    template_name = 'main/appeal_rep.html'
    context_object_name = 'appeal_rep'
    paginate_by = 30

    def get_queryset(self):
        return AppealReport.objects.all().order_by('-id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AppealReportListView, self).get_context_data(**kwargs)
        context['form'] = self.form_class
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        context['support'] = User.objects.filter(groups__name='support')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['months'] = MonthsForm()
        context['years'] = YearsForm()
        return context


class UpdateAppealView(UpdateView):
    """ This class view add new call report """
    model = AppealReport
    form_class = AppealReportForm
    template_name = 'main/update_appeal.html'
    success_url = reverse_lazy('main:appeal_rep')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['support'] = User.objects.filter(groups__name='support')
        context['support_heads'] = User.objects.filter(groups__name='support_heads')
        return context


class GameListFromSkksView(ListView):
    """ This class return game list page """

    model = GameListFromSkks
    form_class = GameListFromSkksForm
    template_name = 'main/skks_games.html'
    context_object_name = 'game_list'
    paginate_by = 20

    def get_queryset(self):
        game_id = self.request.GET.get('game_id')
        game_name = self.request.GET.get('game_name')
        game_provider = self.request.GET.get('game_provider')
        queryset = GameListFromSkks.objects.all().order_by('game_id')

        try:
            if game_id is not None:
                game_id = game_id.strip()
                queryset = GameListFromSkks.objects.filter(Q(game_id=game_id)).order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_name is not None:
                game_name = game_name.strip()
                queryset = GameListFromSkks.objects.filter(Q(game_name__icontains=game_name)).order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_provider is not None:
                game_provider = game_provider.strip()
                queryset = GameListFromSkks.objects.filter(Q(game_provider__icontains=game_provider)) \
                    .order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GameListFromSkksView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['game_control'] = User.objects.filter(groups__name='game_control')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['games_count'] = GameListFromSkks.objects.all().count()
        return context


class GameListFromSkksTestView(ListView):
    """ This class return game list page """

    model = GameListFromSkksTest
    form_class = GameListFromSkksTestForm
    template_name = 'main/skks_games_test.html'
    context_object_name = 'game_list_test'
    paginate_by = 20

    def get_queryset(self):
        game_id = self.request.GET.get('game_id')
        game_name = self.request.GET.get('game_name')
        game_provider = self.request.GET.get('game_provider')
        queryset = GameListFromSkksTest.objects.all().order_by('game_id')

        try:
            if game_id is not None:
                game_id = game_id.strip()
                queryset = GameListFromSkksTest.objects.filter(Q(game_id=game_id)).order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_name is not None:
                game_name = game_name.strip()
                queryset = GameListFromSkksTest.objects.filter(Q(game_name__icontains=game_name)).order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_provider is not None:
                game_provider = game_provider.strip()
                queryset = GameListFromSkksTest.objects.filter(Q(game_provider__icontains=game_provider)) \
                    .order_by('game_id')
                return queryset
        except ValueError:
            return queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GameListFromSkksTestView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['game_control'] = User.objects.filter(groups__name='game_control')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['games_count'] = GameListFromSkksTest.objects.all().count()
        return context


class GameListFromSiteView(ListView):
    """ This class return game list page """

    model = GameListFromSite
    form_class = GameListFromSiteForm
    template_name = 'main/site_games.html'
    context_object_name = 'game_list_site'
    paginate_by = 20

    def get_queryset(self):
        game_name = self.request.GET.get('game_name')
        game_provider = self.request.GET.get('game_provider')
        game_status = self.request.GET.get('game_status')
        queryset = GameListFromSite.objects.all().order_by('game_name')

        try:
            if game_name is not None:
                game_name = game_name.strip()
                queryset = GameListFromSite.objects.filter(Q(game_name__icontains=game_name)) \
                    .order_by('game_name')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_provider is not None:
                game_provider = game_provider.strip()
                queryset = GameListFromSite.objects.filter(Q(game_provider__icontains=game_provider)) \
                    .order_by('game_name')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_status is not None:
                game_status = game_status.strip()
                queryset = GameListFromSite.objects.filter(Q(game_status__icontains=game_status)) \
                    .order_by('game_name')
                return queryset
        except ValueError:
            return queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GameListFromSiteView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['game_control'] = User.objects.filter(groups__name='game_control')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['games_count'] = GameListFromSite.objects.all().count()
        return context


class MissingGamesListView(ListView):
    """ This class compare tables with games """

    template_name = 'main/missing_games.html'
    context_object_name = 'missing_games'
    paginate_by = 20

    def get_queryset(self):
        queryset = GameListFromSite.objects.filter(~Q(game_name__in=GameListFromSkks.objects.values('game_name'))) \
            .filter(~Q(game_name__in=GameDisableList.objects.values('game_name'))).order_by('game_provider')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MissingGamesListView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['game_control'] = User.objects.filter(groups__name='game_control')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['games_count'] = GameListFromSite.objects \
            .filter(~Q(game_name__in=GameListFromSkks.objects.values('game_name'))) \
            .filter(~Q(game_name__in=GameDisableList.objects.values('game_name'))).count()
        return context


class GameDisableListView(ListView):
    """ This class return game list page """

    model = GameDisableList
    form_class = GameDisableListForm
    template_name = 'main/game_disable.html'
    context_object_name = 'game_disable_list'
    paginate_by = 20

    # games_count = GameDisableList.objects.all().count()

    def get_queryset(self):
        game_name = self.request.GET.get('game_name')
        game_provider = self.request.GET.get('game_provider')
        queryset = GameDisableList.objects.all().order_by('-game_disable_date')

        try:
            if game_name is not None:
                game_name = game_name.strip()
                queryset = GameDisableList.objects.filter(Q(game_name__icontains=game_name)) \
                    .order_by('game_name')
                return queryset
        except ValueError:
            return queryset

        try:
            if game_provider is not None:
                game_provider = game_provider.strip()
                queryset = GameDisableList.objects.filter(Q(game_provider__icontains=game_provider)) \
                    .order_by('game_name')
                return queryset
        except ValueError:
            return queryset

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(GameDisableListView, self).get_context_data(**kwargs)
        context['site_adm'] = User.objects.filter(groups__name='site_adm')
        context['game_control'] = User.objects.filter(groups__name='game_control')
        context['superuser'] = User.objects.filter(is_superuser=True)
        context['games_count'] = GameDisableList.objects.all().count()
        return context


class AddGameDisableView(View):
    """ This class add game to disable list """
    model = GameDisableList
    form_class = GameDisableListForm
    template_name = 'main/add_game_disable.html'
    success_url = '/disabled_games/'

    def get(self, request):
        site_adm_users = User.objects.filter(groups__name='site_adm')
        game_control_users = User.objects.filter(groups__name='game_control')

        data = {
            'site_adm': site_adm_users,
            'game_control': game_control_users,
            'superuser': User.objects.filter(is_superuser=True),
            'form': self.form_class,
        }
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class CCReportView(View):
    """ This class return CC report page """
    template_name = 'main/cc_report2.html'
    context_object_name = 'cc_report'

    month = datetime.datetime.now().month - 1
    year = datetime.datetime.now().year

    filter_date = str(month) + '-' + str(year)

    def get(self, request):
        site_adm_users = User.objects.filter(groups__name='site_adm')
        game_control_users = User.objects.filter(groups__name='game_control')

        get_uniq_users = CallsCheck.objects\
            .filter(upload_date_short__icontains=self.filter_date)\
            .values('user_name')\
            .distinct()

        user_report = []

        for user in get_uniq_users:
            user_name = user['user_name']

            answered_calls = CallsCheck.objects\
                .filter(upload_date_short__icontains=self.filter_date)\
                .filter(user_name=user_name)\
                .filter(~Q(call_result='нет ответа'))\
                .count()

            unanswered_calls = CallsCheck.objects\
                .filter(upload_date_short__icontains=self.filter_date)\
                .filter(user_name=user_name)\
                .filter(Q(call_result='нет ответа'))\
                .count()

            verifications = CallsCheck.objects\
                .filter(upload_date_short__icontains=self.filter_date)\
                .filter(user_name=user_name)\
                .filter(~Q(verified_date=None))\
                .count()

            deposit_count = CRMCheck.objects\
                .filter(upload_date_short__icontains=self.filter_date)\
                .filter(user_name=user_name)\
                .filter(~Q(first_deposit_date=None))\
                .count()

            deposit_sum = CRMCheck.objects\
                .filter(upload_date_short__icontains=self.filter_date)\
                .filter(user_name=user_name)\
                .filter(~Q(first_deposit_amount=None))\
                .aggregate(Sum('first_deposit_amount'))['first_deposit_amount__sum']

            if deposit_sum is None:
                deposit_sum = 0

            user_report.append({
                'user_name': user_name,
                'answered_calls': answered_calls,
                'unanswered_calls': unanswered_calls,
                'verifications': verifications,
                'deposit_count': deposit_count,
                'deposit_sum': deposit_sum,
            })

        data = {
            'site_adm': site_adm_users,
            'game_control': game_control_users,
            'superuser': User.objects.filter(is_superuser=True),
            'filter_date': self.filter_date,
            'user_report': user_report,
        }
        return render(request, self.template_name, data)
