import requests
import streamlit as st

from youtube_transcript_api import YouTubeTranscriptApi

# Function to extract transcript from YouTube video
def extract_transcript(video_id):
    try:
        print("Extracting transcript...")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return None

# Function to send transcript to Amazon Bedrock API
def analyze_transcript(transcript):
    import boto3
    import json
    brt = boto3.client(service_name='bedrock-runtime')

    body = json.dumps({
        "prompt": "\n\nHuman: Summarize following in 10 bullet points\n" + transcript + "\n\nAssistant:",
        "max_tokens_to_sample": 1000,
        "temperature": 0.1,
        "top_p": 0.9,
    })

    #print(body)
    
    #modelId = 'anthropic.claude-v2:1'
    modelId = 'anthropic.claude-instant-v1'
    accept = 'application/json'
    contentType = 'application/json'

    print("Summarizing transcript...")
    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())

    # text
    return response_body.get('completion')


def main():
    st.title("YouTube Video Summarizer")

    # Accept YouTube video ID as input
    video_id = st.text_input("Enter YouTube Video ID:")

    if st.button("Summarize!"):
        transcript = extract_transcript(video_id)
        #st.subheader("Video Title:")
        #st.write(transcript)
        formatted_transcript = " ".join([f"{entry['text']}" for entry in transcript])
        if video_id:
            summary = analyze_transcript(formatted_transcript)
            if "An error occurred" in summary:
                st.error(transcript)
            else:
                st.subheader("Summary in 10 bullet points:")
                st.text_area(" ", summary, height=800)
        else:
            st.warning("Please enter a YouTube Video ID.")

if __name__ == "__main__":
    main()