import streamlit as st
import pandas as pd
import json
import io
import csv
from google import genai
from google.genai import types


# ------------------ UI helpers ------------------
def hide_nav():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------ Views ------------------
def login_page():
    hide_nav()
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state.authenticated = True
            st.session_state.page = "survey"
            st.rerun()
        else:
            st.error("Invalid credentials")


def survey_page():
    hide_nav()
    st.title("Survey")
    st.title("Tell Us a Bit About Yourself")
    with st.form("survey_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=10, max_value=120, step=1)

        gender = st.radio("Gender", ["Male", "Female", "Other", "Prefer not to say"])

        income_range = st.radio(
            "Your Montly Income:",
            ["10,000Rs+", "50,000Rs+", "1,00,000Rs+", "5,00,000Rs+", "10,00,000Rs+"],
        )

        Occupation = st.text_input(
            "Main Occupation ",
        )

        investments = st.multiselect(
            "Do you have any other investments?",
            ["Real Estate", "Trading", "Fixed Deposits"],
        )

        investment_values = {}

        for inv in investments:
            investment_values[inv] = st.number_input(
                f"Enter estimated worth for {inv} in Rs.", key=f"worth_{inv}"
            )
        save = st.form_submit_button("ok")
        submitted = st.form_submit_button("Submit")

    # --- Handle Submission ---
    if save:
        pass
    if submitted:
        if name.strip() == "":
            st.error("Please enter your name.")
        else:
            data = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Income_range": income_range,
                "main_occupation": Occupation,
                "investments": investments,
            }

            df = pd.DataFrame([data])

            st.success("✅ Survey submitted successfully!")
            st.subheader("Your Response")
            st.dataframe(df)

            # Optional: save to CSV
            df.to_csv("survey_responses.csv", mode="a", header=False, index=False)
            st.session_state.page = "dashboard"
            st.rerun()


def dashboard_page():
    hide_nav()
    client = genai.Client()

    st.title("Dashboard")

    st.title("Upload E-Statement")

    uploaded_file = st.file_uploader(
        "Upload your recent e-statement (PDF)",
        type=["pdf"],
        help="Upload your latest bank or credit card e-statement in PDF format",
    )

    if uploaded_file is not None:
        st.success("PDF uploaded successfully ✅")

        # Access file bytes
        pdf_bytes = uploaded_file.getbuffer()

        # Example: show file info
        st.write(
            {
                "Filename": uploaded_file.name,
                "File size (KB)": round(len(pdf_bytes) / 1024, 2),
            }
        )

        # Next step placeholder

        st.info("Analyzing your statement…")

        file_obj = {
            "name": "statement.pdf",  # name of the file
            "file": uploaded_file,  # the BytesIO object
            "mime_type": "application/pdf",  # specify type
        }
        with open("survey_responses.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            csv_string = "\n".join([",".join(row) for row in reader])

        prompt = f"""
        You are a JSON API.

        Return ONLY valid JSON.
        Do NOT include markdown, comments, or extra text.
        Do NOT wrap the response in ```.

        If any field cannot be calculated, return an empty string or empty array.

        Analyze the provided bank statement data below.

        DATA:
        {csv_string}

        TASKS:
        - Calculate the total balance.
        - Identify up to 3 bad financial habits visible in the data.
        - Give a financial health score between 0 and 100.
        - Provide actionable financial advice.

        Respond strictly in JSON using this schema:
        {{
          "total_balance": string,
          "bad_habits": string[],
          "financial_score": number,
          "advice": string[]
        }}

        Respond ONLY with valid JSON and nothing else.
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=[prompt, [str(uploaded_file)]]
        )
        try:
            data = json.loads(str(response.text))
        except json.JSONDecodeError:
            st.error("Failed to parse AI response")
            st.write(response.text)
        else:
            # Display nicely in Streamlit
            st.header("🧞Guru's Analysis")
            st.subheader("💰 Total Balance")
            st.metric(label="Balance", value=data.get("total_balance", "N/A"))

            st.subheader("⚠️ Bad Financial Habits")
            bad_habits = data.get("bad_habits", [])
            if bad_habits:
                for i, habit in enumerate(bad_habits, start=1):
                    st.write(f"{i}. {habit}")
            else:
                st.write("No bad habits detected.")
            st.subheader("🧞Guru's Advice")
            st.write(data.get("advice"), [])

            st.subheader("📊 Financial Health Score")
            st.progress(int(data.get("financial_score", 0)))

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.rerun()


# ------------------ State init ------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ------------------ Router ------------------
if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.page == "survey":
        survey_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()
    else:
        survey_page()
