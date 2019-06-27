from edrs.api.views import RTACurveViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RTACurveViewSet, base_name='rta_curves')
urlpatterns = router.urls
