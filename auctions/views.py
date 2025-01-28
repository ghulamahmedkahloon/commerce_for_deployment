# Bismillahirahmanirahim
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required


from .models import User, Listing, Watchlist
from .forms import ListingForm, BiddingForm, CommentForm

def index(request):
    listings = Listing.objects.annotate(highest_bid=models.Max('bids__bid')).filter(Active=True)
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

@login_required
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
@login_required
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
        current = Listing.objects.get(title = name)
        #Makes bidding form and gives a default value for listing_id
        bidding_form = BiddingForm(initial = {'listing_id': current.id})
        
        # Get the highest bid if placed any
        highest_bid = current.bids.aggregate(max_bid = models.Max('bid'))['max_bid']
        biddings = current.bids.count() # Total number of bidings on the listing
        if highest_bid is not None:
            highest_bidder = current.bids.get(bid = highest_bid).bidder # The highest bidder
        else:
            highest_bidder = None
        comments = current.comments_on_listing.all() # All the comments on the listing
        comment_form = CommentForm(initial= {'listing_id': current.id})

        return render(request, "auctions/current_listing.html",{
            'title': name,
            'listing': current,
            'bidding_form': bidding_form,
            'highest_bid': highest_bid,
            'biddings': biddings,
            'highest_bidder': highest_bidder,
            'comments': comments,
            'comment_form': comment_form
        })
    except:
        return HttpResponse(f'Sorry no listing with the title {name}')

@login_required
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
            return HttpResponseRedirect(reverse('current_listing',args=[bid.listing.title]))
        else:
            listing_id = form.cleaned_data.get('listing_id')  # Get listing_id from the form
            listing = get_object_or_404(Listing, id=listing_id)
            highest_bid = listing.bids.aggregate(max_bid = models.Max('bid'))['max_bid']
            try:
                highest_bidder = listing.bids.get(bid = highest_bid).bidder
            except:
                highest_bidder = None
            return render(request, "auctions/current_listing.html", {
                'title':listing.title,
                'listing': listing,
                'bidding_form': form,
                'highest_bid': highest_bid,
                'biddings': listing.bids.count(),
                'highest_bidder': highest_bidder,
                'comments': listing.comments_on_listing.all(),
                'comment_form': CommentForm(initial= {'listing': listing,'listing_id': listing.id})
            })


    else:
        return HttpResponse("Invalid request method.")


@login_required
def comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            listing_id = form.cleaned_data['listing_id']
            listing = get_object_or_404(Listing, id=listing_id)
            liisting = form.save(commit=False)
            title = listing.title
            liisting.commenter = request.user
            liisting.listing = listing
            form.save()

            return HttpResponseRedirect(reverse('current_listing',args = [title]))


@login_required
def close_auction(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.Active = False
    listing.save()
    return HttpResponseRedirect(reverse('current_listing',args=[listing.title]))


@login_required
def watchlist(request):
    '''Handles the watchlistpage of the user'''
    watchlist, created = Watchlist.objects.get_or_create(watch_lister = request.user)
    listings = watchlist.watch_list_items.all().annotate(highest_bid=models.Max('bids__bid'))
    return render(request, 'auctions/watchlist.html',{
        'watchlist':watchlist,
        'listings':listings
    })

@login_required
def add_to_watchlist(request,listing_id):
    watchlist, created = Watchlist.objects.get_or_create(watch_lister = request.user)
    listing = get_object_or_404(Listing, id = listing_id)
    if watchlist.watch_list_items.filter(id = listing_id).exists():
        watchlist.watch_list_items.remove(listing)
        messages.info(request,'Listing Removed from the Watchlist.')
        return HttpResponseRedirect(reverse('current_listing',args=[listing.title]))
    else:
        watchlist.watch_list_items.add(listing)
        messages.success(request,'Listing added to the watchlist.')
        return HttpResponseRedirect(reverse('current_listing',args=[listing.title]))


def categories(request):
    catagory_list = []
    for value, label in Listing.CATEGORY_CHOICES:
        catagory_list.append(label)
    return render(request,'auctions/categories.html',{'catagory_list':catagory_list})

def category(request, category):
    if category != 'other':
        listings = Listing.objects.filter(category=category).annotate(highest_bid=models.Max('bids__bid')).filter(Active=True)
    else:
        listings = Listing.objects.filter(category= '').annotate(highest_bid=models.Max('bids__bid')).filter(Active=True)
        category = 'other catagories'
    return render(request,'auctions/category.html',{
        'listings':listings,
        'category':category})
