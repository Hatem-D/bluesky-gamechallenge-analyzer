import requests
from pprint import pprint
from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import pytz
import time


class BskySearch:
    def __init__(self):
        self.base_url = "https://api.bsky.app"
        self.search_endpoint = "/xrpc/app.bsky.feed.searchPosts"
        self.delay = 15  # seconds between calls

    def search_posts(self, q, since, until, limit=5):
        params = {
            "q": f"{q}",
            "since": since,
            "until": until,
            "limit": limit
        }

        print(f"\nWaiting {self.delay}s before API call...")
        time.sleep(self.delay)

        search_response = requests.get(
            f"{self.base_url}{self.search_endpoint}",
            params=params
        )

        if search_response.status_code == 200:
            try:
                return search_response.json()
            except Exception as e:
                print("\nJSON parsing error:", str(e))
        else:
            raise Exception(
                f"Search failed: {search_response.status_code}\n{search_response.text}")

    @staticmethod
    def print_posts(posts):

        for i, post in enumerate(posts, 1):
            print(f"\n--- Post {i} ---")
            print("typeOf post : ", type(post))
            print("typeOf post['author'] : ", type(post['author']))
            print("typeOf post['record'] : ", type(post['record']))
            print(f"Author: {post['author']['handle']}")
            print(f"Text: {post['record']['text']}")
            print(f"Posted at: {post['indexed_at']}")
            print(f"Likes: {post['like_count']}")

    @staticmethod
    def get_posts_with_hashtag(client, hashtag, since='yesterday', until='today'):
        cursor = None
        posts = []

        since_iso = BskySearch.convert_date_string(since)
        until_iso = BskySearch.convert_date_string(until)

        while True:
            fetched = client.app.bsky.feed.search_posts(
                params={
                    "q": f"#{hashtag}",
                    "cursor": cursor,
                    "since": since_iso,
                    "until": until_iso
                }
            )
            posts = posts + fetched.posts

            if not fetched.cursor:
                break

            cursor = fetched.cursor

        return posts

    @staticmethod
    def convert_date_string(date_str):
        """Convert string date to ISO 8601 format"""
        if date_str == 'today':
            date = datetime.now(pytz.UTC)
        elif date_str == 'yesterday':
            date = datetime.now(pytz.UTC) - timedelta(days=1)
        else:
            try:
                date = parse(date_str)
                if date.tzinfo is None:
                    date = date.replace(tzinfo=pytz.UTC)
            except:
                raise ValueError(f"Invalid date format: {date_str}")

        return date.isoformat()
