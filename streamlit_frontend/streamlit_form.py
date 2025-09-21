import streamlit as st
import requests

st.set_page_config(page_title="Mind Score + Chatbot", layout="wide")
API_URL = "http://127.0.0.1:8000"  # FastAPI backend

st.title("🧠 Mind Score Prediction Dashboard")

# ------------------- Prediction Section ------------------- #
st.header("📊 Predict Your Mind Score")

age = st.slider("Age", 1, 100, 20)
gender = st.selectbox("Gender", ["Male", "Female"])
academic_level = st.selectbox("Academic Level", ["High School", "Undergraduate", "Graduate"])
country = st.text_input("Country", value="India")
avg_daily_usage_hours = st.slider("Avg daily social media usage (hours)", 0, 24, 3)
most_used_platform = st.selectbox(
    "Most used platform",
    ["Instagram", "Twitter", "TikTok", "YouTube", "Facebook", "LinkedIn",
     "Snapchat", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"]
)
sleep_hours_per_night = st.slider("Average sleeping hours per night", 1, 12, 7)
relationship_status = st.selectbox("Relationship Status", ["Single", "In Relationship", "Complicated"])

if "last_prediction" not in st.session_state:
    st.session_state["last_prediction"] = None

if st.button("🔮 Predict Mind Score"):
    input_data = {
        "age": int(age),
        "Gender": gender,
        "Academic_Level": academic_level,
        "Country": country,
        "Avg_Daily_Usage_Hours": float(avg_daily_usage_hours),
        "Most_Used_Platform": most_used_platform,
        "Sleep_Hours_Per_Night": float(sleep_hours_per_night),
        "Relationship_Status": relationship_status
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=input_data)
        if response.status_code == 200:
            result = response.json()
            prediction = result.get("prediction", "Unknown")
            st.session_state["last_prediction"] = prediction
            st.success(f"🎯 Predicted Mind Score Category: **{prediction}**")
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Connection Error: {e}")

# ------------------- Chatbot Section ------------------- #
st.markdown("---")
st.header("🤖 AI Chatbot")

# Sidebar robot icon
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.markdown("### 💬 Chat with AI")
    chat_container = st.container()

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input
user_message = st.text_input("Type your message:", "")

if st.button("Send", key="send_msg"):
    if user_message.strip():
        context_data = {
            "Mind_Score": st.session_state.get("last_prediction"),
            "Age": age,
            "Sleep_Hours_Per_Night": sleep_hours_per_night,
            "Avg_Daily_Usage_Hours": avg_daily_usage_hours,
            "Academic_Level": academic_level,
        }
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": user_message, "context": context_data}
            )
            if response.status_code == 200:
                reply = response.json().get("response", "No reply")
                st.session_state.chat_history.append(("You", user_message))
                st.session_state.chat_history.append(("Bot", reply))
            else:
                st.error(f"Chatbot Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# Display chat history
with st.expander("💬 Open Chatbot", expanded=True):
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Bot:** {msg}")
 