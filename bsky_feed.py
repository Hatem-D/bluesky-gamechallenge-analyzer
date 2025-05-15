import atproto


class BskyFeed:

    def __init__(self):
        self.base_url = "https://api.bsky.app"
        self.search_endpoint = "/xrpc/app.bsky.feed.searchPosts"

    def get_user_timeline(self, client, cursor='', limit=30):
        data = client.get_timeline(cursor=cursor, limit=limit)
        feed = data.feed
        next_page = data.cursor
        return feed, next_page
