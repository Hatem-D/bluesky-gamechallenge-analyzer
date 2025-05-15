from game_analyzer_text import GameAnalyzerText

analyzer = GameAnalyzerText()
results = analyzer.analyze_posts('data/posts_gamechallenge_20250101.json')
analyzer.print_analysis(results)
