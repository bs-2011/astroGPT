import streamlit as st
from datetime import datetime, date
from openai import OpenAI
import os

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cosmic Guide - AI Spiritual Companion",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Use provided key now; falls back to ENV when you move to prod
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"
client = OpenAI(api_key=OPENAI_API_KEY)

# ──────────────────────────────────────────────────────────────────────────────
# STYLES
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap');

:root { --ink:#2D2B4E; --pri:#6C4AB6; --pri2:#8D72E1; }

.stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }
h1,h2,h3,h4,h5,h6 { font-family: 'Playfair Display', serif; color: var(--ink); }

.guide-card {
  background: white; border-radius: 15px; padding: 25px; margin: 15px 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 4px solid var(--pri2);
  transition: transform .3s ease, box-shadow .3s ease;
}
.guide-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.12); }

.user-message {
  background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%); color: white;
  border-radius: 18px 18px 0 18px; padding: 15px 20px; margin: 10px 0; max-width: 80%; margin-left: auto;
}
.assistant-message {
  background: white; color: var(--ink); border-radius: 18px 18px 18px 0;
  padding: 15px 20px; margin: 10px 0; max-width: 80%;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea;
}
.stButton>button {
  background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%); color: white; border: none;
  border-radius: 50px; padding: 12px 30px; font-weight: 500;
  box-shadow: 0 5px 15px rgba(108,74,182,0.3); transition: all .2s ease;
}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(108,74,182,0.4); }

.pricing-card {
  background: white; border-radius: 15px; padding: 30px; text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin: 15px 0; border: 2px solid transparent;
}
.premium { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); position: relative; overflow: hidden; }
.premium::before {
  content: "POPULAR"; position: absolute; top: 15px; right: -30px; background: #6C4AB6; color: white;
  padding: 5px 30px; font-size: .7rem; transform: rotate(45deg);
}

.nav-item { padding: 15px; margin: 5px 0; border-radius: 8px; cursor: pointer; transition: all .2s ease; }
.nav-item:hover { background-color: rgba(255,255,255,0.1); }
.nav-item.active { background-color: rgba(255,255,255,0.2); font-weight: bold; }

/* 🔝 Keep profile + question visible without scrolling */
.sticky-header {
  position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(6px);
  background: rgba(250,250,255,0.75); border: 1px solid #eaeaea; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px;
  box-shadow: 0 6px 14px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# STATE
# ──────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "Home"

def navigate_to(page: str):
    st.session_state.page = page

# ──────────────────────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────────────────────
def show_home_page():
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("# Cosmic Guide")
        st.markdown("### Your AI-Powered Spiritual Companion")
        st.markdown("""
Discover personalized spiritual guidance through the power of AI.
Whether you're seeking answers about love, career, or personal growth,
our AI guides are here to provide insights and clarity.
        """)
        if st.button("Get Started", key="home_btn"):
            navigate_to("Chat")

    with c2:
        st.image(
            "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&h=400&fit=crop",
            caption="Find your spiritual path with AI guidance"
        )

    st.markdown("---")
    st.markdown("## How It Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="guide-card"><h3>1. Choose Your Guide</h3><p>Select from Vedic, Tarot, or Life Coach perspectives</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="guide-card"><h3>2. Ask Your Question</h3><p>Share what\'s on your mind - love, career, or life purpose</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="guide-card"><h3>3. Receive Guidance</h3><p>Get personalized insights based on your birth details</p></div>', unsafe_allow_html=True)

def show_features_page():
    st.markdown("# Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="guide-card">
            <h3>🔮 Vedic Astrology</h3>
            <p>Get insights based on Vedic astrology principles, planetary positions, and ancient wisdom.</p>
            <ul>
                <li>Personalized birth chart analysis</li>
                <li>Planetary period (Dasha) predictions</li>
                <li>Remedies and solutions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="guide-card">
            <h3>💼 Life Coaching</h3>
            <p>Blend spiritual wisdom with practical advice for modern life challenges.</p>
            <ul>
                <li>Career guidance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="guide-card">
            <h3>🃏 Tarot Readings</h3>
            <p>Receive intuitive tarot card interpretations for guidance and self-reflection.</p>
            <ul>
                <li>Daily card pulls</li>
                <li>Relationship spreads</li>
                <li>Career path readings</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="guide-card">
            <h3>📊 Personalized Reports</h3>
            <p>Get detailed reports based on your birth details and specific questions.</p>
            <ul>
                <li>Compatibility analysis</li>
                <li>Birth chart reports</li>
                <li>Future trend predictions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_pricing_page():
    st.markdown("# Pricing Plans")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Basic</h3><h2>Free</h2><p>For those exploring spiritual guidance</p><hr>
            <p>✓ 1 question per day</p><p>✓ Basic horoscope</p><p>✖ Personalized reports</p><p>✖ Priority support</p><br>
            <button class="stButton">Start Free</button>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="pricing-card premium">
            <h3>Premium</h3><h2>₹299/month</h2><p>For regular spiritual guidance seekers</p><hr>
            <p>✓ Unlimited questions</p><p>✓ Detailed horoscope</p><p>✓ 2 personalized reports/month</p><p>✓ Email support</p><br>
            <button class="stButton">Subscribe Now</button>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Ultimate</h3><h2>₹2499/year</h2><p>For dedicated spiritual practitioners</p><hr>
            <p>✓ Unlimited questions</p><p>✓ Premium horoscope</p><p>✓ 5 personalized reports/month</p><p>✓ Priority 24/7 support</p><br>
            <button class="stButton">Subscribe Now</button>
        </div>
        """, unsafe_allow_html=True)

def show_about_page():
    st.markdown("# About Cosmic Guide")
    st.markdown("""
Cosmic Guide was founded with a simple mission: to make spiritual guidance accessible,
affordable, and personalized for everyone. We combine ancient spiritual wisdom with modern AI technology
to provide insights that can help you navigate life's challenges.
    """)
    st.image("https://images.unsplash.com/photo-1518976024611-28bf4b48222e?w=1000&h=400&fit=crop",
             caption="Where ancient wisdom meets modern technology")
    st.markdown("""
## Our Values
- **Authenticity**: We respect and honor the spiritual traditions we draw from
- **Innovation**: We continuously improve our technology to serve you better
- **Privacy**: Your data and questions are always kept confidential
- **Accessibility**: We believe everyone deserves guidance, regardless of budget
    """)

# ──────────────────────────────────────────────────────────────────────────────
# CHAT
# ──────────────────────────────────────────────────────────────────────────────
def show_chat_page():
    st.markdown("# Chat with Your Guide")

    # 🔝 Sticky header with personal info + question box (always visible)
    with st.container():
        st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1.2, 0.9, 0.9, 1.2])
        with c1:
            user_name = st.text_input("Your Name", value=st.session_state.get("user_name", ""), placeholder="Enter your name")
        with c2:
            dob = st.date_input(
                "Date of Birth",
                value=st.session_state.get("dob", date(1990, 1, 1)),
                min_value=date(1900, 1, 1),
                max_value=date.today())
        with c3:
            birth_time = st.time_input(
                "Time of Birth (if known)",
                value=st.session_state.get("birth_time", datetime.strptime("12:00", "%H:%M").time()))
        with c4:
            birth_place = st.text_input("Place of Birth", value=st.session_state.get("birth_place", ""), placeholder="City, Country")

        gcol1, gcol2 = st.columns([1.3, 2.7])
        with gcol1:
            guide = st.radio(
                "Choose Your Guide",
                ("The Vedic Guru", "The Tarot Reader", "The Modern Life Coach"),
                index=["The Vedic Guru", "The Tarot Reader", "The Modern Life Coach"].index(st.session_state.get("guide", "The Vedic Guru")))
        with gcol2:
            question = st.text_input("Ask your question…", key="input",
                                     placeholder="e.g., What does my career horoscope say for this month?")

            b1, b2 = st.columns([1, 1])
            with b1:
                send_btn = st.button("Send", use_container_width=True)
            with b2:
                clear_btn = st.button("Clear Chat", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Persist profile selections
    st.session_state.user_name = user_name
    st.session_state.dob = dob
    st.session_state.birth_time = birth_time
    st.session_state.birth_place = birth_place
    st.session_state.guide = guide

    # Chat history list (below sticky header)
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><b>{message["guide"]}:</b> {message["content"]}</div>', unsafe_allow_html=True)

    if clear_btn:
        st.session_state.messages = []
        st.rerun()

    if send_btn and question:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": question})

        # Personalities
        guide_personalities = {
            "The Vedic Guru": "You are a compassionate Vedic astrologer with deep knowledge of Jyotish. You provide insights based on planetary positions and offer simple remedies. You speak with wisdom and warmth, often referencing Vedic traditions.",
            "The Tarot Reader": "You are an intuitive tarot reader who interprets cards with empathy and insight. You focus on personal growth and self-discovery, offering guidance rather than predictions.",
            "The Modern Life Coach": "You are a practical life coach who blends spiritual wisdom with actionable advice. You help users find clarity and take positive steps in their lives."
        }

        system_prompt = f"""
{guide_personalities[guide]}

The user's name is {user_name or "Seeker"}.
Their date of birth is {dob}.
They were born around {birth_time} in {birth_place or "Unknown"}.

Provide a thoughtful, helpful response to their question.
Be empathetic and encouraging.
Keep your response under 150 words.
""".strip()

        try:
            with st.spinner(f"{guide} is thinking..."):
                # ✅ Use a current lightweight model for speed/cost. Swap if you prefer.
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    temperature=0.7
                )
            answer = resp.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": answer, "guide": guide})
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def main():
    # Sidebar brand + nav
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; font-size: 24px;">✨ Cosmic Guide</h1>
                <p style="color: #ccc;">Your AI Spiritual Companion</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        menu_options = ["Home", "Chat", "Features", "Pricing", "About"]
        for option in menu_options:
            if st.button(("🌙" if option=="Home" else "🔮" if option=="Chat" else "⭐" if option=="Features" else "💰" if option=="Pricing" else "ℹ️") + f" {option}", use_container_width=True, key=f"nav_{option}"):
                navigate_to(option)

        st.markdown("---")
        # 🔐 No API key prompt here (per your request)

    # Route
    page = st.session_state.page
    if page == "Home":       show_home_page()
    elif page == "Chat":     show_chat_page()
    elif page == "Features": show_features_page()
    elif page == "Pricing":  show_pricing_page()
    elif page == "About":    show_about_page()
    else:                    show_home_page()

if __name__ == "__main__":
    main()
