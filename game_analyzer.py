import pandas as pd
import requests
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


class GameAnalyzer:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = "mistral"

    def clean_text(self, text):
        """Remove URLs and special chars"""
        return re.sub(r'http\S+|[@#]\w+|[^\w\s]', '', text.lower())

    def normalize_title(self, title):
        """Normalize game title for comparison"""
        if not title or title.lower() == 'none':
            return None
        return ''.join(sorted(char.lower() for char in title if char.isalnum()))

    def group_similar_titles(self, df):
        """Group similar game titles and count mentions and likes"""
        title_groups = {}

        # Create groups of similar titles
        for idx, row in df.iterrows():
            title = row['game_title']
            if title and title.lower() != 'none':
                norm_title = self.normalize_title(title)
                if norm_title in title_groups:
                    title_groups[norm_title]['mentions'] += 1
                    title_groups[norm_title]['total_likes'] += row['like_count']
                    title_groups[norm_title]['variants'].add(title)
                    title_groups[norm_title]['uris'].append(
                        row['uri'])  # Add URI to list
                else:
                    title_groups[norm_title] = {
                        'canonical': title,
                        'mentions': 1,
                        'total_likes': row['like_count'],
                        'variants': {title},
                        'uris': [row['uri']]  # Initialize URI list
                    }

        # Add mention counts and total likes to DataFrame
        df['mentions'] = df['game_title'].apply(
            lambda x: title_groups.get(
                self.normalize_title(x), {}).get('mentions', 0)
            if x and x.lower() != 'none' else 0
        )

        df['total_likes'] = df['game_title'].apply(
            lambda x: title_groups.get(
                self.normalize_title(x), {}).get('total_likes', 0)
            if x and x.lower() != 'none' else 0
        )

        # Add all URIs as concatenated string
        df['all_uris'] = df['game_title'].apply(
            lambda x: ' - '.join(title_groups.get(self.normalize_title(x),
                                 {}).get('uris', []))
            if x and x.lower() != 'none' else ''
        )

        return df, title_groups

    def query_local_llm(self, text, temperature=0.3):
        """Query local Ollama LLM for game title extraction with metadata"""
        analysis_prompt = (
            "Task: Extract video game information from this user post and metadata.\n"
            "Return format must be exactly:\n"
            "'game title;year;developer'\n"
            "Rules:\n"
            "- If no game found, return 'None;;'\n"
            "- If game found but year unknown, return 'game title;;developer'\n"
            "- If game found but developer unknown, return 'game title;year;'\n"
            "- If only game found, return 'game title;;'\n"
            "No other format accepted. No extra text or explanations.\n"
            f"Data sample: {text}"
        )

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": analysis_prompt,
                    "temperature": temperature,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            print(f"Query failed with status {response.status_code}")
            return "None;;"
        except Exception as e:
            print(f"Query error: {str(e)}")
            return "None;;"

    def extract_game_titles(self, df):
        """Process DataFrame and extract potential game titles"""
        df['clean_text'] = df['text'].apply(self.clean_text)

        games_data = []
        for idx, row in df.iterrows():
            try:
                text_with_metadata = (
                    f"Text: {row['clean_text']}\n"
                    f"Tags: {', '.join(row['tags'])}\n"
                    f"Image descriptions: {', '.join(row['image_alts']) if row['image_alts'] else 'No images'}"
                )
                result = self.query_local_llm(text_with_metadata)
                game_title, year, developer = result.split(';')
                games_data.append({
                    'game_title': game_title,
                    'release_year': year if year else None,
                    'developer': developer if developer else None
                })
                print(f"Processed {idx + 1}/{len(df)} posts")
            except Exception as e:
                print(f"Error processing post {idx}: {str(e)}")
                games_data.append(
                    {'game_title': 'None', 'release_year': None, 'developer': None})
                continue

        # Add new columns to DataFrame
        df['game_title'] = [d['game_title'] for d in games_data]
        df['release_year'] = [d['release_year'] for d in games_data]
        df['developer'] = [d['developer'] for d in games_data]

        # Group similar titles and add mention counts
        df, groups = self.group_similar_titles(df)
        return df

    def test_connection(self):
        """Test LLM connection with debug info"""
        print("Testing LLM connection...")
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": "Reply only with 'OK' nothing else",
                    "stream": False
                }
            )
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response text: {result.get('response', '')}")
                # Consider any successful response as valid
                return True
            return False
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def save_results(self, df, filename=None):
        """Save analysis results to CSV files"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"game_analysis_{timestamp}"

        # First convert primary URI to URL
        df['web_url'] = df['uri'].apply(self.convert_uri_to_url)

        # Then convert all URIs to URLs
        df['all_urls'] = df['all_uris'].apply(
            lambda uris: ' - '.join([self.convert_uri_to_url(uri)
                                    for uri in uris.split(' - ')])
            if uris else ''
        )

        # Define columns to save
        columns = [
            'game_title', 'release_year', 'developer',
            'total_likes', 'mentions', 'uri', 'web_url',
            'all_uris', 'all_urls'
        ]

        # Split based on 'none' presence in game_title string
        unmatched_games = df[df['game_title'].str.contains(
            'none', case=False, na=False)][columns]
        matched_games = df[~df['game_title'].str.contains(
            'none', case=False, na=False)][columns]

        # Save split results
        matched_games.to_csv(f"data/{filename}_matched.csv", index=False)
        unmatched_games.to_csv(f"data/{filename}_unmatched.csv", index=False)

        return f"Results saved to data/{filename}"

    def convert_uri_to_url(self, uri):
        """Convert Bluesky URI to web URL"""
        # Fallback value for invalid URIs
        FALLBACK_VALUE = "URL conversion failed"

        if not uri or not uri.startswith('at://'):
            return FALLBACK_VALUE

        try:
            # Remove 'at://' and split remaining path
            parts = uri.replace('at://', '').split('/')

            # Check if we have enough parts
            if len(parts) < 3:
                print(f"Invalid URI format: {uri}")
                return FALLBACK_VALUE

            # The DID is always the first part
            did = parts[0]
            # The post_id is always the last part
            post_id = parts[-1]

            # Construct web URL
            return f"https://bsky.app/profile/{did}/post/{post_id}"
        except Exception as e:
            print(f"Error converting URI: {uri}, Error: {str(e)}")
            return FALLBACK_VALUE
