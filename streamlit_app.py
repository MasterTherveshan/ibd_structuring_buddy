import streamlit as st
from openai import OpenAI
import re

st.set_page_config(page_title="IBD Structuring Assistant", page_icon="🏦", layout="wide")

st.markdown("""
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        h1 {font-size: 2.5rem !important; text-align: center; margin-bottom: 2rem !important;}
        [data-testid="stChatMessage"] {border-radius: 10px; padding: 1rem; margin: 0.5rem 0;}
        [data-testid="stChatMessage"][data-testid="user"] {background-color: rgba(240, 242, 246, 0.05);}
        [data-testid="stChatMessage"][data-testid="assistant"] {background-color: rgba(240, 242, 246, 0.1);}
        .stChatInputContainer {padding-bottom: 2rem;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .instruction-box {background-color: rgba(240, 242, 246, 0.05); border-radius: 10px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #4CAF50;}
        .example-box {background-color: rgba(240, 242, 246, 0.05); border-radius: 10px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #2196F3;}
    </style>
""", unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create(
        tool_resources={"file_search": {"vector_store_ids": [st.secrets["VECTOR_STORE_ID"]]}}
    )
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])

st.title("IBD Structuring Assistant")

col1, col2 = st.columns([3, 1])

with col1:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask me anything about IBD structuring..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            assistant_message = messages.data[0].content[0].text.value
            
            # Clean up references and formatting
            cleaned_message = re.sub(r'\[\d+\]', '', assistant_message)
            cleaned_message = re.sub(r'\d+:\d+†[^】]*】', '', cleaned_message)
            cleaned_message = re.sub(r'【.*?】', '', cleaned_message)
            cleaned_message = re.sub(r'[【】]', '', cleaned_message)
            
            # Format the message for better readability
            lines = cleaned_message.split('.')
            formatted_lines = []
            
            for line in lines:
                if not line.strip():
                    continue
                if re.match(r'^\s*\d+\s*', line):
                    formatted_lines.append('\n' + line.strip() + '.')
                else:
                    formatted_lines.append(line.strip() + '.')
            
            cleaned_message = ' '.join(formatted_lines)
            cleaned_message = re.sub(r'\n\s*\n', '\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            message_placeholder.markdown(cleaned_message, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_message})

with col2:
    st.markdown("""
        <div class="instruction-box">
            <h3>📚 About</h3>
            <p>Welcome to the IBD Structuring Assistant. This AI-powered tool helps with:</p>
            <ul>
                <li>Product structuring queries</li>
                <li>Documentation searches</li>
                <li>Process guidance</li>
                <li>Best practice advice</li>
            </ul>
        </div>
        
        <div class="instruction-box">
            <h3>💡 Tips for Best Results</h3>
            <ul>
                <li>Be specific in your questions</li>
                <li>Provide relevant context</li>
                <li>Ask follow-up questions</li>
                <li>Request examples when needed</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Example Questions using buttons
    st.markdown("<div class='example-box'><h3>🔍 Example Questions</h3></div>", unsafe_allow_html=True)
    
    if st.button("What role does the FSCA play in structured finance?"):
        st.session_state.messages.append({"role": "user", "content": "What role does the Financial Sector Conduct Authority (FSCA) play in structured finance transactions in South Africa?"})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content="What role does the Financial Sector Conduct Authority (FSCA) play in structured finance transactions in South Africa?"
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id
        )
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            assistant_message = messages.data[0].content[0].text.value
            cleaned_message = re.sub(r'\[\d+\]', '', assistant_message)
            cleaned_message = re.sub(r'\d+:\d+†[^】]*】', '', cleaned_message)
            cleaned_message = re.sub(r'【.*?】', '', cleaned_message)
            cleaned_message = re.sub(r'[【】]', '', cleaned_message)
            
            lines = cleaned_message.split('.')
            formatted_lines = []
            for line in lines:
                if not line.strip(): continue
                if re.match(r'^\s*\d+\s*', line):
                    formatted_lines.append('\n' + line.strip() + '.')
                else:
                    formatted_lines.append(line.strip() + '.')
            
            cleaned_message = ' '.join(formatted_lines)
            cleaned_message = re.sub(r'\n\s*\n', '\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            message_placeholder.markdown(cleaned_message, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_message})
        st.rerun()

    if st.button("What are the typical risk management strategies for currency volatility?"):
        st.session_state.messages.append({"role": "user", "content": "What are the typical risk management strategies employed by South African banks when dealing with currency volatility in cross-border structured finance transactions?"})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content="What are the typical risk management strategies employed by South African banks when dealing with currency volatility in cross-border structured finance transactions?"
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id
        )
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            assistant_message = messages.data[0].content[0].text.value
            cleaned_message = re.sub(r'\[\d+\]', '', assistant_message)
            cleaned_message = re.sub(r'\d+:\d+†[^】]*】', '', cleaned_message)
            cleaned_message = re.sub(r'【.*?】', '', cleaned_message)
            cleaned_message = re.sub(r'[【】]', '', cleaned_message)
            
            lines = cleaned_message.split('.')
            formatted_lines = []
            for line in lines:
                if not line.strip(): continue
                if re.match(r'^\s*\d+\s*', line):
                    formatted_lines.append('\n' + line.strip() + '.')
                else:
                    formatted_lines.append(line.strip() + '.')
            
            cleaned_message = ' '.join(formatted_lines)
            cleaned_message = re.sub(r'\n\s*\n', '\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            message_placeholder.markdown(cleaned_message, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_message})
        st.rerun()

    if st.button("What are the differences between JSE Main Board and AltX listing requirements?"):
        st.session_state.messages.append({"role": "user", "content": "What are the key differences in regulatory requirements between the JSE's Main Board and the AltX for listing structured finance products?"})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content="What are the key differences in regulatory requirements between the JSE's Main Board and the AltX for listing structured finance products?"
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id
        )
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            assistant_message = messages.data[0].content[0].text.value
            cleaned_message = re.sub(r'\[\d+\]', '', assistant_message)
            cleaned_message = re.sub(r'\d+:\d+†[^】]*】', '', cleaned_message)
            cleaned_message = re.sub(r'【.*?】', '', cleaned_message)
            cleaned_message = re.sub(r'[【】]', '', cleaned_message)
            
            lines = cleaned_message.split('.')
            formatted_lines = []
            for line in lines:
                if not line.strip(): continue
                if re.match(r'^\s*\d+\s*', line):
                    formatted_lines.append('\n' + line.strip() + '.')
                else:
                    formatted_lines.append(line.strip() + '.')
            
            cleaned_message = ' '.join(formatted_lines)
            cleaned_message = re.sub(r'\n\s*\n', '\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            message_placeholder.markdown(cleaned_message, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_message})
        st.rerun()

    if st.button("How do SA Banks Act requirements shape SPV establishment?"):
        st.session_state.messages.append({"role": "user", "content": "How do the South African Banks Act requirements shape the establishment and operation of SPVs used in structured finance transactions?"})
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content="How do the South African Banks Act requirements shape the establishment and operation of SPVs used in structured finance transactions?"
        )
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id
        )
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            
            assistant_message = messages.data[0].content[0].text.value
            cleaned_message = re.sub(r'\[\d+\]', '', assistant_message)
            cleaned_message = re.sub(r'\d+:\d+†[^】]*】', '', cleaned_message)
            cleaned_message = re.sub(r'【.*?】', '', cleaned_message)
            cleaned_message = re.sub(r'[【】]', '', cleaned_message)
            
            lines = cleaned_message.split('.')
            formatted_lines = []
            for line in lines:
                if not line.strip(): continue
                if re.match(r'^\s*\d+\s*', line):
                    formatted_lines.append('\n' + line.strip() + '.')
                else:
                    formatted_lines.append(line.strip() + '.')
            
            cleaned_message = ' '.join(formatted_lines)
            cleaned_message = re.sub(r'\n\s*\n', '\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            message_placeholder.markdown(cleaned_message, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": cleaned_message})
        st.rerun()

    st.markdown("""
        <div class="instruction-box">
            <h3>⚠️ Important Notes</h3>
            <ul>
                <li>All advice should be verified with your team</li>
                <li>The assistant has access to approved documentation</li>
                <li>Confidential information should not be shared</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
