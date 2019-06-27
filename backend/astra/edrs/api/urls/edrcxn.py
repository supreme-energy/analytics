from edrs.api.views import EDRCXNViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRCXNViewSet, base_name='edrcxn')
urlpatterns = router.urls
