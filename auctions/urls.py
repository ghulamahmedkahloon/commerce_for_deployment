from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('watchlist/<int:listing_id>', views.add_to_watchlist, name="add_to_watchlist"),
    path('create_listing', views.listing_view, name="listing"),
    path('comment', views.comment, name="comment"),
    path('bid',views.bid, name="bid"),
    path('close_auction/<int:listing_id>', views.close_auction, name="close_auction"),
    path('<str:name>', views.current_listing, name="current_listing")
]
