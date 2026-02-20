from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeSlotViewSet, ScheduleSlotViewSet, ScheduleViewSet, ScheduleConflictViewSet

router = DefaultRouter()
router.register('time-slots', TimeSlotViewSet)
router.register('slots', ScheduleSlotViewSet)
router.register('schedules', ScheduleViewSet)
router.register('conflicts', ScheduleConflictViewSet)

urlpatterns = [path('', include(router.urls))]
