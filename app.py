import random
from pathlib import Path
import streamlit as st

# ---------------- FILES ----------------

SCORE_FILE = Path("stats.txt")
WRONG_FILE = Path("wrong.txt")

# ---------------- DATA ----------------

BONES = [
    {"name": "Frontal", "latin": "Os frontale", "category": "neurocranium",
     "landmarks": ["Supraorbital foramen", "Glabella", "Frontal sinus"]},

    {"name": "Parietal", "latin": "Os parietale", "category": "neurocranium",
     "landmarks": ["Parietal foramen", "Superior temporal line"]},

    {"name": "Temporal", "latin": "Os temporale", "category": "neurocranium",
     "landmarks": ["Mastoid process", "Styloid process", "External acoustic meatus"]},

    {"name": "Occipital", "latin": "Os occipitale", "category": "neurocranium",
     "landmarks": ["Foramen magnum", "Occipital condyles"]},

    {"name": "Sphenoid", "latin": "Os sphenoidale", "category": "neurocranium",
     "landmarks": ["Sella turcica", "Optic canal", "Superior orbital fissure"]},

    {"name": "Ethmoid", "latin": "Os ethmoidale", "category": "neurocranium",
     "landmarks": ["Cribriform plate", "Crista galli"]},

    {"name": "Maxilla", "latin": "Maxilla", "category": "viscerocranium",
     "landmarks": ["Infraorbital foramen", "Maxillary sinus"]},

    {"name": "Mandible", "latin": "Mandibula", "category": "viscerocranium",
     "landmarks": ["Mental foramen", "Mandibular foramen"]},
]

# ---------------- HELPERS ----------------

def load_stats():
    if not SCORE_FILE.exists():
        return 0, 0
    try:
        c, t = map(int, SCORE_FILE.read_text().split())
        return c, t
    except:
        return 0, 0

def save_stats(c_add, t_add):
    c, t = load_stats()
    SCORE_FILE.write_text(f"{c + c_add} {t + t_add}")

def log_wrong(q, user, correct):
    with open(WRONG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{q}\t{user}\t{correct}\n")

def load_wrongs():
    if not WRONG_FILE.exists():
        return []
    lines = WRONG_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    for l in lines:
        parts = l.split("\t")
        if len(parts) == 3:
            out.append(parts)
    return out

# ---------------- QUIZ LOGIC ----------------

def make_question(bone):
    mode = random.choice(["latin", "category", "landmark"])

    if mode == "latin":
        return f"{bone['name']} kemiğinin Latin adı?", bone["latin"], mode

    if mode == "category":
        return f"{bone['name']} hangi grupta? (neurocranium / viscerocranium)", bone["category"], mode

    example = random.choice(bone["landmarks"])
    return f"{bone['name']} ile ilişkili landmark yaz (örn: {example})", " / ".join(bone["landmarks"]), mode


def check(mode, bone, user, correct):
    u = user.lower().strip()
    if not u:
        return False
    if mode == "landmark":
        return u in [x.lower() for x in bone["landmarks"]]
    return u == correct.lower()

# ---------------- UI ----------------

st.set_page_config("Skull Trainer", "🧠")
st.title("🧠 Skull Trainer Web App")

quiz_tab, review_tab, stats_tab = st.tabs(["Quiz", "Review", "Stats"])

# -------- STATS --------

with stats_tab:
    c, t = load_stats()
    st.metric("Toplam Skor", f"{c}/{t}")
    if t:
        st.progress(c / t)

# -------- QUIZ --------

with quiz_tab:
    if "current" not in st.session_state:
        st.session_state.current = None
        st.session_state.correct = 0
        st.session_state.total = 0

    if st.button("🎯 Yeni Quiz Başlat"):
        pool = BONES[:]
        random.shuffle(pool)
        st.session_state.pool = pool[:8]
        st.session_state.index = 0
        st.session_state.correct = 0
        st.session_state.total = len(st.session_state.pool)
        st.session_state.current = None

    if "pool" in st.session_state and st.session_state.index < st.session_state.total:

        if st.session_state.current is None:
            bone = st.session_state.pool[st.session_state.index]
            q, ans, mode = make_question(bone)
            st.session_state.current = (bone, q, ans, mode)

        bone, q, ans, mode = st.session_state.current
        st.info(q)

        user = st.text_input("Cevabın", key=str(st.session_state.index))

        if st.button("Cevapla"):
            if check(mode, bone, user, ans):
                st.success("Doğru ✅")
                st.session_state.correct += 1
            else:
                st.error(f"Yanlış ❌ Doğru: {ans}")
                log_wrong(q, user, ans)

            st.session_state.index += 1
            st.session_state.current = None

            if st.session_state.index >= st.session_state.total:
                save_stats(st.session_state.correct, st.session_state.total)
                st.success(f"Quiz bitti! Skor: {st.session_state.correct}/{st.session_state.total}")

# -------- REVIEW --------

with review_tab:
    wrongs = load_wrongs()

    if not wrongs:
        st.write("Henüz yanlış yok 😌")
    else:
        for q, user, correct in wrongs[-10:]:
            st.warning(q)
            st.write(f"Sen: {user}")
            st.write(f"Doğru: {correct}")
            st.divider()
