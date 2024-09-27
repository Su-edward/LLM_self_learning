import streamlit as st
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh 

#參數設定
def get_llminfo():
    st.sidebar.header("使用者選擇", divider='rainbow')

    client = OpenAI(
        api_key = st.session_state["api_key"]
    )

    with st.sidebar.popover("相關參數設定"):

        model_list = client.models.list()
        tip1="選擇使用模型"

        model_names = [model.id for model in model_list]
        model = st.selectbox("選擇模型", model_names,help=tip1)

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





def chat(model, prompt,temperature, top_p, max_tokens):

    client = OpenAI(
        api_key = st.session_state["api_key"]
    )
    completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f'{prompt}'}
    ],
    temperature=temperature,          
    top_p=top_p,
    max_tokens=max_tokens,
    )
    return completion.choices[0].message.content



def main():
    st.title("LLM 基本對話")

    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

    if st.session_state["api_key"]  =="":
        key =  st.sidebar.text_input("請輸入api_key", type='password')
        if st.sidebar.button("啟用"):
            st.session_state["api_key"] = key

    if st.session_state["api_key"]  !="":
        try:
            model, temperature, top_p, max_tokens =  get_llminfo()

            st_autorefresh(interval=500,limit=2)

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
                        response = chat(model, prompt, temperature, top_p, max_tokens)
                    except Exception as e:
                        response = f"發生錯誤: {str(e)}"
                    
                    st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"{str(e)}")
            #st.session_state["api_key"] = ""


    else :
        st.info("請先輸入openai Key")
if __name__ == '__main__':
    main()
