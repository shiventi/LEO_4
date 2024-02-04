import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from pathlib import Path
from subprocess import call
import datetime
import time
from playsound import playsound
import re
from googlesearch import search

def check_internet_connection():
    try:
        response = requests.get('http://www.google.com', timeout=0.5)
        response.raise_for_status()
        return True
    except requests.ConnectionError:
        return False

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "I was on the verge of selling your data."}]

def convert_to_seconds(hours, minutes, seconds):
    return hours * 3600 + minutes * 60 + seconds

def link_finder(query, num_results=10):
    result_hrefs = []

    for j in search(query, num_results=num_results):
        result_hrefs.append(j)

    return result_hrefs

def convert_to_seconds(hours, minutes, seconds):
    return hours * 3600 + minutes * 60 + seconds

def set_timer(hours, minutes, seconds):
    total_seconds = convert_to_seconds(hours, minutes, seconds)    
    countdown_container = st.sidebar.empty()
    
    for remaining_time in range(total_seconds, 0, -1):

        hours_remaining, minutes_remaining = divmod(remaining_time, 3600)
        minutes_remaining, seconds_remaining = divmod(minutes_remaining, 60)
        countdown_container.text(f"Time Remaining: {hours_remaining}h {minutes_remaining}m {seconds_remaining}s")
        
        time.sleep(1)
    
    countdown_container.success("Timer complete!")


st.set_page_config(page_title="LEO", page_icon="🦁", layout = "wide")

st.sidebar.markdown("# **🦁💬 LEO**")

a = st.secrets["NAME"]

st.write(a)

st.sidebar.markdown("This personal assistant is created using the open-source Gemini-Pro and Pro-Vision LLM model from Google.")

if check_internet_connection():
    st.sidebar.success('Successful pretests', icon='✅')
else:
    st.sidebar.error('Unsuccessful pretests. Check WiFi!', icon='🚨')

st.sidebar.divider()


google_api_key = st.sidebar.text_input("Enter your Google API key:")
if not google_api_key:
    st.sidebar.warning("Please enter your Google API key.")
    st.stop()



os.environ['GOOGLE_API_KEY'] = google_api_key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

st.sidebar.divider()


safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]

model_gemini_pro = genai.GenerativeModel(model_name='gemini-pro', safety_settings=safety_settings)
model_gemini_pro_vision = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)



if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


allowed_file_types = ["jpg", "jpeg", "png", "txt", "doc", "docx", "py", "ipynb"]
uploaded_file = st.sidebar.file_uploader("Upload an image or text file", type=allowed_file_types)


def generate_google_response(prompt_input, content_data=None, content_type="text"):
    if content_data is not None:
        if content_type == "image":
            response = model_gemini_pro_vision.generate_content(contents=[prompt_input, content_data])
        else:
            response = model_gemini_pro.generate_content(contents=[prompt_input, content_data])
    else:
        response = model_gemini_pro.generate_content(contents=[prompt_input])

    return response.text

if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

#call(["osascript -e 'set volume output volume 0'"], shell=True)
#volume = st.sidebar.slider('Volume', 0, 10)
#if volume:
    #call(["osascript -e 'set volume output volume 0'"], shell=True)
    #call(["osascript -e 'set volume output volume '" + str(volume*10)], shell=True)
st.sidebar.divider()

reminder_types = ["Select", "Date"]

def filter_reminders(reminders):
    current_date = datetime.datetime.today().date()
    filtered_reminders = []
    for reminder in reminders:
        if ":" in reminder:
            date_str, reminder_text = reminder.split(":", 1)
            reminder_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if current_date <= reminder_date:
                filtered_reminders.append((reminder_date, reminder_text.strip()))
    return filtered_reminders

st.sidebar.markdown("## **Quick Features**")

reminder_types_t = ["Select","Timer"]
selected_reminder_type = st.sidebar.selectbox("Timer", reminder_types_t)

if selected_reminder_type == "Timer":
    timer_hours = st.sidebar.number_input("Set Timer (hours)", min_value=0, value=0)
    timer_minutes = st.sidebar.number_input("Set Timer (minutes)", min_value=0, max_value=59, value=0)
    timer_seconds = st.sidebar.number_input("Set Timer (seconds)", min_value=0, max_value=59, value=0)

    if st.sidebar.button("Start Timer"):
        set_timer(timer_hours, timer_minutes, timer_seconds)

reminder_types_l = ["Select","Web Scrape"]
selected_reminder_type = st.sidebar.selectbox("Web Scrape", reminder_types_l)

if selected_reminder_type == "Web Scrape":
    input_link = st.sidebar.text_input("Input a link")
    if input_link:
        try:
            webpage = requests.get(input_link)
            soup = BeautifulSoup(webpage.content, 'html.parser')
            prompt_text = soup.get_text()
            response = generate_google_response(prompt_text)
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
        except Exception as e:
            st.write(f"Error: {e}")

reminder_types_s = ["Select","Find Link"]
selected_reminder_type = st.sidebar.selectbox("Find Link", reminder_types_s)

if selected_reminder_type == "Find Link":
    input_search = st.sidebar.text_input("What would you like to search")
    if input_search:
        try:
            query = input_search
            query = query.replace(" ", "+")
            a = link_finder(query)

            with st.sidebar.expander("Results"):
                try:
                    for href in a:
                        st.write(href)
                except FileNotFoundError:
                    st.info(f"Error: {e}")
    
        except Exception as e:
            st.write(f"Error: {e}")


st.sidebar.divider()

if st.sidebar.button('Clear Chat History', on_click=clear_chat_history):
    clear_chat_history()

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if uploaded_file:
                if uploaded_file.type.startswith('image'):
                    content_type = "image"
                    image_path = "uploaded_image.png"
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.read())
                    content_data = {'mime_type': 'image/png', 'data': open(image_path, "rb").read()}
                elif uploaded_file.type.startswith('text') or uploaded_file.type.endswith(('doc', 'docx', 'py', 'ipynb', 'pdf')):
                    content_type = "text"
                    content_data = uploaded_file.getvalue().decode("utf-8")
                else:
                    st.write("Unsupported file type. Please upload an image, .txt, .doc, .docx, .py, .ipynb, or .pdf file.")
                    content_type = None
                    content_data = None

                if content_type:
                    response = generate_google_response(prompt, content_data=content_data, content_type=content_type)
                    st.write(response)

                    if content_type == "image":
                        os.remove(image_path)
            else:
                response = generate_google_response(prompt)
                st.write(response)

    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
