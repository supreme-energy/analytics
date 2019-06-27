from edrs.api.views import EDRScoutMotorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRScoutMotorViewSet, base_name='edrscoutmotor')
urlpatterns = router.urls
