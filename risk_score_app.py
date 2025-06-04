# app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DataPulse_API_KEY = os.getenv("DataPulse_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# --- App UI ---
st.title("🏦 Kenya Loan Eligibility Checker")
st.markdown("""
This app checks loan eligibility using DataPulse's **Kenya Risk Score API**.
""")

# User input form
with st.form("loan_form"):
    user_id = st.text_input("User ID", placeholder="e.g., CUST-12345 , to be provided")
    loan_amount = st.number_input("Loan Amount (KES)", min_value=1000, value=50000)
    submitted = st.form_submit_button("Check Eligibility")

# --- API Integration ---
if submitted:
    if not user_id:
        st.error("Please enter a User ID!")
    else:
        with st.spinner("Checking risk score..."):
            try:
                # Step 1: Call DataPulse API
                response = requests.get(
                    "https://api.DataPulse.com/v10/kenya-risk-score-beta",
                    params={"user_id": user_id},
                    headers={"Authorization": f"Bearer {DataPulse_API_KEY}"}
                )
                response.raise_for_status()
                risk_data = response.json()

                # Step 2: Decision Logic
                risk_score = risk_data.get("risk_score", 0)
                decision = "Rejected"
                reason = "High risk"

                if risk_score >= 700:
                    decision = "Approved"
                    reason = "Low risk"
                elif 500 <= risk_score < 700 and loan_amount <= 50000:
                    decision = "Approved"
                    reason = "Medium risk (limited amount)"

                # Step 3: Display Results
                st.subheader("📊 Results")
                col1, col2 = st.columns(2)
                col1.metric("Risk Score", risk_score)
                col2.metric("Decision", decision)

                st.info(f"**Reason:** {reason}")

                # Step 4: Send Alert if Rejected (Slack/Email)
                if decision == "Rejected" and SLACK_WEBHOOK_URL:
                    alert_data = {
                        "text": f"🚨 Loan Rejected\nUser: {user_id}\nScore: {risk_score}\nAmount: KES {loan_amount}"
                    }
                    requests.post(SLACK_WEBHOOK_URL, json=alert_data)

            except Exception as e:
                st.error(f"API Error: {str(e)}")

# --- Database Logging (Optional) ---
if submitted and 'risk_score' in locals():
    st.divider()
    st.write("### 📝 Audit Log")
    st.json({
        "user_id": user_id,
        "risk_score": risk_score,
        "loan_amount": loan_amount,
        "decision": decision,
        "timestamp": st.session_state.get("timestamp")
    })
