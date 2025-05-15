from game_analyzer import GameAnalyzer
from data_manager import DataManager


def show_df_info(df):
    # Debug DataFrame structure
    print("\nDataFrame Info:")
    print(df.info())

    print("\nDataFrame Shape:")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 2 rows with all columns:")
    print(df.head(2).to_string())

    print("\nSample of 'text' column:")
    print(df['text'].head())


# Initialize and test
analyzer = GameAnalyzer()
dm = DataManager()
df = dm.load_to_pandas('posts_gamechallenge_20241201.json')
# show_df_info(df)


print("Starting connection test...")
if analyzer.test_connection():
    print("Connection successful!")
    # Continue with analysis
    results = ()
    results = analyzer.extract_game_titles(df)
    print(results[['text', 'clean_text', 'game_title', 'like_count']].head())
    print("Saving results and generating CSVs...")
    analyzer.save_results(results, '2024_Dec')
else:
    print("Failed to connect to Ollama LLM")
