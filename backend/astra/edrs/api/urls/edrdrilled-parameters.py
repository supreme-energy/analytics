from edrs.api.views import EDRDrilledParameterViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRDrilledParameterViewSet,
                base_name='edrdrilled-parameters')
urlpatterns = router.urls
