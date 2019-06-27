from personnel.api.views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', UserViewSet, base_name='users')
urlpatterns = router.urls
