from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'attendances/levels', AttendanceLevelViewSet, basename='attendancelevel')
router.register(r'attendances', AttendanceViewSet, basename='attendance')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'homework-reviews', GroupHomeWorkViewSet, basename='homeworkreview')
router.register(r'homework-submissions', HomeWorkViewSet, basename='homeworksubmission')
router.register(r'table-types', TableTypeViewSet, basename='tabletype')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'parents', ParentsViewSet, basename='parent')
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'teachers', TeacherViewSet, basename='teachers')


urlpatterns = [
    path('create/student/', StudentCreateAPIView.as_view(), name='create-student'),
    path('create/teacher/', TeacherCreateAPIView.as_view(), name='create-teacher'),
    
    path('users/create/user/', UserCreateView.as_view(), name='create-user'),
    path("users/create/superuser/", CreateSuperUserView.as_view(), name="create-superuser"),
    path('users/student-groups/<int:student_id>/', StudentGroupsView.as_view(), name='student-groups'),
    path('teacher/dashboard/', TeacherDashboard.as_view(), name='teacher-dashboard'),
    path('student/dashboard/', StudentDashboard.as_view(), name='student-dashboard'),

    path('teachers/<int:teacher_id>/groups/', teacher_group_list, name='teacher-group-list'),
    path('students/attendance/', StudentAttendanceListView.as_view(), name='student-attendance'),

    # path('create/student/', StudentCreateAPIView.as_view(), name='create-student'),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", CurrentUserView.as_view(), name="me"),
    
    path("statistics/students-statistic/", StudentStatisticView.as_view(), name="students-statistic"),
    path("statistics/teachers-statistic/", TeacherStatisticView.as_view(), name="teachers-statistic"),
    path("statistics/attendance-statistics/", AttendanceStatisticView.as_view(), name="attendance-statistics"),
    path("statistics/courses-statistics/", CourseStatisticView.as_view(), name="courses-statistics"),
    path("statistics/groups-statistics/", GroupStatisticView.as_view(), name="groups-statistics"),

    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/set-new-password/', SetNewPasswordAPIView.as_view(), name='set-new-password'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path("auth/token/refresh-only/", ObtainRefreshTokenView.as_view(), name="obtain_refresh_token"),
    
    path('', include(router.urls)),
]