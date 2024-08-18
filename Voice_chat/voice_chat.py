import openai
import streamlit as st
from gtts import gTTS
from pygame import mixer
import tempfile
import PyPDF2


# 語音功能
def speak(sentence, lang):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=sentence, lang=lang)
        tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play(1)

# pdf讀取
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

st.title("語音助理")

with st.sidebar.popover("啟用大語言功能"):
    api_key = st.text_input("輸入 OpenAI API Key", type="password")
    openai.api_key = api_key

    model = st.selectbox(
        "選擇OpenAI模型",
        options=["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"],
        index=1  # 默認選 "gpt-4o-mini"
    )
    max_tokens = st.slider("選擇最大 tokens 数量", min_value=100, max_value=2000, value=100, step=50)
    temperature = st.slider("選擇生成的 tempature (温度)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)


    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
        st.session_state["model"] = ""
        st.session_state["maxtoken"] = ""
        st.session_state["temperature"] = ""
        st.session_state["voice"] = False
        st.session_state["pdf"] = False
    
    if st.button("啟用"):
        st.session_state["api_key"] = api_key
        st.session_state["model"] = model
        st.session_state["max_token"] = max_tokens
        st.session_state["temperature"] = temperature


if st.session_state["api_key"] != "":
    st.sidebar.info("大語言功能已啟用")

if st.sidebar.checkbox("語音回答"):
    st.session_state["voice"] = True
else:
    st.session_state["voice"] = False


if st.sidebar.checkbox("使用PDF內容回答"):
    st.session_state["pdf"] = True
    uploaded_file = st.sidebar.file_uploader("上傳 PDF 文件", type="pdf")
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        with st.expander("PDF 内容"):
            st.write( pdf_text, height=200)
else:
    st.session_state["pdf"] = False

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 確認是否有api
if st.session_state["api_key"] == "":
    st.info("請先輸入Api key 以進行對話")

elif prompt := st.chat_input("What is up?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if st.session_state["pdf"]:
                stream = openai.chat.completions.create(
                    model=st.session_state["model"],
                    messages=[
                        {"role": "system", "content": f"""你是一個專業的AI小助理，具有豐富的數據科學知識和經驗。
                        你主要的任務是根據使用者的問題,根據{pdf_text}的內容,使用對應語言回答,若是沒有指定,則使用繁體中文."""},
                        *[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    ],
                    stream=True,
                )
            else:
                stream = openai.chat.completions.create(
                    model=st.session_state["model"],
                    messages=[
                        {"role": "system", "content": """你是一個專業的AI小助理，具有豐富的數據科學知識和經驗。
                        你主要的任務是根據使用者的問題,使用對應語言回答,若是沒有指定,則使用繁體中文."""},
                        *[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    ],
                    stream=True,
                )

            response = st.write_stream(stream)
            # 合成语音
            if st.session_state["voice"]:
                speak(response, 'zh-tw')
            else:
                pass

        except:
            response = "請輸入正確的API key"
            st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
