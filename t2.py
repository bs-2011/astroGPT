import streamlit as st
import openai
from datetime import datetime, date
import random
import requests
from PIL import Image
import io
import base64
import os
import pytz
import json
from streamlit_lottie import st_lottie
import time

# Set page configuration
st.set_page_config(
    page_title="Cosmic Guide - AI Spiritual Companion",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Poppins:wght@300;400;500;600&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #2D2B4E;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    .guide-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #8D72E1;
    }
    
    .guide-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
    }
    
    .user-message {
        background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%);
        color: white;
        border-radius: 18px;
        padding: 15px 20px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        box-shadow: 0 5px 15px rgba(108, 74, 182, 0.3);
    }
    
    .assistant-message {
        background: white;
        color: #2D2B4E;
        border-radius: 18px;
        padding: 15px 20px;
        margin: 10px auto 10px 0;
        max-width: 80%;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #eaeaea;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(108, 74, 182, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(108, 74, 182, 0.4);
        background: linear-gradient(135deg, #5D3AA0 0%, #7B62C7 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2D2B4E 0%, #4A3B8C 100%);
        color: white;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        color: #6C4AB6;
        font-size: 0.9rem;
        border-top: 1px solid #eaeaea;
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .pricing-card {
        background: white;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin: 15px 0;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        border: 2px solid #8D72E1;
    }
    
    .premium {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        position: relative;
        overflow: hidden;
    }
    
    .premium::before {
        content: "POPULAR";
        position: absolute;
        top: 15px;
        right: -30px;
        background: #6C4AB6;
        color: white;
        padding: 5px 30px;
        font-size: 0.7rem;
        transform: rotate(45deg);
    }
    
    .nav-item {
        padding: 15px;
        margin: 5px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .nav-item.active {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: bold;
    }
    
    .daily-horoscope {
        background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .zodiac-selector {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding: 10px 0;
        margin: 15px 0;
    }
    
    .zodiac-item {
        flex: 0 0 auto;
        text-align: center;
        cursor: pointer;
        padding: 10px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .zodiac-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .zodiac-item.selected {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: bold;
    }
    
    .tarot-card {
        width: 120px;
        height: 180px;
        background: #2D2B4E;
        color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    
    .tarot-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }
    
    .tarot-spread {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        margin: 20px 0;
    }
    
    .birth-details-form {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, #6C4AB6 0%, #8D72E1 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .suggestion-chip {
        display: inline-block;
        background: rgba(108, 74, 182, 0.1);
        border: 1px solid #6C4AB6;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    
    .suggestion-chip:hover {
        background: rgba(108, 74, 182, 0.2);
        transform: translateY(-2px);
    }
    
    .typing-indicator {
        display: flex;
        padding: 15px 20px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        margin: 0 3px;
        background-color: #8D72E1;
        border-radius: 50%;
        opacity: 0.6;
        animation: typing-animation 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) {
        animation-delay: 0s;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing-animation {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.6;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    .info-tooltip {
        position: relative;
        display: inline-block;
        margin-left: 5px;
        cursor: pointer;
    }
    
    .info-tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: #2D2B4E;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .info-tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    .remedies-pack {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "zodiac_sign" not in st.session_state:
    st.session_state.zodiac_sign = None
if "daily_horoscope" not in st.session_state:
    st.session_state.daily_horoscope = None
if "tarot_cards" not in st.session_state:
    st.session_state.tarot_cards = []
if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = {}
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "typing" not in st.session_state:
    st.session_state.typing = False
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "show_remedies_prompt" not in st.session_state:
    st.session_state.show_remedies_prompt = False

# Load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_stars = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_myejiggj.json")
lottie_moon = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_9mlame2v.json")
lottie_crystal = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_k6yfqbbw.json")

# Custom navigation function
def navigate_to(page):
    st.session_state.page = page

# Generate daily horoscope
def generate_daily_horoscope(zodiac_sign):
    if not st.session_state.api_key_valid:
        return "Please enter a valid OpenAI API key to get your daily horoscope."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.api_key)
        
        prompt = f"""
        Generate a daily horoscope for {zodiac_sign} for today ({date.today().strftime('%B %d, %Y')}).
        Make it personalized, engaging, and insightful. Include:
        - Overall energy of the day
        - Career focus
        - Love and relationships
        - Health and wellness
        - Lucky numbers or colors
        
        Write it in a warm, conversational tone. Avoid emojis to maintain professionalism.
        Keep it to about 150-200 words.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert astrologer with a warm, engaging style. You provide insightful daily horoscopes that feel personal and relevant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating horoscope: {str(e)}"

# Generate tarot reading
def generate_tarot_reading(question, cards):
    if not st.session_state.api_key_valid:
        return "Please enter a valid OpenAI API key to get your tarot reading."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.api_key)
        
        card_descriptions = ", ".join([f"{card} ({'Upright' if random.random() > 0.5 else 'Reversed'})" for card in cards])
        
        prompt = f"""
        The user has asked: "{question}"
        
        They have drawn the following tarot cards: {card_descriptions}
        
        Please provide a insightful tarot reading that:
        1. Explains the significance of each card in relation to the question
        2. Provides guidance based on the cards drawn
        3. Offers practical advice or things to consider
        4. Ends with an empowering message
        
        Write in a warm, mystical yet practical tone. Make it feel personal and meaningful.
        Use about 200-250 words.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an experienced tarot reader with deep intuition and wisdom. You provide meaningful interpretations that help people gain clarity and insight."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating tarot reading: {str(e)}"

# Detect topic from question
def detect_topic(question):
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['wealth', 'money', 'rich', 'finance', 'financial', 'prosperity']):
        return 'wealth'
    elif any(word in question_lower for word in ['love', 'relationship', 'marriage', 'partner', 'romance', 'dating']):
        return 'love'
    elif any(word in question_lower for word in ['career', 'job', 'business', 'work', 'profession', 'vocation']):
        return 'career'
    elif any(word in question_lower for word in ['health', 'wellness', 'fitness', 'illness', 'disease', 'medical']):
        return 'health'
    elif any(word in question_lower for word in ['education', 'study', 'learning', 'knowledge', 'school', 'college']):
        return 'education'
    elif any(word in question_lower for word in ['family', 'children', 'parents', 'siblings', 'home']):
        return 'family'
    else:
        return 'general'

# Check if remedies prompt should be shown
def should_show_remedies_prompt(topic, conversation_stage):
    # Show remedies prompt for specific topics at the right conversation stage
    if topic in ['wealth', 'love', 'career', 'health'] and conversation_stage.get('stage') == 'solutions':
        return random.random() < 0.7  # 70% chance to show remedies prompt
    return False

# Generate conversational response with engagement strategy
def generate_conversational_response(question, user_info, guide, conversation_stage, tarot_cards=None):
    if not st.session_state.api_key_valid:
        return "Please enter a valid OpenAI API key to continue."
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.api_key)
        
        # Detect topic
        current_topic = detect_topic(question)
        
        # Reset conversation stage if topic has changed
        if st.session_state.current_topic and st.session_state.current_topic != current_topic:
            conversation_stage = {'stage': 'initial', 'topics': [current_topic]}
        
        # Update current topic
        st.session_state.current_topic = current_topic
        
        # Get user name or use a generic term
        user_name = user_info.get("name", "dear seeker")
        
        # Define guide personalities with engagement-focused prompts
        guide_personalities = {
            "The Vedic Guru": f"""You are a compassionate Vedic astrologer with deep knowledge of Jyotish. 
            The user's name is {user_info.get('name', 'seeker')}, gender is {user_info.get('gender', '')}, 
            born on {user_info.get('dob', '')} at {user_info.get('birth_time', '')} in {user_info.get('birth_place', '')}.
            
            Current conversation stage: {conversation_stage.get('stage', 'initial')}
            Previous topics discussed: {conversation_stage.get('topics', [])}
            Current topic: {current_topic}
            
            Your response strategy:
            1. For initial questions, provide insights about planetary positions and houses but don't give complete solutions yet
            2. Encourage follow-up questions to explore specific areas
            3. Only provide remedies and specific solutions when explicitly asked
            4. End with an engaging question to continue the conversation
            5. Use the user's name only in the first response of a conversation thread
            
            Speak with wisdom and warmth, but avoid overly formal language.
            Keep responses under 150 words but make them meaningful and engaging.
            """,
            
            "The Tarot Reader": f"""You are an intuitive tarot reader with a mystical yet practical approach.
            The user has drawn these cards: {', '.join(tarot_cards) if tarot_cards else 'No cards drawn yet'}.
            
            Current conversation stage: {conversation_stage.get('stage', 'initial')}
            Previous topics discussed: {conversation_stage.get('topics', [])}
            Current topic: {current_topic}
            
            Your response strategy:
            1. Interpret the cards in relation to their question but leave room for exploration
            2. Encourage follow-up questions about specific aspects of the reading
            3. Only provide detailed guidance when explicitly requested
            4. End with an engaging question to continue the conversation
            
            Speak in a poetic, metaphorical style while keeping the advice practical.
            Keep responses under 150 words but make them insightful.
            """,
            
            "The Modern Life Coach": f"""You are a practical life coach who blends spiritual wisdom with actionable advice.
            The user's name is {user_info.get('name', 'seeker')}, gender is {user_info.get('gender', '')}, 
            born on {user_info.get('dob', '')}.
            
            Current conversation stage: {conversation_stage.get('stage', 'initial')}
            Previous topics discussed: {conversation_stage.get('topics', [])}
            Current topic: {current_topic}
            
            Your response strategy:
            1. Provide initial insights but encourage deeper exploration
            2. Offer frameworks rather than complete solutions in the first response
            3. Only provide specific action plans when explicitly requested
            4. End with an engaging question to continue the conversation
            
            Speak in an encouraging, motivational tone.
            Keep responses under 150 words but make them actionable.
            """,
            
            "Numerology Expert": f"""You are a numerology expert who analyzes numbers from birth dates and names.
            The user's name is {user_info.get('name', 'seeker')}, born on {user_info.get('dob', '')}.
            
            Current conversation stage: {conversation_stage.get('stage', 'initial')}
            Previous topics discussed: {conversation_stage.get('topics', [])}
            Current topic: {current_topic}
            
            Your response strategy:
            1. Share initial numerological insights but leave room for deeper exploration
            2. Encourage questions about specific numbers or aspects
            3. Only provide detailed interpretations when explicitly requested
            4. End with an engaging question to continue the conversation
            
            Speak with authority but warmth, making the numerical insights personal and relevant.
            Keep responses under 150 words but make them informative.
            """
        }
        
        # Prepare the prompt
        system_prompt = guide_personalities[guide]
        
        # For tarot readings, use the specialized function
        if guide == "The Tarot Reader" and tarot_cards:
            response_content = generate_tarot_reading(question, tarot_cards)
        else:
            # Generate response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.8 if guide == "The Tarot Reader" else 0.7
            )
            response_content = response.choices[0].message.content
        
        return response_content
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Update conversation stage
def update_conversation_stage(question, response):
    # Extract topic from question
    current_topic = detect_topic(question)
    topics = st.session_state.conversation_stage.get('topics', [])
    
    if current_topic not in topics:
        topics.append(current_topic)
    
    # Update stage based on conversation depth
    stage = 'initial'
    if len(topics) > 1:
        stage = 'exploring'
    if any(topic in response.lower() for topic in ['remedy', 'solution', 'mantra', 'gemstone']):
        stage = 'solutions'
    
    st.session_state.conversation_stage = {
        'stage': stage,
        'topics': topics,
        'last_topic': current_topic
    }
    
    # Check if we should show remedies prompt
    st.session_state.show_remedies_prompt = should_show_remedies_prompt(current_topic, st.session_state.conversation_stage)

# Display typing indicator
def show_typing_indicator():
    st.markdown("""
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """, unsafe_allow_html=True)

# Display remedies pack prompt
def show_remedies_prompt():
    st.markdown("""
    <div class="remedies-pack">
        <h3>✨ Personalized Remedies Pack</h3>
        <p>Based on your current situation, our astrologers have prepared a personalized remedies pack including:</p>
        <ul style="text-align: left; display: inline-block;">
            <li>Specific mantras for your situation</li>
            <li>Recommended gemstones</li>
            <li>Planetary rituals</li>
            <li>Personalized yantra</li>
        </ul>
        <p>This comprehensive pack can help enhance the positive energies in your life.</p>
        <button class="stButton">Explore Remedies Pack</button>
    </div>
    """, unsafe_allow_html=True)

# Main app
def main():
    # Sidebar navigation
    with st.sidebar:
        # Logo
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; font-size: 24px;">✨ Cosmic Guide</h1>
                <p style="color: #ccc;">Your AI Spiritual Companion</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Navigation menu
        menu_options = {
            "Home": "house",
            "Chat": "chat",
            "Features": "star",
            "Pricing": "currency-rupee",
            "About": "info-circle"
        }
        
        for option, icon in menu_options.items():
            is_active = st.session_state.page == option
            emoji = "🌙" if option == "Home" else "🔮" if option == "Chat" else "⭐" if option == "Features" else "💰" if option == "Pricing" else "ℹ️"
            if st.button(f"{emoji} {option}", key=f"nav_{option}", use_container_width=True):
                navigate_to(option)
        
        st.markdown("---")
        
        # Only show API key input on Chat page
        if st.session_state.page == "Chat":
            st.header("🔮 Your Cosmic Profile")
            
            # API Key Input
            api_key = st.text_input("Enter your OpenAI API Key:", type="password", 
                                   help="Get your API key from https://platform.openai.com/api-keys")
            
            if api_key:
                st.session_state.api_key = api_key
                st.session_state.api_key_valid = True
                st.success("API key saved successfully!")
            
            st.markdown("---")
            
            # User information
            with st.expander("Personal Details", expanded=True):
                user_name = st.text_input("Your Name", placeholder="Enter your name")
                gender = st.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Prefer not to say"])
                dob = st.date_input("Date of Birth", value=date(1990, 1, 1), 
                                   min_value=date(1900, 1, 1), 
                                   max_value=date.today())
                birth_time = st.text_input("Exact Time of Birth (HH:MM)", value="12:00", 
                                         help="Enter your exact time of birth in 24-hour format (e.g., 14:30 for 2:30 PM)")
                birth_place = st.text_input("Place of Birth", placeholder="City, Country")
            
            st.markdown("---")
            
            # Guide selection
            st.header("Choose Your Guide")
            guide = st.radio("Select a spiritual guide:", 
                            ("The Vedic Guru", "The Tarot Reader", "The Modern Life Coach", "Numerology Expert"),
                            index=0)
            
            # Guide descriptions
            if guide == "The Vedic Guru":
                st.info("Specializes in Vedic astrology, planetary positions, and ancient remedies. Expect detailed astrological insights based on your birth chart.")
            elif guide == "The Tarot Reader":
                st.info("Provides insights through tarot card interpretations and intuitive guidance. Expect card draws and mystical interpretations.")
            elif guide == "The Modern Life Coach":
                st.info("Offers practical life advice blending modern coaching with spiritual wisdom. Expect actionable steps and motivational guidance.")
            else:
                st.info("Analyzes numbers from your birth date and name to reveal life paths and destinies. Expect numerological calculations and insights.")
            
            # Store these values in session state
            st.session_state.user_info = {
                "name": user_name,
                "gender": gender,
                "dob": dob,
                "birth_time": birth_time,
                "birth_place": birth_place
            }
            st.session_state.guide = guide
    
    # Render the current page
    if st.session_state.page == "Home":
        show_home_page()
    elif st.session_state.page == "Chat":
        show_chat_page()
    elif st.session_state.page == "Features":
        show_features_page()
    elif st.session_state.page == "Pricing":
        show_pricing_page()
    elif st.session_state.page == "About":
        show_about_page()

def show_home_page():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("# Cosmic Guide")
        st.markdown("### Your AI-Powered Spiritual Companion")
        st.markdown("""
        Discover personalized spiritual guidance through the power of AI. 
        Whether you're seeking answers about love, career, or personal growth, 
        our AI guides are here to provide insights and clarity.
        """)
        
        if st.button("Get Started", key="home_btn"):
            navigate_to("Chat")
    
    with col2:
        if lottie_stars:
            st_lottie(lottie_stars, height=300, key="stars")
    
    st.markdown("---")
    
    # Daily Horoscope Section
    st.markdown("## 📅 Today's Cosmic Energy")
    
    zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                   "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Create zodiac selector
    st.markdown("### Select your zodiac sign:")
    cols = st.columns(6)
    for i, sign in enumerate(zodiac_signs):
        with cols[i % 6]:
            if st.button(f"♈{sign}" if i == 0 else 
                        f"♉{sign}" if i == 1 else
                        f"♊{sign}" if i == 2 else
                        f"♋{sign}" if i == 3 else
                        f"♌{sign}" if i == 4 else
                        f"♍{sign}" if i == 5 else
                        f"♎{sign}" if i == 6 else
                        f"♏{sign}" if i == 7 else
                        f"♐{sign}" if i == 8 else
                        f"♑{sign}" if i == 9 else
                        f"♒{sign}" if i == 10 else
                        f"♓{sign}"):
                st.session_state.zodiac_sign = sign
    
    if st.session_state.zodiac_sign:
        st.markdown(f"### Your {st.session_state.zodiac_sign} Horoscope for Today")
        
        if st.button("Generate Daily Horoscope"):
            with st.spinner("Consulting the stars..."):
                horoscope = generate_daily_horoscope(st.session_state.zodiac_sign)
                st.session_state.daily_horoscope = horoscope
        
        if st.session_state.daily_horoscope:
            st.markdown(f'<div class="daily-horoscope">{st.session_state.daily_horoscope}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>1. Choose Your Guide</h3>
            <p>Select from Vedic, Tarot, Life Coach, or Numerology perspectives</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>2. Share Your Details</h3>
            <p>Provide your birth details for personalized insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>3. Receive Guidance</h3>
            <p>Get personalized insights based on your unique cosmic blueprint</p>
        </div>
        """, unsafe_allow_html=True)

def show_chat_page():
    st.markdown("# Chat with Your Guide")
    
    # Display guide information
    guide = st.session_state.get("guide", "The Vedic Guru")
    
    if guide == "The Vedic Guru":
        st.markdown("""
        <div class="highlight-box">
            <h3>🧘 The Vedic Guru</h3>
            <p>Specializes in Vedic astrology based on your birth details. Provides insights on planetary influences, doshas, and remedies. Expect detailed astrological analysis and spiritual guidance.</p>
        </div>
        """, unsafe_allow_html=True)
    elif guide == "The Tarot Reader":
        st.markdown("""
        <div class="highlight-box">
            <h3>🔮 The Tarot Reader</h3>
            <p>Uses tarot cards to provide intuitive guidance. Can help with specific questions about love, career, or personal growth. Expect mystical insights and symbolic interpretations.</p>
            <div class="info-tooltip">ℹ️
                <span class="tooltip-text">Click 'Draw 3 Cards' to select your tarot spread, then ask your question for an interpretation.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif guide == "The Modern Life Coach":
        st.markdown("""
        <div class="highlight-box">
            <h3>💼 The Modern Life Coach</h3>
            <p>Blends spiritual wisdom with practical advice. Helps with goal setting, motivation, and personal development. Expect actionable steps and empowering guidance.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="highlight-box">
            <h3>🔢 Numerology Expert</h3>
            <p>Analyzes numbers from your birth date and name to reveal life paths, destinies, and personal traits. Expect calculations of life path numbers, expression numbers, and more.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tarot card selection for Tarot Reader
    if guide == "The Tarot Reader":
        st.markdown("### Select Your Tarot Spread")
        
        tarot_deck = [
            "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
            "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
            "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
            "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
        ]
        
        if st.button("Draw 3 Cards", key="draw_cards"):
            st.session_state.tarot_cards = random.sample(tarot_deck, 3)
        
        if st.session_state.tarot_cards:
            st.markdown("### Your Cards:")
            cols = st.columns(3)
            for i, card in enumerate(st.session_state.tarot_cards):
                with cols[i]:
                    st.markdown(f'<div class="tarot-card">{card}</div>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><b>{message["guide"]}:</b> {message["content"]}</div>', unsafe_allow_html=True)
        
        # Show remedies prompt if needed
        if st.session_state.get("show_remedies_prompt", False):
            show_remedies_prompt()
        
        # Show typing indicator if needed
        if st.session_state.get("typing", False):
            show_typing_indicator()
    
    # Suggested questions
    if len(st.session_state.messages) == 0 or len(st.session_state.messages) < 3:
        st.markdown("### 💡 You might want to ask about:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Wealth and financial prospects", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Tell me about my wealth and financial prospects"})
                st.rerun()
            if st.button("Career path and opportunities", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What does my career path look like?"})
                st.rerun()
        with col2:
            if st.button("Love and relationships", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Tell me about my love life and relationships"})
                st.rerun()
            if st.button("Personal growth", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "How can I grow personally and spiritually?"})
                st.rerun()
    
    # Chat input at bottom
    st.markdown("---")
    question = st.chat_input("Ask your question...", key="input", 
                            placeholder="e.g., What does my career horoscope say for this month?")
    
    clear_btn = st.button("Clear Chat", use_container_width=True)
    
    if clear_btn:
        st.session_state.messages = []
        st.session_state.tarot_cards = []
        st.session_state.conversation_stage = {}
        st.session_state.current_topic = None
        st.session_state.show_remedies_prompt = False
        st.rerun()
    
    if question:
        if not st.session_state.api_key_valid:
            st.error("Please enter a valid OpenAI API key in the sidebar to continue.")
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Get values from session state
            user_info = st.session_state.get("user_info", {})
            guide = st.session_state.get("guide", "The Vedic Guru")
            tarot_cards = st.session_state.get("tarot_cards", [])
            conversation_stage = st.session_state.get("conversation_stage", {})
            
            # Set typing state
            st.session_state.typing = True
            st.rerun()
            
            # Generate response
            answer = generate_conversational_response(
                question, user_info, guide, conversation_stage, tarot_cards
            )
            
            # Update conversation stage
            update_conversation_stage(question, answer)
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "guide": guide
            })
            
            # Reset typing state
            st.session_state.typing = False
            
            # Rerun to update the chat display
            st.rerun()

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
                <li>Compatibility analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="guide-card">
            <h3>💼 Life Coaching</h3>
            <p>Blend spiritual wisdom with practical advice for modern life challenges.</p>
            <ul>
                <li>Career guidance</li>
                <li>Relationship advice</li>
                <li>Goal setting and achievement</li>
                <li>Mindfulness practices</li>
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
                <li>Celtic cross spreads</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="guide-card">
            <h3>📊 Numerology Reports</h3>
            <p>Discover your life path, expression, and soul urge numbers for deeper self-understanding.</p>
            <ul>
                <li>Life path number analysis</li>
                <li>Expression number insights</li>
                <li>Personal year cycles</li>
                <li>Compatibility analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ## Why Choose Cosmic Guide?
    
    - **24/7 Availability**: Get guidance anytime, anywhere
    - **Affordable**: Fraction of the cost of traditional astrologers
    - **Private**: Your questions and data remain confidential
    - **Multiple Perspectives**: Choose from different spiritual traditions
    - **Personalized**: Insights based on your unique birth details
    - **Interactive**: Draw tarot cards, calculate numerology, and more
    """)

def show_pricing_page():
    st.markdown("# Pricing Plans")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Basic</h3>
            <h2>Free</h2>
            <p>For those exploring spiritual guidance</p>
            <hr>
            <p>✓ 3 questions per day</p>
            <p>✓ Basic horoscope</p>
            <p>✖ Personalized reports</p>
            <p>✖ Priority support</p>
            <br>
            <button class="stButton">Start Free</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pricing-card premium">
            <h3>Premium</h3>
            <h2>₹299/month</h2>
            <p>For regular spiritual guidance seekers</p>
            <hr>
            <p>✓ Unlimited questions</p>
            <p>✓ Detailed horoscope</p>
            <p>✓ 2 personalized reports/month</p>
            <p>✓ Email support</p>
            <br>
            <button class="stButton">Subscribe Now</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Ultimate</h3>
            <h2>₹2499/year</h2>
            <p>For dedicated spiritual practitioners</p>
            <hr>
            <p>✓ Unlimited questions</p>
            <p>✓ Premium horoscope</p>
            <p>✓ 5 personalized reports/month</p>
            <p>✓ Priority 24/7 support</p>
            <br>
            <button class="stButton">Subscribe Now</button>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ## Enterprise Solutions
    
    Looking for Cosmic Guide for your organization? We offer custom solutions for:
    
    - **Wellness programs** for employees
    - **White-label solutions** for spiritual businesses
    - **API access** for developers
    
    Contact us at enterprise@cosmicguide.com for more information.
    """)

def show_about_page():
    st.markdown("# About Cosmic Guide")
    
    st.markdown("""
    Cosmic Guide was founded with a simple mission: to make spiritual guidance accessible, affordable, 
    and personalized for everyone. We combine ancient spiritual wisdom with modern AI technology to 
    provide insights that can help you navigate life's challenges.
    """)
    
    if lottie_crystal:
        st_lottie(lottie_crystal, height=300, key="crystal")
    
    st.markdown("""
    ## Our Values
    
    - **Authenticity**: We respect and honor the spiritual traditions we draw from
    - **Innovation**: We continuously improve our technology to serve you better
    - **Privacy**: Your data and questions are always kept confidential
    - **Accessibility**: We believe everyone deserves guidance, regardless of budget
    
    ## Frequently Asked Questions
    
    **Is this replacing traditional astrologers?**  
    No, Cosmic Guide is meant to complement traditional guidance, not replace it. We provide affordable 
    access to basic insights, but for major life decisions, we still recommend consulting with experienced practitioners.
    
    **How accurate are the readings?**  
    Our AI provides guidance based on established spiritual principles and your input. Many users find 
    our insights helpful and accurate, but as with any form of guidance, your personal interpretation 
    and intuition are important.
    
    **Can I get a refund?**  
    Yes, we offer a 7-day money-back guarantee on all paid plans if you're not satisfied with the service.
    
    **How is my data used?**  
    We take privacy seriously. Your questions and birth data are used solely to generate your readings 
    and are never shared with third parties. You can delete your data at any time.
    """)

if __name__ == "__main__":
    main()
