from projections.api.views import ProjectionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ProjectionViewSet, base_name='projections')
urlpatterns = router.urls
