from rest_framework import serializers, status
from math import radians, cos, sin

from surveys.models import Survey
from jobs.models import Job
from plans.models import Plan


class SurveySerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    dist_plan = serializers.SerializerMethodField(read_only=True)

    def get_dist_plan(self, obj):
        active_survey = Survey.objects.filter(job=obj.job).last()

        if active_survey and active_survey.id == obj.id:
            print("active_survey", active_survey)
            print("active_survey_id", active_survey.id, obj.id)
            md_s = None if obj.md is None else float(obj.md)
            tvd_s = None if obj.tvd is None else float(obj.tvd)
            north_s = None if obj.north is None else float(obj.north)
            east_s = None if obj.east is None else float(obj.east)

            plans_on_job = Plan.objects.filter(job=obj.job)
            tvd_pgt = None
            md_pgt = None
            tvd_plt = None
            md_plt = None
            vsplane_p = None
            tvd_intp = None
            abs_tvd_intp = None
            right_left_intp = None
            abs_right_left_intp = None
            north_pgt = None

            plan_pt_gt = plans_on_job.filter(md__gt=md_s).first()
            if plan_pt_gt:
                vsplane_p = float(plan_pt_gt.vsplane)
                plan_tvd_intp = tvd_pgt = float(plan_pt_gt.tvd)
                tvd_intp = tvd_s - plan_tvd_intp
                abs_tvd_intp = abs(tvd_intp)
                md_pgt = float(plan_pt_gt.md)
                plan_north_intp = north_pgt = float(plan_pt_gt.north)
                plan_east_intp = east_pgt = float(plan_pt_gt.east)
                right_left_intp = cos(radians(vsplane_p))*(north_s - plan_north_intp) + sin(
                    radians(vsplane_p))*(east_s - plan_east_intp)
                abs_right_left_intp = abs(rl_intp)

            plan_pt_lt = plans_on_job.filter(md__lt=md_s).last()
            if plan_pt_lt:
                vsplane_p = float(plan_pt_lt.vsplane)
                plan_tvd_intp = tvd_plt = float(plan_pt_lt.tvd)
                tvd_intp = tvd_s - plan_tvd_intp
                abs_tvd_intp = abs(tvd_intp)
                md_plt = float(plan_pt_lt.md)
                plan_north_intp = north_plt = float(plan_pt_lt.north)
                plan_east_intp = east_plt = float(plan_pt_lt.east)
                right_left_intp = cos(radians(vsplane_p))*(north_s - plan_north_intp) + sin(
                    radians(vsplane_p))*(east_s - plan_east_intp)
                abs_right_left_intp = abs(right_left_intp)

            if tvd_pgt and md_pgt and tvd_plt and md_plt:
                plan_tvd_intp = tvd_plt + \
                    (tvd_pgt - tvd_plt)(md_s - md_plt) / (md_pgt - md_plt)
                tvd_intp = tvd_s - plan_tvd_intp
                abs_tvd_intp = abs(tvd_intp)

            if north_pgt and east_pgt and east_plt and md_pgt and north_plt and md_plt and vsplane_p:
                plan_north_intp = north_plt + \
                    (north_pgt - north_plt)(md_s - md_plt) / (md_pgt - md_plt)
                plan_east_intp = east_plt + \
                    (east_pgt - east_plt)(md_s - md_plt) / (md_pgt - md_plt)
                right_left_intp = cos(radians(vsplane_p))*(north_s - plan_north_intp) + sin(
                    radians(vsplane_p))*(east_s - plan_east_intp)
                abs_right_left_intp = abs(right_left_intp)

            return {
                "survey_high_low": "" if abs_tvd_intp is None else abs_tvd_intp,
                "survey_high_low_label": "" if tvd_intp is None else "High" if tvd_intp > 0 else "Low",
                "survey_right_left": "" if abs_right_left_intp is None else abs_right_left_intp,
                "survey_right_left_label": "" if right_left_intp is None else "Left" if right_left_intp > 0 else "Right",
            }

        else:
            return ""

    class Meta:
        model = Survey
        fields = '__all__'
        read_only_fields = ('creation_date', 'number', 'active')
        extra_kwargs = {
            'mag_total': {'allow_null': True, 'required': False},
            'grav_total': {'allow_null': True, 'required': False},
            'dip': {'allow_null': True, 'required': False},
            'temp': {'allow_null': True, 'required': False},
            'zero_vs': {'allow_null': True, 'required': False},
            'uid': {'allow_null': True, 'required': False},
            'rig_time': {'allow_null': True, 'required': False},
        }
