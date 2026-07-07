"""Settings page for configuration."""

import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

API_BASE_URL = "http://localhost:8000"

st.title("⚙️ Settings")

tab1, tab2 = st.tabs(["AWS Bedrock", "System"])

with tab1:
    st.subheader("AWS Bedrock Configuration")
    st.write("Configure your AWS Bedrock credentials for Claude AI decision making.")

    col1, col2 = st.columns(2)
    with col1:
        aws_access_key = st.text_input(
            "AWS Access Key ID",
            type="password",
            key="aws_access_key",
            help="Your AWS Access Key ID"
        )

    with col2:
        aws_secret_key = st.text_input(
            "AWS Secret Access Key",
            type="password",
            key="aws_secret_key",
            help="Your AWS Secret Access Key"
        )

    aws_region = st.selectbox(
        "AWS Region",
        [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ],
        key="aws_region",
        help="AWS region where Bedrock is available"
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Credentials", use_container_width=True):
            if aws_access_key and aws_secret_key:
                try:
                    # Save to environment or config
                    os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
                    os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
                    os.environ["AWS_DEFAULT_REGION"] = aws_region

                    # Send to backend to validate
                    response = requests.post(
                        f"{API_BASE_URL}/settings/bedrock-config",
                        json={
                            "aws_access_key_id": aws_access_key,
                            "aws_secret_access_key": aws_secret_key,
                            "aws_region": aws_region,
                        },
                    )

                    if response.status_code == 200:
                        st.success("✅ Bedrock credentials saved successfully!")
                        st.session_state.bedrock_configured = True
                    else:
                        st.error("❌ Failed to validate Bedrock credentials")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in all fields")

    with col2:
        if st.button("🧪 Test Connection", use_container_width=True):
            if aws_access_key and aws_secret_key:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/settings/bedrock-test",
                        json={
                            "aws_access_key_id": aws_access_key,
                            "aws_secret_access_key": aws_secret_key,
                            "aws_region": aws_region,
                        },
                    )

                    if response.status_code == 200:
                        st.success("✅ Connection test passed!")
                    else:
                        st.error("❌ Connection test failed")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in all fields")

    st.info(
        "Your AWS credentials are stored securely and only used for Claude AI decisions. "
        "Make sure your AWS account has Bedrock access enabled."
    )

with tab2:
    st.subheader("System Information")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("API Base URL", API_BASE_URL)

    with col2:
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                st.metric("API Status", "✅ Healthy")
            else:
                st.metric("API Status", "⚠️ Unhealthy")
        except:
            st.metric("API Status", "❌ Unreachable")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("📋 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")

    with col3:
        if st.button("🔐 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Session reset!")
