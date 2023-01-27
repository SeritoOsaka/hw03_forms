from django import forms
from .models import Post

ROWS: int = 7


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control',
                                                   'rows': ROWS}),
            'group': forms.Select(attrs={'class': 'form-control'})
        }
