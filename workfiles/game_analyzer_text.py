import pandas as pd
import re
import json
from collections import Counter


class GameAnalyzerText:
    def __init__(self):
        self.mask_phrases = [
            "Choose 20 games that greatly influenced you.",
            "One game per day, for 20 days.",
            "No explanations, no reviews, no particular order."
        ]
        self.rejected_words = [
            "the", "and", "day", "game", "games", "playing",
            "today", "tomorrow", "yesterday", "now", "later",
            "first", "second", "third", "next", "last",
            "here", "there", "this", "that", "with",
            "best", "worst", "ever", "never", "always", "retro",
            "retrogames"
        ]
        self.known_games = self._load_known_games()
        self.unmatched_uris = []  # Store unmatched URIs
        self.total_processed = 0
        self.matched_count = 0

    def _load_known_games(self):
        """Load known games from TextDump_GameOnly.txt"""
        try:
            with open('TextDump_GameOnly.txt', 'r', encoding='utf-8') as f:
                return set(game.strip().lower() for game in f.readlines())
        except FileNotFoundError:
            return set()

    def clean_text(self, text):
        """Clean text while preserving : and ,"""
        # Remove mask phrases
        for phrase in self.mask_phrases:
            text = text.replace(phrase, '')

        # Keep only alphanumeric, :, and ,
        text = re.sub(r'[^\w\s:,]', '', text)
        return text.lower().strip()

    def extract_game_titles(self, text, uri=None):
        """Extract potential game titles and track unmatched posts"""
        cleaned_text = self.clean_text(text)

        # Split by common separators
        potential_titles = re.split(r'[,\n]', cleaned_text)
        potential_titles = [title.strip()
                            for title in potential_titles if title.strip()]

        # Match against known games and filter out rejected words
        matched_titles = []
        for title in potential_titles:
            title_lower = title.lower()
            # Check if it's a single word and not in known games
            if len(title_lower.split()) == 1 and title_lower not in self.known_games:
                continue
            # Check other rejection criteria
            if title_lower not in self.rejected_words and title_lower in self.known_games:
                matched_titles.append(title)

        # Log unmatched post if no valid matches found
        if uri:
            self.total_processed += 1
            if not matched_titles:
                self.unmatched_uris.append(uri)
            else:
                self.matched_count += 1

        return matched_titles

    def analyze_posts(self, json_file):
        """Analyze posts and count game occurrences"""
        with open(json_file, 'r') as f:
            data = json.load(f)

        game_mentions = []
        for post in data['posts']:
            games = self.extract_game_titles(post['text'], post['uri'])
            game_mentions.extend(games)

        print(f"\nTotal posts processed: {self.total_processed}")
        print(f"Posts with matches: {self.matched_count}")
        print(f"Posts without matches: {len(self.unmatched_uris)}")

        # Save unmatched URIs after processing all posts if unmatched URIs exist
        if self.unmatched_uris:
            self.save_unmatched_uris()
            print(f"Saved {len(self.unmatched_uris)} unmatched URIs to file")

        # Count occurrences
        game_counts = Counter(game_mentions)
        return dict(game_counts.most_common())

    def save_unmatched_uris(self, filename='unmatched_posts.txt'):
        """Save unmatched URIs to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for uri in self.unmatched_uris:
                f.write(f"{uri}\n")

    def print_analysis(self, game_counts):
        """Print analysis results"""
        print("\nGame Mentions Analysis:")
        print("----------------------")
        for game, count in game_counts.items():
            print(f"{game}: {count} mentions")
