import os
import django
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
load_dotenv()
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_project.settings')
django.setup()

from core.models import Movie, Person, MovieCast

# TMDB API Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # Replace with your actual API key
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

def get_movies_by_endpoint(endpoint, num_pages=500):
    """Fetch movies from different TMDB endpoints"""
    movies = []
    
    for page in range(1, num_pages + 1):
        url = f'{TMDB_BASE_URL}/{endpoint}'
        params = {
            'api_key': TMDB_API_KEY,
            'page': page,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if not data.get('results'):
                print(f"No more results for {endpoint} at page {page}")
                break
            
            movies.extend(data['results'])
            print(f"  Page {page}: {len(data['results'])} movies")
            
            # Rate limiting
            time.sleep(0.25)
        
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            time.sleep(1)
    
    return movies

def get_movie_details(movie_id):
    """Fetch detailed movie info including runtime and genres"""
    url = f'{TMDB_BASE_URL}/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        time.sleep(0.1)
        return response.json()
    except Exception as e:
        return {}

def get_movie_credits(movie_id):
    """Fetch cast, directors, and writers"""
    url = f'{TMDB_BASE_URL}/movie/{movie_id}/credits'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        time.sleep(0.1)
        return response.json()
    except Exception as e:
        return {}

def get_movie_crew(credits):
    """Extract top crew members (directors, writers, producers)"""
    crew = credits.get('crew', [])
    top_crew = []
    
    # Get directors
    directors = [c for c in crew if c['job'] == 'Director']
    top_crew.extend(directors[:3])
    
    # Get writers/screenwriters
    writers = [c for c in crew if c['department'] == 'Writing']
    top_crew.extend(writers[:3])
    
    # Get producers
    producers = [c for c in crew if c['job'] == 'Producer']
    top_crew.extend(producers[:2])
    
    return top_crew

def populate_movies(num_movies=10000):
    """Populate database with movies from TMDB"""
    
    endpoints = [
        'movie/popular',
        'movie/top_rated',
        'movie/upcoming',
        'movie/now_playing'
    ]
    
    all_movies = []
    movies_added = 0
    
    print(f"\n{'='*70}")
    print(f"TMDB Database Population - Fetching {num_movies} movies")
    print(f"{'='*70}\n")
    
    # Fetch movies from all endpoints
    movies_per_endpoint = int(num_movies / len(endpoints))
    for endpoint in endpoints:
        print(f"\n[Fetching] {endpoint} (~{movies_per_endpoint} movies)")
        movies = get_movies_by_endpoint(endpoint, num_pages=int(movies_per_endpoint / 20))
        all_movies.extend(movies)
        print(f"  Total fetched: {len(all_movies)}")
    
    # Remove duplicates by movie ID
    unique_movies = {}
    for movie in all_movies:
        if movie['id'] not in unique_movies:
            unique_movies[movie['id']] = movie
    
    print(f"\n{'='*70}")
    print(f"[Processing] {len(unique_movies)} unique movies")
    print(f"{'='*70}\n")
    
    # Process each movie
    for movie_id, movie_data in unique_movies.items():
        if movies_added >= num_movies:
            break
        
        try:
            # Skip movies without release date or title
            if not movie_data.get('title') or not movie_data.get('release_date'):
                continue
            
            # Check if movie already exists
            if Movie.objects.filter(movie_name=movie_data['title']).exists():
                continue
            
            # Parse release date
            try:
                release_date_obj = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
            except:
                continue
            
            # Get detailed info
            details = get_movie_details(movie_id)
            
            # Extract data
            genres = details.get('genres', [])
            genre_name = genres[0]['name'] if genres else 'Unknown'
            runtime = details.get('runtime', 120)
            runtime = runtime if runtime > 0 else 120
            
            poster_url = f"{IMAGE_BASE_URL}{movie_data['poster_path']}" if movie_data.get('poster_path') else ''
            
            # Create Movie
            movie = Movie.objects.create(
                movie_name=movie_data['title'],
                movie_description=movie_data.get('overview', 'No description available'),
                release_date=release_date_obj,
                genre=genre_name,
                length=runtime,
                poster_url=poster_url
            )
            
            movies_added += 1
            print(f"[{movies_added}/{num_movies}] ✓ {movie.movie_name} ({genre_name}) - {runtime}m")
            
            # Get credits
            credits = get_movie_credits(movie_id)
            
            # Add cast (top 10)
            cast_list = credits.get('cast', [])[:10]
            for cast_index, cast_member in enumerate(cast_list):
                try:
                    person, created = Person.objects.get_or_create(
                        person_name=cast_member['name']
                    )
                    
                    # Determine role type
                    if cast_index == 0:
                        role_type = 'Lead'
                    elif cast_index < 5:
                        role_type = 'Supporting'
                    else:
                        role_type = 'Actor'
                    
                    MovieCast.objects.create(
                        movie=movie,
                        person=person,
                        role_type=role_type
                    )
                except Exception as e:
                    pass
            
            # Add crew (directors, writers, producers)
            crew_list = get_movie_crew(credits)
            for crew_member in crew_list:
                try:
                    person, created = Person.objects.get_or_create(
                        person_name=crew_member['name']
                    )
                    
                    role_type = crew_member.get('job', 'Crew')
                    
                    MovieCast.objects.create(
                        movie=movie,
                        person=person,
                        role_type=role_type
                    )
                except Exception as e:
                    pass
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
            continue
    
    print(f"\n{'='*70}")
    print(f"✓ Successfully added {movies_added} movies to database!")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    try:
        populate_movies(num_movies=10000)
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
    except Exception as e:
        print(f"Fatal Error: {e}")