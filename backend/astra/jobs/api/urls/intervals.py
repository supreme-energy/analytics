from jobs.api.views import IntervalViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', IntervalViewSet, base_name='intervals')
urlpatterns = router.urls
