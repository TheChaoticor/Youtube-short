
import streamlit as st
import requests
import os

# Flask backend URL
BACKEND_URL = "http://127.0.0.1:5000/process"

st.title("YouTube Shorts Generator")
st.write("Enter a YouTube video URL to generate engaging shorts.")

# Input for YouTube URL
youtube_url = st.text_input("YouTube Video URL")

if st.button("Generate Shorts"):
    if youtube_url:
        with st.spinner("Processing video..."):
            try:
                # Send request to backend
                response = requests.post(BACKEND_URL, json={"youtube_url": youtube_url})
                if response.status_code == 200:
                    # Save the file
                    with open("short.mp4", "wb") as f:
                        f.write(response.content)

                    # Display the video
                    st.video("short.mp4")

                    # Download button
                    st.download_button(
                        label="Download Shorts",
                        data=open("short.mp4", "rb").read(),
                        file_name="short.mp4",
                        mime="video/mp4",
                    )
                else:
                    st.error(f"Error: {response.json().get('error')}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a valid YouTube URL.")
