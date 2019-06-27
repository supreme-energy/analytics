from edrs.api.views import RTAVerticalViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', RTAVerticalViewSet, base_name='rta_vertical')
urlpatterns = router.urls
