from django.db import models
from django.utils.translation import ugettext as _
from handle_cron import make_file, manage_cron


class Job(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    well_api = models.CharField(max_length=14, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)  # auto generated
    spud_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    sses_id = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Jobs"


class WellConnector(models.Model):
    job = models.OneToOneField(
        Job, related_name="job_well_connectors", on_delete=models.PROTECT, null=True, blank=True)
    uid = models.CharField(max_length=50)
    uidWellbore = models.CharField(max_length=50, null=True, blank=True)
    well_name = models.CharField(max_length=50)
    rig_name = models.CharField(max_length=50, null=True, blank=True)
    data_frequency = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    cron_on = models.BooleanField(default=False)
    data_valid = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(WellConnector, self).__init__(*args, **kwargs)
        self.__original_cron_on = self.cron_on

    def save(self, *args, **kwargs):
        connector_being_added = False

        if self.pk is None:
            connector_being_added = True

        # Well connector being added
        if connector_being_added:
            make_file(self.uid, self.uidWellbore, self.data_frequency,
                      self.url, self.username, self.password, self.cron_on)

        # Well connector being edited and cron_on changed
        if connector_being_added is False and self.cron_on != self.__original_cron_on:
            manage_cron(self.uid, self.cron_on)

        super(WellConnector, self).save(*args, **kwargs)

    def __str__(self):
        return self.well_name

    class Meta:
        verbose_name_plural = "Well Connectors"


class Interval(models.Model):
    job = models.ForeignKey(Job, related_name="job_intervals",
                            on_delete=models.PROTECT)  # 0 or Many Intervals to 1 Job
    name = models.CharField(max_length=20)
    hole_size = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    start_depth = models.DecimalField(max_digits=8, decimal_places=2)
    end_depth = models.DecimalField(max_digits=8, decimal_places=2)
    cased = models.BooleanField(default=False)
    casing_size = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Intervals"


class Formation(models.Model):
    job = models.ForeignKey(Job, related_name="job_formations",
                            on_delete=models.PROTECT)
    name = models.CharField(max_length=20)
    start_depth = models.DecimalField(max_digits=8, decimal_places=2)
    end_depth = models.DecimalField(max_digits=8, decimal_places=2)
    rock_type = models.CharField(max_length=20, null=True, blank=True)
    pore_pressure = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)
    mud_weight = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Formations"
