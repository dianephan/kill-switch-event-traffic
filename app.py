import os
import random
from flask import Flask, render_template
import ldclient
from ldclient.config import Config
from ldclient.context import Context
import requests

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")

# Initialize the LaunchDarkly client
ldclient.set_config(Config(sdk_key))

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

@app.route('/')
def index():
    # Create a user context
    user_context = Context.builder('example-user-key').kind('user').name('Sandy').build()

    # Get feature flag values
    show_avatar = ldclient.get().variation('show-avatar-and-reccs', user_context, False)
    
    if show_avatar:
        avatar_url = get_random_avatar()
        # Recommendations are only shown if we get a real avatar
        show_recommendations = True
    else:
        avatar_url = "https://media.tenor.com/ocYNcAWYyHMAAAAM/99-cat.gif"
        show_recommendations = False

    # Generate social media feed
    names = ["Leslie Knope", "Ron Swanson", "April Ludgate", "Andy Dwyer", "Tom Haverford", "Ann Perkins", "Ben Wyatt", "Chris Traeger", "Donna Meagle", "Jerry Gergich"]
    feed_posts = []

    # Hardcoded quotes for each character
    character_quotes = {
        "Leslie Knope": [
            "We have to remember what's important in life: friends, waffles, and work. Or waffles, friends, work. But work has to come third.",
            "I am big enough to admit that I am often inspired by myself.",
            "There's nothing we can't do if we work hard, never sleep, and shirk all other responsibilities in our lives."
        ],
        "Ron Swanson": [
            "I'm not interested in caring about people.",
            "There's only one thing I hate more than lying: skim milk. Which is water that's lying about being milk.",
            "Give a man a fish and feed him for a day. Don't teach a man to fish… and you feed yourself. He's a grown man. And fishing's not that hard."
        ],
        "April Ludgate": [
            "I guess I kind of hate most things, but I never really seem to hate you.",
            "Time is money; money is power; power is pizza; pizza is knowledge. Let's go.",
            "I want to be a veterinarian because I love children."
        ],
        "Andy Dwyer": [
            "I have no idea what I'm doing, but I know I'm doing it really, really well.",
            "Anything is a toy if you play with it.",
            "I tried to make ramen in the coffee pot and I broke everything."
        ],
        "Tom Haverford": [
            "Treat yo' self!",
            "Sometimes you gotta work a little, so you can ball a lot.",
            "I call eggs 'pre-birds' or 'future birds.' Either way, they're delicious."
        ],
        "Ann Perkins": [
            "Everybody loves a gross medical story.",
            "I am not a boring person. I am fun. I am.",
            "Jogging is the worst! I know it keeps you healthy, but god, at what cost?"
        ],
        "Ben Wyatt": [
            "I calzone betrayed me?",
            "I was 18 when I became mayor of my hometown. The only thing I was prepared to run was a lemonade stand.",
            "I love accounting. That's why I became an accountant."
        ],
        "Chris Traeger": [
            "Literally, I am the happiest person in the world.",
            "I have run 10 miles a day, every day, for 18 years.",
            "If I keep my body moving, and my mind occupied at all times, I will avoid falling into a bottomless pit of despair. "
        ],
        "Donna Meagle": [
            "Treat yo' self.",
            "You best watch yourself. You are on Donna's radar.",
            "I am not interested in caring about people."
        ],
        "Jerry Gergich": [
            "I guess I just have one of those faces.",
            "I'm just happy to be included.",
            "I stepped in a pie."
        ]
    }

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

    return render_template(
        'index.html',
        user=user_context.to_dict(),
        avatar_image=avatar_url,
        show_avatar=show_avatar,
        posts=feed_posts,
        show_recommendations=show_recommendations
    )

if __name__ == "__main__":
    if not sdk_key:
        print("*** Please set the LAUNCHDARKLY_SDK_KEY env first")
        exit()

    if not ldclient.get().is_initialized():
        print("*** SDK failed to initialize. Please check your internet connection and SDK credential for any typo.")
        exit()

    print("*** SDK successfully initialized")
    
    app.run(debug=True)

    