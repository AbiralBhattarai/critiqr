from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself'}),
            'avatar_url': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_content', 'rating']
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        
        if rating is not None:
            if rating < 1 or rating > 5:
                raise forms.ValidationError("Rating must be between 1 and 5.")
        
        return rating
    


class MovieWithCastForm(forms.Form):
    # Movie fields
    movie_name = forms.CharField(max_length=255)
    movie_description = forms.CharField(widget=forms.Textarea)
    release_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    genre = forms.CharField(max_length=50)
    length = forms.IntegerField(min_value=1, help_text='Movie time in minutes')
    poster_url = forms.URLField(required=False)
    
    # Cast fields comma separated
    cast = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Actor1, Actor2, Actor3'}),
        help_text='Enter cast names separated by commas'
    )
    role_type = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Actor, Director, Producer'}),
        help_text='Enter role types separated by commas (must match cast count)'
    )
    
    def clean_length(self):
        length = self.cleaned_data.get('length')
        
        if length is not None:
            if length <= 0:
                raise forms.ValidationError("Movie length must be greater than 0 minutes.")
        
        return length
