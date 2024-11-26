import streamlit as st
import pandas as pd
from pathlib import Path
import base64
from modules.file_operations import upload_file

# Directory to save uploaded PDF files
UPLOAD_DIR = Path("pisnick_pdf")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize the metadata DataFrame
if 'pdf_metadata' not in st.session_state:
    st.session_state.pdf_metadata = pd.DataFrame(columns=['Originalni jmeno', 'Alternativni jmeno', 'Author', 'File Path'])

st.title("Digitalizovaný zpěvník Vlaštovky a Amazonky")

# Upload PDFs
uploaded_files = st.file_uploader("Nahraj písničku (pdf)", type="pdf", accept_multiple_files=True)
if uploaded_files is not None:
    if st.button("Nahrej/Upload"):
        # Upload the file to S3
        upload_file(uploaded_file, bucket_name, file_name)
        st.success("Nahrávání poroběhlo úspěšně! / File uploaded successfully!")
       
for uploaded_file in uploaded_files:
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    new_entry = pd.DataFrame({
        'Originalni jmeno': [uploaded_file.name],
        'Alternativni jmeno': [uploaded_file.name],
        'Author': [''],
        'File Path': [str(file_path)]
    })
    st.session_state.pdf_metadata = pd.concat([st.session_state.pdf_metadata, new_entry], ignore_index=True)

# Edit metadata for each uploaded PDF
for index, row in st.session_state.pdf_metadata.iterrows():
    st.text_input(f"Originalni jmeno {row['Originalni jmeno']}", value=row['Alternativni jmeno'], key=f"Alternativni jmeno_{index}")
    st.text_input(f"Author {row['Originalni jmeno']}", value=row['Author'], key=f"author_{index}")

# Update metadata with user inputs
for index in range(len(st.session_state.pdf_metadata)):
    st.session_state.pdf_metadata.at[index, 'Alternativni jmeno'] = st.session_state[f"Alternativni jmeno_{index}"]
    st.session_state.pdf_metadata.at[index, 'Author'] = st.session_state[f"author_{index}"]

# Sort and display PDFs
sort_option = st.selectbox("Seřaď PDFka podle:", options=["Originalni jmeno", "Alternativni jmeno", "Author"])
sorted_metadata = st.session_state.pdf_metadata.sort_values(by=sort_option)

for index, row in sorted_metadata.iterrows():
    st.write(f"**{row['Alternativni jmeno']}** by {row['Author']}")
    if st.button(f"Otevřít {row['Alternativni jmeno']}", key=f"view_{index}"):
        with open(row['File Path'], "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        st.markdown(pdf_display, unsafe_allow_html=True)
