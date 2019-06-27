from django.contrib import admin
from .models import (EDRRaw, EDRProcessed, EDRDrilled, EDRScoutMotor, EDRCXN, EDRTrip, EDRComment)


admin.site.register(EDRRaw)
admin.site.register(EDRProcessed)
admin.site.register(EDRDrilled)
admin.site.register(EDRScoutMotor)
admin.site.register(EDRCXN)
admin.site.register(EDRTrip)
admin.site.register(EDRComment)
