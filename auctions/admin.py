from django.contrib import admin
from .models import User, Listing, bids, Watchlist

class BiddingLook(admin.ModelAdmin):
    list_display = ('listing', 'bid','bidder')
# Register your models here.
admin.site.register(User)
admin.site.register(Listing)
admin.site.register(bids, BiddingLook)
admin.site.register(Watchlist)