# Cosmic Guide — v2.3
# Topic detection + phase reset + Remedies Pack upsell + Tarot modal + UI polish
# (Professional tone, no emojis)

import os
import json
import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

import streamlit as st
from streamlit_lottie import st_lottie

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
# CSS (professional; better bubbles + tarot contrast)
# ---------------------------
st.markdown(
    r"""
<style>
  :root {
    --bg: #f7f8fc;
    --ink: #1a1c2d;
    --sub: #5b5e7f;
    --accent: #6C4AB6;
    --accent2: #8D72E1;
    --line: #e7e9f2;
    --card: #ffffff;
    --dark: #0f1020;
  }
  .stApp { background: var(--bg) !important; }
  h1, h2, h3, h4, h5, h6 { color: var(--ink) !important; }
  .card { background: var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px; box-shadow: 0 4px 14px rgba(16,18,54,.06); }
  .banner { background: linear-gradient(90deg, rgba(108,74,182,.10), rgba(141,114,225,.10)); border:1px solid rgba(108,74,182,.25); border-radius:12px; padding:12px 16px; }
  .user-message { background: linear-gradient(135deg, var(--accent), var(--accent2)); color:#fff; border-radius:16px; padding:14px 16px; margin: 8px 0; }
  .assistant-message { background: var(--card); color: var(--ink); border:1px solid var(--line); border-radius:16px; padding:14px 16px; margin:8px 0; }
  .msg-label { font-size:.85rem; opacity:.9; margin-bottom:6px; }
  .tarot-card { width:150px; height:210px; background: var(--dark); color:#eef0ff; border:1px solid #2a2b44; border-radius:12px; display:flex; align-items:center; justify-content:center; text-align:center; padding:12px; font-weight:600; }
  .tarot-wrap { display:flex; gap:12px; flex-wrap:wrap; }
  .chip { display:inline-block; padding:6px 12px; border:1px solid #d3d6ea; border-radius:999px; font-size:.86rem; margin:4px 6px 0 0; }
  input, textarea { border:1px solid var(--line) !important; }
  .helper { color:#6f729a; font-size:.9rem; }
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
if "selected_card" not in st.session_state:
    st.session_state.selected_card: Tuple[str, str] | None = None
if "greeted" not in st.session_state:
    st.session_state.greeted = {"The Vedic Guru": False, "The Tarot Reader": False, "The Modern Life Coach": False, "Numerology Expert": False}
if "vedic_phase" not in st.session_state:
    st.session_state.vedic_phase = 1
if "last_topic" not in st.session_state:
    st.session_state.last_topic = None
if "topic_counts" not in st.session_state:
    st.session_state.topic_counts: Dict[str,int] = {}
if "upsell_ready" not in st.session_state:
    st.session_state.upsell_ready = False

MODEL = os.environ.get("COSMIC_MODEL", "gpt-4o-mini")

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ---------------------------
# Helpers
# ---------------------------

def load_lottieurl(url: str):
    try:
        import requests
        r = requests.get(url, timeout=8)
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
            model=MODEL,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=temp,
        )
        return out.choices[0].message.content.strip()
    except Exception as e:
        return f"(AI error) {e}"

# -------- Topic detection
TOPIC_KEYWORDS = {
    "money": ["money","wealth","income","salary","finance","debt","loan","profit","rich","cash","luck"],
    "love": ["love","marry","marriage","relationship","partner","girlfriend","boyfriend","wife","husband","breakup"],
    "career": ["job","career","promotion","work","boss","interview","business","startup","client","sales","market"],
    "health": ["health","fitness","illness","disease","wellbeing","sleep","diet"],
    "family": ["family","parents","mother","father","child","children"],
    "education": ["exam","study","college","degree","school"],
    "spiritual": ["spiritual","karma","remedy","mantra","pooja","gem","gemstone","dosha"],
}

def detect_topic(text: str) -> str:
    s = text.lower()
    scores = {k:0 for k in TOPIC_KEYWORDS}
    for k, words in TOPIC_KEYWORDS.items():
        for w in words:
            if w in s:
                scores[k] += 1
    # pick highest; default career/business if tie on business keywords, else general
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "general"


def maybe_reset_phase_on_topic(new_topic: str):
    last = st.session_state.last_topic
    if last is None:
        st.session_state.last_topic = new_topic
        st.session_state.topic_counts[new_topic] = 1
        return False
    if new_topic != last:
        st.session_state.last_topic = new_topic
        st.session_state.topic_counts[new_topic] = st.session_state.topic_counts.get(new_topic,0)+1
        st.session_state.vedic_phase = 1
        return True
    # same topic → increment count
    st.session_state.topic_counts[new_topic] = st.session_state.topic_counts.get(new_topic,0)+1
    return False

# Upsell conditions
CRITICAL_WORDS = ["stuck","blocked","delay","urgent","court","debt","loss","bad luck","no job","breakup","health issue"]

def should_offer_remedies_pack(topic: str, q: str) -> bool:
    ql = q.lower()
    crit = any(w in ql for w in CRITICAL_WORDS)
    long_thread = st.session_state.topic_counts.get(topic,0) >= 2 and st.session_state.vedic_phase >= 2
    asking_remedy = any(w in ql for w in ["remedy","mantra","gem","stone","pooja","wear","solution"])
    return crit or long_thread or asking_remedy

# ---------------------------
# Generators (professional tone)
# ---------------------------

def generate_daily_horoscope(zodiac_sign: str) -> str:
    client = require_openai()
    if not client: return ""
    prompt = (
        f"Daily horoscope for {zodiac_sign} on {date.today():%B %d, %Y}. "
        "Professional, newspaper-style. Include: overall energy, career, relationships, wellbeing, one lucky color. No emojis. 120–150 words."
    )
    return llm(client, "You are a precise horoscope columnist.", prompt, 0.6)


def tarot_interpret(question: str, cards: List[Tuple[str,str]]) -> str:
    client = require_openai()
    if not client: return ""
    listed = ", ".join([f"{n} ({o})" for n,o in cards])
    sys = (
        "You are an experienced tarot reader. Keep it professional; explain each card succinctly, then give two practical next steps. "
        "End with one thoughtful question to invite a follow-up."
    )
    usr = f"Question: {question or 'General'}. Cards: {listed}."
    return llm(client, sys, usr, 0.8)

# ---------------------------
# Persona prompts with progressive disclosure
# ---------------------------

def phase_instructions() -> str:
    ph = st.session_state.vedic_phase
    if ph == 1:
        return (
            "PHASE 1 — PLANETS ONLY: Explain relevant planets/nakshatras/houses in 4–6 bullets for the user's topic. "
            "Do NOT provide remedies yet. Ask exactly one specific follow-up question that varies by topic. "
            "Do not repeat the user's question. No greetings/sign-off."
        )
    if ph == 2:
        return (
            "PHASE 2 — REMEDIES ON REQUEST: Offer up to two focused remedies (e.g., mantra routine, habit). "
            "Use the correct mantra 'Om Gam Ganapataye Namaha' if Ganesha is relevant. Avoid gems unless user asks. "
            "Close with a single question inviting a choice of next step. No sign-off."
        )
    return (
        "PHASE 3 — CRYSTAL PLAN: Provide a 3-step plan with relative timings (e.g., 'next 2–3 months'). "
        "Make steps measurable. No sign-off."
    )


def build_system_prompt(guide: str, first_message: bool) -> str:
    base_rules = (
        "Professional tone. No emojis. Do not repeat the user's question. Keep answers 110–180 words."
    )
    if guide == "The Vedic Guru":
        greet = "Start with 'Dear {name},' once only in the first reply." if first_message else "Do not greet; go straight to substance."
        return f"You are a warm, concise Vedic astrologer. {phase_instructions()} {greet} {base_rules}"
    if guide == "The Tarot Reader":
        return ("You are an intuitive tarot guide. Concise narrative, two actions, and one follow-up question. No emojis.")
    if guide == "The Modern Life Coach":
        return ("You are a pragmatic coach. Provide a numbered mini-plan (3–5 steps) and ask one reflective question. No fluff.")
    return ("You are a numerology expert. Compute Life Path from DOB and give one weekly focus area. Professional tone.")

# ---------------------------
# Sidebar (profile + guide)
# ---------------------------
with st.sidebar:
    st.markdown("<div style='text-align:center'><h3>✨ Cosmic Guide</h3><div class='helper'>Your AI Spiritual Companion</div></div>", unsafe_allow_html=True)
    api_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.api_key = api_key
    st.session_state.api_ok = bool(api_key)

    st.markdown("---")
    st.subheader("Your Profile")
    name = st.text_input("Name", value=st.session_state.get("user_name","Seeker"))
    gender = st.selectbox("Gender", ["Prefer not to say","Female","Male","Non-binary","Other"], index=0)
    dob = st.date_input("Date of Birth", value=st.session_state.get("dob", date(1995,1,1)))
    birth_time = st.text_input("Exact Time of Birth (HH:MM)", value=st.session_state.get("birth_time","12:00"))
    birth_place = st.text_input("Place of Birth", value=st.session_state.get("birth_place",""))
    st.session_state.update({"user_name":name,"gender":gender,"dob":dob,"birth_time":birth_time,"birth_place":birth_place})

    st.markdown("---")
    guide = st.radio("Choose your guide", ("The Vedic Guru","The Tarot Reader","The Modern Life Coach","Numerology Expert"))

# ---------------------------
# Home lead-in
# ---------------------------
col1, col2 = st.columns([1,1])
with col1:
    st.markdown("# Cosmic Guide")
    st.write("Ask focused questions and get specific, human answers. For business users, try the chips below to jump in.")
    chips = st.container()
    with chips:
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        if c1.button("Market niche fit"): st.session_state.messages.append({"role":"user","content":"Which niches match my strengths for a profitable business?"})
        if c2.button("Pricing strategy"): st.session_state.messages.append({"role":"user","content":"How should I price my new service this quarter?"})
        if c3.button("Launch window"): st.session_state.messages.append({"role":"user","content":"When is a favorable window to launch in the next few months?"})
        if c4.button("Client acquisition"): st.session_state.messages.append({"role":"user","content":"What is a practical plan to acquire first 10 clients?"})
        if c5.button("Funding outlook"): st.session_state.messages.append({"role":"user","content":"What are my prospects for funding in the coming months?"})
        if c6.button("Sales rituals vs actions"): st.session_state.messages.append({"role":"user","content":"Balance spiritual remedies and sales actions for revenue growth?"})
with col2:
    if lottie_stars:
        st_lottie(lottie_stars, height=200, key="stars")

st.markdown("---")

# ---------------------------
# Daily Horoscope
# ---------------------------
st.subheader("Today's Cosmic Energy")
cols = st.columns(6)
for i, s in enumerate(SIGNS):
    with cols[i % 6]:
        if st.button(s, key=f"sign_{s}"):
            st.session_state.zodiac_sign = s
            st.session_state.daily_horoscope = generate_daily_horoscope(s)
if st.session_state.zodiac_sign and st.session_state.daily_horoscope:
    st.markdown(f"### {st.session_state.zodiac_sign}")
    st.markdown(f"<div class='card'>{st.session_state.daily_horoscope}</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Tarot Studio (with modal help and clickable cards)
# ---------------------------
st.subheader("Tarot Studio")

# Modal help (fallback to expander if experimental_dialog not available)
if st.button("How to use Tarot"):
    st.session_state.show_tarot_help = True

if st.session_state.get("show_tarot_help"):
    try:
        @st.experimental_dialog("How Tarot Works")
        def _tarot_help():
            st.write("1) Click 'Draw 3 Cards'. 2) Click a card to see its meaning and ask about it. 3) Press 'Interpret' to get a concise reading and two next steps.")
            if st.button("Got it"):
                st.session_state.show_tarot_help = False
        _tarot_help()
    except Exception:
        with st.expander("How Tarot Works", True):
            st.write("1) Draw cards. 2) Click a card to see meaning and ask. 3) Press Interpret for a concise reading.")
            if st.button("Close"):
                st.session_state.show_tarot_help = False

# Deck
TAROT = [
    "The Fool","The Magician","The High Priestess","The Empress","The Emperor",
    "The Hierophant","The Lovers","The Chariot","Strength","The Hermit",
    "Wheel of Fortune","Justice","The Hanged Man","Death","Temperance",
    "The Devil","The Tower","The Star","The Moon","The Sun","Judgement","The World"
]

if st.button("Draw 3 Cards"):
    drawn = random.sample(TAROT, 3)
    st.session_state.tarot_cards = [(c, random.choice(["upright","reversed"])) for c in drawn]
    st.session_state.selected_card = None

if st.session_state.tarot_cards:
    st.write("Your cards (click to preview):")
    cols = st.columns(len(st.session_state.tarot_cards))
    for (name, orient), col in zip(st.session_state.tarot_cards, cols):
        if col.button(f"{name}\n({orient})", key=f"card_{name}"):
            st.session_state.selected_card = (name, orient)
        col.markdown("<div class='tarot-card'>Click the button above</div>", unsafe_allow_html=True)

if st.session_state.selected_card:
    name, orient = st.session_state.selected_card
    st.markdown(f"<div class='banner'><b>{name}</b> — {orient}. Ask a focused question or press Interpret.</div>", unsafe_allow_html=True)

q_tarot = st.text_input("Tarot question (optional)")
if st.button("Interpret Tarot") and st.session_state.tarot_cards:
    text = tarot_interpret(q_tarot, st.session_state.tarot_cards)
    st.markdown(f"<div class='assistant-message'>{text}</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Chat (form submit prevents double-click issue)
# ---------------------------
st.header("Chat with your Guide")

# Render history
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"<div class='user-message'><div class='msg-label'>You</div>{m['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-message'><div class='msg-label'>{m['guide']}</div>{m['content']}</div>", unsafe_allow_html=True)
        # Inline upsell card if present
        if m.get("upsell"):
            st.markdown(
                """
                <div class='card'>
                  <b>Recommended: Remedies Pack</b><br>
                  <div class='helper'>Personalised remedies + weekly check-ins. Ideal when issues are persistent or time-sensitive.</div>
                  <ul>
                    <li>Two tailored remedies (spiritual + practical)</li>
                    <li>30‑day action checklist</li>
                    <li>Follow-up prompts to track progress</li>
                  </ul>
                  <div class='helper'>Triggered because: high-impact topic and multiple follow-ups.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with st.form("chat_form", clear_on_submit=True):
    q = st.text_input("Ask your question…", placeholder="e.g., When will my revenue improve?")
    submitted = st.form_submit_button("Send")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.vedic_phase = 1
    st.session_state.greeted = {k: False for k in st.session_state.greeted}
    st.session_state.last_topic = None
    st.session_state.topic_counts = {}
    st.session_state.upsell_ready = False

# Handle new question
if submitted and q:
    st.session_state.messages.append({"role":"user","content": q})

    # Topic detection + phase reset if changed
    topic = detect_topic(q)
    changed = maybe_reset_phase_on_topic(topic)
    if changed:
        st.markdown(f"<div class='banner'>New topic detected — switching to a fresh analysis for <b>{topic}</b>.</div>", unsafe_allow_html=True)

    # Phase escalation triggers (user asking for solutions or specifics)
    ql = q.lower()
    if st.session_state.vedic_phase == 1 and any(w in ql for w in ["remedy","solution","gem","mantra","fix","wear","pooja"]):
        st.session_state.vedic_phase = 2
    elif st.session_state.vedic_phase in (1,2) and any(w in ql for w in ["exact","specific","steps","plan","crystal","how to"]):
        st.session_state.vedic_phase = 3

    client = require_openai()
    if client:
        first = not st.session_state.greeted.get(guide, False)
        system = build_system_prompt(guide, first)

        # Build a compact user context (without echoing full question later)
        ctx = (
            f"Name: {st.session_state.get('user_name','friend')}. "
            f"Gender: {st.session_state.get('gender','')}. "
            f"DOB: {st.session_state.get('dob', date(1995,1,1))}. "
            f"Birth time: {st.session_state.get('birth_time','12:00')}. "
            f"Birth place: {st.session_state.get('birth_place','')}. "
            f"Topic: {topic}."
        )
        user_prompt = f"{ctx}\nQuestion: {q}"

        # Produce answer
        if guide == "The Tarot Reader" and st.session_state.tarot_cards:
            text = tarot_interpret(q, st.session_state.tarot_cards)
        else:
            text = llm(client, system, user_prompt, temp=0.85 if guide=="The Tarot Reader" else 0.7)

        upsell = False
        if guide == "The Vedic Guru" and should_offer_remedies_pack(topic, q):
            upsell = True

        st.session_state.messages.append({"role":"assistant","guide": guide, "content": text, "upsell": upsell})
        st.session_state.greeted[guide] = True
