from edrs.api.views import RigStateViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RigStateViewSet, base_name='rig_state')
urlpatterns = router.urls
