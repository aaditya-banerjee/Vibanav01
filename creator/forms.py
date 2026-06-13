from django import forms
from store.models import DesignSubmission # <-- Notice we import from store!

class DesignSubmissionForm(forms.ModelForm):
    class Meta:
        model = DesignSubmission
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of your design'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about the inspiration...'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }