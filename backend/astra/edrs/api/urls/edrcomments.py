from edrs.api.views import EDRCommentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EDRCommentViewSet, base_name='edrcomments')
urlpatterns = router.urls
