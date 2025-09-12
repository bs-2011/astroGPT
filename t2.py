"""
Cosmic Guide MVP - Streamlit Production Version
Optimized for Diwali Launch
Focus: Business users, engagement mechanics, fast responses
"""

import streamlit as st
import hashlib
import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
import re

# OpenAI setup
try:
    from openai import OpenAI
except ImportError:
    st.error("Please install openai: pip install openai")
    st.stop()

# ============== Configuration ==============
st.set_page_config(
    page_title="Cosmic Guide - AI Business Astrology",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - No emojis, high contrast
st.markdown("""
<style>
    /* Core Design System */
    :root {
        --primary: #2E3440;
        --secondary: #4C566A;
        --accent: #5E81AC;
        --success: #A3BE8C;
        --warning: #EBCB8B;
        --danger: #BF616A;
        --bg: #FFFFFF;
        --surface: #F8F9FA;
        --text: #2E3440;
        --text-light: #4C566A;
        --border: #E5E9F0;
    }
    
    /* Typography */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background: var(--bg);
        color: var(--text);
    }
    
    /* Message Bubbles */
    .user-msg {
        background: var(--accent);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        word-wrap: break-word;
    }
    
    .ai-msg {
        background: var(--surface);
        color: var(--text);
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 70%;
        border: 1px solid var(--border);
    }
    
    /* Business Command Center */
    .command-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .command-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: var(--accent);
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, var(--accent), var(--secondary));
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
    }
    
    .metric {
        font-size: 2em;
        font-weight: bold;
        color: var(--success);
    }
    
    /* Remove Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .user-msg, .ai-msg {
            max-width: 85%;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============== Session State ==============
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'messages': [],
        'user_profile': {},
        'onboarded': False,
        'challenge': None,
        'api_key': '',
        'conversation_depth': 0,
        'last_topic': None,
        'engagement_score': 0,
        'premium_triggered': False,
        'daily_question_used': False,
        'last_question_date': None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============== Core Functions ==============

def detect_intent(text: str) -> Dict[str, any]:
    """Advanced intent detection for business context"""
    text_lower = text.lower()
    
    intents = {
        'launch_timing': ['when', 'launch', 'start', 'begin', 'timing', 'muhurat'],
        'pricing': ['price', 'charge', 'cost', 'rate', 'fee', 'pricing'],
        'market': ['market', 'niche', 'audience', 'customer', 'segment'],
        'team': ['hire', 'team', 'partner', 'cofounder', 'employee'],
        'funding': ['investor', 'funding', 'raise', 'capital', 'investment'],
        'growth': ['grow', 'scale', 'expand', 'increase', 'boost'],
        'problem': ['problem', 'issue', 'challenge', 'stuck', 'difficult'],
        'decision': ['should', 'decide', 'choice', 'option', 'vs'],
    }
    
    detected = []
    urgency = 0
    
    for intent, keywords in intents.items():
        if any(keyword in text_lower for keyword in keywords):
            detected.append(intent)
    
    # Urgency detection
    urgent_words = ['urgent', 'immediately', 'now', 'today', 'tomorrow', 'asap', 'quickly']
    urgency = sum(1 for word in urgent_words if word in text_lower)
    
    return {
        'intents': detected,
        'urgency': min(urgency, 3),
        'is_business': len(detected) > 0,
        'complexity': len(text.split()) > 20
    }

def generate_layer1_response(question: str, profile: Dict) -> str:
    """Generate Hook Layer - Immediate, specific insight"""
    client = OpenAI(api_key=st.session_state.api_key)
    
    prompt = f"""
    User Profile: {json.dumps(profile, default=str)}
    Question: {question}
    
    Provide ONE powerful, specific insight in 30-40 words maximum.
    Make it surprising or counterintuitive if possible.
    Use present tense. No fluff. No greetings.
    
    Format: Direct statement that creates curiosity.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise business astrology advisor. Brief, impactful insights only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "The cosmic patterns suggest examining this from a different angle. Let me analyze further..."

def generate_layer2_response(question: str, profile: Dict, context: List) -> str:
    """Generate Exploration Layer - Detailed analysis"""
    client = OpenAI(api_key=st.session_state.api_key)
    
    prompt = f"""
    User Profile: {json.dumps(profile, default=str)}
    Question: {question}
    Previous Context: {context[-3:] if context else 'None'}
    
    Provide detailed analysis with:
    1. Three specific observations based on cosmic timing
    2. One actionable step for next 7 days
    3. One warning or thing to avoid
    
    Keep under 150 words. Professional tone. No emojis.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert combining Vedic astrology with business strategy."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Based on current planetary positions, focusing on systematic progress will yield results."

def generate_business_command(command_type: str, profile: Dict) -> str:
    """Generate specific business guidance based on command type"""
    client = OpenAI(api_key=st.session_state.api_key)
    
    commands = {
        'launch_timing': "Calculate optimal launch window in next 3 months considering planetary positions and market cycles.",
        'pricing': "Determine pricing strategy based on numerological compatibility and market positioning.",
        'partnership': "Analyze compatibility for business partnership including trust factors and growth potential.",
        'market_analysis': "Identify 3 profitable niches based on birth chart strengths and market gaps.",
        'funding': "Assess funding readiness and optimal timing for investor approach.",
        'team_hiring': "Provide hiring timeline and team composition guidance for next quarter."
    }
    
    prompt = f"""
    User Profile: {json.dumps(profile, default=str)}
    Command: {commands.get(command_type, 'Provide business guidance')}
    
    Provide:
    1. Specific timeline or number
    2. Three action items
    3. One success metric
    
    Format as structured business advice. No spiritual jargon. Under 120 words.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business strategist using cosmic timing. Be specific and actionable."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Strategic timing analysis in progress. Please ensure API key is configured."

def check_daily_limit() -> bool:
    """Check if user has used their daily free question"""
    if not st.session_state.api_key:
        return True  # No limit if no API key
    
    today = date.today()
    if st.session_state.last_question_date != today:
        st.session_state.daily_question_used = False
        st.session_state.last_question_date = today
    
    return not st.session_state.daily_question_used

def calculate_engagement_score() -> int:
    """Calculate user engagement for premium triggers"""
    score = 0
    score += len(st.session_state.messages) * 10
    score += st.session_state.conversation_depth * 20
    
    # Business intent bonus
    for msg in st.session_state.messages[-5:]:
        if msg['role'] == 'user':
            intent = detect_intent(msg['content'])
            if intent['is_business']:
                score += 15
            score += intent['urgency'] * 10
    
    return min(score, 100)

# ============== UI Components ==============

def show_onboarding():
    """Smart onboarding flow"""
    st.markdown("# Welcome to Cosmic Guide")
    st.markdown("### Your AI-Powered Business Astrology Advisor")
    
    if not st.session_state.challenge:
        st.markdown("#### What brings you here today?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Launch my business", use_container_width=True):
                st.session_state.challenge = "business_launch"
                st.rerun()
            if st.button("💰 Increase revenue", use_container_width=True):
                st.session_state.challenge = "revenue"
                st.rerun()
                
        with col2:
            if st.button("🤝 Find partners", use_container_width=True):
                st.session_state.challenge = "partnership"
                st.rerun()
            if st.button("📈 Scale operations", use_container_width=True):
                st.session_state.challenge = "scaling"
                st.rerun()
                
        with col3:
            if st.button("💼 Career transition", use_container_width=True):
                st.session_state.challenge = "career"
                st.rerun()
            if st.button("🎯 General guidance", use_container_width=True):
                st.session_state.challenge = "general"
                st.rerun()
    
    else:
        # Collect minimal info
        with st.form("profile_form"):
            st.markdown("#### Quick Profile Setup")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("First Name", placeholder="John")
                birth_date = st.date_input("Birth Date", 
                                          value=date(1990, 1, 1),
                                          min_value=date(1950, 1, 1),
                                          max_value=date.today())
            
            with col2:
                birth_time = st.time_input("Birth Time (if known)", value=datetime.now().time())
                location = st.text_input("Birth City", placeholder="Delhi")
            
            submitted = st.form_submit_button("Get My First Insight", use_container_width=True)
            
            if submitted and name:
                st.session_state.user_profile = {
                    'name': name,
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'location': location,
                    'challenge': st.session_state.challenge
                }
                st.session_state.onboarded = True
                
                # Generate welcome insight
                welcome = f"Welcome {name}. Based on your birth chart, the next 21 days are crucial for {st.session_state.challenge.replace('_', ' ')}. Mercury's position suggests unexpected opportunities approaching."
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': welcome,
                    'layer': 'welcome'
                })
                st.rerun()

def show_business_command_center():
    """Quick action buttons for business users"""
    st.markdown("### Business Command Center")
    
    col1, col2, col3 = st.columns(3)
    
    commands = [
        ("Launch Timing", "launch_timing", col1),
        ("Pricing Strategy", "pricing", col2),
        ("Partnership Check", "partnership", col3),
        ("Market Analysis", "market_analysis", col1),
        ("Funding Readiness", "funding", col2),
        ("Team Hiring", "team_hiring", col3),
    ]
    
    for label, command, column in commands:
        with column:
            if st.button(label, key=f"cmd_{command}", use_container_width=True):
                response = generate_business_command(command, st.session_state.user_profile)
                st.session_state.messages.append({
                    'role': 'user',
                    'content': f"Analyze: {label}",
                    'command': True
                })
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'layer': 'command'
                })
                st.rerun()

def show_chat_interface():
    """Main chat interface with progressive disclosure"""
    
    # Display messages
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.markdown(f"<div class='user-msg'>{message['content']}</div>", 
                       unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-msg'>{message['content']}</div>", 
                       unsafe_allow_html=True)
            
            # Show premium trigger if applicable
            if st.session_state.engagement_score > 50 and not st.session_state.premium_triggered:
                if len(st.session_state.messages) > 6:
                    show_premium_prompt()
                    st.session_state.premium_triggered = True
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input("Ask your question...", 
                                      placeholder="When should I launch my product?",
                                      label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)
    
    if submitted and user_input:
        # Check daily limit for free users
        if not st.session_state.api_key and not check_daily_limit():
            st.warning("Daily free question limit reached. Add API key or upgrade for unlimited access.")
            return
        
        # Process message
        process_user_message(user_input)

def process_user_message(user_input: str):
    """Process user message with layer system"""
    
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input
    })
    
    # Detect intent
    intent = detect_intent(user_input)
    
    # Update engagement
    st.session_state.conversation_depth += 1
    st.session_state.engagement_score = calculate_engagement_score()
    
    # Generate appropriate layer response
    if st.session_state.conversation_depth == 1 or intent['urgency'] > 1:
        # Layer 1: Hook
        response = generate_layer1_response(user_input, st.session_state.user_profile)
        layer = 'hook'
    elif st.session_state.conversation_depth < 4:
        # Layer 2: Exploration
        response = generate_layer2_response(
            user_input, 
            st.session_state.user_profile,
            [m['content'] for m in st.session_state.messages[-3:]]
        )
        layer = 'exploration'
    else:
        # Layer 3: Would be premium
        response = "This requires deep analysis. Your chart shows complex patterns that need comprehensive review. Consider our Growth plan for detailed roadmap."
        layer = 'premium_gate'
    
    # Add response
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response,
        'layer': layer
    })
    
    # Mark daily question as used for free users
    if not st.session_state.api_key:
        st.session_state.daily_question_used = True
    
    st.rerun()

def show_premium_prompt():
    """Show premium upgrade prompt"""
    st.markdown("""
    <div class='insight-card'>
        <h3>Unlock Your Complete Cosmic Blueprint</h3>
        <p>You're asking the right questions. Get unlimited guidance with:</p>
        <ul>
            <li>Detailed 3-month business roadmap</li>
            <li>Daily auspicious timing alerts</li>
            <li>Team compatibility analysis</li>
            <li>Priority support</li>
        </ul>
        <p><strong>Special: ₹199/month (normally ₹499)</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.
