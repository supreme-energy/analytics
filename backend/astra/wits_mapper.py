import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astra.settings')
application = get_wsgi_application()

# from surveys.models import Survey
from edrs.livewits import edrdata, surveys
from edrs.models import EDRRaw
from django.utils.dateparse import parse_datetime


def witsmapper(uidWell, uidWellbore, data_frequency, url, username, password):
    edrs_on_job = EDRRaw.objects.filter(uid=uidWell)

    if edrs_on_job.count() != 0:
        # print("there are edrs on the job")
        lastest_edr = edrs_on_job.latest('id')
        latest_time = lastest_edr.rig_time
    else:
        latest_time = parse_datetime("2019-06-24T08:00:00-00:00")

    edrraw = edrdata(uidWell, uidWellbore, latest_time, data_frequency, url, username, password)

    for i in range(0, len(edrraw), 1):
        edr_rig_time = parse_datetime(edrraw.rig_time.values[i])

        if(edr_rig_time > latest_time and edrraw.hole_depth.values[i]):
            edr = EDRRaw(
                uid=uidWell,
                rig_time=edrraw.rig_time.values[i] if edrraw.rig_time.values[i] != "" else None,
                rop_a=edrraw.rop_a.values[i] if edrraw.rop_a.values[i] != "" else None,
                hole_size=edrraw.hole_size.values[i] if edrraw.hole_size.values[i] != "" else None,
                edr_mse=edrraw.edr_mse.values[i] if edrraw.edr_mse.values[i] != "" else None,
                bit_depth=edrraw.bit_depth.values[i] if edrraw.bit_depth.values[i] != "" else None,
                block_height=edrraw.block_height.values[i] if edrraw.block_height.values[i] != "" else None,
                diff_press=edrraw.diff_press.values[i] if edrraw.diff_press.values[i] != "" else None,
                rop_i=edrraw.rop_i.values[i] if edrraw.rop_i.values[i] != "" else 0,
                pump_press=edrraw.pump_press.values[i] if edrraw.pump_press.values[i] != "" else None,
                flow_in=edrraw.flow_in.values[i] if edrraw.flow_in.values[i] != "" else 0,
                flow_out=edrraw.flow_out.values[i] if edrraw.flow_out.values[i] != "" else None,
                gamma_ray=edrraw.gamma_ray.values[i] if edrraw.gamma_ray.values[i] != "" else None,
                overpull=edrraw.overpull.values[i] if edrraw.overpull.values[i] != "" else None,
                svy_azi=edrraw.svy_azi.values[i] if edrraw.svy_azi.values[i] != "" else None,
                tf_grav=edrraw.tf_grav.values[i] if edrraw.tf_grav.values[i] != "" else None,
                svy_inc=edrraw.svy_inc.values[i] if edrraw.svy_inc.values[i] != "" else None,
                tf_mag=edrraw.tf_mag.values[i] if edrraw.tf_mag.values[i] != "" else None,
                hookload=edrraw.hookload.values[i] if edrraw.hookload.values[i] != "" else 0,
                td_rpm=edrraw.td_rpm.values[i] if edrraw.td_rpm.values[i] != "" else None,
                td_torque=edrraw.td_torque.values[i] if edrraw.td_torque.values[i] != "" else None,
                mud_ti=edrraw.mud_ti.values[i] if edrraw.mud_ti.values[i] != "" else None,
                mud_to=edrraw.mud_to.values[i] if edrraw.mud_to.values[i] != "" else None,
                hole_depth=edrraw.hole_depth.values[i] if edrraw.hole_depth.values[i] != "" else None,
                total_spm=edrraw.total_spm.values[i] if edrraw.total_spm.values[i] != "" else None,
                strokes_total=edrraw.strokes_total.values[i] if edrraw.strokes_total.values[i] != "" else None,
                tvd=edrraw.tvd.values[i] if edrraw.tvd.values[i] != "" else None,
                wob=edrraw.wob.values[i] if edrraw.wob.values[i] != "" else None,
                oscillator=edrraw.oscillator.values[i] if edrraw.oscillator.values[i] != "" else False)
            edr.save()


    # edrraw, uidWell, uidWellbore, well_name, rig_name = surveys(rig_id)

    # surveys_on_job = Survey.objects.filter(uid=uidWell)

    # if surveys_on_job.count() != 0:
    #     print("there are surveys on the job")
    #     lastest_edr = surveys_on_job.latest('id')
    #     latest_time = lastest_edr.rig_time
    # else:
    #     print("there are no surveys on the job")
    #     latest_time = parse_datetime("1970-01-01T12:00:00-00:00")

    # for i in range(0, len(edrraw), 1):
    #     edr_rig_time = parse_datetime(edrraw.rig_time.values[i])
    #     if(edr_rig_time > latest_time):
    #         print("Survey on Rig: ", rig_id, " -- Time: ", latest_time)
    #         survey = Survey(
    #             uid=uidWell,
    #             rig_time=edrraw.rig_time.values[i],
    #             md=edrraw.md.values[i],
    #             tvd=edrraw.tvd.values[i],
    #             inc=edrraw.incl.values[i],
    #             azi=edrraw.azi.values[i],
    #             edr_dls=edrraw.dls.values[i],
    #             edr_dispNs=edrraw.dispNs.values[i],
    #             edr_dispEw=edrraw.dispEw.values[i],
    #             person=Person.objects.get(pk=1),  # Required
    #             name="Totco",  # Required
    #             north="0",  # Required
    #             east="0",  # Required
    #             vertical_section="0",  # Required
    #             dogleg="0",  # Required
    #             build_rate="0",  # Required
    #             turn_rate="0",  # Required
    #             calculated_tf="0",  # Required
    #             calculated_ang="0",  # Required
    #             step_out="0"  # Required
    #         )
    #         survey.save()
