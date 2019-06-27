from bhas.api.views import BhaViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', BhaViewSet, base_name='bhas')
urlpatterns = router.urls
