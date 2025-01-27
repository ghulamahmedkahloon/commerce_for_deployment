# Bismillahirahmanirahim
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    #It already makes fields for name, email and password
    #If we want we can make more fields here. But I am leaving with as it is.
    pass


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics','Electronics'),
        ('Toys','Toys'),
        ('Home','Home'),
        ('Fashion','Fashion'),
        ('Magical','Magical')
    ]
    title = models.CharField(max_length= 50)
    description = models.TextField(max_length=1000)
    starting = models.DecimalField(max_digits=10, decimal_places= 2)
    image_url = models.URLField(blank=True, max_length= 1000)
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES, blank=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'listings')
    time_created = models.DateTimeField(auto_now_add=True) #Records the time when an entry is created.
    # It wont change when it is updated.

    # Records whether the listing is Active or not.
    Active = models.BooleanField(default=True)
    def __str__(self):
        return f'{self.title} starting from {self.starting} by {self.listed_by}'
    

class bids(models.Model):
    listing = models.ForeignKey(Listing, on_delete= models.CASCADE, related_name= 'bids')
    bidder = models.ForeignKey(User, on_delete= models.CASCADE, related_name= 'biddings', null = True)
    bid = models.DecimalField(max_digits=10, decimal_places= 2, null = True)

    class Meta:
        verbose_name = 'bid'

    def __str__(self):
        return f'{self.bidder} bidded {self.bid} on {self.listing}'



class comments(models.Model):
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE, related_name='comments_on_listing',null = True)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_comments', null = True)
    comment = models.TextField(max_length=1000, null=True)
    posted = models.DateField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'comment'

    def __str__(self):
        return f'{self.id}: {self.commenter} commented on {self.listing}'

class Watchlist(models.Model):
    watch_lister = models.OneToOneField(User, on_delete= models.CASCADE)
    watch_list_items = models.ManyToManyField(Listing, related_name='watchlist')