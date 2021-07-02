from rest_framework import serializers
from django.contrib.auth import get_user_model

from main.models import Post, Comment, Category

User = get_user_model()


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

    def get_rating(self, instance):
        total_rating = sum(instance.comment.values_list('rating', flat=True))
        reviews_count = instance.reviews.count()
        rating = total_rating / reviews_count if reviews_count > 0 else 0
        return round(rating, 1)

    def to_representation(self, instance):
        representation = super().to_representation(instance) # чтобы добавить
        representation['comment'] = CommentSerializer(instance.comment.all(), many=True).data
        representation['comment'] = self.get_rating(instance)
        return representation


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text1', 'post', 'rating')

    # def validate_product(self, post):
    #     request = self.context.get('request')
    #     if post.reviews.filter(author=request.user).exists():
    #         raise serializers.ValidationError('Вы не можете добавить второй отзыв на этот товар')
    #     return post

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










