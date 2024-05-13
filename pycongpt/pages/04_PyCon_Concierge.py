import tempfile

import config as cfg
import duckdb
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import DuckDB
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from streamlit_chat import message


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "generated" not in st.session_state:
        st.session_state["generated"] = ["Hello! Feel free to ask me any questions."]

    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey! 👋"]


def conversation_chat(query, chain, history):
    result = chain({"question": query, "chat_history": history})
    history.append((query, result["answer"]))

    return result["answer"]


def display_chat_history(chain):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_input(
                "Question:", placeholder="Ask about your Documents", key="input"
            )
            submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input:
            with st.spinner("Generating response ......"):
                output = conversation_chat(
                    query=user_input, chain=chain, history=st.session_state["history"]
                )

            st.session_state["past"].append(user_input)
            st.session_state["generated"].append(output)

    if st.session_state["generated"]:
        with reply_container:
            for i in range(len(st.session_state["generated"])):
                message(
                    st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs",
                )
                message(
                    st.session_state["generated"][i],
                    key=str(i),
                    avatar_style="fun-emoji",
                )


def create_conversational_chain(vector_store):
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", temperature=0.1, openai_api_key=cfg.OPENAI_API_KEY
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
        memory=memory,
    )

    return chain


def main():
    initialize_session_state()
    st.title("PyCon Concierge")
    # st.sidebar.title("Document Processing")

    loader = DirectoryLoader(
        cfg.DATA_DIR / "pycon-2024-schedule",
        glob="*.txt",
        loader_cls=TextLoader,
        use_multithreading=True,
        show_progress=True,
    )

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )

    text_chunks = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vector_store = DuckDB.from_documents(text_chunks, embeddings, connection=duckdb.connect("pycon2024_schedule.ddb"))

    chain = create_conversational_chain(vector_store=vector_store)

    display_chat_history(chain=chain)


if __name__ == "__main__":
    main()
