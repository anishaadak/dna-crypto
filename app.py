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


def do_damage():
    if st.session_state.original:
        dna = "".join(st.session_state.original.split()).upper()
    else:
        dna = "".join(st.session_state.dna.split()).upper()
    if not dna:
        st.session_state.status = ("error", "Encrypt a message first.")
        return
    n = min(st.session_state.n_damage, len(dna))
    positions = random.sample(range(len(dna)), n)
    for i in positions:
        dna = damage_letter(dna, i)
    st.session_state.dna = dna
    st.session_state.status = ("warning", f"Damaged {n} letter(s) on purpose.")


def do_check():
    status, text = check_dna(st.session_state.dna, st.session_state.password or None)
    if status in ("intact", "no_damage_found"):
        level = "success"
    elif status == "repairable":
        level = "info"
    else:
        level = "error"
    st.session_state.status = (level, f"{status.upper()}: {text}")


def do_repair():
    try:
        fixed, positions = repair_dna(st.session_state.dna)
        st.session_state.dna = fixed
    except ValueError:
        st.session_state.status = ("error", "Too damaged to repair, or not valid DNA.")
        return
    if not positions:
        st.session_state.status = ("info", "No damage found.")
    elif st.session_state.original and fixed == st.session_state.original:
        st.session_state.status = (
            "success",
            f"Fixed {len(positions)} damaged byte(s). The DNA matches the original.",
        )
    else:
        st.session_state.status = (
            "success",
            f"Fixed {len(positions)} damaged byte(s).",
        )


def do_reset():
    if st.session_state.original:
        st.session_state.dna = st.session_state.original
        st.session_state.status = ("info", "DNA reset to the original.")
    else:
        st.session_state.status = ("error", "Encrypt a message first.")


def do_decrypt():
    try:
        _, positions = repair_dna(st.session_state.dna)
    except ValueError:
        st.session_state.status = ("error", "The DNA is too damaged or not valid.")
        return
    try:
        message = decrypt_from_dna(st.session_state.dna, st.session_state.password)
        if positions:
            st.session_state.status = (
                "success",
                f"Decrypted message: {message} (repaired {len(positions)} damaged byte(s) in memory first. The DNA in the box was not changed.)",
            )
        else:
            st.session_state.status = ("success", f"Decrypted message: {message}")
    except InvalidTag:
        st.session_state.status = ("error", "Wrong password, or the data was changed.")
    except ValueError:
        st.session_state.status = ("error", "The DNA is too damaged or not valid.")


st.text_area("Message", key="message")
st.text_input("Password", type="password", key="password")
st.text_area("DNA", key="dna", height=200)
st.button("Encrypt to DNA", on_click=do_encrypt)

st.slider("Letters to damage", 1, 30, 3, key="n_damage")
col1, col2 = st.columns(2)
col1.button("Damage the DNA", on_click=do_damage)
col2.button("Reset to original DNA", on_click=do_reset)

col1, col2, col3 = st.columns(3)
col1.button("Check", on_click=do_check)
col2.button("Repair", on_click=do_repair)
col3.button("Decrypt", on_click=do_decrypt)

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
