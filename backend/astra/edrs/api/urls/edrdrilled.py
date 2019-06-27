from edrs.api.views import EDRDrilledViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRDrilledViewSet, base_name='edrdrilled')
urlpatterns = router.urls
