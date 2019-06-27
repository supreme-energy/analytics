from personnel.api.views import PersonViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', PersonViewSet, base_name='personnel')
urlpatterns = router.urls
