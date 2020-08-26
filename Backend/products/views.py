from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, exceptions
from .models import Product, Seller, Category
from .serializers import ProductSerializer, ProductsAllInfoSerializer, CategorySerializer, SellerSerializer


class ProductList(APIView):
    """
    List all products or create new one
    """

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductsAllInfoSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIVIew(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    filter_fields = (
        'category__id',
    )
    search_fields = (
        'title',
    )


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class SellerViewSet(ModelViewSet):
    serializer_class = SellerSerializer
    queryset = Seller.objects.all()
