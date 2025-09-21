from flask import Flask, render_template, request
import google.generativeai as genai
import os, requests
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

app = Flask(__name__)
FASTAPI_URL = "http://127.0.0.1:8000/user-data"

@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    if request.method == "POST":
        user_input = request.form["message"]

        # Get user data
        try:
            user_data = requests.get(FASTAPI_URL).json()
        except:
            user_data = {"error": "Failed to get user data"}

        if "error" not in user_data:
            context = f"User data: {user_data}\nQuestion: {user_input}\nGive improvement advice based on data."
        else:
            context = f"Question: {user_input}\n(Note: No user data found.)"

        response = model.generate_content(context)
        reply = response.text

    return render_template("index.html", reply=reply)

if __name__ == "__main__":
    app.run(debug=True)
