import json
import random
import time
from datetime import date
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Skull Trainer", page_icon="🧠", layout="centered")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_DB = DATA_DIR / "users.json"  # user-specific storage

ASSETS_DIR = Path("assets/bones")

MOBILE_CSS = """
<style>
/* Streamlit theme variables:
   --background-color, --secondary-background-color, --text-color, --primary-color */

:root{
  --card-radius: 16px;
}

/* Genel container: tema neyse ona uy */
.block-container{
  padding-top: 1.2rem;
  padding-bottom: 3rem;
  max-width: 900px;
}

/* Kart hissi (her iki temada da güzel) */
[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius: var(--card-radius) !important;
}

/* Butonlar: primary rengi kullanır, her temada uyumlu */
.stButton button{
  border-radius: 16px !important;
  padding: 0.75rem 1.1rem !important;
  font-weight: 700 !important;
  border: 1px solid rgba(127,127,127,0.25) !important;
}

/* Input'lar */
div[data-baseweb="input"] input{
  border-radius: 14px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"]{
  font-size: 1.05rem;
  font-weight: 700;
}

/* --- LIGHT THEME OVERRIDES --- */
@media (prefers-color-scheme: light){
  .block-container{
    background: linear-gradient(180deg, rgba(245,250,255,1) 0%, rgba(238,244,255,1) 100%);
  }
  h1{ color: #1f2fbf; font-weight: 800; }
  .stButton button{
    background: linear-gradient(135deg, #4f6cff, #6ea8ff) !important;
    color: white !important;
    box-shadow: 0 6px 14px rgba(79,108,255,0.35);
  }
  div[data-baseweb="input"] input{
    border: 2px solid rgba(79,108,255,0.28) !important;
  }
}

/* --- DARK THEME OVERRIDES --- */
@media (prefers-color-scheme: dark){
  .block-container{
    background: radial-gradient(1200px 600px at 20% 0%, rgba(90,110,255,0.18), transparent 50%),
                radial-gradient(900px 500px at 90% 20%, rgba(60,200,255,0.12), transparent 50%);
  }
  h1{ color: #dbe6ff; font-weight: 800; }
  .stButton button{
    background: linear-gradient(135deg, #3f5bff, #2bd6ff) !important;
    color: #071018 !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    border: none !important;
  }
  div[data-baseweb="input"] input{
    border: 2px solid rgba(43,214,255,0.22) !important;
  }
}
</style>
"""


st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# -------------------- DATA --------------------
BONES = [
    {"name": "Frontal",   "latin": "Os frontale",   "category": "neurocranium",
     "landmarks": ["Supraorbital foramen", "Glabella", "Frontal sinus"]},
    {"name": "Parietal",  "latin": "Os parietale",  "category": "neurocranium",
     "landmarks": ["Parietal foramen", "Superior temporal line"]},
    {"name": "Temporal",  "latin": "Os temporale",  "category": "neurocranium",
     "landmarks": ["Mastoid process", "Styloid process", "External acoustic meatus", "Carotid canal"]},
    {"name": "Occipital", "latin": "Os occipitale", "category": "neurocranium",
     "landmarks": ["Foramen magnum", "Occipital condyles", "External occipital protuberance", "Hypoglossal canal"]},
    {"name": "Sphenoid",  "latin": "Os sphenoidale","category": "neurocranium",
     "landmarks": ["Sella turcica", "Optic canal", "Superior orbital fissure", "Foramen rotundum", "Foramen ovale", "Foramen spinosum"]},
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

# Cranial nerves & foramina (Kurul modu)
CN_FORAMINA = [
    {"cn": "CN I",  "name": "Olfactory",      "foramen": "Cribriform plate"},
    {"cn": "CN II", "name": "Optic",          "foramen": "Optic canal"},
    {"cn": "CN III","name": "Oculomotor",     "foramen": "Superior orbital fissure"},
    {"cn": "CN IV", "name": "Trochlear",      "foramen": "Superior orbital fissure"},
    {"cn": "CN V1", "name": "Ophthalmic",     "foramen": "Superior orbital fissure"},
    {"cn": "CN V2", "name": "Maxillary",      "foramen": "Foramen rotundum"},
    {"cn": "CN V3", "name": "Mandibular",     "foramen": "Foramen ovale"},
    {"cn": "CN VI", "name": "Abducens",       "foramen": "Superior orbital fissure"},
    {"cn": "CN VII","name": "Facial",         "foramen": "Internal acoustic meatus"},
    {"cn": "CN VIII","name":"Vestibulocochlear","foramen":"Internal acoustic meatus"},
    {"cn": "CN IX", "name": "Glossopharyngeal","foramen": "Jugular foramen"},
    {"cn": "CN X",  "name": "Vagus",          "foramen": "Jugular foramen"},
    {"cn": "CN XI", "name": "Accessory",      "foramen": "Jugular foramen"},
    {"cn": "CN XII","name": "Hypoglossal",    "foramen": "Hypoglossal canal"},
    {"cn": "CN VII (exit)", "name":"Facial (exit)", "foramen":"Stylomastoid foramen"},
]

# -------------------- USER ID (per-user, not mixed) --------------------
def short_id(n=8):
    alphabet = "abcdefghijkmnpqrstuvwxyz23456789"
    return "".join(random.choice(alphabet) for _ in range(n))

def get_user_id():
    # Streamlit query params: user-specific id in URL (?u=xxxx)
    qp = st.query_params
    if "u" in qp and str(qp["u"]).strip():
        return str(qp["u"]).strip()
    uid = short_id()
    st.query_params["u"] = uid
    return uid

USER_ID = get_user_id()

# -------------------- STORAGE --------------------
def _load_users_db() -> dict:
    if not USERS_DB.exists():
        return {}
    try:
        return json.loads(USERS_DB.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_users_db(db: dict) -> None:
    USERS_DB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def get_user_record(uid: str) -> dict:
    db = _load_users_db()
    if uid not in db:
        db[uid] = {
            "stats": {"correct": 0, "total": 0},
            "wrongs": [],  # list of {q,user,correct,ts}
        }
        _save_users_db(db)
    return db[uid]

def update_user_record(uid: str, record: dict) -> None:
    db = _load_users_db()
    db[uid] = record
    _save_users_db(db)

def add_stats(uid: str, correct_delta: int, total_delta: int) -> None:
    rec = get_user_record(uid)
    rec["stats"]["correct"] += int(correct_delta)
    rec["stats"]["total"] += int(total_delta)
    update_user_record(uid, rec)

def log_wrong(uid: str, q: str, user: str, correct: str) -> None:
    rec = get_user_record(uid)
    rec["wrongs"].append({"q": q, "user": user, "correct": correct, "ts": int(time.time())})
    update_user_record(uid, rec)

def get_wrongs(uid: str):
    return get_user_record(uid)["wrongs"]

def clear_wrongs(uid: str):
    rec = get_user_record(uid)
    rec["wrongs"] = []
    update_user_record(uid, rec)

def reset_stats(uid: str):
    rec = get_user_record(uid)
    rec["stats"] = {"correct": 0, "total": 0}
    update_user_record(uid, rec)

def export_progress(uid: str) -> str:
    rec = get_user_record(uid)
    payload = {"uid": uid, "exported_at": int(time.time()), "data": rec}
    return json.dumps(payload, ensure_ascii=False, indent=2)

def import_progress(uid: str, json_text: str) -> tuple[bool, str]:
    try:
        payload = json.loads(json_text)
        data = payload.get("data")
        if not isinstance(data, dict):
            return False, "JSON formatı tanınmadı. (data yok)"
        if "stats" not in data or "wrongs" not in data:
            return False, "JSON formatı tanınmadı. (stats/wrongs eksik)"
        if not isinstance(data["stats"], dict) or not isinstance(data["wrongs"], list):
            return False, "JSON formatı bozuk."
        update_user_record(uid, data)
        return True, "Import tamam ✅"
    except json.JSONDecodeError:
        return False, "JSON okunamadı. (format hatalı)"
    except Exception:
        return False, "Import sırasında beklenmeyen hata oldu."


# -------------------- HELPERS --------------------
def bone_image_path(bone_name: str):
    p_png = ASSETS_DIR / f"{bone_name.lower()}.png"
    p_jpg = ASSETS_DIR / f"{bone_name.lower()}.jpg"
    if p_png.exists():
        return p_png
    if p_jpg.exists():
        return p_jpg
    return None

def wrong_weights(pool_names: list[str]) -> dict:
    """
    Wrong listesindeki kemik adı soru içinde geçiyorsa o kemiğin ağırlığını artır.
    """
    weights = {name: 1 for name in pool_names}
    for item in get_wrongs(USER_ID):
        q = item["q"].lower()
        for name in pool_names:
            if name.lower() in q:
                weights[name] += 3
    return weights

def pick_weighted(pool: list[dict]) -> dict:
    names = [b["name"] for b in pool]
    wmap = wrong_weights(names)
    weights = [wmap[b["name"]] for b in pool]
    return random.choices(pool, weights=weights, k=1)[0]

def make_bone_question(bone: dict):
    mode = random.choice(["latin", "category", "landmark"])
    if mode == "latin":
        return f"**{bone['name']}** kemiğinin Latin adı nedir?", bone["latin"], mode
    if mode == "category":
        return f"**{bone['name']}** hangi kategori? (neurocranium / viscerocranium)", bone["category"], mode
    example = random.choice(bone["landmarks"]) if bone["landmarks"] else ""
    return f"**{bone['name']}** ile ilişkili landmark yaz (örn: {example})", " / ".join(bone["landmarks"]), mode

def check_bone_answer(mode: str, bone: dict, user: str, correct: str) -> bool:
    u = user.strip().lower()
    if not u:
        return False
    if mode == "landmark":
        return u in {x.lower() for x in bone["landmarks"]}
    return u == correct.lower()

def make_cn_question():
    item = random.choice(CN_FORAMINA)
    style = random.choice(["cn_to_foramen", "foramen_to_cn"])
    if style == "cn_to_foramen":
        q = f"**{item['cn']} ({item['name']})** hangi yapıdan geçer?"
        a = item["foramen"]
        return q, a, style
    else:
        q = f"**{item['foramen']}** içinden geçen sinir hangisi?"
        a = f"{item['cn']} ({item['name']})"
        return q, a, style

def check_cn_answer(style: str, user: str, correct: str) -> bool:
    u = user.strip().lower()
    if not u:
        return False
    # foramen->cn sorusunda kullanıcı "CN X" yazsa da kabul edelim
    if style == "foramen_to_cn":
        return u in correct.lower() or u.replace(" ", "") in correct.lower().replace(" ", "")
    return u == correct.lower()

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚙️ Controls")
base_url = "https://skull-trainer-nehir.streamlit.app"
personal_link = f"{base_url}?u={USER_ID}"
st.sidebar.code(personal_link)

st.sidebar.write("**Kullanıcı kodun:**")
st.sidebar.code(USER_ID)

st.sidebar.divider()
st.sidebar.write("**Export / Import**")
export_text = export_progress(USER_ID)
st.sidebar.download_button(
    "⬇️ Progress indir (JSON)",
    data=export_text,
    file_name="skull_trainer_progress.json",
    mime="application/json",
    use_container_width=True,
)

import_box = st.sidebar.text_area("⬆️ JSON yapıştır (Import)", height=120, placeholder="Buraya export JSON'u yapıştır...")
if st.sidebar.button("Import et", use_container_width=True):
    if not import_box.strip():
        st.sidebar.warning("Önce JSON yapıştır 😄")
    else:
        ok, msg = import_progress(USER_ID, import_box)
        if ok:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

# -------------------- UI --------------------
st.title("🧠 Skull Trainer Web App")

tabs = st.tabs(["Skull Quiz", "Exam", "CN Foraminal", "Review", "Stats"])

# ---------- SKULL QUIZ ----------
with tabs[0]:
    st.subheader("Skull Quiz (Öğrenen Mod)")
    c1, c2 = st.columns(2)
    with c1:
        n_q = st.number_input("Soru sayısı", 1, 50, 10)
    with c2:
        focus = st.selectbox("Kategori", ["hepsi", "neurocranium", "viscerocranium"])
    show_img = st.toggle("Görsel göster (assets varsa)", value=True)

    if "skull" not in st.session_state:
        st.session_state.skull = {"running": False}

    def start_skull():
        pool = BONES[:]
        if focus != "hepsi":
            pool = [b for b in pool if b["category"] == focus]
        st.session_state.skull = {"running": True, "pool": pool, "i": 0, "total": int(n_q), "correct": 0, "cur": None}

    st.button("🚀 Yeni Quiz Başlat", on_click=start_skull, use_container_width=True)

    s = st.session_state.skull
    if s.get("running"):
        if s["i"] >= s["total"]:
            s["running"] = False
            add_stats(USER_ID, s["correct"], s["total"])
            st.balloons()
            st.success(f"🏁 Bitti! Skor: {s['correct']}/{s['total']}")
        else:
            if s["cur"] is None:
                bone = pick_weighted(s["pool"]) if s["pool"] else random.choice(BONES)
                q, ans, mode = make_bone_question(bone)
                s["cur"] = {"bone": bone, "q": q, "ans": ans, "mode": mode}

            cur = s["cur"]
            bone = cur["bone"]
            st.progress((s["i"] + 1) / s["total"])
            st.caption(f"✨ XP: {s['correct']*10}  |  🎯 Accuracy: {(s['correct']/max(1,s['i']))*100:.0f}%")
            st.info(cur["q"])

            if show_img:
                img = bone_image_path(bone["name"])
                if img:
                    st.image(str(img), use_container_width=True)
                else:
                    st.caption("🖼️ Görsel yok. (assets/bones içine eklersen otomatik çıkar.)")

            user = st.text_input("Cevabın", key=f"sk_ans_{s['i']}")
            colA, colB = st.columns(2)
            with colA:
                if st.button("✅ Cevapla", use_container_width=True):
                    ok = check_bone_answer(cur["mode"], bone, user, cur["ans"])
                    if ok:
                        s["correct"] += 1
                        st.success("Doğru ✅")
st.toast("🔥 Nice! +10 XP", icon="🧠")
                    else:
                        st.toast("😈 Almost. Review’e düştü.", icon="📌")
                        log_wrong(USER_ID, cur["q"], user, cur["ans"])
                    s["i"] += 1
                    s["cur"] = None
            with colB:
                if st.button("⏭️ Pas", use_container_width=True):
                    s["i"] += 1
                    s["cur"] = None

# ---------- EXAM ----------
with tabs[1]:
    st.subheader("Exam Mode (Zamanlı)")
    c1, c2, c3 = st.columns(3)
    with c1:
        exam_q = st.number_input("Soru", 5, 60, 20)
    with c2:
        minutes = st.number_input("Süre (dk)", 1, 60, 5)
    with c3:
        exam_focus = st.selectbox("Kategori (exam)", ["hepsi", "neurocranium", "viscerocranium"])

    if "exam" not in st.session_state:
        st.session_state.exam = {"running": False}

    def start_exam():
        pool = BONES[:]
        if exam_focus != "hepsi":
            pool = [b for b in pool if b["category"] == exam_focus]
        st.session_state.exam = {
            "running": True, "pool": pool, "i": 0, "total": int(exam_q), "correct": 0,
            "cur": None, "start": time.time(), "limit": int(minutes) * 60
        }

    colA, colB = st.columns(2)
    with colA:
        st.button("🧪 Exam başlat", on_click=start_exam, use_container_width=True)
    with colB:
        if st.button("🛑 Durdur", use_container_width=True):
            st.session_state.exam = {"running": False}

    e = st.session_state.exam
    if e.get("running"):
        elapsed = int(time.time() - e["start"])
        left = max(0, e["limit"] - elapsed)
        st.write(f"⏳ Kalan süre: **{left//60:02d}:{left%60:02d}**")
        st.progress(1 - (left / e["limit"]) if e["limit"] else 0)

        if left == 0 or e["i"] >= e["total"]:
            e["running"] = False
            add_stats(USER_ID, e["correct"], e["total"])
            st.error(f"🏁 Exam bitti! Skor: {e['correct']}/{e['total']}")
        else:
            if e["cur"] is None:
                bone = pick_weighted(e["pool"]) if e["pool"] else random.choice(BONES)
                q, ans, mode = make_bone_question(bone)
                e["cur"] = {"bone": bone, "q": q, "ans": ans, "mode": mode}

            cur = e["cur"]
            bone = cur["bone"]
            st.write(f"**Soru {e['i']+1}/{e['total']}**")
            st.info(cur["q"])
            user = st.text_input("Cevabın", key=f"ex_ans_{e['i']}")
            if st.button("✅ Cevapla (Exam)", use_container_width=True):
                ok = check_bone_answer(cur["mode"], bone, user, cur["ans"])
                if ok:
                    e["correct"] += 1
                    st.success("✅")
                else:
                    st.error(f"❌ Doğru: {cur['ans']}")
                    log_wrong(USER_ID, cur["q"], user, cur["ans"])
                e["i"] += 1
                e["cur"] = None

# ---------- CN FORAMINA ----------
with tabs[2]:
    st.subheader("CN Foraminal Mode (Kurul)")
    st.caption("Cranial nerves ve foramina ezberi. Ağlatır ama kazandırır.")

    if "cn" not in st.session_state:
        st.session_state.cn = {"running": False}

    def start_cn():
        st.session_state.cn = {"running": True, "i": 0, "total": 15, "correct": 0, "cur": None}

    st.button("⚡ CN Quiz Başlat", on_click=start_cn, use_container_width=True)

    cn = st.session_state.cn
    if cn.get("running"):
        if cn["i"] >= cn["total"]:
            cn["running"] = False
            add_stats(USER_ID, cn["correct"], cn["total"])
            st.success(f"🏁 CN bitti! Skor: {cn['correct']}/{cn['total']}")
        else:
            if cn["cur"] is None:
                q, a, style = make_cn_question()
                cn["cur"] = {"q": q, "a": a, "style": style}

            cur = cn["cur"]
            st.write(f"**Soru {cn['i']+1}/{cn['total']}**")
            st.info(cur["q"])
            user = st.text_input("Cevabın", key=f"cn_ans_{cn['i']}")

            colA, colB = st.columns(2)
            with colA:
                if st.button("✅ Cevapla (CN)", use_container_width=True):
                    ok = check_cn_answer(cur["style"], user, cur["a"])
                    if ok:
                        cn["correct"] += 1
                        st.success("Doğru ✅")
                    else:
                        st.error(f"Yanlış ❌ Doğru: {cur['a']}")
                        log_wrong(USER_ID, cur["q"], user, cur["a"])
                    cn["i"] += 1
                    cn["cur"] = None
            with colB:
                if st.button("⏭️ Pas (CN)", use_container_width=True):
                    cn["i"] += 1
                    cn["cur"] = None

# ---------- REVIEW ----------
with tabs[3]:
    st.subheader("Review (Sana özel)")
    wrongs = get_wrongs(USER_ID)

    if not wrongs:
        st.write("Henüz yanlış yok. Ya efsanesin ya da hiç zorlamadın. 😌")
    else:
        st.caption("Yanlış havuzu sadece sana ait. Arkadaşların seni sabote edemiyor, üzgünüm.")
        # Son 20 yanlış
        for item in list(reversed(wrongs[-20:])):
            st.warning(item["q"])
            st.write(f"Sen: **{item['user']}**")
            st.write(f"Doğru: **{item['correct']}**")
            st.divider()

        colA, colB = st.columns(2)
        with colA:
            if st.button("🧽 Yanlışları temizle", use_container_width=True):
                clear_wrongs(USER_ID)
                st.success("Temizlendi. Yeni hayat.")
        with colB:
            st.caption("İstersen Export ile arkadaşına kendi progress’ını bile yollarsın.")

# ---------- STATS ----------
with tabs[4]:
    st.subheader("Stats (Sana özel)")
    rec = get_user_record(USER_ID)
st.metric("🔥 Streak", rec.get("streak", 0))
    c = rec["stats"]["correct"]
    t = rec["stats"]["total"]
    st.metric("Toplam Doğru / Toplam Soru", f"{c}/{t}")
    if t:
        st.progress(c / t)

    colA, colB = st.columns(2)
    with colA:
        if st.button("🧹 Stats sıfırla", use_container_width=True):
            reset_stats(USER_ID)
            st.success("Sıfırlandı.")
  
def bump_streak(uid: str):
    rec = get_user_record(uid)
    today = str(date.today())
    last = rec.get("last_day")
    streak = int(rec.get("streak", 0))

    if last == today:
        rec["streak"] = streak
    else:
        # dün müydü? (basit yaklaşım)
        # eğer dün değilse streak sıfırlanır
        rec["streak"] = streak + 1 if last else 1
        rec["last_day"] = today

    update_user_record(uid, rec)
         

