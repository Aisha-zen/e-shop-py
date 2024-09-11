from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer, UserDetailsSerializer
from rest_framework import generics, status
from .models import Product, Category
from django.shortcuts import get_object_or_404
from .serializers import ProductSerializer, CategorySerializer
from .recommender import recommend

# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()
        # Logout the user (clears the session)
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserDetailsSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductRetrieveView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ProductCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProductUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class ProductDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BulkProductCreateAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        products_data = request.data

        if not isinstance(products_data, list):
            return Response({"error": "Invalid data format, expected a list of products"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=products_data, many=True)
        if serializer.is_valid():
            serializer.save()  # This will create all the products in bulk
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommenderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        top_n = 5
        recommended_products = recommend(pk, top_n)
        data = []

        for id in recommended_products:
            obj = get_object_or_404(Product, id=id)
            serializer = ProductSerializer(obj)
            data.append(serializer.data)

        return Response(data, status=status.HTTP_200_OK)


class CategoryView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
