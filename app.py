import datetime
import re
import textwrap
from fpdf import FPDF
from num2words import num2words
import pandas as pd
import streamlit as st

# --- MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Tax Invoice Generator", layout="wide")


# --- Helper Function: Extract Number from Alphanumeric String ---
def extract_number(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    # Finds whole numbers or decimals (e.g., "100", "25.5") inside text
    match = re.search(r"[-+]?\d*\.?\d+", val_str)
    return float(match.group()) if match else 0.0


# --- PDF Generation Function ---
def create_pdf(
    bill_no,
    date,
    work_order_no,
    customer_details,
    party_gst,
    vehicle_no,
    eway_no,
    df,
    sgst,
    cgst,
    igst,
    grand_total,
    amount_in_words,
):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Outer Border
    pdf.rect(10, 10, 190, 277)

    # Main Title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 8, "TAX INVOICE", border=1, ln=1, align="C")

    # Company Header Block
    header_y_start = pdf.get_y()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(190, 8, "LAKSHMI ENGINEERING WORKS", border=0, ln=1, align="C")

    pdf.set_font("Arial", "", 9)
    pdf.cell(
        190,
        5,
        "Gate, Gril Works, Rolling Shutters, Steel Window, S.S Fabrication, Aluminium Fabrication",
        border=0,
        ln=1,
        align="C",
    )
    pdf.cell(
        190,
        5,
        "No 34 Avalahalli Behind Nandhi Garden Apartments, J.P Nagar 9 phase 7 BLOCK Anjanapura post Bangalore 560062",
        border=0,
        ln=1,
        align="C",
    )
    pdf.cell(
        190,
        5,
        "Email: lakshmiengworks56@gmail.com | Cell: 9449242826, 9242485027",
        border=0,
        ln=1,
        align="C",
    )

    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 6, "GST: 29AACFL9092R1ZA", border=0, ln=1, align="C")
    header_y_end = pdf.get_y()
    pdf.rect(10, header_y_start, 190, header_y_end - header_y_start)

    # Split Section
    split_y_start = pdf.get_y()

    # Left Side
    pdf.set_xy(10, split_y_start)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(95, 6, " To,", border=0, ln=1)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(95, 5, f" {customer_details}", border=0)
    pdf.set_xy(10, pdf.get_y() + 2)
    pdf.cell(95, 6, f" Party's GST No.: {party_gst}", border=0, ln=1)
    left_bottom_y = pdf.get_y()

    # Right Side
    pdf.set_xy(105, split_y_start)
    pdf.cell(95, 6, f" Bill No: {bill_no}", border=0, ln=1)
    pdf.set_x(105)
    pdf.cell(95, 6, f" DATE: {date}", border=0, ln=1)
    pdf.set_x(105)
    pdf.cell(95, 6, f" Work Order No.: {work_order_no}", border=0, ln=1)
    pdf.set_x(105)
    pdf.cell(95, 6, f" By Vehicle No.: {vehicle_no}", border=0, ln=1)
    pdf.set_x(105)
    pdf.cell(95, 6, f" E-way No.: {eway_no}", border=0, ln=1)
    right_bottom_y = pdf.get_y()

    max_y = max(left_bottom_y, right_bottom_y)
    pdf.rect(10, split_y_start, 190, max_y - split_y_start)
    pdf.line(105, split_y_start, 105, max_y)

    pdf.set_y(max_y)

    # Table Header
    pdf.set_font("Arial", "B", 9)
    col_widths = [10, 85, 15, 20, 20, 40]
    headers = ["SI No", "Particulars", "HSN Code", "Qty", "Rate", "Amount"]

    for i in range(len(headers)):
        pdf.cell(col_widths[i], 8, headers[i], border=1, align="C")
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", "", 9)
    subtotal = 0

    for index, row in df.iterrows():
        particulars_text = str(row["Particulars"]).strip()

        if particulars_text != "":
            raw_qty_str = str(row["Qty"]).strip()
            qty_num = extract_number(raw_qty_str)

            qty_val = raw_qty_str if qty_num > 0 else ""
            rate_val = (
                f"{float(row['Rate']):.2f}" if float(row["Rate"]) > 0 else ""
            )

            amt = qty_num * float(row["Rate"])
            subtotal += amt
            amt_val = f"{amt:.2f}" if amt > 0 else ""

            wrapped_text = textwrap.wrap(particulars_text, width=48)
            if not wrapped_text:
                wrapped_text = [""]

            pdf.cell(
                col_widths[0], 6, str(row["SI No"]), border="LR", align="C"
            )
            pdf.cell(
                col_widths[1], 6, f" {wrapped_text[0]}", border="LR", align="L"
            )
            pdf.cell(
                col_widths[2], 6, str(row["HSN Code"]), border="LR", align="C"
            )
            pdf.cell(col_widths[3], 6, qty_val, border="LR", align="C")
            pdf.cell(col_widths[4], 6, rate_val, border="LR", align="R")
            pdf.cell(col_widths[5], 6, amt_val, border="LR", align="R")
            pdf.ln()

            if len(wrapped_text) > 1:
                for extra_line in wrapped_text[1:]:
                    pdf.cell(col_widths[0], 6, "", border="LR", align="C")
                    pdf.cell(
                        col_widths[1],
                        6,
                        f" {extra_line}",
                        border="LR",
                        align="L",
                    )
                    pdf.cell(col_widths[2], 6, "", border="LR", align="C")
                    pdf.cell(col_widths[3], 6, "", border="LR", align="C")
                    pdf.cell(col_widths[4], 6, "", border="LR", align="R")
                    pdf.cell(col_widths[5], 6, "", border="LR", align="R")
                    pdf.ln()

    # Fill remaining space
    for _ in range(8):
        for w in col_widths:
            pdf.cell(w, 6, "", border="LR")
        pdf.ln()

    pdf.cell(190, 0, "", border="T", ln=1)

    # Totals Section
    pdf.set_font("Arial", "B", 9)

    def print_total_row(label, amount):
        pdf.cell(sum(col_widths[:5]), 7, f"{label}  ", border=1, align="R")
        pdf.cell(col_widths[5], 7, f"{amount:.2f}", border=1, align="R")
        pdf.ln()

    print_total_row("Total", subtotal)
    print_total_row("SGST %", sgst)
    print_total_row("CGST %", cgst)
    print_total_row("IGST %", igst)

    pdf.set_font("Arial", "B", 10)
    print_total_row("Gr Total Amount", grand_total)

    # Footer Section
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(
        190, 6, f" Total Rupees: {amount_in_words}", border=0, ln=1, align="L"
    )

    pdf.ln(10)
    pdf.cell(
        190, 6, "FOR: LAKSHMI ENGINEERING WORKS", border=0, ln=1, align="R"
    )
    pdf.ln(12)
    pdf.cell(190, 6, "PROPRIETOR", border=0, ln=1, align="R")

    return pdf.output(dest="S").encode("latin1")


# --- Streamlit UI Configuration ---

st.markdown(
    "<h1 style='text-align: center;'>TAX INVOICE</h1>", unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center;'>LAKSHMI ENGINEERING WORKS</h3>",
    unsafe_allow_html=True,
)
st.divider()

col1, col2 = st.columns(2)
with col1:
    bill_no = st.text_input("Bill No:")
    date = st.date_input("DATE:", datetime.date.today())
    work_order_no = st.text_input("Work Order No:")

with col2:
    customer_address = st.text_area("To (Customer Name & Address):")
    party_gst = st.text_input("Party's GST No:")
    vehicle_no = st.text_input("By Vehicle No:")
    eway_no = st.text_input("E-way No:")

st.divider()

# --- Table ---
st.subheader("Particulars")

if "invoice_data" not in st.session_state:
    df = pd.DataFrame(
        {
            "SI No": ["1", "2", "3", "4", "5"],
            "Particulars": ["", "", "", "", ""],
            "HSN Code": ["", "", "", "", ""],
            "Qty": ["", "", "", "", ""], 
            "Rate": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Amount": [0.0, 0.0, 0.0, 0.0, 0.0],
        }
    )
    st.session_state.invoice_data = df
else:
    # BULLETPROOF FIX: Forces cached integer columns to convert to strings
    st.session_state.invoice_data["Qty"] = st.session_state.invoice_data["Qty"].astype(str)

# Render Data Editor (Qty is now a flexible Text Column)
edited_df = st.data_editor(
    st.session_state.invoice_data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Qty": st.column_config.TextColumn(
            "Qty", width="medium"
        ),
        "Rate": st.column_config.NumberColumn(min_value=0.0, format="₹%.2f"),
        "Amount": st.column_config.NumberColumn(disabled=True),
    },
)

# Live Calculation using Regex extraction
numeric_qty = edited_df["Qty"].apply(extract_number)
calculated_amounts = (numeric_qty * edited_df["Rate"].astype(float)).round(2)
current_amounts = edited_df["Amount"].astype(float).round(2)

if not current_amounts.equals(calculated_amounts):
    edited_df["Amount"] = calculated_amounts
    st.session_state.invoice_data = edited_df
    st.rerun()

st.divider()
col_empty, col_totals = st.columns([2, 1])

with col_totals:
    subtotal = edited_df["Amount"].sum()
    st.write(f"**Total Amount:** ₹{subtotal:.2f}")

    sgst_pct = st.number_input("SGST %", min_value=0.0, value=9.0, step=0.1)
    cgst_pct = st.number_input("CGST %", min_value=0.0, value=9.0, step=0.1)
    igst_pct = st.number_input("IGST %", min_value=0.0, value=0.0, step=0.1)

    sgst_amt = subtotal * (sgst_pct / 100)
    cgst_amt = subtotal * (cgst_pct / 100)
    igst_amt = subtotal * (igst_pct / 100)

    grand_total = subtotal + sgst_amt + cgst_amt + igst_amt

    st.write(f"SGST: ₹{sgst_amt:.2f}")
    st.write(f"CGST: ₹{cgst_amt:.2f}")
    st.write(f"IGST: ₹{igst_amt:.2f}")
    st.markdown(f"### **Grand Total: ₹{grand_total:.2f}**")

st.divider()
amount_in_words = ""
if grand_total > 0:
    rounded_total = round(grand_total, 2)
    amount_in_words = (
        num2words(rounded_total, lang="en_IN").title() + " Rupees Only"
    )
    amount_in_words = amount_in_words.replace("Point Zero Zero", "").strip()

st.info(f"**Total Rupees (in words):** {amount_in_words}")

if st.button("Generate Invoice PDF", type="primary"):
    if not bill_no:
        st.error("Please enter a Bill Number before generating.")
    else:
        pdf_bytes = create_pdf(
            bill_no,
            date.strftime("%d-%m-%Y"),
            work_order_no,
            customer_address,
            party_gst,
            vehicle_no,
            eway_no,
            edited_df,
            sgst_amt,
            cgst_amt,
            igst_amt,
            grand_total,
            amount_in_words,
        )

        st.success("PDF Generated Successfully!")
        st.download_button(
            label="⬇️ Download Invoice PDF",
            data=pdf_bytes,
            file_name=f"Invoice_{bill_no}.pdf",
            mime="application/pdf",
        )
