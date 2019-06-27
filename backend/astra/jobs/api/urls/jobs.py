from jobs.api.views import JobViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', JobViewSet, base_name='jobs')
urlpatterns = router.urls
