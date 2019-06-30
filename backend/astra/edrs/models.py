from django.db import models
from jobs.models import Job, Formation, Interval, WellConnector
from plans.models import Plan
from bhas.models import Bha
from surveys.models import Survey
from .live_cleaner import phase2, phase100, drillitup2, drillitup20
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min, Sum, Variance
from scipy.signal import savgol_filter
from django.db.models import Q

class EDRRaw(models.Model):
    job = models.ForeignKey(Job, related_name="job_edr",
                            on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 Job
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    rig_time = models.DateTimeField()
    uid = models.CharField(max_length=50)
    hole_depth = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True)
    bit_depth = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    tvd = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    wob = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    block_height = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    diff_press = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    flow_in = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    flow_out = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    gamma_ray = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    pump_press = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    rop_i = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    rop_a = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    strokes_total = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    svy_azi = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    svy_inc = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    tf_grav = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    tf_mag = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    td_rpm = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    td_torque = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    edr_slips = models.BooleanField(default=False)
    total_spm = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    hookload = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    overpull = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    edr_mse = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    oscillator = models.BooleanField(default=False)
    edr_RS1 = models.IntegerField(null=True, blank=True)
    edr_RS2 = models.IntegerField(null=True, blank=True)
    edr_RS3 = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=False)
    cont_inc = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    cont_azi = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True)
    back_press = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    ann_press = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    mud_ti = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    mud_to = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    mud_wi = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    mud_wo = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)

    def save(self, *args, **kwargs):
        # print("inside edrraw save")
        edrraw_being_added = False

        if self.pk is None:
            edrraw_being_added = True

        # print(edrraw_being_added)

        if edrraw_being_added:
            DATA_FREQUENCY = 5  # 30 Seconds
            all_edrs_on_job = EDRRaw.objects.filter(uid=self.uid)
            all_processed_on_job = EDRProcessed.objects.filter(uid=self.uid)
            # print("edr count", all_edrs_on_job.count())

            # Previous edrraw exists -- Calculate and Save EDR Processed
            if all_edrs_on_job.count() > 0:
                bit_status = 0
                slip_status = 0
                pump_status = 0
                time_elapsed = 0
                data_gap = 0
                hole_size = None
                motor_rpg = 0
                bha_length = None
                VSPlane = None
                current_bha = None
                current_interval = None

                connector = WellConnector.objects.filter(uid=self.uid).exclude(job=None).first()

                try:
                    current_interval = Interval.objects.get(job=connector.job, start_depth__lt=self.hole_depth, end_depth__gte=self.hole_depth)
                    hole_size = current_interval.hole_size
                except:
                    pass

                try:
                    current_bha = Bha.objects.get(job=connector.job, depth_in__lt=self.hole_depth, depth_out__gte=self.hole_depth)
                    hole_size = current_bha.hole_size
                    bha_length = current_bha.bha_length
                    # Get motor rpg from motor asset
                    # if 
                    #     motor_rpg = bhas_on_job.motor_rpg
                except:
                    try: 
                        current_bha = Bha.objects.get(job=connector.job, depth_in__lt=self.hole_depth, depth_out=None)
                        hole_size = current_bha.hole_size
                        bha_length = current_bha.bha_length
                        # Get motor rpg from motor asset
                        # motor_rpg = bhas_on_job.motor_rpg
                    except:
                        pass
                
                try:
                    current_plan = Plan.objects.get(job=connector.job, active=True).last()
                    VSPlane = current_plan.vsplane

                    lt_plan = Plan.objects.get(job=connector.job, active=True, md__lt=self.hole_depth).last() 
                    gt_plan = Plan.objects.get(job=connector.job, active=True, md__gt=self.hole_depth).first()
                except:
                    pass
                    

                if all_processed_on_job.count() > 0:
                    # Latest processed data on job
                    prev_process = all_processed_on_job.latest('id')

                    bit_status = prev_process.bit_status
                    slip_status = prev_process.slip_status
                    pump_status = prev_process.pump_status
                    time_elapsed = prev_process.time_elapsed
                    data_gap = prev_process.data_gap

                first = all_edrs_on_job.first()
                prev = all_edrs_on_job.latest('id')

                min20_hole_depth = prev.hole_depth

                if all_edrs_on_job.count() >= 19:
                    # Min hole depth of the latest 20
                    min20_hole_depth = all_edrs_on_job.order_by(
                        '-id')[:20].aggregate(Min('hole_depth')).get('hole_depth__min')
                    # print("current depth", self.hole_depth)
                    # print("current bit depth", self.bit_depth)
                    # print("min20_hole_depth", min20_hole_depth)

                day_num, day_night, bit_status, slip_status, block_status, pump_status, rot_sli, time_elapsed, data_gap, trip_status, rig_activity, clean_1, clean_2, clean_3 = phase2(
                    first.rig_time, parse_datetime(self.rig_time), prev.rig_time, self.hole_depth, prev.hole_depth, self.bit_depth, prev.bit_depth, self.rop_i, self.hookload, self.block_height,
                    prev.block_height, self.td_rpm, self.oscillator, self.flow_in, bit_status, slip_status, pump_status, time_elapsed, min20_hole_depth, data_gap, DATA_FREQUENCY)

                super(EDRRaw, self).save(*args, **kwargs)

                edr_processed = EDRProcessed(
                    edr_raw=self,
                    uid=self.uid,
                    data_gap=data_gap,
                    day_num=day_num,
                    day_night=True if day_night == 1 else False,
                    bit_status=bit_status,
                    slip_status=slip_status,
                    block_status=block_status,
                    pump_status=pump_status,
                    time_elapsed=time_elapsed.total_seconds() / 3600,
                    trip_status=trip_status,
                    rot_sli=rot_sli,
                    rig_activity=rig_activity,
                    clean_1=clean_1,
                    clean_2=clean_2,
                    clean_3=clean_3,
                    trip_out_number=0,
                    trip_in_number=0)
                edr_processed.save()

                # EDR Top Connection Calculations
                if bit_status == 2:
                    print("In top connection calculations")
                    w_bit_status = all_processed_on_job.filter(bit_status=-1)
                    if w_bit_status.count() > 0:
                        E_ID = edr_processed
                        S_ID = w_bit_status.latest('id')
                        all_edrcxn_on_job = EDRCXN.objects.filter(uid=self.uid)
                        latest_cxn_time = all_edrcxn_on_job.latest('id').edr_raw.rig_time if all_edrcxn_on_job.count() > 0 else parse_datetime("1970-01-01T12:00:00-05:00")
                        cxn_range = all_processed_on_job.filter(edr_raw__rig_time__gte=S_ID.edr_raw.rig_time, edr_raw__rig_time__lte=E_ID.edr_raw.rig_time)

                        if S_ID.edr_raw.rig_time > latest_cxn_time and (parse_datetime(E_ID.edr_raw.rig_time) - S_ID.edr_raw.rig_time) < timedelta(minutes=30):
                            print("Top connection time is valid")
                            pump_status_2 = cxn_range.filter(pump_status=2).count()
                            pump_status_1 = cxn_range.filter(pump_status=-1).count()
                            slip_status_2 = cxn_range.filter(slip_status=2).first()
                            slip_status_1 = cxn_range.filter(slip_status=-1).last()

                            if pump_status_2 > 0 and pump_status_1 > 0 and slip_status_2 and slip_status_1:
                                print("Top connection statuses are good")
                                total_time = (parse_datetime(E_ID.edr_raw.rig_time) - S_ID.edr_raw.rig_time).total_seconds() / 60  # minutes
                                btm_slips = (slip_status_2.edr_raw.rig_time - S_ID.edr_raw.rig_time).total_seconds() / 60  # minutes
                                slips_slips = (slip_status_1.edr_raw.rig_time - slip_status_2.edr_raw.rig_time).total_seconds() / 60  # minutes
                                slips_btm = (parse_datetime(E_ID.edr_raw.rig_time) - slip_status_1.edr_raw.rig_time).total_seconds() / 60  # minutes
                                day_night = True if (S_ID.edr_raw.rig_time).hour >= 6 and (S_ID.edr_raw.rig_time).hour < 18 else False
                                pump_cycles = min(pump_status_2, pump_status_1)
                                cxn_count = all_edrcxn_on_job.last().cxn_count + 1 if all_edrcxn_on_job.count() > 0 else 1

                                edr_cxn = EDRCXN(
                                    uid=self.uid,
                                    edr_raw=self,
                                    total_time=total_time,
                                    btm_slips=btm_slips,
                                    slips_slips=slips_slips,
                                    slips_btm=slips_btm,
                                    day_night=day_night,
                                    pump_cycles=pump_cycles,
                                    cxn_count=cxn_count)

                                edr_cxn.save()

                # EDR Drilled Calcuations
                if clean_1 == 0 and clean_3 == 0:
                    # print("clean_1 and clean_3 -- Running Drilling Data")
                    all_drilled_on_job = EDRDrilled.objects.filter(
                        uid=self.uid)

                    last_drilled = all_drilled_on_job.last()

                    # Other drilled on job exist
                    if last_drilled:
                        prev_block_height = last_drilled.edr_raw.block_height
                        prev_hole_depth = last_drilled.edr_raw.hole_depth
                        prev_stand_count = last_drilled.stand_count
                    # First drilled on job
                    else:
                        prev_hole_depth = 0
                        prev_block_height = 94
                        prev_stand_count = 0

                    # print("model - prev_stand_count ", prev_stand_count)

                    drilled_ft, stand_count, astra_mse, bit_rpm = drillitup2(
                        self.hole_depth, prev_hole_depth, self.block_height, prev_block_height, prev_stand_count,
                        self.rop_i, self.wob, self.td_torque, self.flow_in, hole_size, motor_rpg, self.td_rpm)

                    edr_drilled = EDRDrilled(
                        uid=self.uid,
                        bha=current_bha if current_bha is not None else None,
                        edr_raw=self,
                        drilled_ft=drilled_ft,
                        bit_rpm=bit_rpm,
                        stand_count=stand_count,
                        astra_mse=astra_mse,
                        rop_i=self.rop_i,
                        rop_a=self.rop_a,
                        slide_count=0,
                        rot_count=0
                    )

                    edr_drilled.save()

                    if all_drilled_on_job.count() > 20:
                        drilled_20_rows = all_drilled_on_job.order_by('-id')[:20]
                        drilled_pks = [item.edr_raw.id for item in drilled_20_rows]
                        # drilled_pks = drilled_20_rows.values_list('id', flat=True)

                        raw_20_rows = all_edrs_on_job.filter(id__in=drilled_pks).order_by('-id')[:20]
                        processed_20_rows = all_processed_on_job.filter(edr_raw__id__in=drilled_pks).order_by('-id')[:20]

                        prev_bha = drilled_20_rows[8].bha
                        processed_5_rows = processed_20_rows[4:9]
                        drilled_ft = drilled_20_rows[9].drilled_ft
                        stand_count = drilled_20_rows[9].stand_count
                        prev_stand_count = drilled_20_rows[8].stand_count
                        drilled_row_10 = drilled_20_rows[9]
                        prev_rot_sli = processed_20_rows[8].rot_sli
                        current_rot_sli = processed_20_rows[9].rot_sli
                        next_rot_sli = processed_20_rows[10].rot_sli
                        astra_mse = drilled_20_rows[9].astra_mse

                        avg_20_rop_i = raw_20_rows.aggregate(Avg('rop_i')).get('rop_i__avg')
                        avg_20_rop_a = raw_20_rows.aggregate(Avg('rop_a')).get('rop_a__avg')

                        try:
                            var_20_tf_grav = raw_20_rows.aggregate(Variance('tf_grav')).get('tf_grav__variance')
                        except:
                            var_20_tf_grav = 0
                        try:
                            var_20_tf_mag = float(raw_20_rows.aggregate(Variance('tf_mag')).get('tf_mag__variance'))
                        except:
                            var_20_tf_mag = 0

                        avg_20_astra_mse = drilled_20_rows.aggregate(Avg('astra_mse')).get('astra_mse__avg')
                        avg_5_rot_sli = processed_5_rows.aggregate(Avg('rot_sli')).get('rot_sli__avg')

                        # print("current_rot_sli ", float(current_rot_sli))
                        # print("avg_5_rot_sli ", float(avg_5_rot_sli))
                        # print("next_rot_sli ", float(next_rot_sli))
                        # print("prev_rot_sli ", float(prev_rot_sli))

                        # print("stand_count ", stand_count)
                        # print("prev_stand_count ", prev_stand_count)

                        normalized_tf, slide_value_tf, rop_i, rop_a, astra_mse, slide_status, rot_status = drillitup20(
                            drilled_row_10.edr_raw.rop_i,
                            avg_20_rop_i,
                            drilled_row_10.edr_raw.rop_a,
                            avg_20_rop_a,
                            drilled_row_10.edr_raw.tf_grav,
                            var_20_tf_grav,
                            drilled_row_10.edr_raw.tf_mag,
                            var_20_tf_mag,
                            astra_mse,
                            avg_20_astra_mse,
                            VSPlane,
                            current_rot_sli,
                            avg_5_rot_sli,
                            next_rot_sli,
                            prev_rot_sli,
                            float(drilled_ft),
                            current_bha,
                            prev_bha,
                            float(stand_count),
                            float(prev_stand_count))

                        # print("rot_status ", rot_status)

                        drilled_row_10.normalized_tf = normalized_tf
                        drilled_row_10.slide_value_tf = slide_value_tf
                        drilled_row_10.rop_i = rop_i
                        drilled_row_10.rop_a = rop_a
                        drilled_row_10.astra_mse = astra_mse
                        drilled_row_10.slide_status = slide_status
                        drilled_row_10.rot_status = rot_status

                        super(EDRDrilled, drilled_row_10).save(update_fields=["normalized_tf", "slide_value_tf", "rop_i", "rop_a", "astra_mse", "slide_status", "rot_status"])

                        edr_drilled.save()

                        if slide_status == -1:
                            last_slide_start = all_drilled_on_job.filter(slide_status=-1).last()  # slide starts

                            if (float(edr_drilled.edr_raw.hole_depth) - float(last_slide_start.edr_raw.hole_depth)) > 5:
                                prev_slide_end = all_drilled_on_job.filter(slide_status=-1).last()  # slide ends
                                if last_slide_start.edr_raw.rig_time > prev_slide_end.edr_raw.rig_time:
                                    slide_range = all_drilled_on_job.filter(id__gte=last_slide_start.id, id__lte=edr_drilled.id)
                                    max_slide_count = all_drilled_on_job.aggregate(Max('slide_count')).get('slide_count')

                                    for slide in slide_range:
                                        slide.slide_count = max_slide_count + 1
                                        super(EDRDrilled, slide).save(update_fields=["slide_count"])

                        if rot_status == -1:
                            last_rot_start = all_drilled_on_job.filter(rot_status=-1).last()  # rot starts

                            if (float(edr_drilled.edr_raw.hole_depth) - float(last_rot_start.edr_raw.hole_depth)) > 5:
                                prev_rot_end = all_drilled_on_job.filter(rot_status=-1).last()  # rot ends
                                if last_rot_start.edr_raw.rig_time > prev_rot_end.edr_raw.rig_time:
                                    rot_range = all_drilled_on_job.filter(id__gte=last_rot_start.id, id__lte=edr_drilled.id)
                                    max_rot_count = all_drilled_on_job.aggregate(Max('rot_count')).get('rot_count')

                                    for rot in rot_range:
                                        rot.rot_count = max_rot_count + 1
                                        super(EDRDrilled, rot).save(update_fields=["rot_count"])

            else:
                super(EDRRaw, self).save(*args, **kwargs)

            # EDR Processed Phase 100 Calculations
            if all_edrs_on_job.count() > 200:
                # self is now index 0
                raw_100_rows = all_edrs_on_job.order_by('-id')[:100]
                raw_200_rows = all_edrs_on_job.order_by('-id')[:200]

                # the order is reversed, index 0 is now the newest
                processed_100_rows = all_processed_on_job.order_by('-id')[:100]

                # Raw
                raw_row_49 = raw_100_rows[50]
                raw_row_50 = raw_100_rows[49]
                max_100_hole_depth = raw_100_rows.aggregate(
                    Max('hole_depth')).get('hole_depth__max')
                min_20_hole_depth = raw_100_rows[40:60].aggregate(
                    Min('hole_depth')).get('hole_depth__min')
                max_100_bit_depth = raw_100_rows.aggregate(
                    Max('bit_depth')).get('bit_depth__max')
                min_100_bit_depth = raw_100_rows.aggregate(
                    Min('bit_depth')).get('bit_depth__min')
                avg_100_bit_depth = raw_100_rows.aggregate(
                    Avg('bit_depth')).get('bit_depth__avg')
                avg_50_bit_depth = raw_100_rows[25:75].aggregate(
                    Avg('bit_depth')).get('bit_depth__avg')
                avg_top_100_bit_depth = raw_100_rows[0:100].aggregate(
                    Avg('bit_depth')).get('bit_depth__avg')
                avg_200_bit_depth = raw_200_rows.aggregate(
                    Avg('bit_depth')).get('bit_depth__avg')
                raw_100_bit_depth = list(raw_100_rows[25:75].values_list('bit_depth',flat=True))
                savgol=savgol_filter(raw_100_bit_depth, window_length=49, polyorder=2, deriv=1)
                savgol50=savgol[24]
                # Processed
                processed_row_49 = processed_100_rows[50]
                processed_row_50 = processed_100_rows[49]
                avg_30_rot_sli = processed_100_rows[35:65].aggregate(
                    Avg('rot_sli')).get('rot_sli__avg')
                avg_30_pump_status = processed_100_rows[35:65].aggregate(
                    Avg('pump_status')).get('pump_status__avg')
                avg_30_pump_status = processed_100_rows[35:65].aggregate(
                    Avg('pump_status')).get('pump_status__avg')
                max_100_clean_2 = processed_100_rows.aggregate(
                    Max('clean_2')).get('clean_2__max')

                clean_1, clean_3, bit_variance, trip_status2, rig_activity2 = phase100(
                    raw_row_50.hole_depth, raw_row_49.hole_depth, max_100_hole_depth, min_20_hole_depth, raw_row_50.bit_depth,
                    raw_row_49.bit_depth, max_100_bit_depth, min_100_bit_depth, avg_top_100_bit_depth, avg_50_bit_depth, avg_30_rot_sli,
                    avg_30_pump_status, raw_row_50.flow_in, processed_row_50.clean_2, max_100_clean_2, processed_row_49.data_gap,savgol50)
                
                # print("clean_1: ", clean_1, type(clean_1))
                # print("clean_3: ", clean_3, type(clean_3))
                # print("bit_variance: ", round(
                #     bit_variance, 3), type(bit_variance))
                # print("trip_status2: ", trip_status2, type(trip_status2))
                # print("rig_activity2: ", rig_activity2, type(rig_activity2))

                processed_row_50.clean_1 = clean_1
                processed_row_50.clean_3 = clean_3
                processed_row_50.bit_variance = round(bit_variance, 3)
                processed_row_50.trip_status2 = trip_status2
                processed_row_50.rig_activity2 = rig_activity2

                super(EDRProcessed, processed_row_50).save( 
                    update_fields=["clean_1", "clean_3", "bit_variance", "trip_status2", "rig_activity2", "trip_out_number"])

                # Tripping Out
                if trip_status2 == 4:
                    # print("tripping out")
                    process_hole_depth = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth)
                    tripping_out_processed = process_hole_depth.filter(trip_status2=4)

                    total_tripping_time = tripping_out_processed.count() * DATA_FREQUENCY  # seconds
                    print("total_tripping_time -- OUT ", total_tripping_time)

                    last_processed = tripping_out_processed.filter(edr_raw__rig_time__lt=processed_row_50.edr_raw.rig_time).last()
                    first_processed = tripping_out_processed.filter(edr_raw__rig_time__lt=processed_row_50.edr_raw.rig_time).first()
                    

                    if last_processed:
                        regional_min = None

                        # Calculate Regional Minimum Bit Depth
                        regional_range =  process_hole_depth.filter(edr_raw__bit_depth__lte=500)
                        first_regional_point = regional_range.first()
                        last_regional_point = regional_range.last()
                        
                        # 2 regional points exists for hole depth
                        if first_regional_point is not None and last_regional_point is not None and first_regional_point != last_regional_point:
                            regional_min_val = regional_range.aggregate(Min('edr_raw__bit_depth')).get('edr_raw__bit_depth__min')
                            regional_min = regional_range.filter(edr_raw__bit_depth__lte=regional_min_val).first()


                        # print("tripping out, last_processed")
                        if (processed_row_50.edr_raw.rig_time - last_processed.edr_raw.rig_time) < timedelta(hours=2) and regional_min is None:
                            # print("tripping out, success")
                            # print("last_processed.trip_out_number ", last_processed.trip_out_number)
                            # print("last id, current id ", last_processed.id, processed_row_50.id)
                            if last_processed.trip_out_number > 0:
                                # print("--- Inside last_processed.trip_out_number > 1 ---")
                                processed_row_50.trip_out_number = last_processed.trip_out_number
                                
                                processed_50_last_range = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth, edr_raw__rig_time__gte=last_processed.edr_raw.rig_time, edr_raw__rig_time__lte=processed_row_50.edr_raw.rig_time)

                                edr_trip = EDRTrip.objects.filter(uid=self.uid, trip_direction=False, trip_count=processed_row_50.trip_out_number).first()

                                if edr_trip.bha_time is None:
                                    if bha_length is None:
                                        bha_length = min([float(processed_row_50.edr_raw.hole_depth) / 10, 1000])
                                    
                                    if processed_row_50.edr_raw.bit_depth <= bha_length:
                                        edr_trip.bha_time = processed_row_50.edr_raw.rig_time
                                        super(EDRTrip, edr_trip).save(update_fields=["bha_time"])
                                
                                edr_trip.end_time = self.rig_time
                                super(EDRTrip, edr_trip).save(update_fields=["end_time"])

                                for item in processed_50_last_range:
                                    # print("inside loop tripping_out")
                                    item.trip_out_number = last_processed.trip_out_number
                                    super(EDRProcessed, item).save(update_fields=["trip_out_number"])
                                    print("trip Out Number", item.trip_out_number)

                                super(EDRProcessed, processed_row_50).save(update_fields=["trip_out_number"])

                            elif (total_tripping_time / 1800) >= 1:
                                max_trip_number = all_processed_on_job.exclude(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth).aggregate(Max('trip_out_number')).get('trip_out_number__max')
                                print("max_trip_number ", max_trip_number)
                                print("total_tripping_time ", total_tripping_time)
                                processed_row_50.trip_out_number = max_trip_number + 1

                                processed_50_last_range = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth, edr_raw__rig_time__gte=first_processed.edr_raw.rig_time, edr_raw__rig_time__lte=processed_row_50.edr_raw.rig_time)

                                
                                print("first_processed.edr_raw  TRIP OUT", first_processed.edr_raw.id)
                                new_edr_trip = EDRTrip(
                                    uid=self.uid,
                                    edr_raw=first_processed.edr_raw,
                                    bha=current_bha,
                                    interval=current_interval,
                                    total_time=(parse_datetime(self.rig_time) - first_processed.edr_raw.rig_time).total_seconds() / 3600, # hours
                                    start_time=first_processed.edr_raw.rig_time,
                                    end_time=self.rig_time,
                                    depth=first_processed.edr_raw.hole_depth,
                                    trip_direction=False, # Trip Out
                                    casing=False,
                                    trip_count=processed_row_50.trip_out_number,
                                )
                                new_edr_trip.save()


                                if current_bha:
                                    prev_trip_in = EDRTrip.objects.filter(uid=self.uid, trip_direction=True).last()

                                    if prev_trip_in: 
                                        edr_drilled_bha = EDRDrilled.objects.filter(uid=self.uid, edr_raw__rig_time__gte=prev_trip_in.start_time)
                                        first_drilling_point = edr_drilled_bha.first()
                                        last_drilling_point = edr_drilled_bha.last()
                                        try:
                                            surveys_on_job = Survey.objects.filter(Q(uid=self.uid) | Q(job=connector.job))
                                        except:
                                            surveys_on_job = Survey.objects.filter(uid=self.uid)

                                        current_bha.downhole_hrs = (first_processed.edr_raw.rig_time - prev_trip_in.start_time).total_seconds() / 3600
                                        current_bha.footage_drilled = float(first_processed.edr_raw.hole_depth) - float(current_bha.depth_in) # current_bha.depth_in could be prev_trip_in.start_time
                                        current_bha.drilling_hrs = (last_drilling_point.edr_raw.rig_time - first_drilling_point.edr_raw.rig_time).total_seconds() / 3600
                                        current_bha.circulating_hrs = all_processed_on_job.filter(Q(edr_raw__rig_time__gte=prev_trip_in.start_time) & Q(edr_raw__rig_time__lte=first_processed.edr_raw.rig_time) & (Q(rig_activity2=2) | Q(rig_activity2=3))).count() * DATA_FREQUENCY / 3600 
                                        current_bha.sliding_hrs = edr_drilled_bha.filter(~Q(slide_count=0) | ~Q(slide_count=None)).count() * DATA_FREQUENCY / 3600
                                        current_bha.rotating_hrs = drilling_hrs - sliding_hrs
                                        current_bha.feet_slid = edr_drilled_bha.filter(~Q(slide_count=0) | ~Q(slide_count=None)).aggregate(Sum('drilled_ft')).get('drilled_ft__sum')
                                        current_bha.feet_rotated = footage_drilled - feet_slid
                                        current_bha.total_rop = edr_drilled_bha.aggregate(Avg('rop_a')).get('rop_a__avg')
                                        current_bha.sliding_rop = edr_drilled_bha.filter(~Q(slide_count=0) | ~Q(slide_count=None)).aggregate(Avg('rop_a')).get('rop_a__avg')
                                        current_bha.rotating_rop = edr_drilled_bha.filter(~Q(rot_count=0) | ~Q(rot_count=None)).aggregate(Avg('rop_a')).get('rop_a__avg')
                                        

                                        if surveys_on_job.count() > 0:
                                            try:
                                                current_bha.inc_in = surveys_on_job.filter(md__gt=first_processed.edr_raw.hole_depth).first().inc_in
                                            except:
                                                pass
                                            try:
                                                current_bha.inc_out = surveys_on_job.filter(md__lt=first_processed.edr_raw.hole_depth).last().inc_out
                                            except:
                                                pass
                                            try:
                                                current_bha.azi_in = surveys_on_job.filter(md__gt=first_processed.edr_raw.hole_depth).first().azi_in
                                            except:
                                                pass
                                            try:
                                                current_bha.azi_out = surveys_on_job.filter(md__lt=first_processed.edr_raw.hole_depth).last().azi_out
                                            except:
                                                pass
                                            current_bha.dogleg = surveys_on_job.aggregate(Avg('dogleg')).get('dogleg__avg')
                                            current_bha.motor_yield = surveys_on_job.aggregate(Avg('my')).get('my__avg')
                                            current_bha.build_rate = surveys_on_job.aggregate(Avg('build_rate')).get('build_rate__avg')
                                            current_bha.turn_rate = surveys_on_job.aggregate(Avg('90')).get('turn_rate__avg')

                                            super(Bha, current_bha).save(update_fields=["downhole_hrs", "footage_drilled", "drilling_hrs", "circulating_hrs", 
                                                                                        "sliding_hrs", "rotating_hrs", "feet_slid", "feet_rotated", "total_rop", 
                                                                                        "sliding_rop", "rotating_rop", "inc_in", "inc_out", "azi_in", "azi_out", 
                                                                                        "dogleg", "motor_yield", "build_rate", "turn_rate"])
                                    

                                for item in processed_50_last_range:
                                    # print("inside loop tripping_out")
                                    item.trip_out_number = max_trip_number + 1
                                    super(EDRProcessed, item).save(update_fields=["trip_out_number"])
                                    print("trip Out Number", item.trip_out_number)
                # Tripping In
                if trip_status2 == 6:
                    # print("tripping in")
                    process_hole_depth = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth)
                    tripping_in_processed = process_hole_depth.filter(trip_status2=6)


                    total_tripping_time = tripping_in_processed.count() * DATA_FREQUENCY  # seconds
                    print("total_tripping_time -- In ", total_tripping_time)

                    last_processed = tripping_in_processed.filter(edr_raw__rig_time__lt=processed_row_50.edr_raw.rig_time).last()
                    first_processed = tripping_in_processed.filter(edr_raw__rig_time__lt=processed_row_50.edr_raw.rig_time).first()


                    if last_processed:
                        regional_min = None

                        # Calculate Regional Minimum Bit Depth
                        regional_range =  process_hole_depth.filter(edr_raw__bit_depth__lte=500)
                        first_regional_point = regional_range.first()
                        last_regional_point = regional_range.last()
                        
                        # 2 regional points exists for hole depth
                        if first_regional_point is not None and last_regional_point is not None and first_regional_point != last_regional_point:
                            regional_min_val = regional_range.aggregate(Min('edr_raw__bit_depth')).get('edr_raw__bit_depth__min')
                            regional_min = regional_range.filter(edr_raw__bit_depth__lte=regional_min_val).first()

                            if regional_min:
                                # EDR Trip Out at hole depth
                                edr_trip = EDRTrip.objects.filter(uid=self.uid, trip_direction=False, edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth).first()
                                
                                # Update EDRTrip
                                if edr_trip:
                                    edr_trip.end_time = regional_min.edr_raw.rig_time
                                    super(EDRTrip, edr_trip).save(update_fields=["end_time"])


                        # print("tripping in, last_processed")
                        if (processed_row_50.edr_raw.rig_time - last_processed.edr_raw.rig_time) < timedelta(hours=2):
                            # print("tripping in, success")
                            # print("last_processed.trip_in_number ", last_processed.trip_in_number)
                            # print("last id, current id ", last_processed.id, processed_row_50.id)
                            if last_processed.trip_in_number > 0:
                                # print("--- Inside last_processed.trip_in_number > 1 ---")
                                processed_row_50.trip_in_number = last_processed.trip_in_number
                                
                                processed_50_last_range = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth, edr_raw__rig_time__gte=last_processed.edr_raw.rig_time, edr_raw__rig_time__lte=processed_row_50.edr_raw.rig_time)

                                edr_trip = EDRTrip.objects.filter(uid=self.uid, trip_direction=True, trip_count=processed_row_50.trip_out_number).first()

                                if edr_trip.bha_time is None:
                                    if bha_length is None:
                                        bha_length = min([float(processed_row_50.edr_raw.hole_depth) / 10, 1000])
                                    
                                    if processed_row_50.edr_raw.bit_depth >= bha_length:
                                        edr_trip.bha_time = processed_row_50.edr_raw.rig_time
                                        super(EDRTrip, edr_trip).save(update_fields=["bha_time"])
                                
                                edr_trip.end_time = self.rig_time
                                super(EDRTrip, edr_trip).save(update_fields=["end_time"])


                                for item in processed_50_last_range:
                                    # print("inside loop tripping_in")
                                    item.trip_in_number = last_processed.trip_in_number
                                    super(EDRProcessed, item).save(update_fields=["trip_in_number"])
                                    print("trip in Number", item.trip_in_number)

                                super(EDRProcessed, processed_row_50).save(update_fields=["trip_in_number"])

                            elif (total_tripping_time / 1800) >= 1:
                                max_trip_number = all_processed_on_job.exclude(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth).aggregate(Max('trip_in_number')).get('trip_in_number__max')
                                print("max_trip_number ", max_trip_number)
                                print("total_tripping_time ", total_tripping_time)
                                processed_row_50.trip_in_number = max_trip_number + 1

                                processed_50_last_range = all_processed_on_job.filter(edr_raw__hole_depth=processed_row_50.edr_raw.hole_depth, edr_raw__rig_time__gte=first_processed.edr_raw.rig_time, edr_raw__rig_time__lte=processed_row_50.edr_raw.rig_time)

                                print("first_processed.edr_raw  TRIP IN", first_processed.edr_raw.id)
                                new_edr_trip = EDRTrip(
                                    uid=self.uid,
                                    edr_raw=first_processed.edr_raw,
                                    bha=current_bha,
                                    interval=current_interval,
                                    total_time=(parse_datetime(self.rig_time) - first_processed.edr_raw.rig_time).total_seconds() / 3600, # hours
                                    start_time=first_processed.edr_raw.rig_time,
                                    end_time=self.rig_time,
                                    depth=first_processed.edr_raw.hole_depth,
                                    trip_direction=True, # Trip In
                                    casing=False,
                                    trip_count=processed_row_50.trip_out_number,
                                )

                                new_edr_trip.save()

                                for item in processed_50_last_range:
                                    # print("inside loop tripping_in")
                                    item.trip_in_number = max_trip_number + 1
                                    super(EDRProcessed, item).save(update_fields=["trip_in_number"])
                                    print("trip in Number", item.trip_in_number)
    def __str__(self):
        return str(self.uid)

    class Meta:
        verbose_name_plural = "Raw EDRs"


class EDRProcessed(models.Model):
    # job = models.ForeignKey(Job, related_name="job_edr_proc",
    #                         on_delete=models.CASCADE, null=True, blank=True)  # 0 or many EDR_Lines to 1 Job
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    edr_raw = models.OneToOneField(EDRRaw, related_name="edrraw_edrproc",
                                   on_delete=models.CASCADE, null=True, blank=True)  # 1 EDR_Lines to 1 processed line for now, May reduce data later
    uid = models.CharField(max_length=50)
    data_gap = models.DecimalField(
        max_digits=15, decimal_places=4, blank=True, null=True)  # seconds
    time_elapsed = models.DecimalField(
        max_digits=15, decimal_places=4, blank=True, null=True)  # hours
    day_num = models.IntegerField()
    day_night = models.BooleanField(default=True)
    bit_status = models.IntegerField()
    slip_status = models.IntegerField()
    block_status = models.IntegerField()
    pump_status = models.IntegerField()
    cxn_count = models.IntegerField(null=True, blank=True)
    trip_status = models.IntegerField()
    trip_status2 = models.IntegerField(blank=True, null=True)
    trip_out_number = models.IntegerField()
    trip_in_number = models.IntegerField()
    rot_sli = models.IntegerField()
    rig_activity = models.IntegerField()
    rig_activity2 = models.IntegerField(blank=True, null=True)
    clean_1 = models.IntegerField()
    clean_2 = models.IntegerField()
    clean_3 = models.IntegerField(blank=True, null=True)
    tq_variance = models.DecimalField(
        max_digits=15, decimal_places=3, blank=True, null=True)
    bit_variance = models.DecimalField(
        max_digits=15, decimal_places=3, blank=True, null=True)

    def __str__(self):
        return self.uid

    class Meta:
        verbose_name_plural = "Processed EDRs"


class EDRDrilled(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    # edit_date = models.DateTimeField(auto_now=True)  # auto generated
    uid = models.CharField(max_length=50)
    edr_raw = models.OneToOneField(EDRRaw, related_name="edr_raw_edrdrill",
                                   on_delete=models.CASCADE)  # 1 EDR_Lines to 1 raw line for now, May reduce data later
    interval = models.ForeignKey(Interval, related_name="interval_edr_drill",
                                 on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 interval
    bha = models.ForeignKey(Interval, related_name="bha_edr_drill",
                            on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 0 or 1 interval
    formation = models.ForeignKey(Interval, related_name="formation_edr_drill",
                                  on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 interval
    drilled_ft = models.DecimalField(max_digits=15, decimal_places=3)
    bit_rpm = models.DecimalField(max_digits=10, decimal_places=3)
    slide_status = models.IntegerField(null=True, blank=True)
    rot_status = models.IntegerField(null=True, blank=True)
    normalized_tf = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True)
    slide_count = models.IntegerField(null=True, blank=True)
    rot_count = models.IntegerField(null=True, blank=True)
    stand_count = models.IntegerField()
    astra_mse = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    slide_value_tf = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True)
    rop_i = models.DecimalField(max_digits=15, decimal_places=3)
    rop_a = models.DecimalField(max_digits=15, decimal_places=3)

    def __str__(self):
        return str(self.uid)

    class Meta:
        verbose_name_plural = "Drill EDRs"


class EDRCXN(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    uid = models.CharField(max_length=50)
    edr_raw = models.OneToOneField(EDRRaw, related_name="edr_raw_edrcxn", on_delete=models.CASCADE)  # 1 EDR_Line to 1 raw line for now
    total_time = models.DecimalField(max_digits=15, decimal_places=3)
    btm_slips = models.DecimalField(max_digits=15, decimal_places=3)
    slips_slips = models.DecimalField(max_digits=15, decimal_places=3)
    slips_btm = models.DecimalField(max_digits=15, decimal_places=3)
    day_night = models.BooleanField(default=False)
    pump_cycles = models.IntegerField()
    cxn_count = models.IntegerField()
    pumps_pumps = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return self.uid

    class Meta:
        verbose_name_plural = "CXN EDRs"


class EDRTrip(models.Model):
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    uid = models.CharField(max_length=50)
    edr_raw = models.OneToOneField(EDRRaw, related_name="edrraw_edrtrip",
                                 on_delete=models.CASCADE)  # 1EDRTrip to 1 raw line for now
    bha = models.ForeignKey(Interval, related_name="bha_edr_trip",
                            on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 interval
    interval = models.ForeignKey(Interval, related_name="interval_edr_trip",
                                 on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 interval
    total_time = models.DecimalField(max_digits=15, decimal_places=3)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    depth = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    trip_direction = models.BooleanField(default=False)
    casing = models.BooleanField(default=False)
    trip_count = models.IntegerField()
    bha_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.uid

    class Meta:
        verbose_name_plural = "Trip EDRs"


class EDRComment(models.Model):
    # job = models.ForeignKey(Job, related_name="job_edr_comments",
    #                         on_delete=models.PROTECT, null=True, blank=True)  # 0 or many EDR_Lines to 1 Job
    creation_date = models.DateTimeField(
        auto_now_add=True)  # date generated when created
    uid = models.CharField(max_length=50)
    rig_time = models.DateTimeField()
    comments = models.TextField()

    def __str__(self):
        return str(self.uid)

    class Meta:
        verbose_name_plural = "EDR Comments"
