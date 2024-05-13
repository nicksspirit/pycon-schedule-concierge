import streamlit as st

st.set_page_config(page_title="Home", page_icon=":home:", layout="wide")


def main():
    st.title("Streamlit App")
    st.subheader("A faster way to build and share data apps")

    video_url = "https://s3-us-west-2.amazonaws.com/assets.streamlit.io/videos/hero-video.mp4"
    st.video(video_url, autoplay=True, muted=True)


if __name__ == "__main__":
    main()
