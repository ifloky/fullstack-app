from django.db import models
from django.utils import timezone
import datetime


class RiskReport(models.Model):
    objects = None
    shift_date = models.DateField()
    shift_type = models.CharField(max_length=10)
    verified_clients = models.IntegerField()
    re_verified_clients = models.IntegerField()
    processed_conclusions = models.IntegerField()
    processed_support_requests = models.IntegerField()
    tacks_help_desk = models.IntegerField()
    oapi_requests = models.IntegerField()
    schemes_revealed = models.IntegerField()
    user_name = models.CharField(max_length=200)
    form_date_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shift_date

    class Meta:
        verbose_name = 'Личный отчет за смену'
        verbose_name_plural = 'Личный отчет за смену'


class RiskReportDay(models.Model):
    objects = None
    shift_date = models.DateField()
    foto_clients = models.IntegerField()
    deposits_sum = models.IntegerField()
    withdrawals_sum = models.IntegerField()
    ggr_sport = models.IntegerField()
    ggr_casino = models.IntegerField()
    withdrawals_5000 = models.IntegerField()
    user_name = models.CharField(max_length=200)
    form_date_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shift_date

    class Meta:
        verbose_name = 'Отчет за сутки'
        verbose_name_plural = 'Отчет за сутки'


class GetRiskReport(models.Model):
    objects = None
    shift_date = models.DateField()
    verified_clients = models.IntegerField()
    re_verified_clients = models.IntegerField()
    processed_conclusions = models.IntegerField()
    processed_support_requests = models.IntegerField()
    tacks_help_desk = models.IntegerField()
    oapi_requests = models.IntegerField()
    schemes_revealed = models.IntegerField()
    foto_clients = models.IntegerField()
    deposits_sum = models.IntegerField()
    withdrawals_sum = models.IntegerField()
    ggr_sport = models.IntegerField()
    ggr_casino = models.IntegerField()
    withdrawals_5000 = models.IntegerField()

    def __str__(self):
        return self.shift_date

    class Meta:
        verbose_name = 'Отчет по рискам'
        verbose_name_plural = 'Отчет по рискам'


class CallsCheck(models.Model):
    objects = None
    client_id = models.IntegerField(unique=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_phone = models.CharField(max_length=200)
    call_result = models.CharField(max_length=200, blank=True, null=True)
    call_date = models.DateTimeField(blank=True, null=True)
    verified_date = models.DateField(blank=True, null=True)
    user_name = models.CharField(max_length=200, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_date_short = models.CharField(max_length=7, default=datetime.date.today().strftime("%m-%Y"))
    calls_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.client_id

    class Meta:
        verbose_name = 'Проверка не верифицированных клиентов'
        verbose_name_plural = 'Проверка не верифицированных клиентов'


class CRMCheck(models.Model):
    objects = None
    client_id = models.IntegerField(unique=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_phone = models.CharField(max_length=200)
    call_result = models.CharField(max_length=200, blank=True, null=True)
    call_date = models.DateTimeField(blank=True, null=True)
    first_deposit_date = models.DateField(blank=True, null=True)
    first_deposit_amount = models.IntegerField(blank=True, null=True)
    user_name = models.CharField(max_length=200, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_date_short = models.CharField(max_length=7, default=datetime.date.today().strftime("%m-%Y"))
    calls_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.client_id

    class Meta:
        verbose_name = 'Проверка клиентов не сделавших депозит'
        verbose_name_plural = 'Проверка клиентов не сделавших депозит'


class AppealReport(models.Model):
    objects = None
    appeal_type = models.CharField(max_length=200)
    appeal_result = models.CharField(max_length=200)
    appeal_date = models.DateTimeField(default=timezone.localtime)
    user_name = models.CharField(max_length=200)
    appeal_date_short = models.CharField(max_length=7, default=datetime.date.today().strftime("%m-%Y"))

    def __str__(self):
        return self.appeal_type

    class Meta:
        verbose_name = 'Отчет по звонкам'
        verbose_name_plural = 'Отчет по звонкам'


class GameListFromSkks(models.Model):
    objects = None
    game_id = models.IntegerField()
    game_name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=200)
    game_provider = models.CharField(max_length=200)
    game_permitted_date = models.DateTimeField(default=timezone.localtime)
    game_name_find = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.game_name

    class Meta:
        verbose_name = 'Список игр из СККС (Production)'
        verbose_name_plural = 'Список игр из СККС (Production)'


class GameListFromSkksTest(models.Model):
    objects = None
    game_id = models.IntegerField()
    game_name = models.CharField(max_length=200)
    game_type = models.CharField(max_length=200)
    game_provider = models.CharField(max_length=200)
    game_permitted_date = models.DateTimeField(default=timezone.localtime)
    game_name_find = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.game_name

    class Meta:
        verbose_name = 'Список игр из СККС (Test)'
        verbose_name_plural = 'Список игр из СККС (Test)'


class GameListFromSite(models.Model):
    objects = None

    game_name = models.CharField(max_length=200)
    game_provider = models.CharField(max_length=200)
    game_status = models.CharField(max_length=200)
    game_name_find = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.game_name

    class Meta:
        verbose_name = 'Список игр из сайта (Production)'
        verbose_name_plural = 'Список игр из сайта (Production)'


class GameDisableList(models.Model):
    objects = None

    game_name = models.CharField(max_length=200)
    game_provider = models.CharField(max_length=200)
    game_disable_date = models.DateTimeField(default=timezone.localtime)
    user_name = models.CharField(max_length=200)
    game_name_find = models.CharField(null=True, blank=True, max_length=200,
                                      default='game_name'.upper().replace(' ', ''))

    def __str__(self):
        return self.game_name

    class Meta:
        verbose_name = 'Список отключенных игр'
        verbose_name_plural = 'Список отключенных игр'
