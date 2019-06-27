from jobs.api.views import WellConnectorViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', WellConnectorViewSet, base_name='well-connectors')
urlpatterns = router.urls
