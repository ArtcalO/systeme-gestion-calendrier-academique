from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModulePrerequisiteViewSet, EnrollmentRequestViewSet

router = DefaultRouter()
router.register('module-prerequisites', ModulePrerequisiteViewSet)
router.register('enrollment-requests', EnrollmentRequestViewSet)

urlpatterns = [path('', include(router.urls))]
