import streamlit as st
import time

# --- Topic 86: Page Config ---
st.set_page_config(page_title="Streamlit Guide", page_icon="🚀", layout="wide")

# --- Topic 76: Display Elements ---
st.title("Streamlit 🚀 Complete Guide Core Elements")
st.header("Topic 76: Display Elements")
st.write("`st.write()` is the universal display handler.")
st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

# --- Topic 78: Layout & Containers ---
st.header("Topic 78: Layout & Containers")
col1, col2 = st.columns(2)
with col1:
    st.info("This is Column 1")
with col2:
    st.success("This is Column 2")

with st.expander("Click to Expand"):
    st.write("Hidden content revealed!")

tab1, tab2 = st.tabs(["Tab A", "Tab B"])
with tab1:
    st.write("Content of Tab A")
with tab2:
    st.write("Content of Tab B")

# --- Topic 77: Input Widgets ---
st.header("Topic 77: Input Widgets")
name = st.text_input("Enter your name:")
age = st.slider("Select your age", 0, 100, 25)
st.write(f"Name: {name}, Age: {age}")

# --- Topic 82: Forms ---
st.header("Topic 82: Forms")
with st.form("my_form"):
    user_input = st.text_input("Feedback")
    submitted = st.form_submit_button("Submit Form")
    if submitted:
        st.success("Form submitted successfully!")

# --- Topic 79: Session State ---
st.header("Topic 79: Session State")
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment Counter"):
    st.session_state.counter += 1
st.write(f"Counter current value: {st.session_state.counter}")

# --- Topic 80: Caching ---
st.header("Topic 80: Caching")
@st.cache_data
def expensive_computation():
    time.sleep(2) # Simulate work
    return "Data Computed!"

st.write(expensive_computation())

# --- Topic 81: Chat UI ---
st.header("Topic 81: Chat UI")
with st.chat_message("assistant"):
    st.write("Hello! I am a chat bubble.")

chat_val = st.chat_input("Type a message...")
if chat_val:
    st.write(f"You typed: {chat_val}")

# --- Topic 83: Status & Feedback ---
st.header("Topic 83: Status & Feedback")
with st.spinner("Loading animation..."):
    time.sleep(1)
st.success("Loaded!")

with st.status("Downloading data..."):
    st.write("Step 1 complete")
    time.sleep(0.5)
    st.write("Step 2 complete")
