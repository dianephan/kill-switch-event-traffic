import random
from character_data import names, character_quotes
import requests

def get_random_avatar():
    try:
        url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(url)
        response.raise_for_status()
        avatar_data = response.json()
        return avatar_data[0]['url']
    except requests.exceptions.RequestException as e:
        print(f"Failed to get avatar from thecatapi.com: {e}")
        return "https://media.tenor.com/ocYNcAWYyHMAAAAM/99-cat.gif"

def generate_feed(show_avatar):
    feed_posts = []
    for _ in range(5):
        post = {}
        try:
            # Get random name
            post['name'] = random.choice(names)

            # Get random quote for the character
            post['quote'] = f"\"{random.choice(character_quotes[post['name']])}\""

            # Get random avatar
            if show_avatar:
                post['avatar'] = get_random_avatar()
            else:
                post['avatar'] = "https://media.tenor.com/ocYNcAWYyHMAAAAM/99-cat.gif"
            
            feed_posts.append(post)

        except Exception as e:
            print(f"Could not generate post: {e}")
            continue
    return feed_posts 