import streamlit as st
from billboard_scraper import scrape_billboard_data
from spotify import get_token, process_songs, search_song
from data_analysis import (
    load_and_inspect_data,
    plot_popularity_distribution,
    plot_popularity_by_genre,
    plot_genre_counts,
    analyze_top_artists,
)
from clustering import (
    load_and_preprocess_data,
    apply_kmeans_clustering,
    interpret_clusters,
    recommend_songs_based_on_cluster,
)
import pandas as pd
import matplotlib.pyplot as plt

import io
import sys

def main():
    st.title("Music Explorer App 🎵")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    options = st.sidebar.radio(
        "Choose a section:",
        ["Home", "Scrape Billboard Data", "Spotify API", "Data Analysis", "Cluster Songs", "Search Song"],
    )

    if options == "Home":
        st.header("Welcome to the Music Explorer App")
        st.write("This app allows you to scrape music data, enrich it with Spotify API, analyze trends, and recommend songs.")


    elif options == "Scrape Billboard Data":
        st.header("Step 1: Scrape Billboard Hot 100 Data")
        if st.button("Scrape Data"):
            # Scrape data
            scrape_billboard_data()

            # Inform the user that the data has been scraped
            st.success("Billboard data scraped successfully and saved to 'billboard_top_100_cleaned.csv'.")

            # Load the CSV file to display it
            df_billboard = pd.read_csv('billboard_top_100_cleaned.csv')

            # Display the dataframe in Streamlit
            st.write("Top 100 Songs and Artists:")
            st.dataframe(df_billboard)


    elif options == "Spotify API":
        st.header("Step 2: Enrich Billboard Data with Spotify Details")
        input_csv = "billboard_top_100_cleaned.csv"
        output_csv = "billboard_with_genres.csv"

        if st.button("Add details to songs"):
            token = get_token()
            process_songs(input_csv, token, output_csv)
            st.success(f"Spotify data added successfully and saved to '{output_csv}'.")

            # Load the processed CSV to display it
            df_processed_songs = pd.read_csv(output_csv)

            # Display the dataframe in Streamlit
            st.write("Processed Songs with Spotify Details:")
            st.dataframe(df_processed_songs)


    elif options == "Data Analysis":
        st.header("Step 3: Analyze the Enriched Data")
        output_csv = "billboard_with_genres.csv"
        data = load_and_inspect_data(output_csv)

        st.subheader("Visualizations")
        if st.button("Show Popularity Distribution"):
            plot_popularity_distribution(data)
            st.pyplot(plt.gcf())  # Display the plot in Streamlit

        if st.button("Show Popularity by Genre"):
            plot_popularity_by_genre(data)
            st.pyplot(plt.gcf())

        if st.button("Show Genre Counts"):
            plot_genre_counts(data)
            st.pyplot(plt.gcf())

        if st.button("Analyze Top Artists"):
            analyze_top_artists(data)
            st.pyplot(plt.gcf())

    # elif options == "Cluster Songs":
    #     st.header("Step 3: Cluster Songs")
    #     st.write("This section allows you to cluster songs and analyze the clusters.")
    #
    #     if st.button("Cluster Songs"):
    #         # Load and preprocess data
    #         st.write("Loading and preprocessing data...")
    #         preprocessed_data = load_and_preprocess_data("billboard_with_genres.csv")
    #
    #         # Apply K-Means clustering
    #         st.write("Applying K-Means clustering...")
    #         clustered_data = apply_kmeans_clustering(preprocessed_data)
    #         st.pyplot(plt.gcf())
    #
    #         # Display cluster interpretations
    #         st.write("Cluster Interpretations:")
    #         cluster_interpretation = interpret_clusters(clustered_data)
    #         st.write(cluster_interpretation)
    #
    #         interpret_clusters(clustered_data)
    #         # Capture the printed output of the interpret_clusters function
    #         captured_output = io.StringIO()
    #         sys.stdout = captured_output  # Redirect stdout to capture the prints
    #
    #         # Reset stdout
    #         sys.stdout = sys.__stdout__
    #
    #         # Now display the captured output using Streamlit
    #         st.text(captured_output.getvalue())  # Display the captured text in the Streamlit app
    #
    #
    #         # Save clustered data in session state
    #         st.session_state["clustered_data"] = clustered_data

    elif options == "Cluster Songs":
        st.header("Step 3: Cluster Songs")
        st.write("This section allows you to cluster songs and analyze the clusters.")

        if st.button("Cluster Songs"):
            # Load and preprocess data
            st.write("Loading and preprocessing data...")
            preprocessed_data = load_and_preprocess_data("billboard_with_genres.csv")

            # Apply K-Means clustering
            st.write("Applying K-Means clustering...")
            clustered_data = apply_kmeans_clustering(preprocessed_data)
            st.pyplot(plt.gcf())

            # Save clustered data in session state
            st.session_state["clustered_data"] = clustered_data

            # Capture the printed output of the interpret_clusters function
            captured_output = io.StringIO()
            sys.stdout = captured_output  # Redirect stdout to capture the prints

            # Display cluster interpretations (will capture printed output)
            st.write("Cluster Interpretations:")
            st.write(interpret_clusters(clustered_data))

            # Reset stdout
            sys.stdout = sys.__stdout__

            # Now display the captured output using Streamlit
            st.text(captured_output.getvalue())  # Display the captured text in the Streamlit app


    # elif options == "Search Song":
    #     st.header("Step 4: Search for a Song and Get Recommendations")
    #     st.write("Search for a song and get recommendations from the same cluster.")
    #
    #     if "clustered_data" not in st.session_state:
    #         st.warning("Please cluster songs first in the 'Cluster Songs' section.")
    #     else:
    #         # Input fields for song details
    #         song_name = st.text_input("Enter the title of a song:", placeholder="e.g., Blinding Lights")
    #         artist_name = st.text_input("Enter the artist of the song:", placeholder="e.g., The Weeknd")
    #
    #         # Get recommendations
    #         if st.button("Get Recommendations"):
    #             if not song_name or not artist_name:
    #                 st.error("Please provide both the song title and artist name.")
    #             else:
    #                 st.write("Searching for the song and generating recommendations...")
    #                 token = get_token()
    #                 clustered_data = st.session_state["clustered_data"]
    #
    #                 # Fetch and display recommendations
    #                 recommendations = recommend_songs_based_on_cluster(clustered_data, token, song_name, artist_name)
    #
    #                 if recommendations is None:
    #                     st.error("Sorry, no recommendations could be generated.")
    #                 else:
    #                     st.success("Recommendations generated! 🎶")
    #                     st.write("Here are some songs you might enjoy:")
    #
    #                     # Display recommendations as a clickable table
    #                     for index, row in recommendations.iterrows():
    #                         st.markdown(
    #                             f"**{row['track_name']}** by {row['artist_name']} "
    #                             f"([Listen on Spotify]({row['track_url']}))"
    #                         )

    elif options == "Search Song":
        st.header("Step 4: Search for a Song and Get Recommendations")
        st.write("Search for a song and get recommendations from the same cluster.")

        if "clustered_data" not in st.session_state:
            st.warning("Please cluster songs first in the 'Cluster Songs' section.")
        else:
            # Input fields for song details
            song_name = st.text_input("Enter the title of a song:", placeholder="e.g., Blinding Lights")
            artist_name = st.text_input("Enter the artist of the song:", placeholder="e.g., The Weeknd")

            # Get recommendations
            if st.button("Get Recommendations"):
                if not song_name or not artist_name:
                    st.error("Please provide both the song title and artist name.")
                else:
                    st.write("Searching for the song and generating recommendations...")

                    # Redirect stdout to capture the printed output
                    captured_output = io.StringIO()
                    sys.stdout = captured_output  # Redirect stdout to capture the prints

                    try:
                        # Call the recommend_songs_based_on_cluster function
                        token = get_token()
                        clustered_data = st.session_state["clustered_data"]

                        # Fetch and display recommendations
                        recommendations = recommend_songs_based_on_cluster(clustered_data, token, song_name, artist_name)

                        if recommendations is None:
                            st.error("Sorry, no recommendations could be generated.")
                        else:
                            st.success("Recommendations generated! 🎶")
                            st.write("Here are some songs you might enjoy:")

                            # Display recommendations as a clickable table
                            for index, row in recommendations.iterrows():
                                st.markdown(
                                    f"**{row['track_name']}** by {row['artist_name']} "
                                    f"([Listen on Spotify]({row['track_url']}))"
                                )

                    finally:
                        # Reset stdout back to the original stdout
                        sys.stdout = sys.__stdout__

                    # Display the captured output
                    st.text(captured_output.getvalue())  # Display the captured console output


if __name__ == "__main__":
    main()


# streamlit run main.py