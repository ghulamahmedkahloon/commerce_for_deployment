# Bismillahirahmanirahim
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, bids
from .forms import ListingForm, BiddingForm

def index(request):
    listings = Listing.objects.annotate(highest_bid=models.Max('bids__bid'))
    return render(request, "auctions/index.html",{
        'listings':listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# For Creating Listing
def listing_view(request):
    # If the user submits a form
    if request.method == 'POST':
        # Make a form and bound the data submitted with it in order to validate and save it.
        # As if data wont be bounded their wont be data in form to validate.
        form = ListingForm(request.POST)
        if form.is_valid():
            listiing = form.save(commit=False)
            #This saves the form but doesn't commit it to the database yet. 
            # This allows you to manually assign the listed_by field. 
            listiing.listed_by = request.user
            form.save()
            return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/listing.html",{'form': ListingForm()})


def current_listing(request, name):
    try:
        current = Listing.objects.get(title = name.title())
        #Makes bidding form and gives a default value for listing_id
        bidding_form = BiddingForm(initial = {'listing_id': current.id})
        
        # Get the highest bid if placed any
        highest_bid = current.bids.aggregate(max_bid = models.Max('bid'))['max_bid']
        

        return render(request, "auctions/current_listing.html",{
            'title': name,
            'listing': current,
            'bidding_form': bidding_form,
            'highest_bid': highest_bid
        })
    except:
        return HttpResponse(f'Sorry no listing with the title {name}')
    
def bid(request):
    """A func for handling the bidding"""
    if request.method == 'POST':
        #Makes a form and bound the data with it. Without it you wont be able to validate it.
        form = BiddingForm(request.POST)
        if form.is_valid():
            #The next step save the form but does not upload it to the database.
            bid = form.save(commit=False)
            bid.bidder = request.user
            bid.listing = get_object_or_404(Listing, id= form.cleaned_data['listing_id'])
            bid.save()
            return render(request, "auctions/current_listing.html",{
            'title': bid.listing.title,
            'listing': bid.listing,
            'highest_bid': bid.listing.bids.aggregate(max_bid = models.Max('bid'))['max_bid'],
            'bidding_form': BiddingForm(initial = {'listing': bid.listing})
            })
        else:
            listing_id = form.cleaned_data.get('listing_id')  # Get listing_id from the form
            listing = get_object_or_404(Listing, id=listing_id)
            return render(request, "auctions/current_listing.html", {
                'listing': listing,
                'bidding_form': form,
                'highest_bid': listing.bids.aggregate(max_bid = models.Max('bid'))['max_bid']
            })
    else:
        return HttpResponse("Invalid request method.")


def watchlist(request):
    '''Handles the watchlist of the user'''
    if request.method == 'POST':
        pass
    return render(request, 'auctions/watchlist.html')


def layout_view(request):
    return render(request, 'auctions/waqti_layout.html')