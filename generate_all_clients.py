from github_api_client import generate_github_api_client
from twitter_api_client import generate_twitter_api_client
from stripe_api_client import generate_stripe_api_client
from spotify_api_client import generate_spotify_api_client
from openweathermap_api_client import generate_openweathermap_api_client


def generate_all_clients():
    print("Generating GitHub API Client...")
    generate_github_api_client()

    print("Generating Twitter API Client...")
    generate_twitter_api_client()

    print("Generating Stripe API Client...")
    generate_stripe_api_client()

    print("Generating Spotify API Client...")
    generate_spotify_api_client()

    print("Generating OpenWeatherMap API Client...")
    generate_openweathermap_api_client()

    print("All API clients generated successfully!")


if __name__ == "__main__":
    generate_all_clients()
