import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.set_page_config(
    page_title="DebtCompare Pro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DebtCompare Pro")

st.write("برنامج مقارنة المديونيات")

st.markdown("""
القواعد الحالية:

- المقارنة برقم العميل فقط
- استخدام شيت مديونيه المباشر
- استخدام صافي المديونيه
- دعم PDF واحد أو أكثر
""")

excel_file = st.file_uploader(
    "📂 اختر ملف المديونية",
    type=["xlsx"]
)

pdf_files = st.file_uploader(
    "📄 اختر ملفات PDF",
    type=["pdf"],
    accept_multiple_files=True
)


def read_debt(file):

    raw = pd.read_excel(
        file,
        sheet_name="مديونيه المباشر",
        header=None
    )

    headers = raw.iloc[3]

    debt = raw.iloc[4:].copy()

    debt.columns = headers

    debt = debt[
        [
            "رقم العميل",
            "اسم العميل",
            "صافي المديونيه"
        ]
    ]

    debt = debt.dropna(
        subset=["رقم العميل"]
    )

    debt["رقم العميل"] = (
        debt["رقم العميل"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )

    debt["صافي المديونيه"] = pd.to_numeric(
        debt["صافي المديونيه"],
        errors="coerce"
    )

    return debt


def read_pdf(file):

    rows = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            text = page.extract_text() or ""

            for line in text.split("\n"):

                client = re.search(
                    r"(470\d{7,8})",
                    line
                )

                if not client:
                    continue

                nums = re.findall(
                    r"\d+,\d{2}",
                    line
                )

                if len(nums) >= 3:

                    rows.append({

                        "رقم العميل":

                        client.group(1),

                        "رصيد PDF":

                        float(
                            nums[0]
                            .replace(",", ".")
                        )

                    })

    return pd.DataFrame(rows)


if st.button("▶️ ابدأ المقارنة"):

    if excel_file is None:

        st.error("اختار ملف المديونية")

    elif len(pdf_files) == 0:

        st.error("اختار ملفات PDF")

    else:

        try:

            debt = read_debt(
                excel_file
            )

            pdf = pd.concat(

                [

                    read_pdf(f)

                    for f in pdf_files

                ],

                ignore_index=True

            )

            pdf = pdf.groupby(

                "رقم العميل",

                as_index=False

            )["رصيد PDF"].max()

            result = debt.merge(

                pdf,

                on="رقم العميل",

                how="outer"

            )

            result["الفرق"] = (

                result["صافي المديونيه"]

                .fillna(0)

                -

                result["رصيد PDF"]

                .fillna(0)

            )

            def status(r):

                if pd.isna(
                    r["صافي المديونيه"]
                ):

                    return "PDF فقط"

                if pd.isna(
                    r["رصيد PDF"]
                ):

                    return "مديونية فقط"

                if abs(
                    r["الفرق"]
                ) < 1:

                    return "مطابق"

                return "يوجد فرق"

            result["الحالة"] = result.apply(
                status,
                axis=1
            )

            output = BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                result[
                    result["الحالة"]
                    == "مطابق"
                ].to_excel(
                    writer,
                    sheet_name="مطابق",
                    index=False
                )

                result[
                    result["الحالة"]
                    == "يوجد فرق"
                ].to_excel(
                    writer,
                    sheet_name="يوجد فرق",
                    index=False
                )

                result[
                    result["الحالة"]
                    == "PDF فقط"
                ].to_excel(
                    writer,
                    sheet_name="PDF فقط",
                    index=False
                )

                result[
                    result["الحالة"]
                    == "مديونية فقط"
                ].to_excel(
                    writer,
                    sheet_name="مديونية فقط",
                    index=False
                )

            st.success("تم إنشاء التقرير")

            st.download_button(

                "💾 تنزيل التقرير",

                data=output.getvalue(),

                file_name="تقرير_المقارنة.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            )

        except Exception as e:

            st.error(str(e))