import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import openai


def recommand_text(model, max_tokens, temperature, text):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": """你是一個專業的資料分析助理，具有豐富的數據科學知識和經驗。你的主要任務是幫助
                 我理解資料集，並提供合適的資料視覺化建議。你需要根據我的需求，推薦最適合的 x 軸和 y 軸，並解釋它
                 們在選定圖表中的意義。."""},
                {"role": "user", "content": f"""我正在進行資料視覺化分析，以下是我的資料集的類型：{text}。請從中選兩個類型,
                 搭配出一種最適合的x軸和y軸，先告訴我x,y軸放什麼,再解釋這些變數在我選擇的圖表類型中的意義,請在不超過
                 {max_tokens}個字內完成說明。圖表類型可以是折線圖、條形圖、散點圖、分佈圖或計數圖。"""}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        st.error(f"發生錯誤: {e}")
        return None


# Set the page config
st.set_page_config(page_title='Data Visualizer',
                   layout='centered',
                   page_icon='📊')

# Title
st.title('📊  資料視覺化')


# Dropdown to select a file
upload_file = st.file_uploader("上傳Excel文件", type=["csv","xlsx", "xls"])


# 選擇是否啟用大語言功能
st.sidebar.header("視覺化圖表建立提示")
with st.sidebar.popover("啟用大語言功能"):
    api_key = st.text_input("輸入 OpenAI API Key", type="password")
    openai.api_key = api_key

    
    model = st.selectbox(
        "選擇OpenAI模型",
        options=["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06"],
        index=1  # 默认选择 "gpt-4o-mini"
    )

    max_tokens = st.slider("選擇最大 tokens 数量", min_value=100, max_value=2000, value=500, step=50)
    temperature = st.slider("選擇生成的 tempature (温度)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
        st.session_state["model"] = ""
        st.session_state["maxtoken"] = ""
        st.session_state["temperature"] = ""
        st.session_state["recommand"] = ""

    
    if st.button("啟用"):
        st.session_state["api_key"] = api_key
        st.session_state["model"] = model
        st.session_state["max_token"] = max_tokens
        st.session_state["temperature"] = temperature


if st.session_state["api_key"] != "":
    st.sidebar.info("大語言功能已啟用")

if upload_file:

    # Read the selected CSV file
    df = pd.read_csv(upload_file)

    col1, col2 = st.columns(2)

    columns = df.columns.tolist()

    with col1:
        st.write("")
        st.write(df.head())

    with col2:
        # Allow the user to select columns for plotting
        x_axis = st.selectbox('Select the X-axis', options=columns+["None"])
        y_axis = st.selectbox('Select the Y-axis', options=columns+["None"])

        plot_list = ['Line Plot', 'Bar Chart', 'Scatter Plot', 'Distribution Plot', 'Count Plot']
        # Allow the user to select the type of plot
        plot_type = st.selectbox('Select the type of plot', options=plot_list)

    # Generate the plot based on user selection
    if st.button('Generate Plot'):

        fig, ax = plt.subplots(figsize=(10, 6))  # 增加圖表大小

        if plot_type == 'Line Plot':
            sns.lineplot(x=df[x_axis], y=df[y_axis], ax=ax)
        elif plot_type == 'Bar Chart':
            sns.barplot(x=df[x_axis], y=df[y_axis], ax=ax)
        elif plot_type == 'Scatter Plot':
            sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax)
        elif plot_type == 'Distribution Plot':
            sns.histplot(df[x_axis], kde=True, ax=ax) # type: ignore
            y_axis = 'Density'
        elif plot_type == 'Count Plot':
            sns.countplot(x=df[x_axis], ax=ax)
            y_axis = 'Count'

        # Automatically adjust label density
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins='auto'))

        # Adjust label sizes
        ax.tick_params(axis='x', labelsize=10)  # Adjust x-axis label size
        ax.tick_params(axis='y', labelsize=10)  # Adjust y-axis label size

        # Adjust title and axis labels with a smaller font size
        plt.title(f'{plot_type} of {y_axis} vs {x_axis}', fontsize=12)
        plt.xlabel(x_axis, fontsize=10) # type: ignore
        plt.ylabel(y_axis, fontsize=10) # type: ignore

        # Automatically adjust subplot params to give specified padding
        plt.tight_layout()

        # Show the results
        st.pyplot(fig)

    if st.sidebar.button('Genreate Analyze way'):
        if st.session_state["api_key"] == "":
            st.sidebar.error("輸入api key 啟用大語言功能")
        else:   
            recommand = recommand_text(st.session_state["model"],st.session_state["max_token"],st.session_state["temperature"],columns)
            st.session_state["recommand"] = recommand
            with st.sidebar.popover("分析建議"):
                st.write(recommand)
    elif st.session_state["recommand"] != "":
        with st.sidebar.popover("分析建議"):
            st.write(st.session_state["recommand"])    
