from django.db import models
from jobs.models import Job
from .survey_mc import survey_mc


class Survey(models.Model):
    job = models.ForeignKey(Job, related_name="job_surveys",
                            on_delete=models.PROTECT, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField(null=True, blank=True)
    md = models.DecimalField(max_digits=10, decimal_places=2)
    inc = models.DecimalField(max_digits=10, decimal_places=3)
    azi = models.DecimalField(max_digits=10, decimal_places=3)
    tvd = models.DecimalField(max_digits=10, decimal_places=3)
    north = models.DecimalField(max_digits=10, decimal_places=3)
    east = models.DecimalField(max_digits=10, decimal_places=3)
    vertical_section = models.DecimalField(max_digits=10, decimal_places=3)
    dogleg = models.DecimalField(max_digits=10, decimal_places=3)
    build_rate = models.DecimalField(max_digits=10, decimal_places=3)
    turn_rate = models.DecimalField(max_digits=10, decimal_places=3)
    calculated_tf = models.DecimalField(max_digits=10, decimal_places=3)
    calculated_ang = models.DecimalField(max_digits=10, decimal_places=3)
    clos_dist = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    clos_azi = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    mag_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    grav_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    dip = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    temp = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    zero_vs = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    step_out = models.DecimalField(
        max_digits=10, decimal_places=2)
    my = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    active = models.NullBooleanField()  # auto
    uid = models.CharField(max_length=50, null=True, blank=True)
    rig_time = models.DateTimeField(null=True, blank=True)
    edr_dls = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    edr_dispNs = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    edr_dispEw = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Retrieve surveys on job
        surveys_on_job = Survey.objects.filter(job=self.job)
        survey_being_added = False
        survey_being_edited = False

        if self.pk is None:
            survey_being_added = True
        else:
            survey_being_edited = True

        # If first survey on job
        if surveys_on_job.count() == 0:
            # print("First Survey on the Job")
            self.number = 1
            self.active = True

        # Other surveys exist on job - survey being edited
        elif self.active:
            # print("Survey is being edited")
            previous_survey = surveys_on_job.get(number=(self.number - 1))

            self.north, self.east, self.tvd, self.build_rate, self.turn_rate, self.calculated_tf, self.calculated_ang, self.step_out, self.dogleg = survey_mc(
                previous_survey, self.inc, self.azi, self.md)

        # Other surveys exist on job - survey being added
        else:
            # Last survey on job
            previous_survey = surveys_on_job.latest('id')

            self.number = previous_survey.number + 1
            self.active = True

            self.north, self.east, self.tvd, self.build_rate, self.turn_rate, self.calculated_tf, self.calculated_ang, self.step_out, self.dogleg = survey_mc(
                previous_survey, self.inc, self.azi, self.md)

        super(Survey, self).save(*args, **kwargs)

    def __str__(self):
        return self.job

    class Meta:
        verbose_name_plural = "Surveys"
