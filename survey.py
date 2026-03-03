import streamlit as st
import pandas as pd

st.title("Tell Us a Bit About Yourself")
with st.form("survey_form"):
    name = st.text_input("Your Name")
    age = st.number_input("Your Age", min_value=0, max_value=120, step=1)

    gender = st.radio("Gender", ["Male", "Female", "Other", "Prefer not to say"])

    satisfaction = st.slider(
        "How satisfied are you with our service?", min_value=1, max_value=5
    )

    features = st.multiselect(
        "Which features do you use?",
        ["Speed", "Design", "Ease of Use", "Support", "Pricing"],
    )

    feedback = st.text_area("Any additional feedback?")

    submitted = st.form_submit_button("Submit")

# --- Handle Submission ---
if submitted:
    if name.strip() == "":
        st.error("Please enter your name.")
    else:
        data = {
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Satisfaction": satisfaction,
            "Features Used": ", ".join(features),
            "Feedback": feedback,
        }

        df = pd.DataFrame([data])

        st.success("✅ Survey submitted successfully!")
        st.subheader("Your Response")
        st.dataframe(df)

        # Optional: save to CSV
        df.to_csv("survey_responses.csv", mode="a", header=False, index=False)
