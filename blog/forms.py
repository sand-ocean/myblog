
from django import forms
from .models import Post,Comment
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title','slug','content','category','status',]
        labels = {
            'title':'标题','slug':'URL别名','content':'正文','category':'分类','status':'状态'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {'content':'评论'}
