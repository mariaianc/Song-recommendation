import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from spotify import search_song

def load_and_preprocess_data(file_path):
    """
    Load and preprocess data for clustering.
    """
    # Load the data
    data = pd.read_csv(file_path)

    # Display initial information about the dataset
    print("Data Head:")
    print(data.head())
    print("\nData Info:")
    print(data.info())
    print("\nData Description:")
    print(data.describe())

    # Check for missing values
    if data.isnull().sum().sum() > 0:
        print("Missing values detected.")
        print(data.isnull().sum())
    else:
        print("No missing values detected.")

    # Drop rows where the primary genre is UNKNOWN
    data = data[data['primary_genre'] != 'UNKNOWN']

    # Normalize popularity (scale from 0 to 1)
    data['popularity_normalized'] = data['popularity'] / 100

    # Convert duration from milliseconds to minutes
    data['duration_min'] = data['duration_ms'] / 60000

    # Normalize duration (scale from 0 to 1)
    min_duration = data['duration_min'].min()
    max_duration = data['duration_min'].max()
    data['duration_normalized'] = (data['duration_min'] - min_duration) / (max_duration - min_duration)

    # One-hot encode the 'primary_genre' column
    data_encoded = pd.get_dummies(data['primary_genre'])

    # Merge the encoded columns back into the original DataFrame
    data = pd.concat([data, data_encoded], axis=1)

    # Drop the original 'primary_genre' column (as it's now encoded)
    data = data.drop(columns=['primary_genre'])

    # Save the preprocessed data to a new CSV file
    data.to_csv('preprocessed_data.csv', index=False)
    print("\nData after preprocessing saved to 'preprocessed_data.csv'")

    return data

def apply_kmeans_clustering(data):
    """
    Apply K-Means clustering to the preprocessed data.
    """
    # We drop non-numeric columns (track_name, artist_name, album_name, track_url) for clustering
    X = data.drop(['track_name', 'artist_name', 'album_name', 'track_url'], axis=1)

    # Step 2: Find the optimal number of clusters using the Elbow Method
    inertia = []  # Sum of squared distances for each K
    K_range = range(1, 11)  # Try values of K from 1 to 10

    for K in K_range:
        kmeans = KMeans(n_clusters=K, random_state=42)
        kmeans.fit(X)
        inertia.append(kmeans.inertia_)

    # Plot the Elbow Method graph
    plt.figure(figsize=(8, 6))
    plt.plot(K_range, inertia, marker='o')
    plt.title('Elbow Method to Find Optimal K')
    plt.xlabel('Number of Clusters (K)')
    plt.ylabel('Inertia (Sum of Squared Distances)')
    plt.show()

    # Based on the Elbow Method, set the optimal K value
    optimal_k = 4  # Choose the value of K that seems optimal based on the elbow plot

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    data['cluster'] = kmeans.fit_predict(X)

    # Step 3: Visualize the clusters using PCA for 2D plotting
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(X)

    # Add the PCA components to the dataframe for plotting
    data['pca_1'] = pca_components[:, 0]
    data['pca_2'] = pca_components[:, 1]

    # Plot the clusters
    plt.figure(figsize=(8, 6))
    plt.scatter(data['pca_1'], data['pca_2'], c=data['cluster'], cmap='viridis', marker='o')
    plt.title('Song Clusters after K-Means Clustering')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.colorbar(label='Cluster')
    plt.show()

    # Save the clustered data to a new CSV file
    data.to_csv('clustered_data.csv', index=False)
    print("\nData with clusters saved to 'clustered_data.csv'")

    return data

def interpret_clusters(data):
    """
    Interpret and summarize the clusters.
    """
    # Group by cluster and calculate the average of the numeric columns (popularity and duration)
    cluster_summary = data.groupby('cluster')[['popularity_normalized', 'duration_normalized']].mean()

    # Print out the cluster summary for popularity and duration
    print("Cluster Summary (Mean values of popularity and duration for each cluster):")
    print(cluster_summary)

    # Group by cluster and calculate the mean presence of each genre (after one-hot encoding)
    genre_columns = [col for col in data.columns if col not in ['track_name', 'artist_name', 'album_name', 'track_url', 'popularity', 'duration_ms', 'duration_min', 'popularity_normalized', 'duration_normalized', 'cluster', 'pca_1', 'pca_2']]
    genre_summary = data.groupby('cluster')[genre_columns].mean()

    # Print out the cluster summary for genres
    print("\nCluster Summary (Mean presence of each genre):")
    print(genre_summary)

    # Now, let's identify the predominant genres for each cluster
    print("\nPredominant genres per cluster:")

    # Iterate over each cluster
    for cluster in genre_summary.index:
        print(f"\nCluster {cluster}:")

        # Get the genres sorted by their mean presence value in the cluster
        sorted_genres = genre_summary.loc[cluster].sort_values(ascending=False)

        # Display the genres with the highest presence (you can decide a threshold)
        predominant_genres = sorted_genres[sorted_genres > 0.05]  # Assuming 5% presence as a threshold

        for genre, presence in predominant_genres.items():
            print(f"  - {genre}: {presence:.2f}")

    return data

def recommend_songs_based_on_cluster(data, token):
    """
    Recommend songs based on the cluster of a user-provided song.
    """
    # Ask user for the song details
    song_name = input("Enter the title of the song: ").strip()
    artist_name = input("Enter the artist of the song: ").strip()

    # Search for the song on Spotify
    song_info = search_song(token, song_name)

    if song_info["artist_name"] == "N/A":
        print("Sorry, the song was not found on Spotify.")
        return

    print(f"Song found: {song_info['track_name']} by {song_info['artist_name']}")

    # Preprocess the song data to fit the clustering model
    song_features = pd.DataFrame([song_info])
    song_features['popularity_normalized'] = song_features['popularity'] / 100
    song_features['duration_min'] = song_features['duration_ms'] / 60000
    min_duration = data['duration_min'].min()
    max_duration = data['duration_min'].max()
    song_features['duration_normalized'] = (song_features['duration_min'] - min_duration) / (max_duration - min_duration)

    # Prepare the one-hot encoding for genres
    genres = data.columns[data.columns.str.startswith('primary_genre_')]
    genre_data = {genre: 0 for genre in genres}
    if f"primary_genre_{song_info['primary_genre']}" in genre_data:
        genre_data[f"primary_genre_{song_info['primary_genre']}"] = 1

    # Add the genre data to the song features
    for genre, value in genre_data.items():
        song_features[genre] = value

    # Align columns with the clustered data
    features_for_clustering = data.drop(['track_name', 'artist_name', 'album_name', 'track_url', 'cluster', 'pca_1', 'pca_2'], axis=1).columns
    song_features = song_features.reindex(columns=features_for_clustering, fill_value=0)

    # Predict the cluster for the new song
    X = data.drop(['track_name', 'artist_name', 'album_name', 'track_url', 'cluster', 'pca_1', 'pca_2'], axis=1)
    kmeans = KMeans(n_clusters=data['cluster'].nunique(), random_state=42)
    kmeans.fit(X)

    new_song_cluster = kmeans.predict(song_features)[0]
    print(f"The song belongs to cluster {new_song_cluster}")

    # Recommend songs from the same cluster
    recommendations = data[data["cluster"] == new_song_cluster]
    recommendations = recommendations[["track_name", "artist_name", "album_name", "track_url"]]

    # Save the recommendations to a CSV file
    recommendations.to_csv("recommendations.csv", index=False)
    print("Recommendations have been saved to 'recommendations.csv'.")
