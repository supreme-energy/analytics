###############################################################
# Scripts to load data into database
###############################################################

# Delete all files in the migrations folder, except __init__.py


# Please change the path to the migrations folder
# Migration folder path is $MigrationPath = "manage.py location" + "\*\migrations\*"

# Example:
# $MigrationPath = "C:\Users\BrianBlackwell\Documents\AstraAnimo\Animo-Backend\backend\astra\*\migrations\*"
# $MigrationPath = "D:\AstraInovationProjects\Animo-Backend\backend\astra\*\migrations\*"
# Remove-Item -Recurse -Path $MigrationPath -Exclude "__init__.py" -Verbose -Force


# Delete db.sqlite3

# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser

###############################################################

# To Start Run:
# python manage.py shell -i python

from django.contrib.auth.models import User
from bids.models import Bid, BidItem, Pricing
from jobs.models import Job, Rig, County, Play, State, Shipment, ShipItem, RigItem
from districts.models import District
from partners.models import Partner
from personnel.models import Person, NotificationType
from activities.models import ActivityGroup, Activity
from activities.models import ActivityType
from surveys.models import Survey
from plans.models import Plan
from assets.models import Asset, Connection, PipeDiameter, Manufacturer, Vendor, BitSize
from bhas.models import Bha

import json

# with open('bitsizes.json') as f:
#     bitsizes_json = json.load(f)


# for size in bitsizes_json:
#     size = BitSize(value=size['value'])
#     size.save()


with open('notificationtypes.json') as f:
    notificationtypes_json = json.load(f)


for type in notificationtypes_json:
    type = NotificationType(name=type['name'])
    type.save()


# with open('connections.json') as f:
#     connections_json = json.load(f)


# for connection in connections_json:
#     connection = Connection(value=connection['value'], type=connection['type'])
#     connection.save()


# with open('pipediameters.json') as f:
#     diameters_json = json.load(f)


# for diameter in diameters_json:
#     diameter = PipeDiameter(value=diameter['value'], type=diameter['type'])
#     diameter.save()


with open('manufacturers.json') as f:
    manufacturers_json = json.load(f)


for manufacturer in manufacturers_json:
    manufacturer = Manufacturer(name=manufacturer['name'])
    manufacturer.save()


with open('vendors.json') as f:
    vendors_json = json.load(f)


for vendor in vendors_json:
    vendor = Vendor(name=vendor['name'])
    vendor.save()


with open('activitygroups.json') as f:
    groups_json = json.load(f)


for group in groups_json:
    group = ActivityGroup(name=group['name'])
    group.save()


with open('activitytypes.json') as f:
    types_json = json.load(f)


for atype in types_json:
    atype = ActivityType(name=atype['name'],
                         activity_group=atype['activity_group'])
    atype.save()


with open('counties.json') as f:
    counties_json = json.load(f)


for county in counties_json:
    county = County(name=county['county'], state=county['state'])
    county.save()


with open('states.json') as f:
    states_json = json.load(f)


for state in states_json:
    state = State(name=state['Name'])
    state.save()


# with open('play.json') as f:
#     play_json = json.load(f)


# for play in play_json:
#     play = Play(name=play['play'])
#     play.save()


with open('2019_June_partners.json') as f:
    partners_json = json.load(f)


for partner in partners_json:
    partner = Partner(name=partner['name'], type=partner['type'],
                      act_id=partner['act_id'], active=partner['active'])
    partner.save()


with open('2019_June_Oxy_rigs.json') as f:
    rigs_json = json.load(f)


for rig in rigs_json:
    rig = Rig(name=rig['name'], partner=Partner.objects.get(
        pk=int(rig['partner'])), company=rig['company'], active=rig['active'])
    rig.save()


with open('districts.json') as f:
    districts_json = json.load(f)


for district in districts_json:
    district = District(name=district['name'], type=district['type'])
    district.save()

with open('users.json', encoding="utf8") as f:
    user_json = json.load(f)


for user in user_json:
    user = User.objects.create_user(
        username=user['username'], password=user['password'])
    user.is_staff = True
    user.save()

with open('personnel.json') as f:
    personnel_json = json.load(f)


for person in personnel_json:
    person = Person(
        first_name=person['first_name'],
        last_name=person['last_name'],
        email=person['email'],
        type=person['type'],
        position=person['position'],
        level=person['level'],
        user=User.objects.get(pk=int(person['user'])),
        status=person['status'],
        phone=person['phone'],
        e_contact_first_name=person['e_contact_first_name'],
        e_contact_last_name=person['e_contact_last_name'],
        e_contact_cell_phone=person['e_contact_cell_phone'],
        e_contact_work_phone=person['e_contact_work_phone'],
        e_contact_relationship=person['e_contact_relationship'],)
    person.save()


# with open('bids.json') as f:
#     bids_json = json.load(f)


# for bid in bids_json:
#     bidIns = Bid(district=District.objects.get(pk=int(bid['district'])),
#                  job_type=bid['job_type'],
#                  partner=Partner.objects.get(pk=int(bid['partner'])),
#                  effective_date=bid['effective_date'],
#                  operator_partner=Partner.objects.get(
#                  pk=int(bid['operator_partner'])),
#                  is_active=True,
#                  is_template=bid['is_template'],
#                  submitter=Person.objects.get(pk=int(bid['submitter'])))
#     bidIns.save()

# with open('bid_items.json', encoding="utf8") as f:
#     biditems_json = json.load(f)


# for item in biditems_json:
#     item = BidItem(creation_date=item['creation_date'],
#                    last_edit_date=item['last_edit_date'],
#                    category=item['category'],
#                    description=item['description'],
#                    status_change=item['status_change'],
#                    is_active=item['is_active'],
#                    submitter=Person.objects.get(pk=int(item['submitter'])),
#                    base_price=item['base_price'],
#                    base_unit=item['base_unit'])
#     item.save()

# with open('bid_pricing.json', encoding="utf8") as f:
#     bidprices_json = json.load(f)


# for price in bidprices_json:
#     price = Pricing(
#         bid_item=BidItem.objects.get(pk=int(price['bid_item'])),
#         notes=price['notes'],
#         bid=Bid.objects.get(pk=int(price['bid'])),
#         prop_price=price['prop_price'],
#         unit=price['prop_unit'])
#     price.save()


with open('2019_June_Oxy_jobs.json', encoding="utf8") as f:
    jobs_json = json.load(f)


for job in jobs_json:
    try:
        job = Job(name=job['name'],
                  type=job['type'],
                  status=job['status'],
                  partner=Partner.objects.get(pk=int(job['partner'])),
                  main_rig=Rig.objects.get(pk=int(job['main_rig'])),
                  legal_name=job['legal_name'],
                  latitude=job['latitude'],
                  longitude=job['longitude'],
                  state=job['state'],
                  county=County.objects.get(pk=int(job['county'])),
                  play=job['play'], timezone=job['timezone'],
                  directions=job['directions'],
                  well_afe=job['well_afe'],
                  well_comments=job['well_comments'],
                  well_notes=job['well_notes'],
                  dip_angle=job['dip_angle'],
                  declination=job['declination'],
                  intensity=job['intensity'],
                  valid_date=job['valid_date'],
                  job_number=job['job_number'],
                  #   bid=Bid.objects.get(pk=int(job['bid'])),
                  est_start_date=job['est_start_date'],
                  est_end_date=job['est_end_date'],
                  northref=str(job['northref']),
                  district=District.objects.get(pk=int(job['district'])))
        job.save()
    except:
        print("Job Not Loaded")


with open('plan_3.json', encoding="utf8") as f:
    plan_json = json.load(f)

for plan in plan_json:
    try:
        plan = Plan(
            person=Person.objects.get(pk=int(plan['person'])),
            job=Job.objects.get(pk=int(plan['job'])),
            creation_date=plan['creation_date'],
            name=plan['name'],
            number=plan['number'],
            active=plan['active'],
            md=plan['md'],
            inc=plan['inc'],
            azi=plan['azi'],
            tvd=plan['tvd'],
            north=plan['north'],
            east=plan['east'],
            vertical_section=plan['vertical_section'],
            dogleg=plan['dogleg'],
            build_rate=plan['build_rate'],
            turn_rate=plan['turn_rate'],
            calculated_tf=plan['calculated_tf'],
            zero_vs=plan['zero_vs'],
            step_out=plan['step_out'],
            tie_in_depth=plan['tie_in_depth'])
        plan.save()
    except:
        print("bad plan")


with open('motors.json', encoding="utf8") as f:
    assets_json = json.load(f)

for asset in assets_json:
    asset = Asset(
        asset_group=asset["asset_group"],
        asset_type=asset["asset_type"],
        serial_num=asset["serial_num"],
        part_num=asset["part_num"],
        rig_item=asset["rig_item"],
        rented=asset["rented"],
        condition_status=asset["condition_status"],
        size=asset["size"],
        length=asset["length"],
        inner_diam=asset["inner_diam"],
        outter_diam=asset["outter_diam"],
        manufacturer=asset["manufacturer"],
        vendor=asset["vendor"],
        initiation_date=asset["initiation_date"],
        service_hours=asset["service_hours"],
        service_date=asset["service_date"],
        dc_hours=asset["dc_hours"],
        top_cxn=asset["top_cxn"],
        bottom_cxn=asset["bottom_cxn"],
        notes=asset["notes"])
    asset.save()

with open('mwd.json', encoding="utf8") as f:
    assets_json = json.load(f)

for asset in assets_json:
    asset = Asset(
        asset_group=asset["asset_group"],
        asset_type=asset["asset_type"],
        serial_num=asset["serial_num"],
        part_num=asset["part_num"],
        rig_item=asset["rig_item"],
        rented=asset["rented"],
        condition_status=asset["condition_status"],
        size=asset["size"],
        length=asset["length"],
        inner_diam=asset["inner_diam"],
        outter_diam=asset["outter_diam"],
        manufacturer=asset["manufacturer"],
        vendor=asset["vendor"],
        initiation_date=asset["initiation_date"],
        service_hours=asset["service_hours"],
        service_date=asset["service_date"],
        dc_hours=asset["dc_hours"],
        top_cxn=asset["top_cxn"],
        bottom_cxn=asset["bottom_cxn"],
        notes=asset["notes"])
    asset.save()

with open('bits.json', encoding="utf8") as f:
    assets_json = json.load(f)

for asset in assets_json:
    asset = Asset(
        asset_group=asset["asset_group"],
        asset_type=asset["asset_type"],
        serial_num=asset["serial_num"],
        rig_item=asset["rig_item"],
        rented=asset["rented"],
        condition_status=asset["condition_status"],
        size=asset["size"],
        length=asset["length"],
        inner_diam=asset["inner_diam"],
        outter_diam=asset["outter_diam"],
        manufacturer=asset["manufacturer"],
        vendor=asset["vendor"],
        initiation_date=asset["initiation_date"],
        service_hours=asset["service_hours"],
        service_date=asset["initiation_date"],
        dc_hours=asset["dc_hours"],
        top_cxn=asset["top_cxn"],
        bottom_cxn=asset["bottom_cxn"],
        notes=asset["notes"])
    asset.save()

with open('bit_rigitem.json', encoding="utf8") as f:
    rigitem_json = json.load(f)

for rigitem in rigitem_json:
    try:
        rigitems = RigItem(
            job=Job.objects.get(pk=rigitem["job"]),
            asset=Asset.objects.get(pk=rigitem["asset"]),
            rig=Rig.objects.get(pk=int(rigitem["rig"])),
            one_time_use=rigitem["one_time_use"],
            active=rigitem["active"])
        rigitems.save()
    except:
        print(rigitem["job"])

with open('motors_shipable.json', encoding="utf8") as f:
    assets_json = json.load(f)

for asset in assets_json:
    asset = Asset(
        asset_group=asset["asset_group"],
        asset_type=asset["asset_type"],
        serial_num=asset["serial_num"],
        rig_item=asset["rig_item"],
        rented=asset["rented"],
        condition_status=asset["condition_status"],
        size=asset["size"],
        length=asset["length"],
        inner_diam=asset["inner_diam"],
        outter_diam=asset["outter_diam"],
        manufacturer=asset["manufacturer"],
        vendor=asset["vendor"],
        initiation_date=asset["initiation_date"],
        service_hours=asset["service_hours"],
        service_date=asset["service_date"],
        dc_hours=asset["dc_hours"],
        top_cxn=asset["top_cxn"],
        bottom_cxn=asset["bottom_cxn"],
        notes=asset["notes"])
    asset.save()

with open('bha_fulldata.json', encoding="utf8") as f:
    bhas_json = json.load(f)

for bha in bhas_json:
    try:
        bhaIns = Bha(
            job=Job.objects.get(pk=int(bha['job'])),
            person=Person.objects.get(pk=int(bha['person'])),
            creation_date=bha['creation_date'],
            name=bha['name'],
            type=bha['type'],
            status=bha['status'],
            status_change=bha['status_change'],
            bha_number=bha['bha_number'],
            hole_size=bha['hole_size'],
            depth_in=bha['depth_in'],
            depth_out=bha['depth_out'],
            time_in=bha['time_in'],
            time_out=bha['time_out'],
            interval=bha['hole_section'],
            incident=bha['incident'],
            incident_comments=bha['incident_comments'],
            trip_reason=bha['trip_reason'],
            trip_comments=bha['trip_comments'],
            is_template=bha['is_template'],
            trajectory=bha['trajectory'],
            objective=bha['objective'],
            comments=bha['comments'],
            survey_distance=bha['survey_distance'],
            gamma_distance=bha['gamma_distance'],
            downhole_hrs=bha['downhole_hrs'],
            circulating_hrs=bha['circulating_hrs'],
            drilling_hrs=bha['drilling_hrs'],
            sliding_hrs=bha['sliding_hrs'],
            rotating_hrs=bha['rotating_hrs'],
            NPT_hrs=bha['NPT_hrs'],
            feet_slid=bha['feet_slid'],
            feet_rotated=bha['feet_rotated'],
            total_rop=bha['total_rop'])
        bhaIns.save()
        # bhaIns.assets.add(Asset.objects.get(pk=int(bha['assets'])))
    except:
        print("bad BHA")

with open('survey_3.json', encoding="utf8") as f:
    survey_json = json.load(f)

for survey in survey_json:
    try:
        survey = Survey(
            person=Person.objects.get(pk=int(survey['person'])),
            job=Job.objects.get(pk=int(survey['job'])),
            creation_date=survey['creation_date'],
            name=survey['name'],
            md=survey['md'],
            inc=survey['inc'],
            azi=survey['azi'],
            tvd=survey['tvd'],
            north=survey['north'],
            east=survey['east'],
            vertical_section=survey['vertical_section'],
            dogleg=survey['dogleg'],
            build_rate=survey['build_rate'],
            turn_rate=survey['turn_rate'],
            calculated_tf=survey['calculated_tf'],
            calculated_ang=survey['calculated_ang'],
            clos_dist=survey['clos_dist'],
            clos_azi=survey['clos_azi'],
            mag_total=survey['mag_total'],
            grav_total=survey['grav_total'],
            dip=survey['number'],
            temp=survey['temp'],
            zero_vs=survey['zero_vs'],
            step_out=survey['step_out'])
        survey.save()
    except:
        print("Survey Not Loaded")


with open('activities_fulldata.json', encoding="utf8") as f:
    activity_json = json.load(f)


for activity in activity_json:
    try:
        activity = Activity(
            person=Person.objects.get(pk=int(activity['person'])),
            job=Job.objects.get(pk=int(activity['job'])),
            start_date=activity['start_date'],
            end_date=activity['end_date'],
            activity_group=activity['activity_group'],
            activity_type=activity['activity_type'],
            start_depth=activity['start_depth'],
            end_depth=activity['end_depth'])
        activity.save()
    except:
        print("No Activity")

# with open('shipments.json', encoding="utf8") as f:a
#     shipment_json = json.load(f)


# for shipment in shipment_json:
#     try:
#         shipment = Shipment(
#             create_by_person=Person.objects.get(
#                 pk=int(shipment['create_by_person'])),
#             received_by_person=Person.objects.get(
#                 pk=int(shipment['received_by_person'])),
#             destination=shipment['destination'],
#             dest_type=shipment['dest_type'],
#             ship_size=shipment['ship_size'],
#             origin_type=shipment['origin_type'],
#             origin_name=shipment['origin_name'],
#             est_ship_date=shipment['est_ship_date'],
#             ship_date=shipment['ship_date'],
#             exp_arrive_date=shipment['exp_arrive_date'],
#             arrive_date=shipment['arrive_date'],
#             ship_by_date=shipment['ship_by_date'],
#             create_date=shipment['create_date'],
#             status=shipment['status'],
#             logistics_partner=Partner.objects.get(pk=int(shipment['logistics_partner'])))
#         shipment.save()
#     except:
#         print("No Shipment")
