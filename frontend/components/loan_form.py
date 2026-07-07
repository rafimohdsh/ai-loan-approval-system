import streamlit as st


def render_loan_application_form():
    """Render the loan application form."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Applicant Information")
        applicant_name = st.text_input("Full Name")
        applicant_email = st.text_input("Email Address")
        applicant_phone = st.text_input("Phone Number")

    with col2:
        st.subheader("Loan Details")
        loan_type = st.selectbox("Loan Type", ["Personal", "Home", "Auto", "Business"])
        loan_amount = st.number_input("Loan Amount ($)", min_value=1000.0)
        loan_term = st.slider("Loan Term (Months)", min_value=6, max_value=360, value=60)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Financial Information")
        annual_income = st.number_input("Annual Income ($)", min_value=0.0)
        existing_debt = st.number_input("Existing Debt ($)", min_value=0.0)

    with col4:
        st.subheader("Employment Details")
        employment_status = st.selectbox(
            "Employment Status",
            ["Full-time Employed", "Part-time Employed", "Self-Employed", "Retired"]
        )
        years_employed = st.number_input("Years Employed", min_value=0.0)

    st.divider()

    st.subheader("Additional Information")
    credit_score = st.number_input("Credit Score (Optional)", min_value=300, max_value=850, value=None)

    return {
        "applicant_name": applicant_name,
        "applicant_email": applicant_email,
        "applicant_phone": applicant_phone,
        "loan_type": loan_type,
        "loan_amount": loan_amount,
        "loan_term_months": loan_term,
        "annual_income": annual_income,
        "existing_debt": existing_debt,
        "employment_status": employment_status,
        "years_employed": years_employed,
        "credit_score": credit_score
    }
