import streamlit as st
from models.excel_export import build_excel_model
from models.ai_memo import generate_investment_memo
import plotly.graph_objects as go
from models.document_extraction import extract_document_text
from models.om_content import generate_om_narrative
from models.om_builder import build_offering_memorandum
try:
    from docx2pdf import convert
    PDF_CONVERSION_AVAILABLE = True
except ImportError:
    PDF_CONVERSION_AVAILABLE = False
import tempfile
import os

st.set_page_config(
    page_title="CRE Intelligence",
    page_icon="🏢",
    layout="wide",
)

st.markdown("""
<style>
.cre-header-wrapper {
    position: relative;
    text-align: center;
    padding: 2.5rem 1rem 2rem 1rem;
}
.cre-version-label {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    font-size: 0.7rem;
    color: #9ca3af;
    font-family: "Helvetica Neue", Arial, sans-serif;
    letter-spacing: 0.05em;
}
.cre-title {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 2.75rem;
    font-weight: 700;
    color: #1a2332;
    letter-spacing: -0.02em;
    margin: 0;
}
.cre-subtitle {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: #4b5563;
    letter-spacing: 0.01em;
    margin-top: 0.4rem;
}
.cre-tagline {
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 0.8rem;
    font-weight: 400;
    color: #9ca3af;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.6rem;
}

/* Page background */
[data-testid="stAppViewContainer"] {
    background-color: #F7F8FA;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Card styling for bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
    margin-bottom: 1.5rem;
}

/* Section headings */
h3 {
    color: #1A2332;
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 1rem;
}

/* Explicitly keep input labels dark and visible */
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] p {
    color: #1A2332 !important;
    font-weight: 500;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #FAFBFC;
    border-radius: 8px;
    padding: 0.75rem;
}
[data-testid="stMetricLabel"] {
    color: #6B7280;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="stMetricValue"] {
    color: #1A2332;
    font-weight: 600;
}

/* Buttons only — target the actual <button> element, nothing else */
button[kind="primary"],
button[kind="secondary"],
button[kind="formSubmit"] {
    background-color: #1A2332 !important;
    color: #FFFFFF !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 500 !important;
}

hr {
    border-color: #E5E7EB;
}
</style>

<div class="cre-header-wrapper">
    <div class="cre-version-label">Version 1.0</div>
    <div class="cre-title">CRE Intelligence</div>
    <div class="cre-subtitle">AI-Powered Commercial Real Estate Investment Platform</div>
    <div class="cre-tagline">Professional Underwriting &bull; Investment Analysis &bull; AI Reporting</div>
</div>
""", unsafe_allow_html=True)

st.divider()

with st.form("financial_model_form"):

    st.subheader("1. Property Information")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            property_name = st.text_input("Property Name")
            property_type = st.selectbox(
                "Property Type",
                ["Multifamily", "Office", "Retail", "Industrial", "Mixed-Use", "Other"],
            )
            property_address = st.text_input("Property Address")
            city = st.text_input("City")
            state = st.text_input("State")
            acquisition_date = st.date_input("Acquisition Date")
        with col2:
            purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, step=10000.0, value=1000000.0)
            year_built = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=2000)
            square_feet = st.number_input("Square Feet", min_value=0.0, step=1000.0, value=50000.0)
            occupancy = st.number_input("Occupancy (%)", min_value=0.0, max_value=100.0, step=1.0, value=95.0)
            vacancy_rate = st.number_input("Vacancy Rate (%)", min_value=0.0, max_value=100.0, step=1.0, value=5.0)
            market_rent_growth = st.number_input("Market Rent Growth (%)", min_value=0.0, max_value=20.0, step=0.1, value=3.0)
            expense_growth = st.number_input("Expense Growth (%)", min_value=0.0, max_value=20.0, step=0.1, value=2.5)

    st.subheader("2. Financing")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            loan_to_value = st.number_input("Loan-to-Value (%)", min_value=0.0, max_value=100.0, step=1.0, value=70.0)
        with col2:
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=6.5)
        with col3:
            amortization_period = st.number_input("Loan Amortization Period (years)", min_value=1, step=1, value=30)

    st.subheader("3. Operating Assumptions")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            annual_noi = st.number_input("Annual NOI ($)", min_value=0.0, step=1000.0, value=120000.0)
            hold_period = st.number_input("Hold Period (years)", min_value=1, step=1, value=5)
        with col2:
            noi_growth_rate = st.number_input("Annual NOI Growth Rate (%)", min_value=0.0, max_value=20.0, step=0.1, value=3.0)
            exit_cap_rate = st.number_input("Exit Cap Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=6.0)

    submitted = st.form_submit_button("Generate Financial Model", use_container_width=True)
    st.subheader("Supporting Documents (Optional)")
with st.container(border=True):
    st.markdown(
        '<p style="color:#6B7280; font-style: italic;">'
        "Uploaded documents are analyzed and used to enrich the AI-generated "
        "investment memorandum and offering memorandum.</p>",
        unsafe_allow_html=True,
    )

    def render_document_slot(slot_key, label, description, accepted_types):
        counter_key = f"{slot_key}_counter"
        data_key = f"{slot_key}_data"

        if counter_key not in st.session_state:
            st.session_state[counter_key] = 0
        if data_key not in st.session_state:
            st.session_state[data_key] = None

        st.markdown(f"**{label}**")
        st.caption(description)

        if st.session_state[data_key] is not None:
            st.success(f"Uploaded: {st.session_state[data_key]['filename']}")
            if st.button("Remove", key=f"{slot_key}_remove_btn"):
                st.session_state[data_key] = None
                st.session_state[counter_key] += 1
                st.rerun()
        else:
            uploaded_file = st.file_uploader(
                label,
                type=accepted_types,
                key=f"{slot_key}_uploader_{st.session_state[counter_key]}",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                extracted_text = extract_document_text(uploaded_file)
                st.session_state[data_key] = {
                    "filename": uploaded_file.name,
                    "text": extracted_text,
                }
                st.rerun()

        st.divider()

    render_document_slot(
        "rent_roll",
        "Rent Roll",
        "Upload the current tenant rent roll.",
        ["xlsx", "xls", "csv"],
    )
    render_document_slot(
        "t12",
        "T-12 Operating Statement",
        "Upload the property's trailing twelve-month operating statement.",
        ["xlsx", "xls", "csv", "pdf"],
    )
    render_document_slot(
        "lease_summary",
        "Lease Summary / Lease Abstract",
        "Upload lease summaries or lease abstracts.",
        ["pdf", "docx"],
    )
    render_document_slot(
        "property_info_sheet",
        "Property Information Sheet",
        "Upload any property information sheet or marketing package containing building specifications.",
        ["pdf", "docx"],
    )
    st.subheader("Property Photos (Optional)")
with st.container(border=True):
    uploaded_photos = st.file_uploader(
        "Upload property photos to include in the Offering Memorandum",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )
    if uploaded_photos:
        st.session_state.property_photos = [p.getvalue() for p in uploaded_photos]
        
if submitted:
    st.session_state.model_generated = True

if st.session_state.get("model_generated"):
    if not property_name:
        st.warning("Please enter a property name.")
        st.stop()

    loan_amount = purchase_price * (loan_to_value / 100)
    initial_equity = purchase_price - loan_amount

    annual_rate = interest_rate / 100
    if annual_rate > 0:
        annual_debt_service = loan_amount * annual_rate / (1 - (1 + annual_rate) ** (-amortization_period))
    else:
        annual_debt_service = loan_amount / amortization_period

    remaining_balance = loan_amount
    for _ in range(int(hold_period)):
        interest_payment = remaining_balance * annual_rate
        principal_payment = annual_debt_service - interest_payment
        remaining_balance = remaining_balance - principal_payment

    total_cash_flow_over_hold = 0
    yearly_data = []
    for year in range(1, int(hold_period) + 1):
        year_noi = annual_noi * ((1 + (noi_growth_rate / 100)) ** (year - 1))
        year_cash_flow = year_noi - annual_debt_service
        total_cash_flow_over_hold = total_cash_flow_over_hold + year_cash_flow
        yearly_data.append({
            "Year": year,
            "NOI": year_noi,
            "Debt Service": annual_debt_service,
            "Cash Flow": year_cash_flow,
        })
    total_cash_flow = annual_noi - annual_debt_service

    projected_exit_noi = annual_noi * ((1 + (noi_growth_rate / 100)) ** hold_period)
    exit_value = projected_exit_noi / (exit_cap_rate / 100)
    net_sale_proceeds = exit_value - remaining_balance
    total_equity_value = initial_equity + total_cash_flow_over_hold + net_sale_proceeds
    equity_multiple = total_equity_value / initial_equity if initial_equity > 0 else 0
    purchase_cap_rate = annual_noi / purchase_price if purchase_price > 0 else 0
    cash_on_cash_return = total_cash_flow / initial_equity if initial_equity > 0 else 0
    dscr = annual_noi / annual_debt_service if annual_debt_service > 0 else 0
    debt_yield = annual_noi / loan_amount if loan_amount > 0 else 0
    loan_constant = annual_debt_service / loan_amount if loan_amount > 0 else 0

    st.success(f"Financial model generated for {property_name}.")

    st.subheader("4. Financial Dashboard")
    with st.container(border=True):
        row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
        with row1_col1:
            st.metric("Purchase Price", f"${purchase_price:,.0f}")
        with row1_col2:
            st.metric("Loan Amount", f"${loan_amount:,.0f}")
        with row1_col3:
            st.metric("Initial Equity", f"${initial_equity:,.0f}")
        with row1_col4:
            st.metric("Estimated Exit Value", f"${exit_value:,.0f}")

        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
        with row2_col1:
            st.metric("Purchase Cap Rate", f"{purchase_cap_rate:.2%}")
        with row2_col2:
            st.metric("Cash-on-Cash Return", f"{cash_on_cash_return:.2%}")
        with row2_col3:
            st.metric("Debt Yield", f"{debt_yield:.2%}")
        with row2_col4:
            st.metric("Loan Constant", f"{loan_constant:.2%}")

        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            st.metric("DSCR", f"{dscr:.2f}x")
        with row3_col2:
            st.metric("Equity Multiple", f"{equity_multiple:.2f}x")

        st.divider()
        st.write(f"- Total cash flow over {hold_period} years: **${total_cash_flow_over_hold:,.0f}**")
        st.write(f"- Net sale proceeds after debt payoff: **${net_sale_proceeds:,.0f}**")
        st.write(f"- Total equity value at exit: **${total_equity_value:,.0f}**")
        st.write(f"- Annual Debt Service: **${annual_debt_service:,.0f}**")
        st.write(f"- Remaining Loan Balance at Exit: **${remaining_balance:,.0f}**")

    st.subheader("5. Cash Flow Statement")
    with st.container(border=True):
        st.dataframe(
            yearly_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "NOI": st.column_config.NumberColumn(format="$%.0f"),
                "Debt Service": st.column_config.NumberColumn(format="$%.0f"),
                "Cash Flow": st.column_config.NumberColumn(format="$%.0f"),
            },
        )

    st.subheader("6. Financial Performance")
    st.markdown(
        '<p style="color:#6B7280; margin-top:-0.75rem; margin-bottom:1rem;">'
        "Projected annual cash flow based on the underwriting assumptions.</p>",
        unsafe_allow_html=True,
    )

    years = [row["Year"] for row in yearly_data]
    cash_flows = [row["Cash Flow"] for row in yearly_data]

    chart_layout_settings = dict(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Helvetica Neue, Arial, sans-serif", color="#1A2332", size=13),
        margin=dict(l=60, r=30, t=50, b=50),
        xaxis=dict(
            title="Year",
            showgrid=False,
            tickmode="linear",
            dtick=1,
        ),
        yaxis=dict(
            title="Cash Flow ($)",
            showgrid=True,
            gridcolor="#E5E7EB",
            gridwidth=1,
            zeroline=False,
            tickprefix="$",
            tickformat=",.0f",
        ),
    )

    with st.container(border=True):
        bar_fig = go.Figure(
            data=[go.Bar(x=years, y=cash_flows, marker_color="#1A2332")]
        )
        bar_fig.update_layout(
            title="Annual Cash Flow",
            **chart_layout_settings,
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    with st.container(border=True):
        line_fig = go.Figure(
            data=[
                go.Scatter(
                    x=years,
                    y=cash_flows,
                    mode="lines+markers",
                    line=dict(color="#1A2332", width=2.5),
                    marker=dict(color="#1A2332", size=7),
                )
            ]
        )
        line_fig.update_layout(
            title="Annual Cash Flow Trend",
            **chart_layout_settings,
        )
        st.plotly_chart(line_fig, use_container_width=True)

    st.subheader("7. AI Investment Memo")
    with st.container(border=True):
        property_data = {
            "property": {
                "name": property_name,
                "type": property_type,
                "address": property_address,
                "city": city,
                "state": state,
                "year_built": year_built,
                "square_feet": square_feet,
                "occupancy_pct": occupancy,
                "vacancy_rate_pct": vacancy_rate,
                "acquisition_date": acquisition_date,
            },
            "financing": {
                "purchase_price": purchase_price,
                "loan_to_value_pct": loan_to_value,
                "interest_rate_pct": interest_rate,
                "amortization_period_years": amortization_period,
                "loan_amount": loan_amount,
                "initial_equity": initial_equity,
            },
            "operating_assumptions": {
                "annual_noi": annual_noi,
                "hold_period_years": hold_period,
                "noi_growth_rate_pct": noi_growth_rate,
                "exit_cap_rate_pct": exit_cap_rate,
                "market_rent_growth_pct": market_rent_growth,
                "expense_growth_pct": expense_growth,
            },
            "metrics": {
                "purchase_cap_rate_pct": round(purchase_cap_rate * 100, 2),
                "cash_on_cash_return_pct": round(cash_on_cash_return * 100, 2),
                "dscr": round(dscr, 2),
                "debt_yield_pct": round(debt_yield * 100, 2),
                "loan_constant_pct": round(loan_constant * 100, 2),
                "equity_multiple": round(equity_multiple, 2),
                "estimated_exit_value": round(exit_value, 0),
                "annual_debt_service": round(annual_debt_service, 0),
                "remaining_loan_balance_at_exit": round(remaining_balance, 0),
                "total_cash_flow_over_hold": round(total_cash_flow_over_hold, 0),
                "net_sale_proceeds": round(net_sale_proceeds, 0),
                "total_equity_value_at_exit": round(total_equity_value, 0),
            },
            "cash_flow_schedule": yearly_data,
            "supporting_documents": {
                key: value["text"]
                for key, value in {
                    "rent_roll": st.session_state.get("rent_roll_data"),
                    "t12_operating_statement": st.session_state.get("t12_data"),
                    "lease_summary": st.session_state.get("lease_summary_data"),
                    "property_information_sheet": st.session_state.get("property_info_sheet_data"),
                }.items()
                if value is not None
            },
        }
    

        if st.button("Generate Investment Memo"):
            with st.spinner("Analyzing deal and writing memo..."):
                memo_text = generate_investment_memo(property_data)
                st.session_state.memo_text = memo_text
                memo_text_safe = memo_text.replace("$", "\\$")
            st.markdown(memo_text_safe)
        elif "memo_text" in st.session_state:
            memo_text_safe = st.session_state.memo_text.replace("$", "\\$")
            st.markdown(memo_text_safe)


    excel_file = build_excel_model(
        property_name,
        purchase_price,
        annual_noi,
        loan_to_value,
        interest_rate,
        hold_period,
        exit_cap_rate,
        noi_growth_rate,
        amortization_period,
    )

    st.download_button(
        label="Download Excel Model",
        data=excel_file,
        file_name=f"{property_name}_financial_model.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("8. Offering Memorandum")
    with st.container(border=True):
        st.markdown(
            '<p style="color:#6B7280; font-style: italic;">'
            "Generates a full Offering Memorandum combining the Investment Memo, "
            "Market Overview, Tenant Overview, financial tables, and charts.</p>",
            unsafe_allow_html=True,
        )

        if st.button("Generate Offering Memorandum"):
            with st.spinner("Building Offering Memorandum..."):
                om_narrative = generate_om_narrative(property_data)
                docx_file = build_offering_memorandum(
                    property_data,
                    om_narrative,
                    bar_fig,
                    line_fig,
                    st.session_state.get("property_photos"),
                )
                st.session_state.om_docx_bytes = docx_file.getvalue()
            st.success("Offering Memorandum generated.")

        if "om_docx_bytes" in st.session_state:
            st.download_button(
                label="Download OM (Word)",
                data=st.session_state.om_docx_bytes,
                file_name=f"{property_name}_Offering_Memorandum.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            if PDF_CONVERSION_AVAILABLE:
                if st.button("Convert to PDF"):
                    with st.spinner("Converting to PDF (requires Microsoft Word)..."):
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            docx_path = os.path.join(tmp_dir, "om.docx")
                            pdf_path = os.path.join(tmp_dir, "om.pdf")
                            with open(docx_path, "wb") as f:
                                f.write(st.session_state.om_docx_bytes)
                            convert(docx_path, pdf_path)
                            with open(pdf_path, "rb") as f:
                                st.session_state.om_pdf_bytes = f.read()

                if "om_pdf_bytes" in st.session_state:
                    st.download_button(
                        label="Download OM (PDF)",
                        data=st.session_state.om_pdf_bytes,
                        file_name=f"{property_name}_Offering_Memorandum.pdf",
                        mime="application/pdf",
                    )
            else:
                st.caption("PDF conversion is only available when running locally with Microsoft Word installed. Download the Word version above.")
            
else:
    st.info("Fill in the inputs above and click the button to generate the financial model.")
