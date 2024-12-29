from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import requests

VideoQuick = Flask(__name__)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

prompt = """You are a YouTube video summarizer. You will be taking the transcript text 
and summarizing the entire video and providing the important summary in points within 250 words.
The transcript text will be appended here: """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript, video_id
    except Exception as e:
        return str(e), None

def generate_content(transcript_text, prompt):
    response = model.generate_content(prompt + transcript_text)
    return response.text

@VideoQuick.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    error = None
    video_id = None
    thumbnail_url = None

    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        transcript, video_id = extract_transcript_details(youtube_url)
        if "Could not retrieve a transcript" in transcript:
            error = "Could not retrieve a transcript for the provided video URL."
        else:
            summary_text = generate_content(transcript, prompt)
            summary_points = summary_text.split('.')
            summary = [point.strip() for point in summary_points if point.strip()]
            # thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
    
    return render_template('YTsummarizer.html', summary=summary, error=error, video_id=video_id, thumbnail_url=thumbnail_url)

@VideoQuick.route('/about')
def about():
    return render_template('YTAbout.html')

@VideoQuick.route('/contact')
def contact():
    return render_template('YTContact.html')

@VideoQuick.route('/login')
def login():
    return render_template('login.html')

@VideoQuick.route('/services')
def services():
    return render_template('services.html')


@VideoQuick.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    VideoQuick.run(debug=True)
