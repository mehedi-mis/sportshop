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
            'question': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }
