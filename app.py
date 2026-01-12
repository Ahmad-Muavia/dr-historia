import gradio as gr
import os
import requests

# Load GROQ API key from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"  # Updated to current GROQ model

# 🎓 History Expert System Prompt
SYSTEM_PROMPT = """You are Dr. Historia, an enthusiastic and knowledgeable history expert with decades of experience. 
You specialize in world history, ancient civilizations, historical events, and cultural heritage.

Your personality:
- Passionate about making history come alive with engaging storytelling
- Provide accurate historical facts with context and significance
- Use vivid descriptions to help users visualize historical events
- Connect past events to their modern-day relevance
- Cite time periods and dates when relevant
- Encourage curiosity about history

You cover topics including:
- Ancient civilizations (Egypt, Rome, Greece, Indus Valley, etc.)
- Medieval history and empires
- World Wars and modern conflicts
- Cultural and social movements
- Famous historical figures and their contributions
- Historical artifacts and archaeological discoveries

Always be accurate, educational, and inspiring!"""

def query_groq(message, chat_history, era_filter, response_length):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Customize prompt based on era filter
    era_context = ""
    if era_filter != "All Eras":
        era_context = f"\n\nFocus your response on {era_filter} history when relevant."
    
    # Adjust temperature based on response length
    temp = 0.7 if response_length == "Detailed" else 0.5
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT + era_context}]
    for user, bot in chat_history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": bot})
    
    # Add length instruction
    length_instruction = ""
    if response_length == "Brief":
        length_instruction = " Keep your response concise (2-3 sentences)."
    elif response_length == "Detailed":
        length_instruction = " Provide a detailed, comprehensive response."
    
    messages.append({"role": "user", "content": message + length_instruction})
    
    response = requests.post(GROQ_API_URL, headers=headers, json={
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temp,
        "max_tokens": 800 if response_length == "Detailed" else 300
    })
    
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    else:
        return f"Error {response.status_code}: {response.text}"

def respond(message, chat_history, era_filter, response_length):
    if not message.strip():
        return "", chat_history
    
    bot_reply = query_groq(message, chat_history, era_filter, response_length)
    chat_history.append((message, bot_reply))
    return "", chat_history

# Custom CSS for better UI
custom_css = """
#component-0 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
}
.gradio-container {
    font-family: 'Arial', sans-serif;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏛️ Dr. Historia - Your AI History Expert
    ### Explore the fascinating world of history with your personal historian!
    Ask about any historical event, civilization, or figure from any time period.
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=500,
                label="Chat with Dr. Historia",
                avatar_images=("👤", "🎓")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Ask your history question",
                    placeholder="e.g., Tell me about the Roman Empire...",
                    scale=4
                )
                submit_btn = gr.Button("Send 📤", scale=1, variant="primary")
            
            with gr.Row():
                clear = gr.Button("Clear Chat 🗑️")
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Settings")
            
            era_filter = gr.Dropdown(
                choices=["All Eras", "Ancient History", "Medieval Period", 
                        "Early Modern", "Modern History", "Contemporary"],
                value="All Eras",
                label="🕰️ Time Period Focus",
                info="Filter responses by historical era"
            )
            
            response_length = gr.Radio(
                choices=["Brief", "Moderate", "Detailed"],
                value="Moderate",
                label="📝 Response Length",
                info="Choose how detailed you want answers"
            )
            
            gr.Markdown("""
            ### 💡 Example Questions:
            - What caused World War I?
            - Tell me about Cleopatra
            - How did the Silk Road impact trade?
            - What were the Crusades?
            - Explain the Industrial Revolution
            """)
    
    state = gr.State([])
    
    # Event handlers
    msg.submit(respond, [msg, state, era_filter, response_length], [msg, chatbot])
    submit_btn.click(respond, [msg, state, era_filter, response_length], [msg, chatbot])
    clear.click(lambda: ([], []), None, [chatbot, state])

demo.launch(share=True)