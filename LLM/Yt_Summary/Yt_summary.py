import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
import openai
import re

def clean_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '_', title)

def extract_video_id(url):
    parsed_url = urlparse(url)
    video_id = None
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            video_id = query.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            video_id = parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            video_id = parsed_url.path.split('/')[2]
    elif parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]
    
    return video_id

def download_subtitle(url, language_code='en'):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("無法獲取影片ID。")
            return None, None

        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        yt = YouTube(url)
        video_title = yt.title

        subtitle_text = "".join([entry['text'] + "\n" for entry in transcript])
        
        st.success("字幕下載成功！")
        return subtitle_text, video_title
    
    except Exception as e:
        st.error(f"錯誤: {e}")
        return None, None

def summarize_text(model, max_tokens, temperature, text):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"""請將以下原文翻譯成中文，並以重點標題和段落的形式重新整理該文章，使用白話文，使一般人能夠理解。
                 請按以下要求處理：1. 翻譯成中文。2. 以重點標題和段落形式重新整理。3. 使用白話文，通俗易懂。4. 使用Markdown格式，包括分段和列表。{text}."""}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return None

def process_video(model, max_tokens, temperature, video_url):
    Yt_text, Yt_title = download_subtitle(video_url)
    
    if Yt_text and Yt_title:
        summary = summarize_text(model, max_tokens, temperature, Yt_text)     
        if summary:
            st.text_area("摘要结果", summary, height=400)
            
            cleaned_title = clean_filename(Yt_title)
            summary_file = f"{cleaned_title}.txt"
            st.download_button(
                label="下載摘要",
                data=summary,
                file_name=summary_file,
                mime="text/plain"
            )
        else:
            st.error("無法生成摘要。")
    else:
        st.error("無法下載字幕。")

# Streamlit 界面
st.title("YouTube 摘要生成器")

# 在侧边栏让用户输入 API Key
api_key = st.sidebar.text_input("輸入 OpenAI API Key", type="password")
openai.api_key = api_key

# 在侧边栏让用户选择模型
model = st.sidebar.selectbox(
    "選擇OpenAI模型",
    options=["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"],
    index=1  # 默认选择 "gpt-4o-mini"
)

# 在侧边栏让用户选择max_tokens, temperature
max_tokens = st.sidebar.slider("選擇最大 tokens 数量", min_value=100, max_value=2000, value=500, step=50)
temperature = st.sidebar.slider("選擇生成的 tempature (温度)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

video_url = st.text_input("輸入 YouTube 網址:")

if st.button("生成摘要"):
    if api_key and video_url:
        process_video(model, max_tokens, temperature, video_url)
    else:
        st.warning("請輸入有效的 API Key 和 YouTube 網址。")
