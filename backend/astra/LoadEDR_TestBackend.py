###############################################################
# Scripts to load data into database
###############################################################

# Example:


# Delete db.sqlite3

# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser

###############################################################

# To Start Run:
# python manage.py shell -i python
# Copy Data Below And Paste into terminal. Hit enter twice to start loading data

from django.contrib.auth.models import User
from jobs.models import Job, WellConnector
from edrs.models import EDRRaw
from personnel.models import Person, NotificationType


import json


with open('Clydesdale_Raw_Example.json', encoding="utf8") as f:
    edrs_json = json.load(f)


for edr in edrs_json:
    # try:
        edr = EDRRaw(
            job_id= edr['job_id'],
            uid=edr['uid'],
            creation_date=edr['creation_date'],
            active=edr['active'],
            rig_time=edr['rig_time'],
            hole_depth=edr['hole_depth'],
            wob=edr['wob'],
            td_rpm=edr['td_rpm'],
            td_torque=edr['td_torque'],
            rop_a=edr['rop_a'],
            diff_press=edr['diff_press'],
            flow_in=edr['flow_in'],
            pump_press=edr['pump_press'],
            edr_mse=edr['edr_mse'],
            bit_depth=edr['bit_depth'],
            block_height=edr['block_height'],
            gamma_ray=edr['gamma_ray'],
            hookload=edr['hookload'],
            mud_ti=edr['mud_ti'],
            mud_to=edr['mud_to'],
            mud_wi=edr['mud_wi'],
            mud_wo=edr['mud_wo'],
            overpull=edr['overpull'],
            strokes_total=edr['strokes_total'],
            rop_i=edr['rop_i'],
            svy_azi=edr['svy_azi'],
            svy_inc=edr['svy_inc'],
            tf_grav=edr['tf_grav'],
            tf_mag=edr['tf_mag'],
            tvd=edr['tvd'],
            flow_out=edr['flow_out'],
            ann_press=edr['ann_press'],
            back_press=edr['back_press'],
            edr_RS1=edr['edr_RS1'],
            edr_RS2=edr['edr_RS2'],
            edr_RS3=edr['edr_RS3'],
            edr_slips=edr['edr_slips'],
            oscillator=edr['oscillator'])
        edr.save()
    # except:
    #     print("edr Not Loaded")
