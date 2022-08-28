
from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import generics,permissions,mixins,status
from rest_framework.response import Response
from posts.models import Post
from posts.serializers import PostSerializers,VoteSerializers
from posts.models import Vote
# Create your views here.

class PostList(generics.ListCreateAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializers
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)

class RetrieveDestroy(generics.RetrieveDestroyAPIView):
    queryset=Post.objects.all()
    serializer_class=PostSerializers
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    def delete(self,request,*args,**kwargs):
        post= Post.objects.filter(pk=self.kwargs['pk'],poster=self.request.user)
        if post.exists():
            return self.destroy(request,*args,**kwargs)
        else:
            raise ValidationError("This is not your post buddy")


class VoteCreate(generics.CreateAPIView,mixins.DestroyModelMixin):
    serializer_class=VoteSerializers
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        post=Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(Voter=user,post=post)
    
    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError("You have already voted for this post")
        serializer.save(Voter=self.request.user,post=Post.objects.get(pk=self.kwargs['pk']))

    def delete(self,request,*args,**kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
             raise ValidationError("You never voted for this post")
        
    
