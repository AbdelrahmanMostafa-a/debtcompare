```python
import streamlit as st

st.set_page_config(
    page_title="DebtCompare Pro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DebtCompare Pro")

st.write("برنامج مقارنة المديونيات")

excel = st.file_uploader(
    "📂 اختر ملف المديونية",
    type=["xlsx"]
)

pdfs = st.file_uploader(
    "📄 اختر ملفات PDF",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("▶️ ابدأ المقارنة"):

    if excel is None:

        st.error("اختار ملف المديونية")

    elif len(pdfs) == 0:

        st.error("اختار ملفات PDF")

    else:

        st.success("تمام، المرحلة الجاية هنركب محرك المقارنة الحقيقي.")
```
