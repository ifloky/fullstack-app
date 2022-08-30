from django.db import models


class RiskReport(models.Model):

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
