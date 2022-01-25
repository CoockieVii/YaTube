from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Категория не выбрана"

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
