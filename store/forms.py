from django import forms
from .models import DesignSubmission

class DesignSubmissionForm(forms.ModelForm):
    class Meta:
        model = DesignSubmission
        # We only want the designer to fill out these three fields
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of your design'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about the inspiration...'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }