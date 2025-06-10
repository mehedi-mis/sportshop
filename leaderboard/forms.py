from django import forms
from .models import TriviaQuestion


class TriviaQuestionForm(forms.ModelForm):
    class Meta:
        model = TriviaQuestion
        fields = [
            'question',
            'sport',
            'difficulty',
            'option1',
            'option2',
            'option3',
            'option4',
            'correct_answer',
            'explanation',
            'is_active',
        ]
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sport': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'correct_answer': forms.Select(attrs={'class': 'form-select'}),
            'option1': forms.TextInput(attrs={'class': 'form-control'}),
            'option2': forms.TextInput(attrs={'class': 'form-control'}),
            'option3': forms.TextInput(attrs={'class': 'form-control'}),
            'option4': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
