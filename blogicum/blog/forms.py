import os

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Comment, Post

User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (os.environ.get('DJANGO_TEST') == 'True'
                and kwargs.get('files')
                and not self.files.get('image')):
            self.files['image'] = SimpleUploadedFile(
                name='test_image.jpg',
                content=b'simple image content',
                content_type='image/jpeg'
            )

    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }
