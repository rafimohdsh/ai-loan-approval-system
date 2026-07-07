"""Reviewer Dashboard UI - Main page for loan review operations."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

st.set_page_config(
    page_title="Reviewer Dashboard",
    page_icon="👮",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "http://localhost:8000"

st.title("👮 Loan Review Dashboard")

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        [
            "Dashboard",
            "Application Queue",
            "My Queue",
            "Approve/Reject",
            "Audit History",
            "Reviewer Management",
        ],
    )

    st.divider()

    if "reviewer_id" not in st.session_state:
        st.session_state.reviewer_id = None
        st.session_state.reviewer_name = None

    reviewer_option = st.selectbox(
        "Select Reviewer",
        ["Login as Reviewer", "Manage Reviewers"],
        key="reviewer_select",
    )

    if reviewer_option == "Login as Reviewer":
        reviewer_input = st.text_input(
            "Reviewer ID", key="reviewer_id_input", placeholder="Enter reviewer ID"
        )
        if reviewer_input:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/reviewer/profiles/{reviewer_input}"
                )
                if response.status_code == 200:
                    reviewer_data = response.json()
                    st.session_state.reviewer_id = reviewer_input
                    st.session_state.reviewer_name = reviewer_data["reviewer_name"]
                    st.success(f"Logged in as {reviewer_data['reviewer_name']}")
                else:
                    st.error("Reviewer not found")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Page 1: Dashboard
if page == "Dashboard":
    st.header("Review Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    try:
        response = requests.get(f"{API_BASE_URL}/reviewer/stats")
        if response.status_code == 200:
            stats = response.json()

            with col1:
                st.metric("Total Reviews", stats["total_reviews"])
            with col2:
                st.metric("Approved", stats["approved"])
            with col3:
                st.metric("Rejected", stats["rejected"])
            with col4:
                st.metric("Approval Rate", f"{stats['approval_rate']:.1%}")
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")

    st.divider()

    # Queue Overview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Queue Status")
        try:
            response = requests.get(f"{API_BASE_URL}/reviewer/queue")
            if response.status_code == 200:
                queue_data = response.json()

                status_counts = {}
                for item in queue_data:
                    status = item["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1

                if status_counts:
                    df_status = pd.DataFrame(
                        list(status_counts.items()), columns=["Status", "Count"]
                    )
                    st.bar_chart(df_status.set_index("Status"))
                else:
                    st.info("No applications in queue")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    with col2:
        st.subheader("Priority Distribution")
        try:
            response = requests.get(f"{API_BASE_URL}/reviewer/queue")
            if response.status_code == 200:
                queue_data = response.json()

                priority_counts = {}
                for item in queue_data:
                    priority = item["priority"]
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1

                if priority_counts:
                    df_priority = pd.DataFrame(
                        list(priority_counts.items()), columns=["Priority", "Count"]
                    )
                    st.pie_chart(df_priority.set_index("Priority"))
                else:
                    st.info("No applications in queue")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Page 2: Application Queue
elif page == "Application Queue":
    st.header("📋 Application Queue")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "PENDING", "IN_REVIEW", "RE_DECISION"],
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority", ["All", "high", "medium", "low"]
        )

    try:
        params = {}
        if status_filter != "All":
            params["status"] = status_filter
        if priority_filter != "All":
            params["priority"] = priority_filter

        response = requests.get(f"{API_BASE_URL}/reviewer/queue", params=params)

        if response.status_code == 200:
            queue_data = response.json()

            if queue_data:
                df = pd.DataFrame(queue_data)

                # Display dataframe with sortable columns
                st.dataframe(
                    df[
                        [
                            "applicant_name",
                            "loan_amount",
                            "annual_income",
                            "credit_score",
                            "status",
                            "priority",
                            "assigned_reviewer",
                            "risk_score",
                        ]
                    ].rename(
                        columns={
                            "applicant_name": "Applicant",
                            "loan_amount": "Loan Amount",
                            "annual_income": "Income",
                            "credit_score": "Credit Score",
                            "status": "Status",
                            "priority": "Priority",
                            "assigned_reviewer": "Reviewer",
                            "risk_score": "Risk Score",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                # Select application for action
                st.divider()
                st.subheader("Application Selection")
                selected_app = st.selectbox(
                    "Select application",
                    [f"{app['applicant_name']} - ${app['loan_amount']:,.0f}" for app in queue_data],
                    key="queue_selection",
                )

                if selected_app:
                    idx = [f"{app['applicant_name']} - ${app['loan_amount']:,.0f}" for app in queue_data].index(
                        selected_app
                    )
                    app = queue_data[idx]

                    if st.button("View Details"):
                        st.session_state.selected_assignment_id = app["assignment_id"]
                        st.switch_page("pages/3_application_review.py")
            else:
                st.info("No applications in queue")
    except Exception as e:
        st.error(f"Error loading queue: {str(e)}")


# Page 3: My Queue
elif page == "My Queue":
    st.header("📝 My Queue")

    if not st.session_state.reviewer_id:
        st.warning("Please select a reviewer first")
    else:
        try:
            response = requests.get(
                f"{API_BASE_URL}/reviewer/queue/reviewer/{st.session_state.reviewer_id}"
            )

            if response.status_code == 200:
                queue_data = response.json()

                if queue_data:
                    df = pd.DataFrame(queue_data)

                    st.dataframe(
                        df[
                            [
                                "applicant_name",
                                "loan_amount",
                                "annual_income",
                                "credit_score",
                                "status",
                                "risk_score",
                            ]
                        ].rename(
                            columns={
                                "applicant_name": "Applicant",
                                "loan_amount": "Loan Amount",
                                "annual_income": "Income",
                                "credit_score": "Credit Score",
                                "status": "Status",
                                "risk_score": "Risk Score",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.divider()
                    selected_app = st.selectbox(
                        "Select application to review",
                        [f"{app['applicant_name']} - {app['status']}" for app in queue_data],
                        key="my_queue_selection",
                    )

                    if selected_app:
                        idx = [f"{app['applicant_name']} - {app['status']}" for app in queue_data].index(
                            selected_app
                        )
                        app = queue_data[idx]

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("👀 View & Review"):
                                st.session_state.selected_assignment_id = app["assignment_id"]
                                st.switch_page("pages/3_application_review.py")
                        with col2:
                            if st.button("📜 View History"):
                                st.session_state.selected_loan_id = app["loan_application_id"]
                                st.switch_page("pages/4_audit_history.py")
                else:
                    st.info("No applications assigned to you")
        except Exception as e:
            st.error(f"Error loading your queue: {str(e)}")


# Page 4: Approve/Reject
elif page == "Approve/Reject":
    st.header("✅/❌ Approve or Reject Application")

    if not st.session_state.reviewer_id:
        st.warning("Please select a reviewer first")
    else:
        assignment_id = st.text_input("Assignment ID", placeholder="Enter assignment ID")

        if assignment_id:
            try:
                response = requests.get(f"{API_BASE_URL}/reviewer/assignments/{assignment_id}")

                if response.status_code == 200:
                    assignment = response.json()

                    st.info(f"Reviewing: Assignment {assignment['assignment_id']}")
                    st.write(f"Status: {assignment['status']}")
                    st.write(f"Priority: {assignment['priority']}")

                    st.divider()

                    action = st.radio("Action", ["Approve", "Reject", "Request Re-Decision"])

                    if action == "Approve":
                        review_notes = st.text_area("Approval Notes", height=200)

                        if st.button("✅ Approve Application"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/reviewer/assignments/{assignment_id}/approve",
                                    params={
                                        "review_notes": review_notes,
                                        "reviewer_id": st.session_state.reviewer_id,
                                    },
                                )

                                if response.status_code == 200:
                                    st.success("✅ Application approved successfully!")
                                    st.json(response.json())
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    elif action == "Reject":
                        rejection_reason = st.text_area("Rejection Reason", height=200)

                        if st.button("❌ Reject Application"):
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
                                    st.json(response.json())
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    else:  # Re-Decision
                        review_notes = st.text_area(
                            "Re-Decision Notes (explain why)", height=200
                        )

                        if st.button("🔄 Request Re-Decision"):
                            try:
                                response = requests.post(
                                    f"{API_BASE_URL}/reviewer/assignments/{assignment_id}/re-decision",
                                    params={
                                        "review_notes": review_notes,
                                        "reviewer_id": st.session_state.reviewer_id,
                                    },
                                )

                                if response.status_code == 200:
                                    st.success(
                                        "🔄 Re-decision requested successfully!"
                                    )
                                    st.json(response.json())
                                else:
                                    st.error(f"Error: {response.text}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                else:
                    st.error("Assignment not found")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Page 5: Audit History
elif page == "Audit History":
    st.header("📜 Audit History")

    audit_type = st.radio("View History For", ["Application", "Reviewer"])

    if audit_type == "Application":
        loan_id = st.number_input("Loan Application ID", min_value=1)

        if st.button("Load History"):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/reviewer/audit/{loan_id}"
                )

                if response.status_code == 200:
                    history = response.json()

                    if history:
                        df = pd.DataFrame(history)

                        st.dataframe(
                            df[
                                [
                                    "action_type",
                                    "action_status",
                                    "reviewer_name",
                                    "action_reason",
                                    "action_timestamp",
                                ]
                            ].rename(
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
                    else:
                        st.info("No history found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        if not st.session_state.reviewer_id:
            st.warning("Please select a reviewer first")
        else:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/reviewer/audit/reviewer/{st.session_state.reviewer_id}"
                )

                if response.status_code == 200:
                    history = response.json()

                    if history:
                        df = pd.DataFrame(history)

                        st.dataframe(
                            df[
                                [
                                    "action_type",
                                    "action_status",
                                    "action_reason",
                                    "action_timestamp",
                                ]
                            ].rename(
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
                    else:
                        st.info("No history found")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Page 6: Reviewer Management
elif page == "Reviewer Management":
    st.header("👥 Reviewer Management")

    tab1, tab2 = st.tabs(["List Reviewers", "Add Reviewer"])

    with tab1:
        st.subheader("Active Reviewers")

        try:
            response = requests.get(f"{API_BASE_URL}/reviewer/profiles")

            if response.status_code == 200:
                reviewers = response.json()

                if reviewers:
                    df = pd.DataFrame(reviewers)

                    st.dataframe(
                        df[
                            [
                                "reviewer_name",
                                "email",
                                "department",
                                "role",
                                "total_reviews",
                                "approved_count",
                                "rejected_count",
                            ]
                        ].rename(
                            columns={
                                "reviewer_name": "Name",
                                "email": "Email",
                                "department": "Department",
                                "role": "Role",
                                "total_reviews": "Total Reviews",
                                "approved_count": "Approved",
                                "rejected_count": "Rejected",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No reviewers found")
        except Exception as e:
            st.error(f"Error loading reviewers: {str(e)}")

    with tab2:
        st.subheader("Add New Reviewer")

        reviewer_name = st.text_input("Reviewer Name")
        reviewer_email = st.text_input("Email")
        reviewer_phone = st.text_input("Phone (optional)")
        reviewer_department = st.text_input("Department")
        reviewer_role = st.selectbox("Role", ["REVIEWER", "SENIOR_REVIEWER", "MANAGER"])

        if st.button("➕ Add Reviewer"):
            if reviewer_name and reviewer_email:
                try:
                    payload = {
                        "reviewer_name": reviewer_name,
                        "email": reviewer_email,
                        "phone": reviewer_phone if reviewer_phone else None,
                        "department": reviewer_department,
                        "role": reviewer_role,
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/reviewer/profiles", json=payload
                    )

                    if response.status_code == 201:
                        reviewer = response.json()
                        st.success(
                            f"✅ Reviewer created: {reviewer['reviewer_id']}"
                        )
                        st.json(reviewer)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in all required fields")
