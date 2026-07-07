import streamlit as st

st.set_page_config(
    page_title="Agentic Loan Approval System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add title
st.title("🏦 Agentic Loan Approval System")
st.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate to:",
    ["Dashboard", "Submit Application", "View Applications", "Application Details", "Analytics"]
)

if page == "Dashboard":
    st.subheader("Dashboard")
    st.info("Select a page from the sidebar to get started")

elif page == "Submit Application":
    st.subheader("Submit Loan Application")
    st.write("Application form will be loaded here")

elif page == "View Applications":
    st.subheader("View Applications")
    st.write("List of applications will be displayed here")

elif page == "Application Details":
    st.subheader("Application Details")
    st.write("Application details and agent analysis will be shown here")

elif page == "Analytics":
    st.subheader("Analytics & Statistics")
    st.write("Analytics dashboard will be displayed here")

st.sidebar.markdown("---")
st.sidebar.info("Powered by FastAPI, LangGraph & AWS Bedrock Claude Haiku")
