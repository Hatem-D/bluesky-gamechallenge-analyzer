import requests
from pprint import pprint
from datetime import datetime
from atproto import AsyncFirehoseSubscribeReposClient
from atproto import FirehoseSubscribeReposClient, parse_subscribe_repos_message

client = FirehoseSubscribeReposClient()


def on_message_handler(message) -> None:
    sub_repos = parse_subscribe_repos_message(message)


client.start(on_message_handler)
