import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_billboard_data():
    # URL for Billboard Top 100
    url = "https://www.billboard.com/charts/hot-100"

    # Send HTTP request
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all 'li' elements that contain both the song title (h3) and artist (span)
        song_elements = soup.select('li')  # More specific selection

        songs = []
        artists = []

        # Iterate over each 'li' element to find the song title and artist
        for li in song_elements:
            song = li.find('h3', class_='c-title')  # Get song title (h3 tag)
            artist = li.find('span', class_='c-label')  # Get artist name (span tag)

            # Only add to lists if both song and artist are found
            if song and artist:
                # Strip any extra whitespace or non-printing characters
                song_title = song.get_text(strip=True)
                artist_name = artist.get_text(strip=True)

                # Filter out non-song and non-artist elements like "NEW", "RE-ENTRY"
                if artist_name != 'NEW' and artist_name != 'RE-ENTRY' and (artist_name.isalpha() or ' ' in artist_name):
                    # Ensure both song and artist are not duplicates
                    pair = (song_title, artist_name)  # Create a tuple of the song-artist pair
                    if pair not in zip(songs, artists):  # Check both song and artist together
                        songs.append(song_title)
                        artists.append(artist_name)

        # Save the cleaned data to a CSV
        df_billboard = pd.DataFrame({'Song': songs, 'Artist': artists})

        # # Add a rank column and assign popularity categories
        # df_billboard['Rank'] = range(1, len(df_billboard) + 1)  # Assign ranks from 1 to 100
        #
        # # Categorize based on rank
        # def assign_popularity(rank):
        #     if rank <= 10:
        #         return "Top 10"
        #     elif rank <= 50:
        #         return "Top 50"
        #     else:
        #         return "Top 100"
        #
        # df_billboard['Popularity'] = df_billboard['Rank'].apply(assign_popularity)

        # Save the updated dataframe to a new CSV
        df_billboard.to_csv('billboard_top_100_cleaned.csv', index=False)

        print(f"Extracted Songs: {songs[:32]}")
        print(f"Extracted Artists: {artists[:32]}")
    else:
        print(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
