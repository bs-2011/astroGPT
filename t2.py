# Cosmic Guide — v2.1 (Streamlit)
# Modernized UI + richer logic + Tarot + Numerology + Daily Banners
# ——— Patch: fixes Streamlit time_input step error, adds seconds selector,
# improves high-contrast inputs/labels on dark background.

import os
from datetime import date, datetime, timedelta, time as dt_time
import random
from typing import Dict, List, Tuple

import streamlit as st

# OpenAI (new SDK style)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ---------------------------
# ---------- THEME ----------
# ---------------------------
st.set_page_config(
    page_title="Cosmic Guide — AI Spiritual Companion",
    page_icon="✨",
    layout="wide",
)

# High-contrast, modern CSS
st.markdown(
    r"""
<style>
  :root {
    --bg: #0b0b12;
    --card: #10111a;
    --ink: #f2f2f7;
    --sub: #c6c7d6;
    --accent: #8D72E1;
    --accent-2: #6C4AB6;
    --ok: #34d399;
    --warn: #f59e0b;
    --line: #2a2b44;
    --field: #15162a;
  }
  .stApp { background: radial-gradient(1200px 800px at 10% 10%, #121222, var(--bg)) !important; }
  h1, h2, h3, h4, h5, h6 { color: var(--ink) !important; }
  .subtle { color: var(--sub) !important; }
  .card { background: linear-gradient(180deg, #141528 0%, #0e0f19 100%); border: 1px solid var(--line); border-radius: 16px; padding: 18px 18px; box-shadow: 0 8px 24px rgba(0,0,0,.35); }
  .banner { background: linear-gradient(90deg, rgba(141,114,225,.18), rgba(108,74,182,.18)); border: 1px solid rgba(141,114,225,.35); padding: 14px 18px; border-radius: 14px; }
  .chip { display:inline-block; padding:6px 12px; border:1px solid var(--line); border-radius:999px; margin:2px 6px 0 0; color:var(--ink); font-size:.85rem; }
  .chip.badge { background: #191a2c; }
  .pill { display:inline-block; padding:8px 14px; border-radius:999px; background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%); color:white; font-weight:600; }
  .assistant { background:#0f1020; border:1px solid var(--line); border-radius:14px; padding:12px 14px; color:var(--ink); }
  .user { background:linear-gradient(135deg, #6C4AB6, #8D72E1); color:white; border-radius:14px; padding:12px 14px; }
  .horo-card { background:#0f1020; border:1px solid var(--line); padding:12px 12px; border-radius:12px; height:100%; color:var(--ink); }
  .small { font-size:.9rem; }

  /* Sidebar visuals */
  section[data-testid="stSidebar"] { background:#0f1020 !important; border-right:1px solid var(--line); }

  /* Make inputs readable on dark bg */
  input, textarea { background-color: var(--field) !important; color: var(--ink) !important; border: 1px solid var(--line) !important; }
  div[role="radiogroup"] label, label p, label { color: var(--ink) !important; }
  div[data-baseweb="select"] > div { background-color: var(--field) !important; border: 1px solid var(--line) !important; color: var(--ink) !important; }
  .stDateInput input, .stTimeInput input, .stNumberInput input { background-color: var(--field) !important; color: var(--ink) !important; border: 1px solid var(--line) !important; }
  .stButton>button { background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%); color: white; border: 1px solid rgba(255,255,255,.15); border-radius: 12px; box-shadow: 0 6px 16px rgba(108,74,182,.35); }
  .stButton>button:hover { filter: brightness(1.06); }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# ------- SESSION ------------
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict] = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_ok" not in st.session_state:
    st.session_state.api_ok = False
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "daily_cache" not in st.session_state:
    st.session_state.daily_cache = {}
if "birth_seconds" not in st.session_state:
    st.session_state.birth_seconds = 0

MODEL = os.environ.get("COSMIC_MODEL", "gpt-4o-mini")  # swap as needed

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ---------------------------
# ------ UTILITIES ----------
# ---------------------------

def require_openai():
    if OpenAI is None:
        st.error("OpenAI SDK not found. Install with: pip install openai>=1.0.0")
        return None
    if not st.session_state.api_key:
        st.error("Add your OpenAI API key in the sidebar to use AI features.")
        return None
    try:
        return OpenAI(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"OpenAI init failed: {e}")
        return None


def llm(client: "OpenAI", system: str, user: str, temperature: float = 0.7) -> str:
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"LLM call failed: {e}")
        return ""


def calc_life_path(d: date) -> int:
    s = sum(int(ch) for ch in d.strftime("%Y%m%d"))
    while s not in (11, 22, 33) and s > 9:
        s = sum(int(ch) for ch in str(s))
    return s

TAROT = {
    "The Fool": ("new beginnings, leap of faith", "recklessness, naivety"),
    "The Magician": ("manifestation, skill, willpower", "manipulation, untapped potential"),
    "The High Priestess": ("intuition, hidden knowledge", "secrets, disconnected self"),
    "The Empress": ("abundance, nurture, creation", "dependence, creative block"),
    "The Emperor": ("structure, leadership", "rigidity, control"),
    "The Hierophant": ("tradition, guidance", "rebellion, new paths"),
    "The Lovers": ("union, choices, values alignment", "disharmony, difficult choices"),
    "The Chariot": ("drive, victory", "scattered energy, lack of control"),
    "Strength": ("courage, compassion, inner power", "self-doubt, raw emotion"),
    "The Hermit": ("introspection, wisdom", "isolation, withdrawal"),
    "Wheel of Fortune": ("cycles, luck, change", "resistance to change"),
    "Justice": ("truth, fairness, law", "bias, unfairness"),
    "The Hanged Man": ("surrender, new perspective", "stalling, martyrdom"),
    "Death": ("endings → rebirth", "resistance, stagnation"),
    "Temperance": ("balance, healing", "excess, discord"),
    "The Devil": ("attachments, materialism", "release, awareness"),
    "The Tower": ("sudden change, revelation", "avoidance of upheaval"),
    "The Star": ("hope, renewal", "doubt, fade of faith"),
    "The Moon": ("intuition, the unknown", "fear, confusion"),
    "The Sun": ("joy, clarity, success", "temporary gloom, arrogance"),
    "Judgement": ("awakening, reckoning", "self-doubt, harsh self-judgment"),
    "The World": ("completion, integration", "unfinished business"),
}


def draw_tarot(n: int) -> List[Tuple[str, str]]:
    cards = random.sample(list(TAROT.keys()), k=n)
    out = []
    for c in cards:
        orientation = random.choice(["upright", "reversed"])  # 50/50
        out.append((c, orientation))
    return out

EXPECTATIONS = {
    "The Vedic Guru": {
        "Expect": "Planet-focused insight (Sun/Moon/Dasha), 2–3 practical remedies + timing cues.",
        "BestFor": "Career timing, relationships, remedies, month vibe.",
        "Tone": "Warm, precise, Melooha-like; short, poetic lines; no fatalism."},
    "The Tarot Reader": {
        "Expect": "Card-by-card story; emotional framing + 2 concrete actions.",
        "BestFor": "Crossroads, feelings/energy check, near-term nudges.",
        "Tone": "Empathic, metaphor-rich, grounded."},
    "The Modern Life Coach": {
        "Expect": "Clear steps, SMART goals, micro-commitments.",
        "BestFor": "Career pivots, habits, productivity.",
        "Tone": "Straight-talking, actionable."},
}

PERSONA_PROMPTS = {
    "The Vedic Guru": (
        "You are a compassionate, Melooha-style Vedic guide. Be warm, specific and non-generic. "
        "If birth time is unknown, avoid house-level claims. Give 2–3 practical remedies and 3 concrete actions. "
        "No superstition. No absolutes."
    ),
    "The Tarot Reader": (
        "You are an intuitive tarot reader. Weave a brief narrative based on drawn cards (if any). "
        "Offer 2 grounded actions. Avoid fatalism; empower the user."
    ),
    "The Modern Life Coach": (
        "You are a crisp life coach. Mirror the user's goal, ask one clarifying question only if essential, "
        "then deliver a numbered mini-plan with deadlines and metrics."
    ),
}

# ---------------------------
# ------- DAILY CONTENT ------
# ---------------------------

def get_today_key() -> str:
    return date.today().isoformat()


def daily_banner(client: "OpenAI") -> Dict[str, str]:
    key = (get_today_key(), "banner")
    if key in st.session_state.daily_cache:
        return st.session_state.daily_cache[key]
    prompt = (
        "Give a 3–4 line, upbeat 'Today at a glance' for Indian audience: "
        "mention weekday meaning (neutral), a gentle intention, and a one-liner for career/love/health."
    )
    text = llm(client, "You write concise, friendly newspaper banners.", prompt, temperature=0.6)
    out = {"text": text}
    st.session_state.daily_cache[key] = out
    return out


def daily_horoscopes(client: "OpenAI") -> Dict[str, str]:
    key = (get_today_key(), "horos")
    if key in st.session_state.daily_cache:
        return st.session_state.daily_cache[key]
    prompt = (
        "Write newspaper-style daily horoscopes for the 12 zodiac signs (Aries..Pisces). "
        "One crisp sentence each, max 22 words, actionable and non-fatalistic. Prefix each line with 'Sign:'."
    )
    text = llm(client, "You are a witty horoscope columnist.", prompt, temperature=0.8)
    out: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            head, body = line.split(":", 1)
            k = head.strip().replace("**", "")
            v = body.strip().strip("- ")
            if k in SIGNS and v:
                out[k] = v
    for s in SIGNS:
        out.setdefault(s, "Take a mindful pause, choose one tiny step that improves your day.")
    st.session_state.daily_cache[key] = out
    return out

# ---------------------------
# --------- SIDEBAR ---------
# ---------------------------

def sidebar():
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3>✨ Cosmic Guide</h3><p class='subtle'>Your AI spiritual companion</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        api = st.text_input("OpenAI API key", type="password", help="Kept only for this session.")
        if api:
            st.session_state.api_key = api
            st.session_state.api_ok = True
            st.success("API key saved.")

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>🧘 Your Cosmic Profile</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.get("user_name", ""))
            gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Non-binary", "Other"], index=0)
        with col2:
            dob = st.date_input("Date of Birth", value=st.session_state.get("dob", date(1995,1,1)))
            unknown_time = st.checkbox("I don't know my birth time", value=st.session_state.get("unknown_time", False))

        # Birth time: Streamlit enforces step >= 60s; we add a seconds selector to reach HH:MM:SS
        if not unknown_time:
            base_default = st.session_state.get("birth_time", datetime.strptime("12:00:00", "%H:%M:%S").time())
            base_time = st.time_input(
                "Time of Birth (HH:MM)",
                value=dt_time(base_default.hour, base_default.minute),
                step=timedelta(minutes=1),  # ✅ avoids Streamlit step error
            )
            seconds = st.number_input("Seconds", min_value=0, max_value=59, value=int(st.session_state.get("birth_seconds", 0)))
            bt = dt_time(base_time.hour, base_time.minute, int(seconds))
        else:
            bt = None
            seconds = st.session_state.get("birth_seconds", 0)

        place = st.text_input("Place of Birth (City, Country)", value=st.session_state.get("birth_place", ""))

        st.session_state.update({
            "user_name": name,
            "gender": gender,
            "dob": dob,
            "unknown_time": unknown_time,
            "birth_time": bt,
            "birth_place": place,
            "birth_seconds": seconds,
        })

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# -------- HOME PAGE --------
# ---------------------------

def page_home():
    client = require_openai()
    st.markdown("# 🌌 Cosmic Guide")
    st.markdown("<div class='banner'>Discover personalized spiritual guidance through a friendly AI. Choose a guide, ask a question, and get specific, human-like answers — not generic fluff.</div>", unsafe_allow_html=True)

    if client:
        ban = daily_banner(client)
        st.markdown("\n### Today at a glance")
        st.markdown(f"<div class='card'>{ban['text']}</div>", unsafe_allow_html=True)

        st.markdown("\n### Newspaper-style daily horoscopes")
        data = daily_horoscopes(client)
        rows = [SIGNS[i:i+4] for i in range(0, len(SIGNS), 4)]
        for row in rows:
            cols = st.columns(len(row))
            for s, c in zip(row, cols):
                with c:
                    st.markdown(f"""
                        <div class='horo-card'>
                          <div class='subtle small'>{s}</div>
                          <div style='margin-top:6px'>{data.get(s, '')}</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("\n### Why people use Cosmic Guide")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='card'><b>Specific, kind answers</b><br><span class='subtle small'>Distinct voices; we ask for context and give concrete next steps.</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'><b>Beyond horoscopes</b><br><span class='subtle small'>Tarot, numerology, and coaching — all in one app.</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='card'><b>Privacy-first</b><br><span class='subtle small'>Your data stays in your session; no third-party sharing.</span></div>", unsafe_allow_html=True)

# ---------------------------
# -------- CHAT PAGE --------
# ---------------------------

def persona_card(title: str):
    exp = EXPECTATIONS[title]
    st.markdown(
        f"""
        <div class='card'>
            <div class='pill'>{title}</div>
            <div style='margin-top:10px'><b>What to expect:</b> <span class='subtle'>{exp['Expect']}</span></div>
            <div style='margin-top:6px'><b>Best for:</b> <span class='subtle'>{exp['BestFor']}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_profile() -> str:
    n = st.session_state.get("user_name") or "friend"
    g = st.session_state.get("gender", "")
    dob = st.session_state.get("dob")
    bt = st.session_state.get("birth_time")
    place = st.session_state.get("birth_place", "")
    lp = calc_life_path(dob) if isinstance(dob, date) else ""
    birth_time_str = "unknown" if st.session_state.get("unknown_time") else (bt.strftime("%H:%M:%S") if bt else "unknown")
    return (
        f"Name: {n}. Gender: {g}. DOB: {dob}. Birth time: {birth_time_str}. "
        f"Birth place: {place}. Life Path: {lp}."
    )


def build_system_prompt(guide: str) -> str:
    profile = format_profile()
    accuracy_note = (
        "Birth time unknown → avoid house-level or minute-sensitive claims; prefer themes and actions."
        if st.session_state.get("unknown_time") else
        "You may reference timing/themes, but avoid hard predictions."
    )
    persona = PERSONA_PROMPTS[guide]
    return (
        f"{persona}\n\nContext: {profile}\n{accuracy_note}\n"
        "Rules: No medical/legal advice; be concise but human. Avoid generic platitudes. Use bullets."
    )


def chat_section():
    st.markdown("# 💬 Chat with your Guide")

    colP1, colP2, colP3 = st.columns(3)
    with colP1: persona_card("The Vedic Guru")
    with colP2: persona_card("The Tarot Reader")
    with colP3: persona_card("The Modern Life Coach")

    guide = st.radio("Choose a guide", list(EXPECTATIONS.keys()), horizontal=True)

    st.markdown("<div class='subtle small'>Quick asks:</div>", unsafe_allow_html=True)
    qs = st.container()
    with qs:
        cols = st.columns(6)
        quicks = [
            "Career focus this month",
            "Best business niches for me",
            "Love & relationships guidance",
            "Health & habits to improve",
            "Money mindset & luck cues",
            "One bold risk to take",
        ]
        for i, (c, txt) in enumerate(zip(cols*2, quicks)):
            if c.button(txt, key=f"q_{i}"):
                st.session_state.setdefault("messages", []).append({"role": "user", "content": txt, "guide": guide})

    for m in st.session_state.messages:
        if m.get("guide", guide) != guide:
            continue
        if m["role"] == "user":
            st.markdown(f"<div class='user'><b>You:</b> {m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant'><b>{guide}:</b> {m['content']}</div>", unsafe_allow_html=True)

    q = st.text_input("Ask your question…", placeholder="e.g., Which career paths align with my strengths?")
    left, right = st.columns([1, 6])
    send = left.button("Send")
    clear = right.button("Clear chat")

    if clear:
        st.session_state.messages = []
        st.rerun()

    if send and q:
        st.session_state.messages.append({"role": "user", "content": q, "guide": guide})
        client = require_openai()
        if client:
            with st.spinner("Thinking…"):
                system = build_system_prompt(guide)
                answer = llm(client, system, q, temperature=0.9)
            st.session_state.messages.append({"role": "assistant", "content": answer, "guide": guide})
            st.rerun()

# ---------------------------
# -------- TAROT PAGE -------
# ---------------------------

def page_tarot():
    st.markdown("# 🃏 Tarot Studio")
    spread = st.selectbox("Choose a spread", ["One Card Insight", "Three Card — Past/Present/Future"])  # extend later
    q = st.text_input("Your question (optional)")
    draw = st.button("Draw cards")

    if draw:
        n = 1 if spread.startswith("One") else 3
        cards = draw_tarot(n)
        cols = st.columns(n)
        for (name, orient), c in zip(cards, cols):
            up, rev = TAROT[name]
            meaning = up if orient == "upright" else rev
            c.markdown(f"<div class='card'><b>{name}</b><br><span class='subtle'>{orient}</span><br><div style='margin-top:6px'>{meaning}</div></div>", unsafe_allow_html=True)

        client = require_openai()
        if client:
            joined = ", ".join([f"{n} ({o})" for n, o in cards])
            sys = (
                PERSONA_PROMPTS["The Tarot Reader"]
                + "\nUse the listed cards. Keep it empowering and specific with 2 actions."
            )
            usr = (
                f"Cards drawn: {joined}. "
                f"Question: {q or 'No question provided — give a relevant general insight.'}"
            )
            with st.spinner("Reading cards…"):
                text = llm(require_openai(), sys, usr, temperature=0.9)
            st.markdown(f"<div class='assistant'>{text}</div>", unsafe_allow_html=True)

# ---------------------------
# ------ NUMEROLOGY ----------
# ---------------------------

def page_numerology():
    st.markdown("# 🔢 Numerology")
    dob = st.session_state.get("dob", date(1995,1,1))
    lp = calc_life_path(dob)

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown(f"<div class='card'><div class='pill'>Life Path</div><h2 style='margin-top:8px'>{lp}</h2><div class='subtle small'>DOB: {dob}</div></div>", unsafe_allow_html=True)
    with col2:
        client = require_openai()
        if client:
            brief = llm(
                client,
                "You are a numerology coach. Be concrete and kind.",
                f"Explain Life Path {lp} strengths, blind spots, and 3 practical focus areas this month in 120 words.",
                temperature=0.7,
            )
            st.markdown(f"<div class='card'>{brief}</div>", unsafe_allow_html=True)

# ---------------------------
# ----------- APP -----------
# ---------------------------

def page_home_wrapper():
    page_home()

def chat_section_wrapper():
    chat_section()


def page_about():
    st.markdown("## About Cosmic Guide")
    st.markdown("<div class='card'>We blend ancient wisdom with modern AI. Use responsibly; treat readings as reflective guidance, not certainties.</div>", unsafe_allow_html=True)


# Layout
sidebar()

tabs = st.tabs(["Home", "Chat", "Tarot", "Numerology", "About"])
with tabs[0]:
    page_home_wrapper()
with tabs[1]:
    chat_section_wrapper()
with tabs[2]:
    page_tarot()
with tabs[3]:
    page_numerology()
with tabs[4]:
    page_about()
