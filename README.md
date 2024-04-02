# Spotify Downloader

## About
Spotify Downloader is a web application developed using Flask, a micro web framework in Python. It leverages various Python libraries such as Pytube, MoviePy, and Spotipy to provide functionality for downloading Spotify playlists as MP3 files.

The application utilizes the Spotify API for authentication and accessing user playlists. Upon selecting a playlist, Spotify Downloader searches for each song on YouTube, retrieves the corresponding video, and then converts it to MP3 format.

One of the key features of Spotify Downloader is its ability to handle the download and conversion processes asynchronously. This means that these tasks are performed concurrently in separate threads, allowing the application to remain responsive and not block the main thread.

Additionally, Spotify Downloader provides users with real-time progress updates on the conversion process. This progress bar dynamically reflects the percentage of videos that have been successfully converted to MP3 format, enabling users to track the status of their downloads.

Developed by Felipe Behling in 2024, Spotify Downloader aims to offer a convenient solution for Spotify users who wish to enjoy their favorite playlists offline.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/felipebehling/Spotify-Downloader.git

2. Navigate to the project directory:
    ```bash
    cd spotify-downloader

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt

## Usage

1. Ensure you have a Spotify account and a Spotify Developer application set up to obtain the required credentials.
2. Set up your environment variables for Spotify API credentials:
   ```bash 
    export SPOTIPY_CLIENT_ID='your_client_id'
    export SPOTIPY_CLIENT_SECRET='your_client_secret'
    export SPOTIPY_REDIRECT_URI='your_redirect_uri'

3. Run the Flask application:
   ```bash
   python main.py

4. Open your web browser and navigate to `http://localhost:5000`.

## Acknowledgements
  - Flask - Micro web framework for Python.
  - Pytube - Library for downloading YouTube videos.
  - MoviePy - Library for video editing.
  - Spotipy - Library for the Spotify Web API.
