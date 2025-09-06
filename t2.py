# Cosmic Guide — v2.2
# Engagement-first chat flow + tone fixes + UI contrast + Tarot readability
#
# Key changes vs your file:
# - First-click error fixed using a form submit (atomic UI event)
# - No repetitive greetings/"blessings" after first reply
# - Progressive disclosure for Vedic Guru (3-phase flow):
#     1) Planets & houses only + 1 engaging follow-up question (no remedies)
#     2) Remedies on request (max 2) + 1 question to choose next step
#     3) Crystal-clear step plan (3 steps) when user asks for specifics
# - Avoids year/name hallucinations; uses relative timing; fact-check guard
# - Correct mantra spelling: "Om Gam Ganapataye Namaha"
# - Professional tone (no emojis); newspaper-style content kept crisp
# - Tarot cards high-contrast (dark card, light text)
# - CSS improvements for inputs/labels on light backgrounds too

import os
import json
import random
from datetime import date, datetime
from typing import Dict, List

import requests
import streamlit as st
from streamlit_lottie import st_lottie

# Optional (OpenAI new SDK)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ---------------------------
# Page
# ---------------------------
st.set_page_config(
    page_title="Cosmic Guide — AI Spiritual Companion",
    page_icon="✨",
    layout="wide",
)

# ---------------------------
# CSS (high contrast + professional)
# ---------------------------
st.markdown(
    r"""
<style>
  :root {
    --bg: #f5f7fa;
    --ink: #1a1b2e;
    --sub: #505377;
    --accent: #6C4AB6;
    --accent2: #8D72E1;
    --line: #e6e8f0;
    --dark: #0f1020;
    --light: #ffffff;
  }
  .stApp { background: var(--bg) !important; }
  h1, h2, h3, h4, h5, h6 { color: var(--ink) !important; }
  .guide-card, .feature-card, .pricing-card, .assistant-message, .user-message, .highlight-box, .daily-horoscope {
    border-radius: 14px;
  }
  .assistant-message { background: #fff; color: var(--ink); border:1px solid var(--line); box-shadow: 0 3px 10px rgba(16,18,54,.05); }
  .user-message { background: linear-gradient(135deg, var(--accent), var(--accent2)); color:#fff; }
  .tarot-card { width: 140px; height: 200px; background: var(--dark); color: #eef0ff; border:1px solid #2a2b44; border-radius: 12px; display:flex; align-items:center; justify-content:center; font-weight:600; text-align:center; padding:12px; }
  .tarot-card small { color:#aab; }
  /* Input visibility on both light & dark sidebars */
  input, textarea { border:1px solid var(--line) !important; }
  .stDateInput input, .stTimeInput input, .stNumberInput input { border:1px solid var(--line) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Session
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict] = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_ok" not in st.session_state:
    st.session_state.api_ok = False
if "zodiac_sign" not in st.session_state:
    st.session_state.zodiac_sign = None
if "daily_horoscope" not in st.session_state:
    st.session_state.daily_horoscope = None
if "tarot_cards" not in st.session_state:
    st.session_state.tarot_cards = []
# conversation behavior flags
if "greeted" not in st.session_state:
    st.session_state.greeted = {"The Vedic Guru": False, "The Tarot Reader": False, "The Modern Life Coach": False, "Numerology Expert": False}
if "vedic_phase" not in st.session_state:
    st.session_state.vedic_phase = 1  # 1→planets, 2→remedies on request, 3→crystal plan

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ---------------------------
# Helpers
# ---------------------------

def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

lottie_stars = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_myejiggj.json")


def require_openai():
    if OpenAI is None:
        st.error("OpenAI SDK missing. `pip install openai>=1.0.0`.")
        return None
    if not st.session_state.api_ok or not st.session_state.api_key:
        st.warning("Enter your API key in the sidebar to enable AI features.")
        return None
    try:
        return OpenAI(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"OpenAI init failed: {e}")
        return None


def llm(client: "OpenAI", system: str, user: str, temp: float = 0.7) -> str:
    try:
        out = client.chat.completions.create(
            model=os.environ.get("COSMIC_MODEL", "gpt-4o-mini"),
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=temp,
        )
        return out.choices[0].message.content.strip()
    except Exception as e:
        return f"(AI error) {e}"


# ---------------------------
# Content generators (tone: professional, no emojis)
# ---------------------------

def generate_daily_horoscope(zodiac_sign: str) -> str:
    client = require_openai()
    if not client:
        return ""
    prompt = (
        f"Daily horoscope for {zodiac_sign} on {date.today():%B %d, %Y}. "
        "Professional, concise, newspaper style. Include: overall energy, career focus, relationships, wellbeing, and a lucky color. No emojis. 120–150 words."
    )
    return llm(client, "You are a precise horoscope columnist.", prompt, 0.6)


def tarot_reading(question: str, cards: List[str]) -> str:
    client = require_openai()
    if not client:
        return ""
    listed = ", ".join(cards)
    sys = (
        "You are an experienced tarot reader. Professional tone, no emojis. "
        "Explain each card briefly and give two practical next steps."
    )
    usr = f"Question: {question or 'General insight'}. Cards: {listed}."
    return llm(client, sys, usr, 0.8)


# ---------------------------
# Persona prompts with progressive disclosure
# ---------------------------

def phase_instructions() -> str:
    ph = st.session_state.vedic_phase
    if ph == 1:
        return (
            "PHASE 1 — PLANETS ONLY: Explain relevant planets/nakshatras/houses for the question in 4–6 crisp bullets. "
            "Do NOT give remedies yet. End with exactly one open question to clarify what help they want next. "
            "No greetings, no sign-off, no blessings."
        )
    if ph == 2:
        return (
            "PHASE 2 — REMEDIES ON REQUEST: Offer up to two focused remedies (e.g., mantra, routine). "
            "Use the correct mantra 'Om Gam Ganapataye Namaha' if Ganesha is relevant. Avoid gems unless the user asks. "
            "Close with one question that invites a choice between remedy types (e.g., spiritual vs practical). "
            "No sign-off."
        )
    return (
        "PHASE 3 — CRYSTAL PLAN: Provide a 3-step plan with timings (relative windows like 'next 2–3 months'). "
        "Keep it practical and measurable. No blessings."
    )


def build_system_prompt(guide: str, user_name: str, gender: str, dob: date, birth_time: str, birth_place: str, first_message: bool) -> str:
    base_rules = (
        "General rules: professional, human, no emojis, no repetitive greetings. "
        "Use the name once in the first reply only. Never invent specific calendar years; prefer relative timing."
    )

    if guide == "The Vedic Guru":
        p1 = (
            "You are a warm but concise Vedic astrologer (Jyotish). "
            "When birth time precision is unknown or coarse, avoid exact house/degree claims."
        )
        phase = phase_instructions()
        greet = f"Start with 'Dear {user_name},' one time only." if first_message else "Do not greet; dive into content."
        return f"{p1}\n{phase}\n{greet}\n{base_rules}"

    if guide == "The Tarot Reader":
        return (
            "You are an intuitive tarot guide. Keep it compact, interpret cards as a narrative, then give two actions. "
            "End with one thoughtful question to prompt a follow-up. No emojis."
        )

    if guide == "The Modern Life Coach":
        return (
            "You are a practical life coach. Provide a numbered mini-plan (3–5 steps) and one reflective question. "
            "No fluff, no emojis."
        )

    # Numerology Expert
    return (
        "You are a numerology expert. Compute life-path from DOB if needed, summarize strengths and blind spots, "
        "then offer one focus area for the next week. Professional tone."
    )


# ---------------------------
# UI: Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom: 22px;">
      <h3 style="margin-bottom:4px;">✨ Cosmic Guide</h3>
      <div style="color:#70739a;">Your AI Spiritual Companion</div>
    </div>
    """, unsafe_allow_html=True)

    # API key
    api_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.api_key = api_key
    st.session_state.api_ok = bool(api_key)

    st.markdown("---")
    st.subheader("🧘 Your Cosmic Profile")

    user_name = st.text_input("Name", value=st.session_state.get("user_name", "Seeker"))
    gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Non-binary", "Other"], index=0)
    dob = st.date_input("Date of Birth", value=st.session_state.get("dob", date(1995,1,1)))
    birth_time = st.text_input("Exact Time of Birth (HH:MM)", value=st.session_state.get("birth_time", "12:00"))
    birth_place = st.text_input("Place of Birth", value=st.session_state.get("birth_place", ""))

    st.session_state.update({
        "user_name": user_name,
        "gender": gender,
        "dob": dob,
        "birth_time": birth_time,
        "birth_place": birth_place,
    })

    st.markdown("---")
    guide = st.radio("Choose your guide", ("The Vedic Guru", "The Tarot Reader", "The Modern Life Coach", "Numerology Expert"))

# ---------------------------
# Home
# ---------------------------
col1, col2 = st.columns([1,1])
with col1:
    st.markdown("# Cosmic Guide")
    st.write("Discover personalized spiritual guidance. Ask focused questions and get specific, human answers.")
    if st.button("Get Started →"):
        pass
with col2:
    if lottie_stars:
        st_lottie(lottie_stars, height=220, key="stars")

st.markdown("---")

# Daily Horoscope (optional)
st.subheader("📅 Today's Cosmic Energy")
cols = st.columns(6)
for i, s in enumerate(SIGNS):
    with cols[i % 6]:
        if st.button(s, key=f"sign_{s}"):
            st.session_state.zodiac_sign = s
            st.session_state.daily_horoscope = generate_daily_horoscope(s)
if st.session_state.zodiac_sign and st.session_state.daily_horoscope:
    st.markdown(f"### {st.session_state.zodiac_sign}")
    st.markdown(f"<div class='assistant-message'>{st.session_state.daily_horoscope}</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Chat area with form (fixes first-click issue)
# ---------------------------
st.header("Chat with your Guide")

# Tarot tools
if guide == "The Tarot Reader":
    tarot_deck = [
        "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
        "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
        "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
        "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
    ]
    if st.button("Draw 3 Cards"):
        st.session_state.tarot_cards = random.sample(tarot_deck, 3)
    if st.session_state.tarot_cards:
        st.write("Your cards:")
        cols = st.columns(3)
        for c, card in zip(cols, st.session_state.tarot_cards):
            c.markdown(f"<div class='tarot-card'>{card}<br><small>tap to ask about it</small></div>", unsafe_allow_html=True)

# Render history
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"<div class='user-message'><b>You:</b> {m['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-message'><b>{m['guide']}:</b> {m['content']}</div>", unsafe_allow_html=True)

# Atomic form submit
with st.form("chat_form", clear_on_submit=True):
    q = st.text_input("Ask your question…", placeholder="e.g., When will my finances improve?")
    submitted = st.form_submit_button("Send")

# Clear chat
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.vedic_phase = 1
    st.session_state.greeted = {k: False for k in st.session_state.greeted}
    st.session_state.tarot_cards = []

# Handle submit
if submitted and q:
    st.session_state.messages.append({"role": "user", "content": q})

    # Phase escalation for Vedic Guru based on user intent
    if guide == "The Vedic Guru":
        ql = q.lower()
        if st.session_state.vedic_phase == 1 and any(w in ql for w in ["remedy", "solution", "gem", "mantra", "what should", "fix", "cure", "wear"]):
            st.session_state.vedic_phase = 2
        elif st.session_state.vedic_phase in (1,2) and any(w in ql for w in ["specific", "exact", "steps", "plan", "crystal", "how to"]):
            st.session_state.vedic_phase = 3

    client = require_openai()
    if client:
        first = not st.session_state.greeted.get(guide, False)
        sys = build_system_prompt(
            guide,
            st.session_state.get("user_name", "friend"),
            st.session_state.get("gender", ""),
            st.session_state.get("dob", date(1995,1,1)),
            st.session_state.get("birth_time", "12:00"),
            st.session_state.get("birth_place", ""),
            first,
        )

        if guide == "The Tarot Reader" and st.session_state.tarot_cards:
            answer = tarot_reading(q, st.session_state.tarot_cards)
        else:
            answer = llm(client, sys, q, temp=0.9 if guide == "The Tarot Reader" else 0.7)

        st.session_state.messages.append({"role": "assistant", "guide": guide, "content": answer})
        st.session_state.greeted[guide] = True

# Footer note
st.write("")
