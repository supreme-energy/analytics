from edrs.api.views import EDRProcessedViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRProcessedViewSet, base_name='edrprocessed')
urlpatterns = router.urls
