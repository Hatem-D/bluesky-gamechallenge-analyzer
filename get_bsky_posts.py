from atproto import Client
from pprint import pprint
from dataclasses import asdict
from bsky_search import BskySearch
from bsky_feed import BskyFeed
from data_manager import DataManager
import json
from datetime import datetime, timedelta

msg = "Trying to connect to blue sky social"
print(msg)
# app-attak-afu.bsky.social
# M$4d3znSZAm:


try:
    client = Client()
    response = client.login('app-attak-afu.bsky.social', 'M$4d3znSZAm:')

    # feed = BskyFeed().get_user_timeline(client)

    # if feed:
    #     print("\n\nFeed fetched\n")
    #     print(f"number of posts in feed : {len(feed)}")

    # Search for posts
    for day in range(1, 32):
        current_date = datetime(2024, 5, day)
        next_date = current_date + timedelta(days=1)

        search_result = BskySearch().get_posts_with_hashtag(
            client,
            "gamechallenge",
            since=current_date.strftime('%Y-%m-%d'),
            until=next_date.strftime('%Y-%m-%d')
        )

        if search_result:
            print("number of #gamechallenge posts: ", len(search_result))
            print(
                f"saving to file : posts_gamechallenge_{current_date.strftime('%Y%m%d')}.json")
            dm = DataManager()
            dm.save_raw_json(
                {"posts": search_result},
                f"posts_gamechallenge_{current_date.strftime('%Y%m%d')}.json"
            )

except Exception as e:
    print(f"Error: {str(e)}")
