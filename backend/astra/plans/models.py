from django.db import models
from jobs.models import Job


class Plan(models.Model):
    job = models.ForeignKey(
        Job, related_name="job_plans", on_delete=models.PROTECT)
    creation_date = models.DateTimeField(auto_now_add=True)  # auto generated
    md = models.DecimalField(max_digits=10, decimal_places=2)
    inc = models.DecimalField(max_digits=10, decimal_places=3)
    azi = models.DecimalField(max_digits=10, decimal_places=3)
    tvd = models.DecimalField(max_digits=10, decimal_places=2)
    north = models.DecimalField(max_digits=10, decimal_places=2)
    east = models.DecimalField(max_digits=10, decimal_places=2)
    vertical_section = models.DecimalField(max_digits=10, decimal_places=2)
    dogleg = models.DecimalField(max_digits=10, decimal_places=2)
    build_rate = models.DecimalField(max_digits=10, decimal_places=2)
    turn_rate = models.DecimalField(max_digits=10, decimal_places=2)
    calculated_tf = models.DecimalField(max_digits=10, decimal_places=2)
    depth_in_zone = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    zero_vs = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    step_out = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    # will need to be validated - only 1 plan can be active at a time per job
    active = models.BooleanField(default=True)
    tie_in_depth = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    # use this value if user provides else, use old method for vsplane
    vsplane = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.job

    class Meta:
        verbose_name_plural = "Plans"
