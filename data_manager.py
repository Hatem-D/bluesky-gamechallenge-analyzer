import json
import csv
import pandas as pd
from datetime import datetime
import glob
import os
from dataclasses import asdict
from pprint import PrettyPrinter


class DataManager:
    def __init__(self, base_path="./data"):
        self.base_path = base_path
        self.pp = PrettyPrinter(indent=2)

    def bup_save_raw_json(self, data, filename=None):
        """Save selected fields from PostView objects"""
        if not filename:
            filename = f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        posts = data['posts'] if isinstance(data, dict) else data
        simplified_posts = []

        for post in posts:
            # Extract tags from facets array
            tags = []
            if post.record.facets:
                for facet in post.record.facets:
                    if facet.features[0].tag:  # Each facet has one tag feature
                        tags.append(facet.features[0].tag)

            simplified_post = {
                'handle': post.author.handle,
                'created_at': post.record.created_at,
                'text': post.record.text,
                'tags': tags
            }
            simplified_posts.append(simplified_post)
        with open(f"{self.base_path}/{filename}", 'w') as f:
            json.dump({'posts': simplified_posts}, f, indent=4)

    def save_raw_json(self, data, filename=None):
        """Save selected fields from PostView objects"""
        if not filename:
            filename = f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        posts = data['posts'] if isinstance(data, dict) else data
        simplified_posts = []

        for i, post in enumerate(posts):
            try:
                # Extract tags from facets array
                tags = []
                if post.record.facets:
                    for facet in post.record.facets:
                        for feature in facet.features:
                            if hasattr(feature, 'tag'):
                                tags.append(feature.tag)

                # Extract image alts
                image_alts = []
                if hasattr(post, 'embed') and hasattr(post.embed, 'media'):
                    if hasattr(post.embed.media, 'images'):
                        image_alts = [
                            img.alt for img in post.embed.media.images]

                simplified_post = {
                    'uri': post.uri,
                    'handle': post.author.handle,
                    'created_at': post.record.created_at,
                    'text': post.record.text,
                    'tags': tags,
                    'like_count': getattr(post, 'like_count', 0),
                    'image_alts': image_alts
                }
                simplified_posts.append(simplified_post)

            except Exception as e:
                print(f"\nError processing post {i}: {str(e)}")
                continue

        with open(f"{self.base_path}/{filename}", 'w') as f:
            json.dump({'posts': simplified_posts}, f, indent=4)

    def save_as_csv(self, posts, filename=None):
        """Extract relevant fields to CSV"""
        if not filename:
            filename = f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        fields = ['id', 'author', 'text', 'posted_at', 'likes', 'hashtags']
        rows = []

        for post in posts:
            rows.append({
                'id': post['uri'],
                'author': post['author']['handle'],
                'text': post['record']['text'],
                'posted_at': post['indexed_at'],
                'likes': post.get('like_count', 0),
                'hashtags': self._extract_hashtags(post['record']['text'])
            })

        with open(f"{self.base_path}/{filename}", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def load_to_pandas(self, pattern='posts_*.csv'):
        """
        Load multiple files into pandas DataFrame
        pattern: file pattern to match (e.g., 'posts_*.csv', 'posts_202501*.json')
        """
        files = glob.glob(f"{self.base_path}/{pattern}")

        if not files:
            raise FileNotFoundError(
                f"No files found matching pattern: {pattern}")

        dfs = []
        for file in files:
            if file.endswith('.json'):
                df = pd.read_json(file)
                if 'posts' in df.columns:  # Handle nested JSON
                    df = pd.json_normalize(df['posts'])
            elif file.endswith('.csv'):
                df = pd.read_csv(file)

            df['source_file'] = os.path.basename(file)  # Track source file
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)

    def _convert_to_dict(self, obj):
        """Convert object to JSON serializable dict"""
        try:
            return asdict(obj)
        except TypeError:
            if isinstance(obj, dict):
                return {k: self._convert_to_dict(v) for k, v in obj.items() if k != 'author'}
            elif isinstance(obj, (list, tuple)):
                return [self._convert_to_dict(item) for item in obj]
        return obj

    # Example usage:
    # dm = DataManager()
    # all_jan_posts = dm.load_to_pandas('posts_202501*.csv')
    # all_json_posts = dm.load_to_pandas('posts_*.json')

    @staticmethod
    def _extract_hashtags(text):
        """Extract hashtags from post text"""
        return ' '.join([word for word in text.split() if word.startswith('#')])

    def debug_print(self, obj):
        """Debug print for complex objects"""
        print("\nObject type:", type(obj))
        if isinstance(obj, dict):
            self.pp.pprint(obj)
        elif isinstance(obj, list):
            print(f"List length: {len(obj)}")
            if len(obj) > 0:
                print("First item type:", type(obj[0]))
                self.pp.pprint(obj[0])
        else:
            print("Dir of object:")
            self.pp.pprint(dir(obj))
