from rest_framework import viewsets, status, generics
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import TokenRefreshView
from .models import *
from .serializers import *
from django.db.models import Q
from .serializers import UserAndStudentSerializer
from .serializers import TeacherSerializer
from .permissions import AdminUser
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .permissions import IsTeacher, IsStudent

class TeacherDashboard(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        return Response({"message": "Bu sahifa faqat o‘qituvchilar uchun!"})


class StudentDashboard(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        return Response({"message": "Siz faqat ko‘rishingiz mumkin!"})

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAllSerializer 

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def login(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = authenticate(phone=phone, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Parol muvaffaqiyatli o‘zgartirildi'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
        
    @api_view(['GET'])
    def user_list(request):
        users = User.objects.all()
        serializer = UserAllSerializer(users, many=True)
        return Response(serializer.data)
    
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AdminUser]

    @swagger_auto_schema(request_body=UserCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class StudentStatisticView(generics.GenericAPIView):
    serializer_class = StudentStatisticSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=StudentStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            student_count = Student.objects.filter(created__range=[start_date, end_date]).count()
            return Response({"student_count": student_count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        # Extract user data
        user_data = data.get('user', {})
        phone = user_data.get('phone')
        full_name = user_data.get('full_name')
        password = user_data.get('password')

        # Extract teacher data
        teacher_data = data.get('teacher', {})
        descriptions = teacher_data.get('descriptions')

        # Validate phone number
        if not phone:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(phone=phone).exists():
            return Response({'error': 'User with this phone number already exists'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Create user
        try:
            user = User.objects.create(
                phone=phone,
                full_name=full_name,
                is_active=True
            )
            user.set_password(password)
            user.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create teacher
        try:
            teacher = Teacher.objects.create(
                user=user,
                descriptions=descriptions
            )
        except Exception as e:
            # If teacher creation fails, delete the created user
            user.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return success response
        return Response({
            'message': 'Teacher created successfully',
            'teacher_id': teacher.id,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

class TeacherStatisticView(generics.GenericAPIView):
    serializer_class = TeacherStatisticSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=TeacherStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            teacher_count = Teacher.objects.filter(created__range=[start_date, end_date]).count()
            return Response({"teacher_count": teacher_count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceStatisticView(generics.GenericAPIView):
    serializer_class = AttendanceStatisticSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=AttendanceStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            attendance_count = Attendance.objects.filter(created__range=[start_date, end_date]).count()
            return Response({"attendance_count": attendance_count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseStatisticView(generics.GenericAPIView):
    serializer_class = CourseStatisticSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=CourseStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            course_count = Course.objects.filter(created__range=[start_date, end_date]).count()
            return Response({"course_count": course_count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupStatisticView(generics.GenericAPIView):
    serializer_class = GroupStatisticSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=GroupStatisticSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            group_count = Group.objects.filter(created__range=[start_date, end_date]).count()
            return Response({"group_count": group_count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateSuperUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SuperUserCreateSerializer
    permission_classes = [IsAdminUser]  # Faqat admin foydalanuvchilar yaratishi mumkin

    @swagger_auto_schema(request_body=SuperUserCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_superuser=True, is_staff=True)
            return Response({"message": "Superuser muvaffaqiyatli yaratildi!", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TeacherViewSet(viewsets.ModelViewSet):
    """
    O‘qituvchilar uchun CRUD ViewSet
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AdminUser]  

    @swagger_auto_schema(request_body=UserAndTeacherSerializer)
    @action(detail=False, methods=['post'], permission_classes=[AdminUser])
    def create_teacher(self, request):
        """
        O‘qituvchi yaratish (User va Teacher ma’lumotlarini birgalikda qabul qiladi)
        """
        user_data = request.data.get('user', {})
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user = user_serializer.save(is_teacher=True)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        teacher_data = request.data.get('teacher', {})
        teacher_serializer = TeacherSerializer(data=teacher_data)

        if teacher_serializer.is_valid():
            teacher_serializer.save(user=user)
            return Response(teacher_serializer.data, status=status.HTTP_201_CREATED)
        else:
            user.delete()
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_group_list(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    groups = teacher.group_set.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)
    
class TeacherListView(ListAPIView):
    queryset = Teacher.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AdminUser]
 
# --- Authentication Views ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data.get('phone')
        password = serializer.validated_data.get('password')
        user = authenticate(request, phone=phone, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# --- Attendance ViewSets ---
class AttendanceLevelViewSet(viewsets.ModelViewSet):
    queryset = AttendanceLevel.objects.all()
    serializer_class = AttendanceLevelSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

# --- Courses ViewSet ---
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# --- Groups ViewSet ---
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def students_add(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            group.students.add(student)
            return Response({'detail': 'Student added successfully.'})
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def teachers_add(self, request, pk=None):
        group = self.get_object()
        teacher_id = request.data.get('teacher_id')
        try:
            teacher = Worker.objects.get(id=teacher_id)
            group.teachers.add(teacher)
            return Response({'detail': 'Teacher added successfully.'})
        except Worker.DoesNotExist:
            return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def students_remove(self, request, pk=None):
        group = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            group.students.remove(student)
            return Response({'detail': 'Student removed successfully.'})
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def teachers_remove(self, request, pk=None):
        group = self.get_object()
        teacher_id = request.data.get('teacher_id')
        try:
            teacher = Worker.objects.get(id=teacher_id)
            group.teachers.remove(teacher)
            return Response({'detail': 'Teacher removed successfully.'})
        except Worker.DoesNotExist:
            return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

# --- Homework ViewSets ---
class GroupHomeWorkViewSet(viewsets.ModelViewSet):
    queryset = GroupHomeWork.objects.all()
    serializer_class = GroupHomeWorkSerializer

class HomeWorkViewSet(viewsets.ModelViewSet):
    queryset = HomeWork.objects.all()
    serializer_class = HomeWorkSerializer

# --- Table Types and Tables ViewSets ---
class TableTypeViewSet(viewsets.ModelViewSet):
    queryset = TableType.objects.all()
    serializer_class = TableTypeSerializer

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

# --- Student & Parent ViewSets ---

class StudentViewSet(viewsets.ModelViewSet):
    """Student CRUD API - qo'shish, ko'rish, yangilash, o‘chirish"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        """Yangi student qo‘shish"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Student muvaffaqiyatli qo‘shildi!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def studying(self, request):
        """O‘qiyotgan studentlar"""
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if not start_date or not end_date:
            return Response({"error": "start_date va end_date berilishi shart!"}, status=400)

        students = Student.objects.filter(
            Q(group__start_date__lte=end_date) & Q(group__end_date__gte=start_date)
        ).distinct()

        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def graduated(self, request):
        """Bitirgan studentlar"""
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if not start_date or not end_date:
            return Response({"error": "start_date va end_date berilishi shart!"}, status=400)

        students = Student.objects.filter(
            Q(group__end_date__gte=start_date) & Q(group__end_date__lte=end_date)
        ).distinct()

        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def enrolled(self, request):
        """Qabul qilingan studentlar"""
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if not start_date or not end_date:
            return Response({"error": "start_date va end_date berilishi shart!"}, status=400)

        students = Student.objects.filter(
            Q(created__gte=start_date) & Q(created__lte=end_date)
        ).distinct()

        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

class ParentsViewSet(viewsets.ModelViewSet):
    queryset = Parents.objects.all()
    serializer_class = ParentSerializer

# --- Worker ViewSet ---
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

# --- Comment ViewSet ---
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AdminUser]

# --- Password Management Views ---
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")

        user = User.objects.filter(phone=phone).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        return Response({"status": False, "detail": "Telefon raqam yoki parol noto‘g‘ri"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#  Parolni tiklash (OTP yuborish)
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP muvaffaqiyatli yuborildi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP ni tekshirish
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            otp = serializer.validated_data["otp"]
            user = User.objects.filter(phone=phone, otp_code=otp).first()

            if user:
                return Response({"message": "OTP to‘g‘ri"}, status=status.HTTP_200_OK)

            return Response({"status": False, "detail": "OTP tasdiqlanmagan"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Yangi parol o‘rnatish
class SetNewPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Parol muvaffaqiyatli o‘zgartirildi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ObtainRefreshTokenView(APIView):
    """
    Foydalanuvchi login orqali faqat refresh token oladi.
    """
    permission_classes = [AllowAny]  
    serializer_class = RefreshTokenSerializer  # 🔥 Mana shu qator Swaggerga inputlarni chiqaradi

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)  
                return Response({"refresh": str(refresh)}, status=status.HTTP_200_OK)

            return Response({"detail": "Login yoki parol noto‘g‘ri"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Tokenni yangilash
class CustomTokenRefreshView(TokenRefreshView):
    """Refresh token orqali yangi access token yaratish"""
    permission_classes = [AllowAny]  # Barcha foydalanuvchilar foydalanishi mumkin

    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "status": True,
                "message": "Token muvaffaqiyatli yangilandi",
                "data": serializer.validated_data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": False,
            "detail": "Token yaroqsiz yoki muddati tugagan",
            "code": "token_not_valid"
        }, status=status.HTTP_401_UNAUTHORIZED)


class ProtectedAPIView(APIView):
    """Token talab qiladigan API"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Siz muvaffaqiyatli autentifikatsiyadan o‘tdingiz!"})
# class TeacherCreateAPIView(APIView):
#     permission_classes = [AdminUser]

#     @swagger_auto_schema(request_body=UserAndTeacherSerializer)
#     def post(self, request):
#         user_data = request.data.get('user', {})
#         user_serializer = UserSerializer(data=user_data)

#         if user_serializer.is_valid():
#             user = user_serializer.save(is_teacher=True)
#         else:
#             return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         teacher_data = request.data.get('teacher', {})   
#         teacher_serializer = TeacherSerializer(data=teacher_data)

#         if teacher_serializer.is_valid():
#             teacher_serializer.save(user=user)
#             return Response(teacher_serializer.data, status=status.HTTP_201_CREATED)

#         else:
#             user.delete()
#             return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherCreateAPIView(APIView):
    permission_classes = [AdminUser]

    @swagger_auto_schema(request_body=UserAndTeacherSerializer)
    def post(self, request):
        user_data = request.data.get('user', {})
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user = user_serializer.save(is_teacher=True)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        teacher_data = request.data.get('teacher', {})   
        teacher_serializer = TeacherSerializer(data=teacher_data)

        if teacher_serializer.is_valid():
            teacher_serializer.save(user=user)
            return Response(teacher_serializer.data, status=status.HTTP_201_CREATED)

        else:
            user.delete()
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentCreateAPIView(APIView):
    permission_classes = [AdminUser]

    @swagger_auto_schema(request_body=UserAndStudentSerializer)
    def post(self, request):

        user_data = request.data.get('user', {})
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user = user_serializer.save(is_student=True)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student_data = request.data.get('student', {})
        student_serializer = StudentSerializer(data=student_data)

        if student_serializer.is_valid():
            student = student_serializer.save(user=user)
            return Response(student_serializer.data, status=status.HTTP_201_CREATED)

        else:
            user.delete()
            return Response(student_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class StudentGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        groups = student.group.all()  # Talabaning barcha guruhlarini olish
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class StudentAttendanceListView(ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Attendance.objects.filter(student=self.request.user.student)

class CurrentUserView(RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

# class StudentCreateAPIView(APIView):
#     permission_classes = [AdminUser]

#     @swagger_auto_schema(request_body=UserAndStudentSerializer)
#     def post(self, request):

#         user_data = request.data.get('user', {})
#         user_serializer = UserSerializer(data=user_data)

#         if user_serializer.is_valid():
#             user = user_serializer.save(is_student=True)
#         else:
#             return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         student_data = request.data.get('student', {})
#         student_serializer = StudentSerializer(data=student_data)

#         if student_serializer.is_valid():
#             student = student_serializer.save(user=user)
#             return Response(student_serializer.data, status=status.HTTP_201_CREATED)

#         else:
#             user.delete()
#             return Response(student_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
