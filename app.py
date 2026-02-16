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
import random
import time
from pathlib import Path
import streamlit as st

# -------------------- FILES --------------------
SCORE_FILE = Path("stats.txt")
WRONG_FILE = Path("wrong.txt")
ASSETS_DIR = Path("assets/bones")

# -------------------- DATA --------------------
# İstersen bunu sonra JSON'a taşırız. Şimdilik net ve stabil.
BONES = [
    {"name": "Frontal",   "latin": "Os frontale",   "category": "neurocranium",
     "landmarks": ["Supraorbital foramen", "Glabella", "Frontal sinus"]},
    {"name": "Parietal",  "latin": "Os parietale",  "category": "neurocranium",
     "landmarks": ["Parietal foramen", "Superior temporal line"]},
    {"name": "Temporal",  "latin": "Os temporale",  "category": "neurocranium",
     "landmarks": ["Mastoid process", "Styloid process", "External acoustic meatus"]},
    {"name": "Occipital", "latin": "Os occipitale", "category": "neurocranium",
     "landmarks": ["Foramen magnum", "Occipital condyles", "External occipital protuberance"]},
    {"name": "Sphenoid",  "latin": "Os sphenoidale","category": "neurocranium",
     "landmarks": ["Sella turcica", "Optic canal", "Superior orbital fissure"]},
    {"name": "Ethmoid",   "latin": "Os ethmoidale", "category": "neurocranium",
     "landmarks": ["Cribriform plate", "Crista galli"]},
    {"name": "Maxilla",   "latin": "Maxilla",       "category": "viscerocranium",
     "landmarks": ["Infraorbital foramen", "Maxillary sinus", "Alveolar process"]},
    {"name": "Mandible",  "latin": "Mandibula",     "category": "viscerocranium",
     "landmarks": ["Mental foramen", "Mandibular foramen", "Condylar process"]},
    {"name": "Zygomatic", "latin": "Os zygomaticum","category": "viscerocranium",
     "landmarks": ["Zygomatic arch", "Zygomaticofacial foramen"]},
    {"name": "Nasal",     "latin": "Os nasale",     "category": "viscerocranium",
     "landmarks": ["Nasion"]},
]

NAME_TO_BONE = {b["name"].lower(): b for b in BONES}

# -------------------- MOBILE UI (CSS) --------------------
MOBILE_CSS = """
<style>
/* genel */
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 900px; }
h1, h2, h3 { letter-spacing: -0.02em; }

/* butonlar daha dokunmatik */
.stButton button {
  border-radius: 14px !important;
  padding: 0.70rem 1.0rem !important;
  font-weight: 650 !important;
}

/* input */
div[data-baseweb="input"] input {
  border-radius: 12px !important;
  padding-top: 0.65rem !important;
  padding-bottom: 0.65rem !important;
}

/* mobilde boşluklar */
@media (max-width: 600px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  h1 { font-size: 2rem !important; }
}
</style>
"""

# -------------------- PERSISTENCE --------------------
def load_stats():
    if not SCORE_FILE.exists():
        return 0, 0
    try:
        c, t = map(int, SCORE_FILE.read_text(encoding="utf-8").strip().split())
        return c, t
    except Exception:
        return 0, 0

def save_stats(correct_delta: int, total_delta: int):
    c, t = load_stats()
    c += int(correct_delta)
    t += int(total_delta)
    SCORE_FILE.write_text(f"{c} {t}", encoding="utf-8")

def load_wrongs():
    """returns list of tuples (question, user_answer, correct_answer)"""
    if not WRONG_FILE.exists():
        return []
    out = []
    for line in WRONG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            out.append((parts[0], parts[1], parts[2]))
    return out

def overwrite_wrongs(items):
    with open(WRONG_FILE, "w", encoding="utf-8") as f:
        for q, u, c in items:
            f.write(f"{q}\t{u}\t{c}\n")

def log_wrong(question: str, user_answer: str, correct_answer: str):
    with open(WRONG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{question}\t{user_answer}\t{correct_answer}\n")

# -------------------- "LEARNING" LOGIC --------------------
def wrong_weights():
    """
    Wrong listesine göre kemiklere ağırlık ver:
    bir kemik yanlışlarda çok geçiyorsa daha sık sorulsun.
    """
    counts = {b["name"]: 1 for b in BONES}  # base weight 1
    for q, _, correct in load_wrongs():
        # Soru metninden kemik adını yakalamaya çalış
        # (en stabil yöntem: bone name q içinde geçiyor mu)
        for b in BONES:
            if b["name"].lower() in q.lower():
                counts[b["name"]] += 2
        # ayrıca correct içinde latin adı vs varsa da ekleyelim (hafif)
        for b in BONES:
            if b["latin"].lower() in correct.lower():
                counts[b["name"]] += 1
    return counts

def pick_bone(pool):
    """
    Öğrenen seçim: ağırlıklı random.
    """
    weights = wrong_weights()
    w = [weights.get(b["name"], 1) for b in pool]
    return random.choices(pool, weights=w, k=1)[0]

# -------------------- QUIZ LOGIC --------------------
def make_question(bone):
    mode = random.choice(["latin", "category", "landmark"])

    if mode == "latin":
        return f"**{bone['name']}** kemiğinin Latin adı nedir?", bone["latin"], mode

    if mode == "category":
        return f"**{bone['name']}** hangi kategori? (neurocranium / viscerocranium)", bone["category"], mode

    example = random.choice(bone["landmarks"]) if bone["landmarks"] else ""
    return f"**{bone['name']}** ile ilişkili bir landmark yaz (örn: {example})", " / ".join(bone["landmarks"]), mode

def check_answer(mode, bone, user, correct):
    u = user.strip().lower()
    if not u:
        return False
    if mode == "landmark":
        return u in {x.lower() for x in bone["landmarks"]}
    return u == correct.lower()

def bone_image_path(bone_name: str):
    # frontal -> assets/bones/frontal.png
    p_png = ASSETS_DIR / f"{bone_name.lower()}.png"
    p_jpg = ASSETS_DIR / f"{bone_name.lower()}.jpg"
    if p_png.exists():
        return p_png
    if p_jpg.exists():
        return p_jpg
    return None

# -------------------- APP --------------------
st.set_page_config(page_title="Skull Trainer", page_icon="🧠", layout="centered")
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

st.title("🧠 Skull Trainer")
st.caption("Evet, bunu gerçekten sen yaptın. Şimdi daha da güzel yapıyoruz.")

tab_quiz, tab_exam, tab_review, tab_stats = st.tabs(["Quiz", "Exam", "Review", "Stats"])

# ---------- STATS ----------
with tab_stats:
    st.subheader("📊 İstatistik")
    c, t = load_stats()
    st.metric("Toplam Doğru / Toplam Soru", f"{c}/{t}")
    if t > 0:
        st.progress(c / t)
    colA, colB = st.columns(2)
    with colA:
        if st.button("🧹 Stats sıfırla"):
            SCORE_FILE.write_text("0 0", encoding="utf-8")
            st.success("Stats sıfırlandı.")
    with colB:
        if st.button("🧽 Wrong listesi temizle"):
            overwrite_wrongs([])
            st.success("Wrong listesi temizlendi.")

# ---------- QUIZ ----------
with tab_quiz:
    st.subheader("🎯 Quiz (Öğrenen Mod)")

    col1, col2 = st.columns(2)
    with col1:
        n_q = st.number_input("Soru sayısı", 1, 50, 10)
    with col2:
        focus = st.selectbox("Kategori", ["hepsi", "neurocranium", "viscerocranium"])

    show_img = st.toggle("Görsel göster (assets varsa)", value=True)

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {}

    def start_quiz():
        pool = BONES[:]
        if focus != "hepsi":
            pool = [b for b in pool if b["category"] == focus]
        random.shuffle(pool)
        # quiz’de kemik tekrarına izin verelim mi? öğrenen modda evet mantıklı.
        st.session_state.quiz_state = {
            "pool": pool,
            "i": 0,
            "total": int(n_q),
            "correct": 0,
            "current": None,
        }

    if st.button("🚀 Yeni Quiz Başlat"):
        start_quiz()

    qs = st.session_state.quiz_state
    if qs:
        if qs["i"] < qs["total"]:
            if qs["current"] is None:
                bone = pick_bone(qs["pool"]) if qs["pool"] else random.choice(BONES)
                q, ans, mode = make_question(bone)
                qs["current"] = {"bone": bone, "q": q, "ans": ans, "mode": mode}

            cur = qs["current"]
            bone = cur["bone"]

            st.write(f"**Soru {qs['i'] + 1}/{qs['total']}**")
            st.info(cur["q"])

            if show_img:
                img = bone_image_path(bone["name"])
                if img:
                    st.image(str(img), use_container_width=True)
                else:
                    st.caption("🖼️ Görsel bulunamadı. (assets/bones içine eklersen otomatik çıkar.)")

            user = st.text_input("Cevabın", key=f"quiz_answer_{qs['i']}")

            cols = st.columns(2)
            with cols[0]:
                if st.button("✅ Cevapla", use_container_width=True):
                    ok = check_answer(cur["mode"], bone, user, cur["ans"])
                    if ok:
                        st.success("Doğru ✅")
                        qs["correct"] += 1
                    else:
                        st.error(f"Yanlış ❌ Doğru: {cur['ans']}")
                        log_wrong(cur["q"], user, cur["ans"])

                    qs["i"] += 1
                    qs["current"] = None

                    if qs["i"] >= qs["total"]:
                        save_stats(qs["correct"], qs["total"])
                        st.balloons()
                        st.success(f"🏁 Bitti! Skor: {qs['correct']}/{qs['total']}")

            with cols[1]:
                st.button("⏭️ Pas geç", use_container_width=True, on_click=lambda: qs.update({"i": qs["i"] + 1, "current": None}))

        else:
            st.success("Quiz tamamlandı. Yeni quiz başlatabilirsin.")

# ---------- EXAM MODE ----------
with tab_exam:
    st.subheader("⏱️ Exam Mode (Zamanlı)")
    st.caption("Sınav modu: timer + daha az şaka. (Biraz.)")

    col1, col2, col3 = st.columns(3)
    with col1:
        exam_q = st.number_input("Soru", 5, 60, 20)
    with col2:
        minutes = st.number_input("Süre (dk)", 1, 60, 5)
    with col3:
        exam_focus = st.selectbox("Kategori (exam)", ["hepsi", "neurocranium", "viscerocranium"])

    if "exam" not in st.session_state:
        st.session_state.exam = {"running": False}

    def start_exam():
        pool = BONES[:]
        if exam_focus != "hepsi":
            pool = [b for b in pool if b["category"] == exam_focus]
        st.session_state.exam = {
            "running": True,
            "pool": pool,
            "i": 0,
            "total": int(exam_q),
            "correct": 0,
            "current": None,
            "start_ts": time.time(),
            "limit_sec": int(minutes) * 60,
        }

    cols = st.columns(2)
    with cols[0]:
        st.button("🧪 Exam başlat", use_container_width=True, on_click=start_exam)
    with cols[1]:
        if st.button("🛑 Exam durdur", use_container_width=True):
            st.session_state.exam = {"running": False}

    ex = st.session_state.exam
    if ex.get("running"):
        elapsed = int(time.time() - ex["start_ts"])
        left = max(0, ex["limit_sec"] - elapsed)

        st.write(f"⏳ Kalan süre: **{left//60:02d}:{left%60:02d}**")
        st.progress(1 - (left / ex["limit_sec"]) if ex["limit_sec"] else 0)

        if left == 0:
            ex["running"] = False
            save_stats(ex["correct"], ex["total"])
            st.error(f"⏰ Süre bitti! Skor: {ex['correct']}/{ex['total']}")
        else:
            if ex["i"] < ex["total"]:
                if ex["current"] is None:
                    bone = pick_bone(ex["pool"]) if ex["pool"] else random.choice(BONES)
                    q, ans, mode = make_question(bone)
                    ex["current"] = {"bone": bone, "q": q, "ans": ans, "mode": mode}

                cur = ex["current"]
                bone = cur["bone"]

                st.write(f"**Soru {ex['i'] + 1}/{ex['total']}**")
                st.info(cur["q"])
                user = st.text_input("Cevabın", key=f"exam_answer_{ex['i']}")

                if st.button("✅ Cevapla (Exam)", use_container_width=True):
                    ok = check_answer(cur["mode"], bone, user, cur["ans"])
                    if ok:
                        ex["correct"] += 1
                        st.success("✅")
                    else:
                        st.error(f"❌ Doğru: {cur['ans']}")
                        log_wrong(cur["q"], user, cur["ans"])

                    ex["i"] += 1
                    ex["current"] = None

                    if ex["i"] >= ex["total"]:
                        ex["running"] = False
                        save_stats(ex["correct"], ex["total"])
                        st.success(f"🏁 Exam bitti! Skor: {ex['correct']}/{ex['total']}")
            else:
                ex["running"] = False
                save_stats(ex["correct"], ex["total"])
                st.success(f"🏁 Exam bitti! Skor: {ex['correct']}/{ex['total']}")

# ---------- REVIEW ----------
with tab_review:
    st.subheader("🧾 Review (Yanlışlar)")
    wrongs = load_wrongs()

    if not wrongs:
        st.write("Henüz yanlış yok. Ya çok iyisin ya da hiç denemedin. 😌")
    else:
        st.caption("Doğru yapınca o kart otomatik olarak listeden düşer.")
        # review state
        if "rev" not in st.session_state:
            st.session_state.rev = {"idx": 0, "pool": wrongs[:]}

        if st.button("🔁 Review sıfırla"):
            st.session_state.rev = {"idx": 0, "pool": load_wrongs()[:]}

        rev = st.session_state.rev
        pool = rev["pool"]

        if rev["idx"] >= len(pool):
            st.success("Review bitti. (Yanlışları ezdik.)")
        else:
            q, old_user, correct = pool[rev["idx"]]
            st.info(q)
            st.caption(f"Önceki cevabın: {old_user}")
            user = st.text_input("Şimdi cevapla", key=f"rev_answer_{rev['idx']}")

            cols = st.columns(2)
            with cols[0]:
                if st.button("✅ Kontrol et", use_container_width=True):
                    if user.strip().lower() == correct.strip().lower():
                        st.success("✅ Doğru! Listeden düştü.")
                        # bu elemanı wrong dosyasından çıkar
                        current_all = load_wrongs()
                        # sadece ilk eşleşeni sil (aynı soru tekrar kaydolmuş olabilir)
                        removed = False
                        new_all = []
                        for item in current_all:
                            if not removed and item[0] == q and item[2] == correct:
                                removed = True
                                continue
                            new_all.append(item)
                        overwrite_wrongs(new_all)

                        rev["idx"] += 1
                    else:
                        st.error(f"❌ Hâlâ yanlış. Doğru: {correct}")
                        # güncel cevabı kaydet (eskiyi replace etmek için dosyayı yeniden yazıyoruz)
                        current_all = load_wrongs()
                        updated = False
                        new_all = []
                        for item in current_all:
                            if not updated and item[0] == q and item[2] == correct:
                                new_all.append((q, user, correct))
                                updated = True
                            else:
                                new_all.append(item)
                        overwrite_wrongs(new_all)

                        rev["idx"] += 1

            with cols[1]:
                if st.button("⏭️ Atla", use_container_width=True):
                    rev["idx"] += 1
