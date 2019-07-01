from edrs.api.views import WellOverviewViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', WellOverviewViewSet, base_name='welloverview')
urlpatterns = router.urls
