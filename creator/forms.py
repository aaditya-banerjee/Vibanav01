from django import forms
from store.models import DesignSubmission
from django.core.exceptions import ValidationError

class DesignSubmissionForm(forms.ModelForm):
    class Meta:
        model = DesignSubmission
        fields = ['title', 'description', 'image']
        
        # 1. Frontend Constraints: Inject HTML5 validation directly into the form
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'required': True, 
                'maxlength': '100',
                'placeholder': 'Enter your design title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'required': True, 
                'rows': 4,
                'placeholder': 'Tell us the inspiration behind this design...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'required': True, 
                'accept': 'image/png, image/jpeg' # Restrict file picker to images only
            }),
        }

    # 2. Backend Armor: The clean() method runs on the server to catch hackers/bypasses
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # Enforce a strict 5MB file size limit
            max_size = 5 * 1024 * 1024 # 5 Megabytes
            if image.size > max_size:
                raise ValidationError("This image is too large. Please keep file sizes under 5MB.")
            
            # Double-check the file extension just in case they bypassed the HTML5 'accept' tag
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("Invalid file type. Only PNG and JPEG formats are allowed.")
                
        return image