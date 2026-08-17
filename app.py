import streamlit as st

st.title("🎵 Playing Audio from GitHub")

# Direct raw link to the .m4a file on GitHub
# Replace USERNAME and REPO_NAME with your GitHub details
github_audio_url = "https://raw.githubusercontent.com/himal2005/beehybe/main/Video%20Project%203.m4a"

# Display the audio player
st.audio(github_audio_url, format="audio/mp4")