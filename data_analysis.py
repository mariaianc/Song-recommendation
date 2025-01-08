import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

def load_and_inspect_data(file_path):
    """Load the dataset and display basic information."""
    data = pd.read_csv(file_path)
    print(data.head())
    print(data.info())
    print(data.describe())
    return data

def plot_popularity_distribution(data):
    """Plot the distribution of track popularity."""
    plt.figure(figsize=(8, 6))
    sns.histplot(data['popularity'], kde=True, bins=30, color='blue')
    plt.title('Track Popularity Distribution')
    plt.xlabel('Popularity')
    plt.ylabel('Count')
    plt.xticks(range(0, 101, 10))
    plt.show()

def plot_popularity_by_genre(data):
    """Plot track popularity by genre."""
    filtered_data = data[data['primary_genre'] != 'UNKNOWN']
    plt.figure(figsize=(13, 9))
    sns.boxplot(x='primary_genre', y='popularity', data=filtered_data, hue='primary_genre', palette='Set2')
    plt.title('Track Popularity by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Popularity')
    plt.xticks(rotation=-100)
    plt.show()

def plot_genre_counts(data):
    """Plot the number of songs per genre."""
    genre_counts = data['primary_genre'].value_counts()
    plt.figure(figsize=(12, 8))
    genre_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of Songs per Genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of Songs')
    plt.xticks(rotation=-90)
    plt.show()

def analyze_top_artists(data, weight_factor=10):
    """
    Compute and visualize the top artists based on normalized popularity scores.
    """
    artist_scores = defaultdict(float)
    artist_song_counts = defaultdict(int)

    # Step 1: Split artists and compute popularity contributions
    for _, row in data.iterrows():
        artists = [artist.strip() for artist in row['artist_name'].split(',')]
        popularity = row['popularity']
        for artist in artists:
            artist_scores[artist] += popularity
            artist_song_counts[artist] += 1

    # Step 2: Add weighted number of songs
    for artist in artist_scores:
        artist_scores[artist] += weight_factor * artist_song_counts[artist]

    # Step 3: Normalize the scores
    max_score = max(artist_scores.values())
    normalized_scores = {artist: (score / max_score) * 100 for artist, score in artist_scores.items()}

    # Step 4: Sort artists and prepare data for visualization
    top_10_artists = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    top_10_names, top_10_scores = zip(*top_10_artists)
    top_10_song_counts = [artist_song_counts[artist] for artist in top_10_names]

    # Step 5: Plot the results
    plt.figure(figsize=(14, 8))
    # ax = sns.barplot(x=list(top_10_names), y=list(top_10_scores), palette='viridis')
    ax = sns.barplot(x=list(top_10_names), y=list(top_10_scores), hue=list(top_10_names), dodge=False, palette='viridis', legend=False)
    plt.title('Top 10 Artists by Normalized Popularity')
    plt.xlabel('Artist')
    plt.ylabel('Normalized Popularity (0–100)')
    plt.xticks(rotation=45)
    for i, (score, count) in enumerate(zip(top_10_scores, top_10_song_counts)):
        ax.text(i, score + 1, f'{round(score, 2)}\n({count} songs)', ha='center', va='bottom', fontsize=10)
    plt.show()
