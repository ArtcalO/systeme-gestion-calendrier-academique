from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModulePrerequisiteViewSet

router = DefaultRouter()
router.register('module-prerequisites', ModulePrerequisiteViewSet)

urlpatterns = [path('', include(router.urls))]
