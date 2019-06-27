from edrs.api.views import EDRTripViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRTripViewSet, base_name='edrtrips')
urlpatterns = router.urls
