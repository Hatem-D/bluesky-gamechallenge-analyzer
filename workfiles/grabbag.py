# Check available methods
# ask user if they want to print the available methods
if input("Do you want to print the available client and response methods? (y/n): ").lower() == 'y':
    print("\n\n\n\n*************Available client methods:*************\n")
    pprint([method for method in dir(client) if not method.startswith('_')])
    print("\n\n\n*************Available response methods:*************\n")
    pprint([method for method in dir(response) if not method.startswith('_')])
    # end of check


# example of feed fetch with full parameter control
class BskySearch:
    def __init__(self):
        self.base_url = "https://api.bsky.app"
        self.feed_endpoint = "/xrpc/app.bsky.feed.getTimeline"

    def get_feed_raw(self, access_token, params=None):
        """
        Get feed with full parameter control

        Parameters:
        - algorithm: str (optional) - e.g. 'reverse-chronological'
        - cursor: str (optional) - for pagination
        - limit: int (optional) - default 50, max 100
        - before: str (optional) - show items before timestamp
        """
        default_params = {
            "limit": 50,
        }

        if params:
            default_params.update(params)

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

        response = requests.get(
            f"{self.base_url}{self.feed_endpoint}",
            params=default_params,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            with open('raw_feed.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return data
        else:
            raise Exception(
                f"Feed fetch failed: {response.status_code}\n{response.text}")

    def get_feed_example(self, client):
        """Example usage with parameters"""
        custom_params = {
            "algorithm": "reverse-chronological",
            "limit": 100,
            "before": "2025-01-28T00:00:00Z"
        }
        return self.get_feed_raw(client.session.access_jwt, custom_params)
