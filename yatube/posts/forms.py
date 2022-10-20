from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels_text = {
            'text': ('текст'),
        }
        labels_group = {
            'group': ('группа'),
        }
        labels_image = {
            'image': ('картинка'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': ('текст'),
        }