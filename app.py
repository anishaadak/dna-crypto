import streamlit as st

from dnacrypto.pipeline import encrypt_to_dna
from dnacrypto.encoding import gc_content, longest_run

st.set_page_config(page_title="DNA Crypto", page_icon="🧬")
st.title("DNA Crypto")
st.warning("Demo only. Do not type a real password or a real secret here.")

for key, value in {"dna": "", "original": "", "status": None}.items():
    st.session_state.setdefault(key, value)


def do_encrypt():
    message = st.session_state.message
    password = st.session_state.password
    if not message or not password:
        st.session_state.status = ("error", "Type a message and a password first.")
    else:
        dna = encrypt_to_dna(message, password)
        st.session_state.dna = dna
        st.session_state.original = dna
        st.session_state.status = ("success", f"Encrypted into {len(dna)} DNA letters.")


st.text_area("Message", key="message")
st.text_input("Password", type="password", key="password")
st.text_area("DNA", key="dna", height=200)
st.button("Encrypt to DNA", on_click=do_encrypt)

if st.session_state.dna:
    clean_dna = "".join(st.session_state.dna.split())
    col1, col2, col3 = st.columns(3)
    col1.metric("Letters", len(clean_dna))
    col2.metric("Longest run of one letter", longest_run(clean_dna))
    col3.metric("GC content", f"{gc_content(clean_dna) * 100:.1f}%")

if st.session_state.status is not None:
    kind, text = st.session_state.status
    if kind == "success":
        st.success(text)
    elif kind == "error":
        st.error(text)
    elif kind == "warning":
        st.warning(text)
    else:
        st.info(text)
