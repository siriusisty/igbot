import time
import json
from instagrapi import Client
from instagrapi.exceptions import ClientError

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

# Define proxy settings
proxy_ip = "brd-customer-hl_c97f3814-zone-isp_proxy1:1j6gj7hg9ikt@brd.superproxy.io:22225"
proxy_url = generate_proxy_url(proxy_ip)

# Initialize a variable to store the last exception message
last_exception_message = None

# Main program loop
while True:
    try:
        # Use the current proxy for the client instance
        client = Client()
        client.set_proxy(proxy_url)

        # Set your Instagram credentials
        username = 'meeii.lii'
        password = 'Aksavagearmy1$'

        # Login to your Instagram account
        client.login(username, password)

        # Load search criteria from search.json
        with open('search.json', 'r') as f:
            search_criteria = json.load(f)

        # Search for hashtags based on the specified criteria
        print("Searching...")
        hashtags = client.search_hashtags(query=search_criteria['query'])

        # If no hashtags are found, continue to the next iteration
        if not hashtags:
            print("No hashtags found. Trying again...")
            continue

        # Get posts from the found hashtags
        for hashtag in hashtags:
            print(f"Getting posts for hashtag: {hashtag.name}")
            posts = client.hashtag_medias_recent(hashtag.name, amount=50)

            # Follow the users who made the posts
            print("Following...")
            for post in posts:
                user = client.user_info(post.user.pk)  # Use post.user.pk instead of post.user_id
                client.user_follow(user.pk)
                print(f'Followed user: {user.username}')
                with open('followed.txt', 'a') as f:
                    f.write(f'{user.username}\n')

                # Wait for a short period of time to avoid hitting rate limits
                time.sleep(5)

                # Unfollow the previously followed users
                print("Unfollowing...")
                try:
                    client.user_unfollow(user.pk)
                    print(f'Unfollowed user: {user.username}')
                    with open('unfollowed.txt', 'a') as f:
                        f.write(f'{user.username}\n')
                except ClientError as e:
                    print(f'Error while unfollowing user: {user.username}, Error: {str(e)}')
                    if 'Please wait a few minutes before you try again' in str(e):
                        # Generate a new proxy URL and set it for the next client instance
                        proxy_url = generate_proxy_url(proxy_ip)
                        print('Changing proxy...')
                        with open('proxy_change_log.txt', 'a') as f:
                            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - Changed proxy IP\n')
                    with open('unfollow_errors.txt', 'a') as f:
                        f.write(f'{user.username} - {str(e)}\n')

        # Get new followers
        followers = client.user_followers(client.user_id)
        with open('newfollower.txt', 'a') as f:
            for user_id in followers.keys():
                f.write(f'{client.username_from_user_id(user_id)}\n')

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
