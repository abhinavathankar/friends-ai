import streamlit as st
import random
import time
import feedparser
import google.generativeai as genai
# --- Setup & Configuration ---
st.set_page_config(page_title="Friends Comedy Syndicate", page_icon="☕", layout="centered")
# --- Custom CSS for Phone UI ---
st.markdown("""
<style>
    /* Mobile Container */
    .phone-frame {
        width: 375px;
        height: 700px;
        margin: auto;
        border: 12px solid #1c1c1e; /* Dark border like a case/bezel */
        border-radius: 40px;
        background-color: #000; /* OLED Black */
        position: relative;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.5);
    }
    /* Notch/Header area */
    .phone-header {
        background-color: #1c1c1e00; /* Transparent-ish */
        color: white;
        padding: 15px 20px;
        text-align: center;
        border-bottom: 1px solid #333;
        backdrop-filter: blur(10px);
        position: absolute;
        top: 0;
        width: 100%;
        z-index: 10;
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    
    .group-name {
        font-size: 16px;
        font-weight: 600;
    }
    
    .group-count {
        font-size: 11px;
        color: #8e8e93;
    }
    /* Chat Area */
    .chat-container {
        height: 100%;
        overflow-y: scroll;
        padding-top: 90px; /* Space for header */
        padding-bottom: 20px;
        padding-left: 15px;
        padding-right: 15px;
        background-color: #000;
        scrollbar-width: none; /* Hide scrollbar Firefox */
    }
    .chat-container::-webkit-scrollbar { 
        display: none; /* Hide scrollbar Chrome/Safari */
    }
    /* Bubbles */
    .message-row {
        display: flex;
        margin-bottom: 8px;
        flex-direction: column;
    }
    
    .sender-name {
        font-size: 11px;
        color: #8e8e93;
        margin-bottom: 2px;
        margin-left: 12px;
    }
    
    .bubble {
        max-width: 75%;
        padding: 10px 14px;
        border-radius: 18px;
        font-size: 15px;
        line-height: 1.4;
        color: white;
        position: relative;
    }
    
    /* Left (Others) */
    .bubble-left {
        background-color: #262628; /* Gray */
        align-self: flex-start;
        border-bottom-left-radius: 4px;
    }
    
    /* Right (Chandler/Self) */
    .bubble-right {
        background-color: #0A84FF; /* iOS Blue */
        align-self: flex-end;
        border-bottom-right-radius: 4px;
    }
    
    /* System/Manager Messages */
    .system-msg {
        text-align: center;
        color: #8e8e93;
        font-size: 12px;
        margin: 10px 0;
    }
    /* Animations */
    @keyframes popIn {
        0% { opacity: 0; transform: translateY(10px) scale(0.95); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    .message-row {
        animation: popIn 0.3s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)
# --- Real AI & Data Logic ---
def fetch_real_trending_topic():
    """Fetches real trending topics from Google Trends RSS."""
    try:
        # Google Trends US Daily RSS
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        feed = feedparser.parse(url)
        if feed.entries:
            entry = random.choice(feed.entries)
            return entry.title
    except Exception as e:
        pass
    
    # Fallback if offline
    return random.choice(["Artificial Intelligence", "The Metaverse", "Crypto Crash", "Mars Colonization"])
def generate_ai_response(agent_name, topic, chat_history, api_key):
    """Uses Gemini API to generate a response in character."""
    if not api_key:
        return None  # Fallback to mock if no key
    genai.configure(api_key=api_key)
    # UPDATED MODEL VERSION
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    # Construct Context
    history_text = "\n".join([f"{entry['agent']}: {entry['message']}" for entry in chat_history])
    
    prompt = f"""
    You are roleplaying as {agent_name} from the TV show 'Friends'.
    Current Conversation Topic: {topic}
    
    Recent Chat History:
    {history_text}
    
    Your Goal:
    - Roast the previous speaker or make a cynical/funny comment about the topic.
    - Be modern, unfiltered, and edgy (TV-MA).
    - Keep it short (under 20 words).
    - STAY IN CHARACTER.
    
    Reply ONLY with the message text.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[AI Error: {str(e)}]"
# --- Mock Logic (Fallback) ---
class MockAgent:
    def __init__(self, name):
        self.name = name
    
    def speak(self, topic, chat_history):
        # Fallback simplistic logic
        return f"I have no API key, but I have opinions on {topic}."
# --- Main App Logic ---
# Secrets Management
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    # Local run without secrets.toml
    api_key = None
except KeyError:
    # Secrets file exists but key is missing
    api_key = None
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "topic" not in st.session_state:
    st.session_state.topic = ""
# Generate Button
with st.sidebar:
    st.header("Control Panel")
    if st.button("Generate 'Top Tier' Chat 🏆", type="primary"):
        with st.spinner("Mining real-world comedy..."):
            
            # 1. Get Real Topic
            topic = fetch_real_trending_topic()
            
            # 2. Run Conversation
            current_log = []
            agents = ["Joey", "Chandler", "Ross"]
            last_speaker = "Manager"
            
            # Add topic entry (hidden in UI but good for context)
            current_log.append({"agent": "Manager", "message": f"Topic: {topic}"})
            
            for _ in range(4): # 4 turns
                # Agents are strings now ["Joey", "Chandler", "Ross"]
                available = [a for a in agents if a != last_speaker]
                speaker_name = random.choice(available)
                
                if api_key:
                    # REAL AI
                    msg = generate_ai_response(speaker_name, topic, current_log, api_key)
                else:
                    # MOCK FALLBACK
                    msg = f"Mock response about {topic} because no API key."
                
                current_log.append({"agent": speaker_name, "message": msg})
                last_speaker = speaker_name
            
            # Save to state
            st.session_state.topic = topic
            st.session_state.chat_log = current_log
# --- Render UI ---
def render_phone_ui():
    chat_html = ""
    
    if st.session_state.chat_log:
        for entry in st.session_state.chat_log:
            name = entry["agent"]
            msg = entry["message"]
            
            # Privacy Check: Hide Manager/Critic
            if name in ["Manager", "Critic"]:
                continue
            
            if name == "Chandler":
                # Right align (Blue)
                chat_html += f"""<div class='message-row' style='align-items: flex-end;'>
<div class='bubble bubble-right'>{msg}</div>
</div>"""
            else:
                # Left align (Gray)
                chat_html += f"""<div class='message-row' style='align-items: flex-start;'>
<div class='sender-name'>{name}</div>
<div class='bubble bubble-left'>{msg}</div>
</div>"""
    # Wrap in Phone Frame
    topic_display = st.session_state.topic if st.session_state.topic else "Waiting..."
    full_html = f"""<div class='phone-frame'>
<div class='phone-header'>
<div class='group-name'>Friends Syndicate ☕️</div>
<div class='group-count'>3 People</div>
</div>
<div class='chat-container'>
{chat_html}
</div>
</div>"""
    
    st.markdown(full_html, unsafe_allow_html=True)
render_phone_ui()
# Instruction (Centered)
st.markdown("<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: 10px;'>Visuals simulate iOS.</div>", unsafe_allow_html=True)
# --- Instagram Logic ---
# --- Instagram Logic (Native Python Rendering) ---
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
def generate_instagram_image(topic, chat_log):
    # Canvas Settings (IG Portrait 4:5)
    width = 1080
    height = 1350
    bg_color = (0, 0, 0)
    text_color = (255, 255, 255)
    blue_bubble = (10, 132, 255)
    gray_bubble = (38, 38, 40)
    
    img = Image.new('RGB', (width, height), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Fonts
    try:
        # Standard styling - Increased sizes per user request
        font_main = ImageFont.truetype("arial.ttf", 42)
        font_small = ImageFont.truetype("arial.ttf", 32)
        font_header = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font_main = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_header = ImageFont.load_default()
    # Draw Header
    d.text((50, 50), "Friends Syndicate ☕️", font=font_header, fill=text_color)
    d.text((50, 130), f"Topic: {topic[:35]}...", font=font_small, fill=(142, 142, 147))
    
    # Draw Chat
    y = 250
    margin = 50
    bubble_padding = 30
    max_bubble_width = 800
    
    for entry in chat_log:
        if entry["agent"] in ["Manager", "Critic"]: continue
        
        msg = entry["message"]
        name = entry["agent"]
        
        # 1. Wrap Text
        # Reduced width char limit because font is bigger
        lines = textwrap.wrap(msg, width=35) 
        
        # 2. Calculate Bubble Dimensions
        line_height = 52 # formatting space
        text_block_height = len(lines) * line_height
        bubble_h = text_block_height + (bubble_padding * 2)
        
        # 3. Draw
        if name == "Chandler":
            x = width - max_bubble_width - margin
            color = blue_bubble
            
            d.rounded_rectangle([x, y, x + max_bubble_width, y + bubble_h], radius=35, fill=color)
            
            cy = y + bubble_padding
            for line in lines:
                d.text((x + bubble_padding, cy), line, font=font_main, fill=text_color)
                cy += line_height
        else:
            x = margin
            color = gray_bubble
            
            d.text((x + 10, y - 35), name, font=font_small, fill=(142, 142, 147))
            d.rounded_rectangle([x, y, x + max_bubble_width, y + bubble_h], radius=35, fill=color)
            
            cy = y + bubble_padding
            for line in lines:
                d.text((x + bubble_padding, cy), line, font=font_main, fill=text_color)
                cy += line_height
        
        y += bubble_h + 60
    return img
st.divider()
# "Post to Instagram" Button Logic
if st.button("📸 Create Instagram Post", type="secondary", use_container_width=True):
    if st.session_state.chat_log:
        with st.spinner("Generating High-Res Screenshot..."):
            img = generate_instagram_image(st.session_state.topic, st.session_state.chat_log)
            # Show in UI
            st.image(img, caption="Ready for Instagram!", use_container_width=True)
            
            # Download Button
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name="friends_chat.png",
                mime="image/png"
            )
    else:
        st.warning("Generate a chat first!")



