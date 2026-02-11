from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Avg,Count
from django.contrib.admin.views.decorators import staff_member_required
from .models import *
from .forms import *
from django.conf import settings

# Create your views here.
def home(request):
    all_movies = Movie.objects.all()
    person = Person.objects.all()
    context = {'movie':all_movies,
            'person':person}
    return render(request,'core/home.html',context=context)



def view_profile(request,username:str):
    User = get_user_model()
    curr_user = get_object_or_404(User,username=username)
    if username == request.user.username:
        return redirect('profile')
    
    username = curr_user.username
    followers = curr_user.followers.all()
    following = curr_user.following.all()
    avatar = curr_user.profile.avatar_url if hasattr(curr_user, 'profile') else None
    bio = curr_user.profile.bio if hasattr(curr_user, 'profile') else "bio"
    watch_list = WatchList.objects.filter(user=curr_user)
    watched = Watched.objects.filter(user=curr_user)
    liked = Like.objects.filter(user=curr_user)
    reviews = curr_user.reviews.all()
    is_following = Follower.objects.filter(
        follower = request.user,
        following = curr_user
    ).exists()
    context = {
        'username': username,
        'followers': followers,
        'following': following,
        'avatar': avatar,
        'bio': bio,
        'watch_list': watch_list,
        'reviews': reviews,
        'is_following':is_following,
        'liked':liked,
        'watched':watched
    }
    return render(request,'core/view_profile.html',context=context)



@login_required
def secret(request):
    return render(request,'core/secret.html')



@login_required
def profile(request):
    curr_user = request.user
    username = curr_user.username
    followers = curr_user.followers.all()
    following = curr_user.following.all()
    avatar = curr_user.profile.avatar_url if hasattr(curr_user, 'profile') else None
    bio = curr_user.profile.bio if hasattr(curr_user, 'profile') else "bio"
    watch_list = WatchList.objects.filter(user=curr_user)
    watched = Watched.objects.filter(user=curr_user)
    liked = Like.objects.filter(user=curr_user)
    reviews = curr_user.reviews.all()
    
    context = {
        'username': username,
        'followers': followers,
        'following': following,
        'avatar': avatar,
        'bio': bio,
        'watch_list': watch_list,
        'watched': watched,
        'liked': liked,
        'reviews': reviews
    }
    return render(request, 'core/profile.html', context=context)



@login_required
def edit_profile(request):
    curr_user = request.user
    curr_profile = curr_user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=curr_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=curr_profile)
    context={'username':curr_user.username,
        'form':form}
    return render(request,'core/edit_profile.html',context=context)


def is_admin(user):
    return user.is_staff


@staff_member_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieWithCastForm(request.POST)
        
        if form.is_valid():
            movie = Movie.objects.create(
                movie_name=form.cleaned_data['movie_name'],
                movie_description=form.cleaned_data['movie_description'],
                release_date=form.cleaned_data['release_date'],
                genre=form.cleaned_data['genre'],
                length=form.cleaned_data['length'],
                poster_url=form.cleaned_data['poster_url']
            )
            
            cast_input = form.cleaned_data.get('cast', '').strip()
            role_input = form.cleaned_data.get('role_type', '').strip()
            
            if cast_input:
                cast_names = [name.strip() for name in cast_input.split(',')]
                role_types = [role.strip() for role in role_input.split(',')] if role_input else []
                
                for index, cast_name in enumerate(cast_names):
                    if cast_name:
                        #default to actor as role if role not provided.
                        role_type = role_types[index] if index < len(role_types) else 'Actor'
                        
                        person, created = Person.objects.get_or_create(
                            person_name=cast_name
                        )
                        
                        MovieCast.objects.create(
                            movie=movie,
                            person=person,
                            role_type=role_type
                        )
            
            return redirect('list_movies')
    else:
        form = MovieWithCastForm()
    
    context = {'form': form}
    return render(request, 'core/movie_handling.html', context=context)



@login_required
def follow_user(request, username: str):
    User = get_user_model()
    user_to_follow = get_object_or_404(User, username=username)
    curr_user = request.user
    
    # check if curr user is the user to follow
    if curr_user == user_to_follow:
        return redirect('view_profile', username=username)
    
    # create or get the follow relationship
    Follower.objects.get_or_create(
        follower=curr_user,
        following=user_to_follow
    )
    
    return redirect('view_profile', username=username)


@login_required
def unfollow_user(request,username:str):
    User = get_user_model()
    user_to_unfollow = get_object_or_404(User,username=username)
    curr_user = request.user

    Follower.objects.filter(follower=curr_user,following=user_to_unfollow).delete()
    return redirect('view_profile',username=username)


@login_required
def list_follow(request, username: str, action: str):
    User = get_user_model()
    selected_user = get_object_or_404(User, username=username)
    
    if action == 'followers':
        # get followers
        follow_data = [f.follower for f in selected_user.followers.all()]
    elif action == 'following':
        # get following
        follow_data = [f.following for f in selected_user.following.all()]
    else:
        follow_data = []
    
    context = {
        'follow_data': follow_data,
        'username': username,
        'action':action
    }
    return render(request, 'core/show_follow.html', context=context)


def list_movies(request):
    watchlist = []
    liked_movies = []
    watched_movies = []
    if request.user.is_authenticated:
        user = request.user
        watchlist = WatchList.objects.filter(user=user).values_list('movie_id', flat=True)
        liked_movies = Like.objects.filter(user=user).values_list('movie_id', flat=True)
        watched_movies = Watched.objects.filter(user=user).values_list('movie_id', flat=True)
    
    data = Movie.objects.filter(poster_url__isnull=False).exclude(poster_url='').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')).all().order_by('-release_date')
    paginator = Paginator(data,104)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj':page_obj,
        'movies':page_obj.object_list,
        'watchlist':watchlist,
        'liked_movies': liked_movies,
        'watched_movies': watched_movies,
    }
    return render(request,'core/show_all_movies.html',context=context)



def list_one_movie(request, movie_id: int):
    movie = Movie.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    ).get(id=movie_id)
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')
    # paginate reviews
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    watchlist = []
    liked = False
    watched = False
    if request.user.is_authenticated:
        watchlist = WatchList.objects.filter(user=request.user).values_list('movie_id', flat=True)
        liked = Like.objects.filter(user=request.user, movie=movie).exists()
        watched = Watched.objects.filter(user=request.user, movie=movie).exists()
    
    context = {
        'movie': movie,
        'page_obj': page_obj,
        'reviews': page_obj.object_list,
        'watchlist': watchlist,
        'liked': liked,
        'watched': watched,
    }
    return render(request, 'core/movie.html', context=context)

@login_required
def add_to_watchlist(request, movie_id: int):
    curr_user = request.user
    movie = get_object_or_404(Movie, id=movie_id)
    
    if not WatchList.objects.filter(user=curr_user, movie=movie).exists():
        WatchList.objects.create(user=curr_user, movie=movie)
    
    return redirect(request.META.get('HTTP_REFERER', 'get_all_movies'))

@login_required
def remove_from_watchlist(request, movie_id: int):
    curr_user = request.user
    movie = get_object_or_404(Movie, id=movie_id)
    WatchList.objects.filter(user=curr_user, movie_id=movie.id).delete()
    return redirect(request.META.get('HTTP_REFERER', 'get_all_movies'))



@login_required
def feed(request):
    curr_user = request.user
    
    # get all users that current user is following
    following_users = Follower.objects.filter(
        follower=curr_user
    ).values_list('following', flat=True)
    
    # get reviews from people user is following in random order
    reviews = Review.objects.filter(
        user__in=following_users
    ).order_by('?')
    
    likes = Like.objects.filter(user__in=following_users).order_by('?')

    paginator = Paginator(reviews, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'reviews': page_obj.object_list
    }
    return render(request, 'core/feed.html', context=context)



@login_required
def write_review(request, movie_id: int):
    curr_user = request.user
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = curr_user
            review.movie = movie
            review.save()
            return redirect(reverse('list_one_movie', args=[movie.id]))
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'movie': movie
    }
    return render(request, 'core/write_review.html', context=context)

@login_required
def delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    
    # check if current user wrote the review
    if review.user != request.user:
        return redirect(request.META.get('HTTP_REFERER', 'list_movies'))
    
    review.delete()
    
    return redirect(request.META.get('HTTP_REFERER', 'list_movies'))


@login_required
def edit_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return redirect(request.META.get('HTTP_REFERER', 'list_movies'))
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect(reverse('list_one_movie', args=[review.movie.id]))
    else:
        form = ReviewForm(instance=review)

    context = {'form': form}
    return render(request, 'core/edit_review.html', context=context)


@login_required
def search_movies(request):
    query = request.GET.get('q', '')
    watchlist = []
    liked_movies = []
    if request.user.is_authenticated:
        watchlist = WatchList.objects.filter(user=request.user).values_list('movie_id', flat=True)
        liked_movies = Like.objects.filter(user=request.user).values_list('movie_id', flat=True)
    if query:
        movies_list = Movie.objects.filter(movie_name__icontains=query).annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).all()
    else:
        movies_list = []
    
    paginator = Paginator(movies_list, 100)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'movies': page_obj.object_list,
        'watchlist': watchlist,
        'liked_movies': liked_movies,
        'search_query': query
    }
    return render(request, 'core/search_results.html', context=context)


@login_required
def like_movie(request,movie_id:int):
    curr_user = request.user
    movie = get_object_or_404(Movie,id=movie_id)
    if not Like.objects.filter(user=curr_user,movie=movie).exists():
        Like.objects.create(user=curr_user,movie=movie)

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def unlike_movie(request,movie_id:int):
    curr_user = request.user
    movie = get_object_or_404(Movie,id=movie_id)
    if Like.objects.filter(user=curr_user,movie=movie).exists():
        Like.objects.filter(user=curr_user,movie=movie).delete()
    return redirect(request.META.get('HTTP_REFERER'))



@login_required
def watched_movie(request,movie_id:int):
    curr_user = request.user
    movie = get_object_or_404(Movie,id=movie_id)
    if not Watched.objects.filter(user=curr_user,movie=movie).exists():
        Watched.objects.create(user=curr_user,movie=movie)
    
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unwatch_movie(request,movie_id:int):
    curr_user = request.user
    movie = get_object_or_404(Movie,id=movie_id)
    if Watched.objects.filter(user=curr_user,movie=movie).exists():
        Watched.objects.filter(user=curr_user,movie=movie).delete()
    return redirect(request.META.get('HTTP_REFERER'))