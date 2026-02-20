from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseAssignmentViewSet, TeachingLoadReportViewSet, AlgorithmRunViewSet

router = DefaultRouter()
router.register('', CourseAssignmentViewSet)
router.register('load-reports', TeachingLoadReportViewSet)
router.register('algorithm-runs', AlgorithmRunViewSet)

urlpatterns = [path('', include(router.urls))]
