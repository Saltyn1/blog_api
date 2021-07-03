from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from rest_framework import status, viewsets, mixins, generics
from rest_framework.decorators import api_view, action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import *

from .permissions import IsAuthorOrAdminPermission, DenyAll
from .serializers import PostListSerializer, PostDetailsSerializer, CommentSerializer, FavouriteListSerializer, \
    CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostDetailsSerializer


    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_comment', 'like']:
            return [IsAuthenticated()]
        return []

    @action(detail=False, methods=['GET'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')          #возвращает словарь
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(text__icontains=q))
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)


    def get_queryset(self):
        queryset = super().get_queryset()
        days_count = int(self.request.query_params.get('days', 0))
        if days_count > 0:
            start_date = timezone.now() - timedelta(days=days_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset



    @action(detail=True, methods=['POST'])
    def create_comment(self, request, pk):
        data = request.data.copy()
        data['posts'] = pk
        serializer = CommentSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)


    @action(detail=True, methods=['POST'])
    def like(self, request, pk):
        post = self.get_object()
        user = request.user
        like_obj, created = LikeList.objects.get_or_create(post=post, user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save()
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')



class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrAdminPermission()]


















