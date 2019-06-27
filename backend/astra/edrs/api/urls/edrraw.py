from edrs.api.views import EDRRawViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRRawViewSet, base_name='edrraw')
urlpatterns = router.urls
