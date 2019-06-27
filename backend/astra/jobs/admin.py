from django.contrib import admin
from .models import (Job, Interval, Formation, WellConnector)

admin.site.register(Job)
admin.site.register(Interval)
admin.site.register(Formation)
admin.site.register(WellConnector)
