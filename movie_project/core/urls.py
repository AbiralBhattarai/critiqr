from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('secret/', views.secret, name='secret'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('profile/watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/<str:username>/<str:action>/', views.list_follow, name='show_follow'),
    path('movies/', views.list_movies, name='get_all_movies'),
    path('movies/add/', views.add_movie, name='add_movie'),
    path('movies/search/', views.search_movies, name='search_movies'),
    path('movies/<int:movie_id>/',views.list_one_movie,name='list_one_movie'),
    path('movies/<int:movie_id>/review/', views.write_review, name='add_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('review/edit/<int:review_id>',views.edit_review,name = 'edit_review'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('feed/', views.feed, name='feed'),
]