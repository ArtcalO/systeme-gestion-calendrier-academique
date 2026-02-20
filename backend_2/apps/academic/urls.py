from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (FacultyViewSet, DepartmentViewSet, ProgramViewSet, LevelViewSet,
                    SubjectViewSet, ModuleViewSet, AcademicYearViewSet, CourseViewSet,
                    RoomViewSet, StudentModuleResultViewSet)

router = DefaultRouter()
router.register('faculties', FacultyViewSet)
router.register('departments', DepartmentViewSet)
router.register('programs', ProgramViewSet)
router.register('levels', LevelViewSet)
router.register('subjects', SubjectViewSet)
router.register('modules', ModuleViewSet)
router.register('academic-years', AcademicYearViewSet)
router.register('courses', CourseViewSet)
router.register('rooms', RoomViewSet)
router.register('results', StudentModuleResultViewSet)

urlpatterns = [path('', include(router.urls))]
