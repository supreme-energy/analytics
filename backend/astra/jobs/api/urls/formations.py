from jobs.api.views import FormationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', FormationViewSet, base_name='formations')
urlpatterns = router.urls
