"""Streamlit UI for Loan Approval System."""

import streamlit as st
import requests
import os
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Loan Approval System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { max-width: 1200px; margin: 0 auto; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 16px; }
    .success-box { padding: 20px; background-color: #d4edda; border-radius: 5px; border-left: 4px solid #28a745; }
    .error-box { padding: 20px; background-color: #f8d7da; border-radius: 5px; border-left: 4px solid #dc3545; }
    .info-box { padding: 20px; background-color: #d1ecf1; border-radius: 5px; border-left: 4px solid #17a2b8; }
    </style>
    """, unsafe_allow_html=True)

def apply_loan_form():
    """Form for applying for a loan."""
    st.header("💳 Apply for Loan")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        applicant_name = st.text_input("Full Name", placeholder="John Smith")
        applicant_email = st.text_input("Email", placeholder="john@example.com")
        applicant_phone = st.text_input("Phone", placeholder="+1-555-1234")
        location = st.text_input("Location (City, State)", placeholder="San Francisco, CA")

    with col2:
        st.subheader("Employment Information")
        employment_status = st.selectbox(
            "Employment Status",
            ["Permanent Full-time", "Permanent Part-time", "Contract", "Self-employed", "Other"]
        )
        years_employed = st.number_input("Years Employed", min_value=0.0, step=0.5)
        annual_income = st.number_input("Annual Income ($)", min_value=0, step=1000)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Loan Details")
        loan_amount = st.number_input("Loan Amount ($)", min_value=1000, step=1000)
        loan_type = st.selectbox("Loan Type", ["Personal", "Home", "Auto", "Business", "Other"])
        loan_term_months = st.selectbox("Loan Term (Months)", [12, 24, 36, 48, 60, 84, 120])

    with col4:
        st.subheader("Financial Information")
        credit_score = st.number_input(
            "Credit Score (Optional)",
            min_value=0,
            max_value=850,
            value=0,
            help="Leave 0 if not available"
        )
        existing_debt = st.number_input("Existing Monthly Debt ($)", min_value=0, step=100)

    st.markdown("---")
    submitted = st.button("📤 Submit Application", use_container_width=True, key="submit_loan")

    if submitted:
        if not applicant_name or not applicant_email or not applicant_phone or not location:
            st.error("❌ Please fill in all personal information fields")
            return

        if annual_income <= 0 or loan_amount <= 0:
            st.error("❌ Income and loan amount must be greater than 0")
            return

        with st.spinner("📝 Processing application..."):
            try:
                payload = {
                    "applicant_name": applicant_name,
                    "applicant_email": applicant_email,
                    "applicant_phone": applicant_phone,
                    "location": location,
                    "loan_amount": float(loan_amount),
                    "loan_type": loan_type,
                    "loan_term_months": int(loan_term_months),
                    "annual_income": float(annual_income),
                    "employment_status": employment_status,
                    "years_employed": float(years_employed),
                    "credit_score": int(credit_score) if credit_score > 0 else None,
                    "existing_debt": float(existing_debt)
                }

                response = requests.post(f"{API_BASE_URL}/loans/apply", json=payload)

                if response.status_code == 201:
                    result = response.json()
                    app_id = result["application_id"]

                    st.success("✅ Application submitted successfully!")
                    st.markdown(f"""
                        <div class="success-box">
                        <h3>Application Created</h3>
                        <p><strong>Application ID:</strong> <code>{app_id}</code></p>
                        <p><strong>Status:</strong> {result['status'].upper()}</p>
                        <p><strong>Submitted:</strong> {result['created_at']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.info("ℹ️ Use the 'Check Status' tab to track your application.")
                    st.write("")
                    st.code(f"Application ID: {app_id}", language="text")

                elif response.status_code == 422:
                    st.error("❌ Validation error. Please check your input.")
                    st.write(response.json())

                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Is the server running?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def check_status_page():
    """Page for checking loan status."""
    st.header("📋 Check Application Status")

    col1, col2 = st.columns([3, 1])

    with col1:
        application_id = st.text_input(
            "Enter Application ID",
            placeholder="e.g., a1b2c3d4-e5f6-7890",
            key="app_id_input"
        )

    with col2:
        st.write("")  # Spacing
        check_button = st.button("🔍 Check Status", use_container_width=True)

    if check_button and application_id:
        with st.spinner("⏳ Fetching application details..."):
            try:
                response = requests.get(f"{API_BASE_URL}/loans/status/{application_id}")

                if response.status_code == 200:
                    app = response.json()

                    # Status indicator
                    status_colors = {
                        "pending": "🟡",
                        "under_review": "🔵",
                        "approved": "🟢",
                        "rejected": "🔴",
                        "withdrawn": "⚫"
                    }
                    status_icon = status_colors.get(app["status"], "❓")

                    st.markdown(f"### {status_icon} Status: {app['status'].upper()}")
                    st.markdown("---")

                    # Applicant Info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Applicant", app["applicant_name"])
                    with col2:
                        st.metric("Email", app["applicant_email"])
                    with col3:
                        st.metric("Phone", app["applicant_phone"])

                    # Loan Details
                    st.subheader("💰 Loan Details")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Loan Amount", f"${app['loan_amount']:,.0f}")
                    with col2:
                        st.metric("Type", app["loan_type"])
                    with col3:
                        st.metric("Term", f"{app['loan_term_months']} months")
                    with col4:
                        monthly_payment = (app["loan_amount"] / app["loan_term_months"])
                        st.metric("Est. Monthly", f"${monthly_payment:,.0f}")

                    # Financial Info
                    st.subheader("📊 Financial Information")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Annual Income", f"${app['annual_income']:,.0f}")
                    with col2:
                        st.metric("Employment", app["employment_status"])
                    with col3:
                        st.metric("Years Employed", app["years_employed"])
                    with col4:
                        st.metric("Credit Score", app["credit_score"] if app["credit_score"] else "N/A")

                    # Risk & Decision Info
                    if app.get("risk_score") is not None or app.get("approval_probability") is not None:
                        st.subheader("🎲 Assessment Results")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            risk_score = app.get("risk_score", "N/A")
                            st.metric("Risk Score", f"{risk_score}" if risk_score != "N/A" else risk_score)
                        with col2:
                            prob = app.get("approval_probability", "N/A")
                            if prob != "N/A":
                                st.metric("Approval Probability", f"{prob*100:.1f}%")
                            else:
                                st.metric("Approval Probability", prob)
                        with col3:
                            st.metric("Status", app["status"].upper())

                    # Timestamps
                    st.subheader("⏰ Timeline")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.text(f"Created: {app['created_at']}")
                    with col2:
                        st.text(f"Updated: {app['updated_at']}")
                    with col3:
                        if app.get("approval_reason"):
                            st.text(f"✅ Approved: Yes")
                        elif app.get("rejection_reason"):
                            st.text(f"❌ Rejected: Yes")
                        else:
                            st.text("⏳ Pending Decision")

                elif response.status_code == 404:
                    st.error("❌ Application not found. Please check the Application ID.")
                else:
                    st.error(f"❌ Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Is the server running?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    elif check_button and not application_id:
        st.warning("⚠️ Please enter an Application ID")


def dashboard_page():
    """Dashboard page with statistics."""
    st.header("📊 Dashboard")

    try:
        response = requests.get(f"{API_BASE_URL}/loans/status")
        if response.status_code == 200:
            data = response.json()

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Applications", len(data) if isinstance(data, list) else 0)
            with col2:
                approved = sum(1 for app in (data if isinstance(data, list) else []) if app.get("status") == "APPROVED")
                st.metric("Approved", approved)
            with col3:
                rejected = sum(1 for app in (data if isinstance(data, list) else []) if app.get("status") == "REJECTED")
                st.metric("Rejected", rejected)
            with col4:
                pending = sum(1 for app in (data if isinstance(data, list) else []) if app.get("status") == "PENDING")
                st.metric("Pending", pending)

            st.markdown("---")
            st.subheader("📋 Recent Applications")
            if isinstance(data, list) and data:
                for app in data[:10]:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**{app.get('applicant_name', 'N/A')}**")
                    with col2:
                        st.write(f"${app.get('loan_amount', 0):,.0f}")
                    with col3:
                        st.write(f"{app.get('status', 'N/A')}")
        else:
            st.info("📊 Dashboard - No data available yet")
    except Exception as e:
        st.info("📊 Dashboard - Real-time loan application overview")


def show_decision_page():
    """Page for showing loan decision."""
    st.header("🎯 Loan Decision")

    col1, col2 = st.columns([3, 1])

    with col1:
        application_id = st.text_input(
            "Enter Application ID to view decision",
            placeholder="e.g., a1b2c3d4-e5f6-7890",
            key="decision_app_id"
        )

    with col2:
        st.write("")  # Spacing
        get_decision = st.button("📄 View Decision", use_container_width=True)

    if get_decision and application_id:
        with st.spinner("⏳ Fetching decision details..."):
            try:
                response = requests.get(f"{API_BASE_URL}/loans/status/{application_id}")

                if response.status_code == 200:
                    app = response.json()

                    # Decision Display
                    if app["status"] == "approved":
                        st.markdown("""
                            <div style="padding: 30px; background-color: #d4edda; border-radius: 10px;
                                        border-left: 6px solid #28a745; text-align: center;">
                            <h1 style="color: #28a745; margin: 0;">✅ APPROVED</h1>
                            <h3 style="color: #155724; margin-top: 10px;">Your loan has been approved!</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        st.success(f"Loan Amount: ${app['loan_amount']:,.0f}")

                    elif app["status"] == "rejected":
                        st.markdown("""
                            <div style="padding: 30px; background-color: #f8d7da; border-radius: 10px;
                                        border-left: 6px solid #dc3545; text-align: center;">
                            <h1 style="color: #dc3545; margin: 0;">❌ REJECTED</h1>
                            <h3 style="color: #721c24; margin-top: 10px;">Unfortunately, your application was rejected.</h3>
                            </div>
                            """, unsafe_allow_html=True)

                    elif app["status"] == "pending":
                        st.markdown("""
                            <div style="padding: 30px; background-color: #fff3cd; border-radius: 10px;
                                        border-left: 6px solid #ffc107; text-align: center;">
                            <h1 style="color: #856404; margin: 0;">⏳ PENDING</h1>
                            <h3 style="color: #856404; margin-top: 10px;">Your application is still being reviewed.</h3>
                            </div>
                            """, unsafe_allow_html=True)

                    elif app["status"] == "under_review":
                        st.markdown("""
                            <div style="padding: 30px; background-color: #d1ecf1; border-radius: 10px;
                                        border-left: 6px solid #17a2b8; text-align: center;">
                            <h1 style="color: #0c5460; margin: 0;">🔍 UNDER REVIEW</h1>
                            <h3 style="color: #0c5460; margin-top: 10px;">Our team is currently reviewing your application.</h3>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("---")

                    # Decision Details
                    st.subheader("📋 Decision Details")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Application ID:** {app['application_id']}")
                        st.write(f"**Applicant:** {app['applicant_name']}")
                        st.write(f"**Loan Amount:** ${app['loan_amount']:,.0f}")
                    with col2:
                        st.write(f"**Status:** {app['status'].upper()}")
                        st.write(f"**Decision Date:** {app['updated_at']}")
                        st.write(f"**Submitted:** {app['created_at']}")

                    # Assessment Details
                    if app.get("risk_score") is not None:
                        st.subheader("📊 Assessment Metrics")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Risk Score", f"{app['risk_score']:.1f}/100")
                        with col2:
                            if app.get("approval_probability") is not None:
                                st.metric("Approval Probability", f"{app['approval_probability']*100:.0f}%")
                        with col3:
                            dti = (app.get("existing_debt", 0) / (app["annual_income"] / 12)) if app["annual_income"] > 0 else 0
                            st.metric("Debt-to-Income", f"{dti*100:.1f}%")

                    # Reasons
                    if app.get("approval_reason"):
                        st.info(f"✅ Reason: {app['approval_reason']}")
                    if app.get("rejection_reason"):
                        st.error(f"❌ Reason: {app['rejection_reason']}")
                    if app.get("agent_notes"):
                        st.warning(f"📝 Notes: {app['agent_notes']}")

                elif response.status_code == 404:
                    st.error("❌ Application not found. Please check the Application ID.")
                else:
                    st.error(f"❌ Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Is the server running?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    elif get_decision and not application_id:
        st.warning("⚠️ Please enter an Application ID")


def main():
    """Main app."""
    st.title("🏦 Loan Approval System")
    st.markdown("Fast, secure, and intelligent loan processing")

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📍 Navigation")
        page = st.radio(
            "Select an option:",
            ["📊 Dashboard", "💳 Apply Loan", "📋 Check Status", "🎯 View Decision"],
            label_visibility="collapsed"
        )

    # Route to selected page
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "💳 Apply Loan":
        apply_loan_form()
    elif page == "📋 Check Status":
        check_status_page()
    elif page == "🎯 View Decision":
        show_decision_page()

    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🔐 Secure & Encrypted")
    with col2:
        st.caption("⚡ Instant Processing")
    with col3:
        st.caption("📊 AI-Powered Decisions")


if __name__ == "__main__":
    main()
