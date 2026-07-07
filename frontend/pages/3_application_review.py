"""Application Review Page - Detailed review of a single application."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Application Review",
    page_icon="📋",
    layout="wide",
)

API_BASE_URL = "http://localhost:8000"

st.title("📋 Application Review")

if "selected_assignment_id" not in st.session_state:
    st.warning("Please select an application from the queue first")
else:
    assignment_id = st.session_state.selected_assignment_id

    try:
        # Get assignment details
        response = requests.get(f"{API_BASE_URL}/reviewer/assignments/{assignment_id}")

        if response.status_code == 200:
            assignment = response.json()

            # Get loan application details
            response = requests.get(
                f"{API_BASE_URL}/loans/status/{assignment['loan_application_id']}"
            )

            if response.status_code == 200:
                loan_app = response.json()

                # Header with status
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Applicant", loan_app.get("applicant_name", "N/A"))
                with col2:
                    st.metric("Loan Amount", f"${loan_app.get('loan_amount', 0):,.0f}")
                with col3:
                    st.metric("Status", assignment["status"])

                st.divider()

                # Personal Information
                st.subheader("📝 Personal Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {loan_app.get('applicant_email')}")
                    st.write(f"**Phone:** {loan_app.get('applicant_phone')}")
                    st.write(f"**Location:** {loan_app.get('location')}")
                with col2:
                    st.write(f"**Application ID:** {loan_app.get('application_id')}")
                    st.write(f"**Loan Type:** {loan_app.get('loan_type')}")
                    st.write(f"**Loan Term:** {loan_app.get('loan_term_months')} months")

                st.divider()

                # Financial Information
                st.subheader("💰 Financial Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Annual Income", f"${loan_app.get('annual_income', 0):,.0f}")
                with col2:
                    st.metric("Monthly Income", f"${loan_app.get('annual_income', 0) / 12:,.0f}")
                with col3:
                    st.metric("Existing Debt", f"${loan_app.get('existing_debt', 0):,.0f}")

                # Credit Profile
                col1, col2, col3 = st.columns(3)
                with col1:
                    credit_score = loan_app.get("credit_score")
                    if credit_score:
                        st.metric("Credit Score", credit_score)
                    else:
                        st.metric("Credit Score", "N/A")
                with col2:
                    st.metric("Risk Score", f"{loan_app.get('risk_score', 0):.2f}")
                with col3:
                    st.metric(
                        "Approval Probability",
                        f"{loan_app.get('approval_probability', 0):.0%}",
                    )

                st.divider()

                # Employment Information
                st.subheader("💼 Employment Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Status:** {loan_app.get('employment_status')}")
                    st.write(f"**Years Employed:** {loan_app.get('years_employed')}")
                with col2:
                    dti = (loan_app.get("existing_debt", 0) * 12) / max(
                        loan_app.get("annual_income", 1), 1
                    )
                    st.write(f"**DTI Ratio:** {dti:.1%}")

                st.divider()

                # Approval/Rejection/Re-Decision Section
                st.subheader("🎯 Decision")

                if "reviewer_id" in st.session_state and st.session_state.reviewer_id:
                    action = st.radio(
                        "Select Action",
                        ["Approve", "Reject", "Request Re-Decision"],
                        horizontal=True,
                    )

                    if action == "Approve":
                        st.success("✅ You are about to APPROVE this application")
                        approval_notes = st.text_area("Approval Notes", height=150)

                        if st.button("✅ Confirm Approval", type="primary"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/reviewer/assignments/{assignment_id}/approve",
                                    params={
                                        "review_notes": approval_notes,
                                        "reviewer_id": st.session_state.reviewer_id,
                                    },
                                )

                                if response.status_code == 200:
                                    st.success("✅ Application approved successfully!")
                                    st.balloons()

                                    result = response.json()
                                    st.json(result)
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    elif action == "Reject":
                        st.error("❌ You are about to REJECT this application")
                        rejection_reason = st.text_area("Rejection Reason", height=150)

                        if st.button("❌ Confirm Rejection", type="secondary"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/reviewer/assignments/{assignment_id}/reject",
                                    params={
                                        "rejection_reason": rejection_reason,
                                        "reviewer_id": st.session_state.reviewer_id,
                                    },
                                )

                                if response.status_code == 200:
                                    st.success("❌ Application rejected successfully!")

                                    result = response.json()
                                    st.json(result)
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    else:  # Re-Decision
                        st.warning(
                            "🔄 You are requesting a RE-DECISION from automated workflow"
                        )
                        redecision_notes = st.text_area(
                            "Why are you requesting re-decision?", height=150
                        )

                        if st.button("🔄 Request Re-Decision", type="secondary"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/reviewer/assignments/{assignment_id}/re-decision",
                                    params={
                                        "review_notes": redecision_notes,
                                        "reviewer_id": st.session_state.reviewer_id,
                                    },
                                )

                                if response.status_code == 200:
                                    st.success("🔄 Re-decision requested successfully!")

                                    result = response.json()
                                    st.json(result)
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please select a reviewer from the sidebar first")

                st.divider()

                # Review Notes History
                st.subheader("📜 Review Notes")
                if assignment.get("review_notes"):
                    st.info(f"**Notes:** {assignment['review_notes']}")
                else:
                    st.info("No review notes yet")

                if assignment.get("review_reasoning"):
                    st.warning(f"**Reasoning:** {assignment['review_reasoning']}")

                st.divider()

                # Agent Analysis
                st.subheader("🤖 Agent Analysis")
                if loan_app.get("agent_notes"):
                    st.info(loan_app["agent_notes"])
                else:
                    st.info("No agent notes")

            else:
                st.error("Could not load application details")
        else:
            st.error("Assignment not found")
    except Exception as e:
        st.error(f"Error: {str(e)}")
