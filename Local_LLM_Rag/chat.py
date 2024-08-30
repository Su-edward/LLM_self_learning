import streamlit as st
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import ollama

# Function to load, split, and retrieve documents
def load_and_retrieve_docs(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma.from_texts(texts=splits, embedding=embeddings)
    return vectorstore.as_retriever()

# Function to format documents
def format_docs(docs):
    return "\n\n".join(docs)

# Function that defines the RAG chain
def rag_chain(text, question):
    retriever = load_and_retrieve_docs(text)
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)
    formatted_prompt = f"Question: {question}\n\nContext: {formatted_context}"
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': formatted_prompt}])
    return response['message']['content']

# Function to read PDF
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Main function to display content
def main():

    st.sidebar.header("選擇功能",divider="rainbow")
    rag_sourece = st.sidebar.selectbox("Rag資料來源",("PDF內容","URL內容") )


    st.title("RAG Chain 問題回答")
    st.write(f"使用{rag_sourece}獲取回答。")

    pdf_file = ""
    url = ""

    #選擇資料來源
    if rag_sourece == "pdf內容":
        # Upload PDF
        pdf_file = st.file_uploader("上傳 PDF 檔案", type=["pdf"])
    else:
        # Input URL and question
        url = st.text_input("請輸入 URL (可選):")

    question = st.text_input("請輸入問題:")

    if st.button("提交"):
        if pdf_file and question:
            with st.spinner("正在讀取 PDF 並生成回答..."):
                pdf_text = read_pdf(pdf_file)
                result = rag_chain(pdf_text, question)
                st.write("回答:")
                st.write(result)

                # Adding download button for PDF result
                st.download_button(
                    label="下載結果為 .txt",
                    data=result,
                    file_name="result.txt",
                    mime="text/plain"
                )
        elif url and question:
            with st.spinner("正在生成回答..."):
                result = rag_chain(url, question)
                st.write("回答:")
                st.write(result)

                # Adding download button for URL result
                st.download_button(
                    label="下載結果為 .txt",
                    data=result,
                    file_name="result.txt",
                    mime="text/plain"
                )
        else:
            st.warning("請上傳 PDF 或輸入 URL 並輸入問題。")

if __name__ == "__main__":
    main()
