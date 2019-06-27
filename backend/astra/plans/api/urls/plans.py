from plans.api.views import PlanViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', PlanViewSet, base_name='plans')
urlpatterns = router.urls
