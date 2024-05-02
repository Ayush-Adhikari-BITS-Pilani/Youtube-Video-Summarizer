import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv() ##load all the environment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi
#from rpunct import RestorePuncts

from deep_translator import GoogleTranslator

genai.configure(api_key=os.getenv("API_KEY"))

prompt="""You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points.
Please provide the summary of the text given here:  """

def extract_transcript_details(youtube_video_url):
  #youtube_video_url = "https://www.youtube.com/watch?v=PFPt6PQNslE"
  video_id = youtube_video_url.split("v=")[-1]
  
  transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
  
  # Try fetching the manual transcript
  try:
    transcript = transcript_list.find_manually_created_transcript()
    language_code = transcript.language_code  # Save the detected language
  except:
    # If no manual transcript is found, try fetching an auto-generated transcript in a supported language
    try:
      generated_transcripts = [trans for trans in transcript_list if trans.is_generated]
      transcript = generated_transcripts[0]
      language_code = transcript.language_code  # Save the detected language
    except:
      # If no auto-generated transcript is found, raise an exception
      raise Exception("No suitable transcript found.")
  full_transcript = " ".join([part['text'] for part in transcript.fetch()])

  #rpunct = RestorePuncts()
  #results = rpunct.punctuate(full_transcript)
  return full_transcript

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):

    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text

def summary_translate(summary, lang):
   translated_text = GoogleTranslator(target=lang).translate(summary)
   return translated_text

language_list = ['bengali', 'bhojpuri','danish','english','french','german','hindi','italian', 'japanese', 'malayalam','portuguese','russian','spanish']
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

language_selected = st.selectbox("Select the language in which you want your notes", options=language_list)

if st.button("Get Detailed Notes"):
    transcript_text=extract_transcript_details(youtube_link)

    # st.success("Your notes are ready :) ")


    if transcript_text:
        summary=generate_gemini_content(transcript_text,prompt)

        if(summary):
          translated_summary = summary_translate(summary, language_selected)
          st.write("Detailed Notes in selected language ",language_selected, "is: " )
          st.write(translated_summary)
        
        st.download_button('Download the notes', translated_summary)
        