from billboard_scraper import scrape_billboard_data
from spotify import get_token, process_songs
from data_analysis import (
    load_and_inspect_data,
    plot_popularity_distribution,
    plot_popularity_by_genre,
    plot_genre_counts,
    analyze_top_artists,
)
from clustering import load_and_preprocess_data, apply_kmeans_clustering, interpret_clusters, recommend_songs_based_on_cluster

def main():
    # Step 1: Scrape Billboard data
    print("Step 1: Scraping Billboard Hot 100 data...")
    scrape_billboard_data()
    print("Billboard data scraped successfully and saved to 'billboard_top_100_cleaned.csv'.")

    # Step 2: Enrich Billboard data with Spotify API
    print("Step 2: Enriching Billboard data with Spotify details...")
    input_csv = "billboard_top_100_cleaned.csv"
    output_csv = "billboard_with_genres.csv"
    token = get_token()
    process_songs(input_csv, token, output_csv)
    print(f"Spotify data added successfully and saved to '{output_csv}'.")

    # Step 3: Analyze the enriched data
    print("Step 3: Analyzing the enriched data...")
    data = load_and_inspect_data(output_csv)
    plot_popularity_distribution(data)
    plot_popularity_by_genre(data)
    plot_genre_counts(data)
    analyze_top_artists(data)
    print("Data analysis completed and visualized.")

    # Step 4: Clustering songs based on features
    print("Step 4: Clustering songs...")
    processed_data = load_and_preprocess_data(output_csv)
    clustered_data = apply_kmeans_clustering(processed_data)
    interpret_clusters(clustered_data)
    print("Clustering completed and results interpreted.")

    # Step 5: Recommend songs based on user input
    print("Step 5: Recommending songs based on user input...")
    recommend_songs_based_on_cluster(clustered_data, token)

if __name__ == "__main__":
    main()


#Enter the title of the song: Welcome to the Black Parade
#Enter the artist of the song: MCR