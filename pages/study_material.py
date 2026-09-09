import streamlit as st
from pathlib import Path
from pypdf import PdfReader

from services.database import (
    save_study_material,
    get_study_materials
)


# ---------- LOGIN CHECK ----------
# Check if user is logged in
if "user_id" not in st.session_state:
    st.warning("Please login first.")
    st.switch_page("pages/login.py")
    st.stop()


# ---------- PAGE ----------

st.title("📚 Study Materials")
st.write("Upload your study materials and keep everything organized in one place.")

st.divider()


# ---------- UPLOAD ----------

st.subheader("📤 Upload Study Material")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)


if uploaded_file is not None:

    if st.button("Upload Material", use_container_width=True):

        user_id = st.session_state["user_id"]

        # Create user's upload folder
        upload_dir = Path("database") / "uploads" / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / uploaded_file.name

        # Save PDF
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract text
        reader = PdfReader(str(file_path))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        # Save material information
        save_study_material(
            user_id,
            uploaded_file.name,
            str(file_path)
        )

        st.success("Study material uploaded successfully! 🎉")

        st.info(
            f"Extracted approximately {len(text):,} characters from the PDF."
        )


st.divider()


# ---------- MATERIAL LIST ----------

st.subheader("📖 Your Study Materials")

materials = get_study_materials(
    st.session_state["user_id"]
)

if not materials:

    st.info("You haven't uploaded any study materials yet.")

else:

    for material in materials:

        material_id, file_name, file_path, uploaded_at = material

        with st.container(border=True):

            st.write(f"📄 **{file_name}**")
            st.caption(f"Uploaded: {uploaded_at}")

            st.write(
                f"Extracted PDF available for AI processing."
            )