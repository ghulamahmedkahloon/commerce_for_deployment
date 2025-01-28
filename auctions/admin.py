from django.contrib import admin
from .models import User, Listing, bids, Watchlist, comments

class BiddingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'bid','bidder')

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title','category','starting','listed_by')

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('listing', 'commenter','posted')

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ('watch_list_items',)
# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(bids, BiddingAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(comments, CommentsAdmin)