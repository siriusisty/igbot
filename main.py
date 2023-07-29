import time
import json
import os
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()

# Function to check if the new exception is the same as the previous one
def is_same_exception(new_exception, last_exception):
    return new_exception == last_exception

# Function to generate a new proxy URL
def generate_proxy_url(proxy_ip):
    proxy_parts = proxy_ip.split('@')
    credentials = proxy_parts[0]
    proxy_host, proxy_port = proxy_parts[1].split(':')
    username, password = credentials.split(':')
    proxy_url = f"http://{username}:{password}@{proxy_host}:{proxy_port}"
    return proxy_url

# Get the environment variables
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
proxy_ip = os.getenv("PROXY_URL")

# Initialize a variable to store the last exception message
last_exception_message = None

# Initialize a set to store the usernames that have been followed
followed_users = set()

# Load search criteria from search.json
with open('search.json', 'r') as f:
    search_criteria = json.load(f)

# Get the list of hashtags from the search criteria
hashtags = search_criteria['query']

# Initialize a variable to keep track of the current hashtag index
current_hashtag_index = 0

# Main program loop
while True:
    try:
        # Use the current proxy for the client instance
        client = Client()
        client.set_proxy(proxy_ip)

        # Login to your Instagram account using environment variables
        client.login(username, password)

        # Get the current hashtag to be used
        current_hashtag = hashtags[current_hashtag_index]

        # Search for the current hashtag
        print(f"Searching for hashtag: {current_hashtag}...")
        hashtag = client.search_hashtags(query=current_hashtag)

        # If no hashtags are found, continue to the next iteration
        if not hashtag:
            print("No hashtag found. Trying the next one...")
            # Move on to the next hashtag and reset the index if all hashtags have been tried
            current_hashtag_index = (current_hashtag_index + 1) % len(hashtags)
            continue

        # Get posts from the found hashtag
        print(f"Getting posts for hashtag: {hashtag[0].name}")
        posts = client.hashtag_medias_recent(hashtag[0].name, amount=50)

        # Follow the users who made the posts
        print("Following...")
        for post in posts:
            user = client.user_info(post.user.pk)  # Use post.user.pk instead of post.user_id

            # Check if the user has already been followed
            if user.username in followed_users:
                print(f'Already followed user: {user.username}')
                continue

            # Follow the user and add their username to the set
            client.user_follow(user.pk)
            print(f'Followed user: {user.username}')
            followed_users.add(user.username)

            with open('followed.txt', 'a') as f:
                f.write(f'{user.username}\n')

            # Wait for 2 minutes after following to avoid hitting rate limits
            time.sleep(120)

        # Move on to the next hashtag and reset the index if all hashtags have been tried
        current_hashtag_index = (current_hashtag_index + 1) % len(hashtags)

    except ClientError as e:
        # Check if the new exception is the same as the previous one
        if not is_same_exception(str(e), last_exception_message):
            if 'Please wait a few minutes before you try again' in str(e):
                with open('exceptions.txt', 'a') as f:
                    f.write(f'ClientError: {str(e)}\n')
                # Update the last exception message variable
                last_exception_message = str(e)

                # Generate a new proxy URL and set it for the next client instance
                proxy_url = generate_proxy_url(proxy_ip)

                # Wait for a few minutes before retrying
                time.sleep(300)
            else:
                continue
    except Exception as e:
        # Check if the new exception is the same as the previous one
        if not is_same_exception(str(e), last_exception_message):
            with open('exceptions.txt', 'a') as f:
                f.write(f'Exception: {str(e)}\n')
            # Update the last exception message variable
            last_exception_message = str(e)
