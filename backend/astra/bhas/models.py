from django.db import models
from jobs.models import Job


class Bha(models.Model):
    job = models.ForeignKey(Job, related_name="job_bhas",
                            on_delete=models.PROTECT)  # 0 or many Bhas to 1 Job
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    bha_number = models.IntegerField(null=True, blank=True)  # auto generated
    bha_length = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    depth_in = models.IntegerField()
    depth_out = models.IntegerField(null=True, blank=True)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    drill_time_start = models.DateTimeField(null=True, blank=True)
    drill_time_end = models.DateTimeField(null=True, blank=True)
    hole_size = models.DecimalField(max_digits=10, decimal_places=3)
    survey_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    gamma_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    resistivity_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    shock_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    pressure_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    nb_gamma_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    nb_inc_distance = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    downhole_hrs = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    circulating_hrs = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    drilling_hrs = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    sliding_hrs = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    rotating_hrs = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    feet_slid = models.CharField(max_length=50, null=True, blank=True)
    feet_rotated = models.CharField(max_length=50, null=True, blank=True)
    total_rop = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True)
    inc_in = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    inc_out = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    azi_in = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    azi_out = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    dogleg = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    motor_yield = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    build_rate = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    turn_rate = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    sliding_rop = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True)
    rotating_rop = models.DecimalField(
        max_digits=6, decimal_places=1, null=True, blank=True)
    footage_drilled = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Bhas"
