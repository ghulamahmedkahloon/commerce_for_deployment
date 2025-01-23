# Bismillahirahmanirahim
from django import forms
from .models import Listing, bids
from django.core.exceptions import ValidationError
from django.db import models


#Making a Form for listing.
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title','description','starting','image_url','category']
    # Adding Tailwind
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'rounded-md my-2 w-full border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter listing title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'rounded-md my-2 w-full border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Enter description',
            }),
            'starting': forms.NumberInput(attrs={
                'class': 'rounded-md my-2 w-full border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Starting price',
            }),
            'image_url': forms.TextInput(attrs={
                'class': 'rounded-md my-2 w-full border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter image URL',
            }),
            'category': forms.Select(attrs={
                'class': 'rounded-md my-2 w-full border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500',
            }),
        }
    

class BiddingForm(forms.ModelForm):
    # A form receives the listing_id but I will inshallah not submit it to the user.
    listing_id = forms.IntegerField(widget = forms.HiddenInput()) #Listing id is an integer so use an integer field.
    def clean(self):
        # Calls the parents class clean method to get the cleaned data.
        cleaned_data =  super().clean()
        # This ensures that all standard validation for fields like listing and bid is completed first.
        # In other words it is validated according to the default clean.

        ### After that below we write our custom validations.

        # Extract data for listing and biding
        listing_id = cleaned_data.get('listing_id')
        listing = Listing.objects.get(id=listing_id)
        bid = cleaned_data.get('bid')

        # Get the highest bid for the listing until now
        highest_bid = listing.bids.aggregate(max_bid = models.Max('bid'))['max_bid']
        # Check if the bid is atleast the starting price
        if highest_bid is None and bid < listing.starting:
            raise ValidationError(f'The bid must be atleast {listing.starting}')
        

        # Check if the bid is greater than the highest bid
        if highest_bid is not None and bid <= highest_bid:
            raise ValidationError(f'The Bid must be greater than {highest_bid}')

        # Return the cleaned data if everything is valid.

        # After we have performed custom validation we return the cleaned data so that django can use it
        # for further processing
        return cleaned_data


    class Meta:
        model = bids
        fields = ['bid']