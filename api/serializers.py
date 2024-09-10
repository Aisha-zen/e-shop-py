from rest_framework import serializers
from .models import User, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'username',
                  'date_joined', 'last_login')
        read_only_fields = ('id', 'email', 'date_joined', 'last_login')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'description',
                  'category', 'image', 'rating']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['rating'] = instance.get_rating()
        return representation

    def create(self, validated_data):
        rating_data = validated_data.pop('rating', None)
        product = Product.objects.create(**validated_data)
        if rating_data:
            product.set_rating(rating_data.get('rate', 0),
                               rating_data.get('count', 0))
            product.save()
        return product

    def update(self, instance, validated_data):
        rating_data = validated_data.pop('rating', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if rating_data:
            instance.set_rating(rating_data.get('rate', instance.get_rating()['rate']),
                                rating_data.get('count', instance.get_rating()['count']))
        instance.save()
        return instance
