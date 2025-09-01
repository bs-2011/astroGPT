import streamlit as st
import openai
from datetime import datetime, date
import random
import requests
from PIL import Image
import io
import base64
import os

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
        border-radius: 18px 18px 0 18px;
        padding: 15px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .assistant-message {
        background: white;
        color: #2D2B4E;
        border-radius: 18px 18px 18px 0;
        padding: 15px 20px;
        margin: 10px 0;
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

# Custom navigation function
def navigate_to(page):
    st.session_state.page = page

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
            user_name = st.text_input("Your Name", placeholder="Enter your name")
            dob = st.date_input("Date of Birth", value=date(1990, 1, 1), 
                               min_value=date(1900, 1, 1), 
                               max_value=date.today())
            birth_time = st.time_input("Time of Birth (if known)", value=datetime.strptime("12:00", "%H:%M").time())
            birth_place = st.text_input("Place of Birth", placeholder="City, Country")
            
            st.markdown("---")
            
            # Guide selection
            st.header("Choose Your Guide")
            guide = st.radio("Select a spiritual guide:", 
                            ("The Vedic Guru", "The Tarot Reader", "The Modern Life Coach"),
                            index=0)
            
            # Guide descriptions
            if guide == "The Vedic Guru":
                st.info("Specializes in Vedic astrology, planetary positions, and ancient remedies.")
            elif guide == "The Tarot Reader":
                st.info("Provides insights through tarot card interpretations and intuitive guidance.")
            else:
                st.info("Offers practical life advice blending modern coaching with spiritual wisdom.")
    
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
        st.image("https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&h=400&fit=crop", 
                 caption="Find your spiritual path with AI guidance")
    
    st.markdown("---")
    
    st.markdown("## How It Works")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>1. Choose Your Guide</h3>
            <p>Select from Vedic, Tarot, or Life Coach perspectives</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>2. Ask Your Question</h3>
            <p>Share what's on your mind - love, career, or life purpose</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>3. Receive Guidance</h3>
            <p>Get personalized insights based on your birth details</p>
        </div>
        """, unsafe_allow_html=True)

def show_chat_page():
    st.markdown("# Chat with Your Guide")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><b>{message["guide"]}:</b> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input at bottom
    st.markdown("---")
    question = st.text_input("Ask your question...", key="input", 
                            placeholder="e.g., What does my career horoscope say for this month?")
    
    col1, col2 = st.columns([1, 6])
    with col1:
        send_btn = st.button("Send", use_container_width=True)
    with col2:
        clear_btn = st.button("Clear Chat", use_container_width=True)
    
    if clear_btn:
        st.session_state.messages = []
        st.experimental_rerun()
    
    if send_btn and question:
        if not st.session_state.api_key_valid:
            st.error("Please enter a valid OpenAI API key in the sidebar to continue.")
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Get sidebar values
            user_name = st.session_state.get("user_name", "")
            dob = st.session_state.get("dob", date(1990, 1, 1))
            birth_time = st.session_state.get("birth_time", datetime.strptime("12:00", "%H:%M").time())
            birth_place = st.session_state.get("birth_place", "")
            guide = st.session_state.get("guide", "The Vedic Guru")
            
            # Define guide personalities
            guide_personalities = {
                "The Vedic Guru": "You are a compassionate Vedic astrologer with deep knowledge of Jyotish. You provide insights based on planetary positions and offer simple remedies. You speak with wisdom and warmth, often referencing Vedic traditions.",
                "The Tarot Reader": "You are an intuitive tarot reader who interprets cards with empathy and insight. You focus on personal growth and self-discovery, offering guidance rather than predictions.",
                "The Modern Life Coach": "You are a practical life coach who blends spiritual wisdom with actionable advice. You help users find clarity and take positive steps in their lives."
            }
            
            # Prepare the prompt
            system_prompt = f"""
            {guide_personalities[guide]}
            
            The user's name is {user_name}. 
            Their date of birth is {dob}. 
            They were born around {birth_time} in {birth_place}.
            
            Provide a thoughtful, helpful response to their question. 
            Be empathetic and encouraging. 
            Keep your response under 150 words.
            """
            
            try:
                # Initialize OpenAI client
                from openai import OpenAI
                client = OpenAI(api_key=st.session_state.api_key)
                
                # Show typing indicator
                with st.spinner(f"{guide} is thinking..."):
                    # Generate response
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question}
                        ],
                        temperature=0.7
                    )
                
                # Get the response content
                answer = response.choices[0].message.content
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer, "guide": guide})
                
                # Rerun to update the chat display
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

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
                <li>Relationship advice</li>
                <li>Personal growth strategies</li>
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
    
    st.markdown("---")
    
    st.markdown("""
    ## Why Choose Cosmic Guide?
    
    - **24/7 Availability**: Get guidance anytime, anywhere
    - **Affordable**: Fraction of the cost of traditional astrologers
    - **Private**: Your questions and data remain confidential
    - **Multiple Perspectives**: Choose from different spiritual traditions
    - **Personalized**: Insights based on your unique birth details
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
            <p>✓ 1 question per day</p>
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
    
    st.image("https://images.unsplash.com/photo-1518976024611-28bf4b48222e?w=1000&h=400&fit=crop", 
             caption="Where ancient wisdom meets modern technology")
    
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