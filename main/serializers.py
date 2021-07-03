from rest_framework import serializers
from django.contrib.auth import get_user_model

from main.models import Post, Comment, Category

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'category', 'text', 'created_at', 'author', 'image')



class PostDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


    def get_rating(self, instance):
        total_rating = sum(instance.comments.values_list('rating', flat=True))
        comments_count = instance.comments.count()
        rating = total_rating / comments_count if comments_count > 0 else 0
        return round(rating, 1)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        representation['rating'] = self.get_rating(instance)
        return representation



class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('id', 'f_name')


    def validate_product(self, post):
        request = self.context.get('request')
        if post.comments.filter(author=request.user).exists():
            raise serializers.ValidationError('Вы не можете добавить второй отзыв на этот товар')
        return post


    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['f_name'] = request.user
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['f_name'] = CommentAuthorSerializer(instance.f_name).data
        return rep











