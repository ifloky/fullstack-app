from django.db import models


class Equipment(models.Model):

    apteka_id = models.DecimalField(max_digits=10, decimal_places=0)
    equipment_type = models.CharField(max_length=200)
    equipment_model = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=200, unique=True)
    invoice_number = models.CharField(null=True, blank=True, max_length=200)
    invoice_date = models.DateField(null=True, blank=True)
    purchase_org = models.CharField(null=True, blank=True, max_length=200)
    comments = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.apteka_id

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'


class Security(models.Model):

    apteka_id = models.DecimalField(max_digits=10, decimal_places=0)
    service_name = models.CharField(max_length=200)
    service_ip = models.CharField(max_length=200)
    service_login = models.CharField(null=True, blank=True, max_length=200)
    service_pass = models.CharField(null=True, blank=True, max_length=200)
    service_info = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.apteka_id

    class Meta:
        verbose_name = 'Схема локальной сети'
        verbose_name_plural = 'Схема локальной сети'


class Apteka(models.Model):

    objects = None
    id = models.DecimalField(max_digits=10, decimal_places=0, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.id

    class Meta:
        managed = False
        verbose_name = 'Аптека'
        verbose_name_plural = 'Аптеки'
