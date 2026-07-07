"""Audit History Page - View audit trail for applications and reviewers."""

import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Audit History",
    page_icon="📜",
    layout="wide",
)

API_BASE_URL = "http://localhost:8000"

st.title("📜 Audit History")

tab1, tab2 = st.tabs(["Application Audit Trail", "Reviewer Activity"])

with tab1:
    st.subheader("Application Audit Trail")

    loan_id = st.number_input(
        "Enter Loan Application ID",
        min_value=1,
        key="audit_loan_id",
    )

    if st.button("Load Audit Trail"):
        try:
            response = requests.get(f"{API_BASE_URL}/reviewer/audit/{loan_id}")

            if response.status_code == 200:
                history = response.json()

                if history:
                    df = pd.DataFrame(history)

                    # Convert timestamp to datetime for better display
                    if 'action_timestamp' in df.columns:
                        df['action_timestamp'] = pd.to_datetime(df['action_timestamp'])

                    # Display as table with available columns
                    display_cols = [col for col in [
                        "action_type",
                        "action_status",
                        "reviewer_name",
                        "action_reason",
                        "action_timestamp",
                    ] if col in df.columns]

                    st.dataframe(
                        df[display_cols].rename(
                            columns={
                                "action_type": "Action",
                                "action_status": "Status",
                                "reviewer_name": "Reviewer",
                                "action_reason": "Reason",
                                "action_timestamp": "Timestamp",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Timeline view
                    st.divider()
                    st.subheader("Timeline")

                    for idx, row in df.iterrows():
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 5])
                            with col1:
                                if row["action_type"] == "APPROVE":
                                    st.success("✅")
                                elif row["action_type"] == "REJECT":
                                    st.error("❌")
                                else:
                                    st.warning("🔄")
                            with col2:
                                st.write(
                                    f"**{row['action_type']}** by {row['reviewer_name']}"
                                )
                                st.caption(str(row["action_timestamp"]))
                                if row["action_reason"]:
                                    st.write(f"Reason: {row['action_reason']}")
                else:
                    st.info("No audit history found for this application")
            else:
                st.error("Application not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Reviewer Activity")

    if "reviewer_id" not in st.session_state or not st.session_state.reviewer_id:
        st.warning("Please select a reviewer from the dashboard sidebar first")
    else:
        try:
            response = requests.get(
                f"{API_BASE_URL}/reviewer/audit/reviewer/{st.session_state.reviewer_id}"
            )

            if response.status_code == 200:
                history = response.json()

                if history:
                    df = pd.DataFrame(history)

                    # Statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        approvals = len(df[df["action_type"] == "APPROVE"])
                        st.metric("Approvals", approvals)
                    with col2:
                        rejections = len(df[df["action_type"] == "REJECT"])
                        st.metric("Rejections", rejections)
                    with col3:
                        redecisions = len(df[df["action_type"] == "RE_DECISION"])
                        st.metric("Re-Decisions", redecisions)

                    st.divider()

                    # Activity table
                    if 'action_timestamp' in df.columns:
                        df['action_timestamp'] = pd.to_datetime(df['action_timestamp'])

                    display_cols = [col for col in [
                        "action_type",
                        "action_status",
                        "action_reason",
                        "action_timestamp",
                    ] if col in df.columns]

                    st.dataframe(
                        df[display_cols].rename(
                            columns={
                                "action_type": "Action",
                                "action_status": "Status",
                                "action_reason": "Reason",
                                "action_timestamp": "Timestamp",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Timeline
                    st.divider()
                    st.subheader("Activity Timeline")

                    for idx, row in df.head(10).iterrows():
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 5])
                            with col1:
                                if row["action_type"] == "APPROVE":
                                    st.success("✅")
                                elif row["action_type"] == "REJECT":
                                    st.error("❌")
                                else:
                                    st.warning("🔄")
                            with col2:
                                st.write(f"**{row['action_type']}** - {row['action_status']}")
                                st.caption(str(row["action_timestamp"]))
                                if row["action_reason"]:
                                    st.write(f"Note: {row['action_reason']}")
                else:
                    st.info("No activity history found")
        except Exception as e:
            st.error(f"Error: {str(e)}")
