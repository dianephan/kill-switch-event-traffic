import os
import random
from flask import Flask, render_template
import ldclient
from ldclient.config import Config
from ldclient.context import Context
import requests
from threading import Event
from flask_socketio import SocketIO, emit
from character_data import names, character_quotes
from feed_generator import generate_feed, get_random_avatar

app = Flask(__name__)
socketio = SocketIO(app)

from dotenv import load_dotenv
load_dotenv()

sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
flag_key = "replace-key-here"

@app.route('/')
def index():
    # Get feature flag values
    show_avatar = ldclient.get().variation(flag_key, user_context, False)
    
    if show_avatar:
        avatar_url = get_random_avatar()
        # Recommendations are only shown if we get a real avatar
        show_recommendations = True
    else:
        avatar_url = "https://media.tenor.com/ocYNcAWYyHMAAAAM/99-cat.gif"
        show_recommendations = False

    # Generate social media feed
    feed_posts = generate_feed(show_avatar)

    return render_template(
        'index.html',
        user=user_context.to_dict(),
        avatar_image=avatar_url,
        show_avatar=show_avatar,
        posts=feed_posts,
        show_recommendations=show_recommendations
    )

def show_evaluation_result(key: str, value: bool):
    print()
    print(f"*** The {key} feature flag evaluates to {value}")

class FlagValueChangeListener:
    def flag_value_change_listener(self, flag_change):
        # Notify all connected clients about the flag change
        socketio.emit('flag_update', {
            'key': flag_change.key,
            'new_value': flag_change.new_value
        })
        show_evaluation_result(flag_change.key, flag_change.new_value)

if __name__ == "__main__":
    if not sdk_key:
        print("*** Please set the LAUNCHDARKLY_SDK_KEY env first")
        exit()

    # Initialize the LaunchDarkly client
    ldclient.set_config(Config(sdk_key))

    if not ldclient.get().is_initialized():
        print("*** SDK failed to initialize. Please check your internet connection and SDK credential for any typo.")
        exit()

    print("*** SDK successfully initialized")
    # Set up the evaluation context. This context should appear on your
    # LaunchDarkly contexts dashboard soon after you run the demo.
    user_context = \
        Context.builder('example-user-key').kind('user').name('Sandy').build()

    flag_value = ldclient.get().variation(flag_key, user_context, False)
    show_evaluation_result(flag_key, flag_value)

    if sdk_key is not None:
        change_listener = FlagValueChangeListener()
        listener = ldclient.get().flag_tracker \
            .add_flag_value_change_listener(flag_key, user_context, change_listener.flag_value_change_listener)

    socketio.run(app, debug=True)

    