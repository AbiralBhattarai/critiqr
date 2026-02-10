from django.db import models
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile',unique=True)
    bio = models.TextField(blank=True,null=True)
    avatar_url = models.ImageField(upload_to='avatars/',blank=True,null=True)

    def __str__(self):
        return f"Profile of {self.user}"
    

class Follower(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='followers')

    class Meta:
        unique_together = ('follower','following')

    def __str__(self):
        return f"{self.follower}->{self.following}"
    

class Movie(models.Model):
    movie_name = models.CharField(max_length=255,unique=True)
    movie_description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=50)
    length = models.IntegerField(help_text='Movie time in minutes')
    poster_url = models.URLField(blank=True,null=True)

    def __str__(self):
        return self.movie_name
    

class Person(models.Model):
    person_name = models.CharField(max_length=255)

    def __str__(self):
        return self.person_name
    

class MovieCast(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    role_type = models.CharField(max_length=20)

    class Meta:
        unique_together = ("movie", "person", "role_type")

    def __str__(self):
        return f"{self.person} in {self.movie} ({self.role_type})"



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='reviews')
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='reviews')
    review_content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f'Review by {self.user} on {self.movie}'
    


class WatchList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='watch_list')
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='watchlisted_by')

    class Meta:
        unique_together = ('user','movie')
    
    def __str__(self):
        return f'{self.user}->{self.movie}'
    

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='liked_by')
    
    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} likes {self.movie.movie_name}'


class Watched(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    
    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} has watched {self.movie.movie_name}'