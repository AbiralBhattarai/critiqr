from django.contrib import admin
from .models import (
    Profile,
    Follower,
    Movie,
    Person,
    MovieCast,
    Review,
    WatchList
)
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'avatar_url')

@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')
    search_fields = ('follower__username', 'following__username')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('movie_name', 'genre', 'release_date', 'length')
    search_fields = ('movie_name', 'genre')

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_name',)
    search_fields = ('person_name',)

@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ('movie', 'person', 'role_type')
    search_fields = ('movie__movie_name', 'person__person_name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    search_fields = ('user__username', 'movie__movie_name')
    list_filter = ('rating', 'created_at')

@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')
    search_fields = ('user__username', 'movie__movie_name')