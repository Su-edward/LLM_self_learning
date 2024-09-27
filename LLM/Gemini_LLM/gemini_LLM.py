from streamlit_autorefresh import st_autorefresh 
import streamlit as st
from pypdf import PdfReader 
import google.generativeai as genai
import os
from PIL import Image
import tempfile
import time




#參數設定
def get_llminfo():
    st.sidebar.header("使用者選擇", divider='rainbow')

    model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

    with st.sidebar.popover("相關參數設定"):
        tip1="選擇使用模型"
        model = st.selectbox("選擇gemini模型", model_list,help=tip1,index=model_list.index('models/gemini-1.5-flash-latest'))

        tip2="較低的溫度適用於創意性較低的回應，而較高的溫度則會導致更具多樣性的結果。"
        tempature = st.slider("溫度:", min_value=0.0,
                                        max_value=2.0, value=1.0, step=0.25, help=tip2)
        tip3="設定較低的值會產生較不隨機的回應，而設定較高的值則會產生較隨機的回應。"
        topp = st.slider("Top P:", min_value=0.0,
                                max_value=1.0, value=0.94, step=0.01, help=tip3)
        tip4="回復token的限制"
        maxtokens = st.slider("最高 Tokens:", min_value=100,
                                    max_value=1000, value=100, step=100, help=tip4)
    return model, tempature, topp, maxtokens

# Gemini基本對話
def gemini_chat(model, prompt,generation_config):
    gemini_model = genai.GenerativeModel(model,generation_config=generation_config)
    response = gemini_model.generate_content(prompt)
    return response.text

# Gemini pdf 對話
def gemini_pdf_chat(model, prompt,generation_config,pdf_cotent):
    gemini_model = genai.GenerativeModel(model,generation_config=generation_config)
    response = gemini_model.generate_content([prompt, pdf_cotent])
    return response.text

# Gemini image 對話
def gemini_image_chat(model, prompt,generation_config,image):
    gemini_model = genai.GenerativeModel(model,generation_config=generation_config)
    response = gemini_model.generate_content([image,prompt])
    return response.text

# Gemini video對話
def gemini_video_music_chat(model, prompt,generation_config,video):
    gemini_model = genai.GenerativeModel(model,generation_config=generation_config)
    response = gemini_model.generate_content([video,prompt])
    return response.text

def get_type():
    st.sidebar.header("選擇處理類類型", divider='orange')
    typepdf = st.sidebar.radio("Choose one:",
                               ("Chat",
                                "PDF files",
                                "Images",
                                "Video, mp4 file",
                                "Audio files"))
    return typepdf



def main():
    st.title("gemini 助理")

    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
    if st.session_state["api_key"]  =="":
        key =  st.sidebar.text_input("請輸入api_key", type='password')
        if st.sidebar.button("啟用"):
            st.session_state["api_key"] = key
            st_autorefresh(interval=500,limit=2)
    if st.session_state["api_key"] != "":
        try : 
            # 配置並執行主程式
            #GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY_NEW')
            GOOGLE_API_KEY = st.session_state["api_key"]
            genai.configure(api_key=GOOGLE_API_KEY)
            model, temperature, top_p, max_tokens =  get_llminfo()

            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_tokens,
                "response_mime_type": "text/plain",
                }

            # 對話類型
            type = get_type()

            # 處理檔案
            if type == "PDF files":
                uploaded_files = st.sidebar.file_uploader("上傳pdf檔", type='pdf', accept_multiple_files=True)
                
                if uploaded_files:
                    pdf_text = ""
                    for pdf in uploaded_files:
                        pdf_reader = PdfReader(pdf)
                        for page in pdf_reader.pages:
                            pdf_text += page.extract_text()         
            elif type == "Images":
                image_file = st.sidebar.file_uploader("上傳圖片檔", type=["jpg", "jpeg", "png"])
                if image_file is not None:
                    # 使用PIL打開
                    image = Image.open(image_file)
                    # 顯示
                    with st.expander("上傳圖片"):
                        col1,col2 = st.columns([1,1])
                        with col1:
                            new_width = 200
                            aspect_ratio = (new_width / float(image.size[0]))
                            new_height = int((float(image.size[1]) * float(aspect_ratio)))
                            resized_image = image.resize((new_width, new_height))
                            # 旋轉
                            rotate_angle = st.slider("選擇旋轉角度", 0, 360, 0)
                            # 比例
                            scale = st.slider("選擇縮放比例", 0.1, 2.0, 1.0)
                            # 旋轉圖
                            rotated_image = resized_image.rotate(rotate_angle, expand=True)
                            final_width = int(rotated_image.width * scale)
                            final_height = int(rotated_image.height * scale)
                            final_image = rotated_image.resize((final_width, final_height))
                        with col2:
                            st.image(final_image, use_column_width=False)
            elif type == "Video, mp4 file":
                video_file_name = st.sidebar.file_uploader("上傳影片")
                if video_file_name:
                    with st.expander("上傳影片"):
                        st.video(video_file_name)
                    # 創建臨時路徑
                    temp_dir = tempfile.gettempdir()  
                    fpath2 = os.path.join(temp_dir, video_file_name.name)          
                    with open(fpath2, 'wb') as out_file:
                        out_file.write(video_file_name.getbuffer())
                    video_file = genai.upload_file(path=fpath2)
                    while video_file.state.name == "PROCESSING":
                        time.sleep(5)
                        video_file = genai.get_file(video_file.name)
                    if video_file.state.name == "FAILED":
                        raise ValueError(video_file.state.name)   
            elif type == "Audio files":
                audio_file_name = st.sidebar.file_uploader("上傳音檔")
                if audio_file_name:

                    with st.expander("上傳音樂"):
                        st.audio(audio_file_name)
                    # 臨時存儲
                    temp_dir = tempfile.gettempdir()  
                    fpath2 = os.path.join(temp_dir, audio_file_name.name)  

                    with open(fpath2, 'wb') as out_file:
                        out_file.write(audio_file_name.getbuffer())
                    audio_file = genai.upload_file(path=fpath2)
                    while audio_file.state.name == "PROCESSING":
                        time.sleep(5)
                        audio_file = genai.get_file(audio_file.name)
                    if audio_file.state.name == "FAILED":
                        raise ValueError(audio_file.state.name)
                    
            # 初始化 sesseion&顯示
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # 處理對話
            if prompt := st.chat_input("輸入您的問題"):

                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    try:
                        if type == "Chat":
                            response = gemini_chat(model, prompt,generation_config)
                        elif type == "PDF files":
                            response = gemini_pdf_chat(model, prompt,generation_config,pdf_text) # type: ignore
                        elif type == "Images":
                            response = gemini_image_chat(model, prompt,generation_config,image) # type: ignore
                        elif type == "Video, mp4 file" :
                            response = gemini_video_music_chat(model, prompt,generation_config,video_file) # type: ignore
                        elif type == type == "Audio files":
                            response = gemini_video_music_chat(model, prompt,generation_config,audio_file) # type: ignore
                        else:
                            pass
                    except Exception as e:
                        response = f"發生錯誤: {str(e)}"
                    
                    st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"{str(e)}")
            st.session_state["api_key"] = ""
if __name__ == '__main__':
    main()

