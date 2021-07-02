from django_filters import filters
from rest_framework import status, viewsets, mixins, generics
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# from .filters import PostFilter
from .models import *

from .permissions import IsAuthorOrAdminPermission, DenyAll
from .serializers import PostListSerializer, PostDetailsSerializer, CommentSerializer



class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostDetailsSerializer
    # filter_backends = (filters.DjangoFilterBackend)
    # filterset_class = PostFilter


    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_review', 'like']:
            return [IsAuthenticated()]
        return []


    # api/v1/products/id/create_review
    @action(detail=True, methods=['POST'])
    def create_review(self, request, pk):
        data = request.data.copy()
        data['post'] = pk
        serializer = CommentSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)



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
















