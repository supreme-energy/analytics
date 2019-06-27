from django.db import models
from jobs.models import Job
from .lineproj_mc import lineproj_mc
from .bitproj_mc import bitproj_mc
from surveys.models import Survey


class Projection(models.Model):
    job = models.ForeignKey(
        Job, related_name="job_projections", on_delete=models.PROTECT)
    type = models.CharField(max_length=50, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)  # auto generated
    number = models.IntegerField(null=True, blank=True)
    md = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    inc = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    azi = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    tvd = models.DecimalField(max_digits=10, decimal_places=2)
    north = models.DecimalField(max_digits=10, decimal_places=2)
    east = models.DecimalField(max_digits=10, decimal_places=2)
    vertical_section = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)  # null for line and bit projection
    dogleg = models.DecimalField(max_digits=10, decimal_places=2)
    my = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)  # null for line projection
    build_rate = models.DecimalField(max_digits=10, decimal_places=2)
    turn_rate = models.DecimalField(max_digits=10, decimal_places=2)
    bitto_sensor = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)  # null for line projection
    sli_length = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)  # null for line projection
    calculated_tf = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.NullBooleanField()  # auto

    def save(self, *args, **kwargs):
        # Set vertical_section to 0
        self.vertical_section = 0
        projection_being_added = False
        projection_being_edited = False

        if self.pk is none:
            projection_being_added = True
        else:
            projection_being_edited = True

        try:
            # Retrieve projection on job
            projections_on_job = Projection.objects.filter(job=self.job)
            projections_by_type = projections_on_job.filter(type=self.type)

            # If first projection on job
            if projections_by_type.count() == 0:
                print("First Projection by type on the Job")
                self.number = 1
                self.active = True
                self.md = 0
                self.inc = 0
                self.azi = 0

            # Other projections exist on job - projection being edited
            elif self.active:
                print("Projection is being edited")
                previous_projection = projections_on_job.get(
                    number=(self.number - 1))

            # Other projections exist on job - projection being added
            else:
                print(self.type, "projection is being added")
                # Last projection on job
                projection_on_job_prev = projections_on_job.latest('id')

                # Last projection on job, by type
                projection_by_type_prev = projections_by_type.latest('id')

                # Set the previous projection by type (Line / Bit) to false
                projection_by_type_prev.active = False

                # Set current projection number to previous projection number + 1
                self.number = projection_on_job_prev.number + 1
                self.active = True

                try:
                    super(Projection, projection_by_type_prev).save(
                        update_fields=["active"])
                except:
                    print("Failed to update previous line projection")

            # Get active survey on job
            surveys_on_job = Survey.objects.filter(job=self.job)
            active_survey_on_job = surveys_on_job.get(active=True)

            if str(self.type) == "Line" and active_survey_on_job is not None:
                print("In line calculations")
                self.north, self.east, self.tvd, self.build_rate, self.turn_rate, self.calculated_tf, self.dogleg = lineproj_mc(
                    active_survey_on_job, self.inc, self.azi, self.md)

            if str(self.type) == "Bit" and active_survey_on_job is not None:
                print("In bit calculations")
                self.north, self.east, self.tvd, self.build_rate, self.turn_rate, self.calculated_tf, self.dogleg, self.md, self.inc, self.azi = bitproj_mc(
                    active_survey_on_job, self.calculated_tf, self.my, self.sli_length, self.bitto_sensor)

            super(Projection, self).save(*args, **kwargs)

        except Exception as e:
            print(e)

    def delete(self):
        super(Projection, self).delete()
        # Set latest projection active to true
        projections_by_type = Projection.objects.filter(
            job=self.job, type=self.type)

        if projections_by_type is None:
            projection_by_type_prev = projections_by_type.latest('id')
            print(projection_by_type_prev.count())
            projection_by_type_prev.active = True
            super(Projection, projection_by_type_prev).save(
                update_fields=["active"])

    def __str__(self):
        return self.job

    class Meta:
        verbose_name_plural = "Projections"
