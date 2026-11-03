import random
import streamlit as st

from cryptography.exceptions import InvalidTag

from dnacrypto.pipeline import (
    check_dna,
    damage_letter,
    decrypt_from_dna,
    encrypt_to_dna,
    repair_dna,
)
from dnacrypto.encoding import gc_content, longest_run

st.set_page_config(page_title="DNA Crypto", page_icon="🧬")
st.title("DNA Crypto")
st.warning("Demo only. Do not type a real password or a real secret here.")

for key, value in {
    "dna": "",
    "original": "",
    "original_message": "",
    "status_encrypt": None,
    "status_dna": None,
    "status_decrypt": None,
}.items():
    st.session_state.setdefault(key, value)


def show_status(key):
    entry = st.session_state.get(key)
    if entry is None:
        return
    level, text = entry
    if level == "success":
        st.success(text)
    elif level == "error":
        st.error(text)
    elif level == "warning":
        st.warning(text)
    else:
        st.info(text)


def do_encrypt():
    message = st.session_state.message
    password = st.session_state.enc_password
    if not message or not password:
        st.session_state.status_encrypt = ("error", "Type a message and a password first.")
    else:
        dna = encrypt_to_dna(message, password)
        st.session_state.dna = dna
        st.session_state.original = dna
        st.session_state.original_message = message
        st.session_state.message = ""
        st.session_state.enc_password = ""
        st.session_state.status_encrypt = (
            "success",
            f"Encrypted into {len(dna)} DNA letters. "
            "The message and password were cleared from this page, so only the DNA is left.",
        )
    st.session_state.status_dna = None
    st.session_state.status_decrypt = None


def do_damage():
    if st.session_state.original:
        dna = "".join(st.session_state.original.split()).upper()
    else:
        dna = "".join(st.session_state.dna.split()).upper()
    if not dna:
        st.session_state.status_dna = ("error", "Encrypt a message first.")
        st.session_state.status_decrypt = None
        return
    n = min(st.session_state.n_damage, len(dna))
    positions = random.sample(range(len(dna)), n)
    for i in positions:
        dna = damage_letter(dna, i)
    st.session_state.dna = dna
    st.session_state.status_dna = ("warning", f"Damaged {n} letter(s) on purpose.")
    st.session_state.status_decrypt = None


def do_check():
    status, text = check_dna(
        st.session_state.dna, st.session_state.dec_password or None
    )
    if status in ("intact", "no_damage_found"):
        level = "success"
    elif status == "repairable":
        level = "info"
    else:
        level = "error"
    st.session_state.status_dna = (level, f"{status.upper()}: {text}")


def do_reset():
    if st.session_state.original:
        st.session_state.dna = st.session_state.original
        st.session_state.status_dna = ("info", "DNA reset to the original.")
    else:
        st.session_state.status_dna = ("error", "Encrypt a message first.")
    st.session_state.status_decrypt = None

def do_repair():
    try:
        fixed, positions = repair_dna(st.session_state.dna)
        st.session_state.dna = fixed
    except ValueError:
        st.session_state.status_dna = ("error", "Too damaged to repair, or not valid DNA.")
        st.session_state.status_decrypt = None
        return
    if not positions:
        st.session_state.status_dna = ("info", "No damage found.")
    elif st.session_state.original and fixed == st.session_state.original:
        st.session_state.status_dna = (
            "success",
            f"Fixed {len(positions)} damaged byte(s). The DNA matches the original.",
        )
    else:
        st.session_state.status_dna = (
            "success",
            f"Fixed {len(positions)} damaged byte(s).",
        )
    st.session_state.status_decrypt = None


def do_decrypt():
    if not st.session_state.dec_password:
        st.session_state.status_decrypt = (
            "error",
            "Type the decryption password first.",
        )
        return
    try:
        _, positions = repair_dna(st.session_state.dna)
    except ValueError:
        st.session_state.status_decrypt = (
            "error",
            "The DNA is too damaged or not valid.",
        )
        return
    try:
        message = decrypt_from_dna(st.session_state.dna, st.session_state.dec_password)
        if positions:
            status_text = (
                f"Decrypted message: {message} "
                f"(repaired {len(positions)} damaged byte(s) in memory first. "
                "The DNA in the box was not changed.)"
            )
        else:
            status_text = f"Decrypted message: {message}"
        if st.session_state.original_message:
            if message == st.session_state.original_message:
                status_text += " Matches the message you encrypted."
            else:
                status_text += " Different from the message you encrypted."
        st.session_state.status_decrypt = ("success", status_text)
    except InvalidTag:
        st.session_state.status_decrypt = ("error", "Wrong password, or the data was changed.")
    except ValueError:
        st.session_state.status_decrypt = ("error", "The DNA is too damaged or not valid.")


st.subheader("1. Encrypt")
st.text_area("Message", key="message")
st.text_input("Encryption password", type="password", key="enc_password")
st.button("Encrypt to DNA", on_click=do_encrypt)
show_status("status_encrypt")

st.subheader("2. The DNA")
st.text_area("DNA", key="dna", height=200)

st.slider("Letters to damage", 1, 30, 3, key="n_damage")
col1, col2 = st.columns(2)
col1.button("Damage the DNA", on_click=do_damage)
col2.button("Reset to original DNA", on_click=do_reset)

col1, col2 = st.columns(2)
col1.button("Check", on_click=do_check)
col2.button("Repair", on_click=do_repair)

show_status("status_dna")

if st.session_state.dna:
    clean_dna = "".join(st.session_state.dna.split())
    col1, col2, col3 = st.columns(3)
    col1.metric("Letters", len(clean_dna))
    col2.metric("Longest run of one letter", longest_run(clean_dna))
    col3.metric("GC content", f"{gc_content(clean_dna) * 100:.1f}%")

st.subheader("3. Decrypt")
st.text_input("Decryption password", type="password", key="dec_password")
st.caption(
    "The password is not stored anywhere. When decrypting, the key is made again "
    "from the password and the salt inside the DNA."
)
st.button("Decrypt", on_click=do_decrypt)
show_status("status_decrypt")
