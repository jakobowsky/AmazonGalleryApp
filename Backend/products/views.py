from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, exceptions
from rest_framework.response import Response
from .models import Product, Seller, Category
from .serializers import ProductSerializer, ProductsAllInfoSerializer, CategorySerializer, SellerSerializer
from datetime import datetime
import pytz


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


class ReportView(APIView):
    """
    POST method ONLY
    """

    def post(self, request):
        data = request.data
        self.validate(data)
        category = data.get('category')
        products = data.get('products')
        date = data.get('date')
        category_obj = self.get_category(category)
        response = self.handle_products(products, category_obj, date)
        return Response({"message": response})

    def handle_products(self, products, category_obj, date):
        response = []
        for product in products:
            seller_obj, _ = Seller.objects.get_or_create(name=product.get('seller'))
            date_formatted = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
            date_formatted = pytz.utc.localize(date_formatted)
            obj, created = Product.objects.update_or_create(
                asin=product.get('asin'),
                seller=seller_obj,
                category=category_obj,
                defaults={
                    'photo': product.get('photo'),
                    'updated': date_formatted,
                    'price': product.get('price'),
                    'title': product.get('title'),
                }
            )
            if created:
                response.append(f'{obj.asin} - {obj.title} - created')
            else:
                response.append(f'{obj.asin} - {obj.title} - updated')
        return response

    def get_category(self, category):
        obj, _ = Category.objects.get_or_create(name=category.title())
        return obj

    def validate(self, data):
        if data.get('category') is None:
            raise exceptions.ValidationError(
                'category is null'
            )
        if data.get('products') is None:
            raise exceptions.ValidationError(
                'products is null'
            )
        if data.get('date') is None:
            raise exceptions.ValidationError(
                'date is null'
            )
