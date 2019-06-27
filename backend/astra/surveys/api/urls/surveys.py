from surveys.api.views import SurveyViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', SurveyViewSet, base_name='surveys')
urlpatterns = router.urls
