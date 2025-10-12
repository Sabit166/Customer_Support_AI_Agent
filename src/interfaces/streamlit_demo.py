import streamlit as st
import asyncio
import uuid
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the project root to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import the customer support agents and models with absolute imports
from src.agent.agent import customer_support_agent
# from src.agents.complaint_specialist import complaint_specialist_agent
# from src.agents.technical_support import technical_support_agent
from src.data.models import UserContext     #, ServiceResponse, ComplaintTicket, TechnicalResponse
from agents import Runner

# Page configuration
st.set_page_config(
    page_title="Customer Support AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .content {
        display: flex;
        margin-top: 0.5rem;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message {
        flex: 1;
        color: #000000;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history and user context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4())
    )

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to build conversation context from chat history
def build_conversation_context(chat_history, max_exchanges=5):
    """Build conversation context from chat history for the agent."""
    context_parts = []
    
    # Take last N exchanges (user + assistant pairs)
    recent_messages = chat_history[-(max_exchanges * 2):]
    
    for msg in recent_messages:
        if msg["role"] == "user":
            context_parts.append(f"Customer: {msg['content']}")
        else:
            # Extract meaningful content from structured responses
            content = msg["content"]
            if isinstance(content, dict):
                if content["type"] == "service_response":
                    data = content["data"]
                    response_text = data.get('content', '')
                    if data.get('actions_taken'):
                        response_text += f" (Actions taken: {', '.join(data.get('actions_taken', []))})"
                    context_parts.append(f"Agent: {response_text}")
                elif content["type"] == "technical_response":
                    data = content["data"]
                    context_parts.append(f"Technical Support: {data.get('diagnosis', '')} - {data.get('customer_instructions', '')}")
                elif content["type"] == "complaint_ticket":
                    data = content["data"]
                    context_parts.append(f"Agent: Created complaint ticket {data.get('ticket_id', '')} for: {data.get('complaint_description', '')}")
                else:
                    context_parts.append(f"Agent: {content['data']}")
            else:
                context_parts.append(f"Agent: {content}")
    
    return "\n".join(context_parts)

# Function to format agent responses based on output type
def format_agent_response(output):
    # Check if output is a Pydantic model and convert to dict
    if hasattr(output, "model_dump"):
        output = output.model_dump()
    
    if isinstance(output, dict):
        # Handle ServiceResponse
        if "response_type" in output and "content" in output:
            return {
                "type": "service_response",
                "data": output
            }
        
        # Handle TechnicalResponse
        elif "issue_type" in output and "diagnosis" in output:
            return {
                "type": "technical_response", 
                "data": output
            }
            
        # Handle ComplaintTicket
        elif "ticket_id" in output and "complaint_description" in output:
            return {
                "type": "complaint_ticket",
                "data": output
            }
    
    # Default: return as string
    return {
        "type": "text",
        "data": str(output)
    }

# Function to handle user input
def handle_user_message(user_input: str):
    # Add user message to chat history immediately
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Set the message for processing in the next rerun
    st.session_state.processing_message = user_input

# Sidebar for user preferences
with st.sidebar:
    st.title("Customer Information")
    
    st.subheader("Customer Identification")
    customer_id_mode = st.radio(
        "How would you like to identify yourself?",
        ["I have a Customer ID", "I'm a new customer", "Generate for me"],
        index=1
    )
    
    if customer_id_mode == "I have a Customer ID":
        customer_id = st.text_input(
            "Enter your Customer ID", 
            placeholder="CUST-XXXXXXXX",
            help="Found on your bill or account dashboard"
        )
        if customer_id:
            if not customer_id.startswith("CUST-"):
                st.warning("Customer IDs typically start with 'CUST-'")
            else:
                st.success(f"✅ Using Customer ID: {customer_id}")
                st.session_state.user_context.user_id = customer_id
    
    elif customer_id_mode == "I'm a new customer":
        st.info("👋 Welcome! We'll create a temporary ID for this session.")
        customer_id = f"TEMP-{uuid.uuid4().hex[:8].upper()}"
        st.code(f"Temporary ID: {customer_id}")
        st.session_state.user_context.user_id = customer_id
    
    else:  # Generate for me
        if st.button("Generate Customer ID"):
            customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
            st.success(f"Generated ID: {customer_id}")
            st.session_state.user_context.user_id = customer_id
    
    st.subheader("Contact Information")
    customer_name = st.text_input("Name", value=st.session_state.user_context.user_name or "")
    if customer_name:
        st.session_state.user_context.user_name = customer_name
    
    st.subheader("Service Information")
    service_plan = st.selectbox(
        "Current Service Plan",
        ["Basic", "Standard", "Premium", "Business", "Not sure"],
        index=0
    )
    if service_plan != "Not sure":
        st.session_state.user_context.current_plan = service_plan
    
    service_area = st.text_input("Service Area/ZIP Code")
    if service_area:
        st.session_state.user_context.service_area = service_area
    
    account_status = st.selectbox(
        "Account Status",
        ["Active", "Suspended", "Pending", "Cancelled", "Guest"],
        index=0
    )
    st.session_state.user_context.account_status = account_status
    
    preferred_contact = st.selectbox(
        "Preferred Contact Method",
        ["Email", "Phone", "SMS", "In-app"],
        index=0
    )
    st.session_state.user_context.preferred_contact = preferred_contact
    
    st.divider()
    
    if st.button("Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.success("New conversation started!")
    
    # Display conversation memory info
    st.subheader("Conversation Memory")
    message_count = len(st.session_state.chat_history)
    if message_count > 0:
        st.success(f"🧠 Memory Active: {message_count} messages")
        st.caption("Agent remembers previous questions and context")
    else:
        st.info("🆕 New conversation - no history yet")

# Main chat interface
st.title("🤖 Customer Support AI Agent")
st.caption("Get help with internet services, billing, technical issues, and file complaints!")

# Display chat messages
for message in st.session_state.chat_history:
    with st.container():
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
                st.caption(message["timestamp"])
        else:
            with st.chat_message("assistant"):
                content = message["content"]
                
                # Handle structured responses
                if isinstance(content, dict):
                    if content["type"] == "service_response":
                        data = content["data"]
                        st.success(f"📋 {data.get('response_type', 'information').replace('_', ' ').title()}")
                        st.write(data.get('content', ''))
                        
                        if data.get('actions_taken'):
                            st.write("**⚡ Actions Taken:**")
                            for action in data.get('actions_taken', []):
                                st.write(f"• {action}")
                        
                        if data.get('ticket_id'):
                            st.info(f"🎫 **Ticket ID:** {data.get('ticket_id')}")
                        
                        if data.get('next_steps'):
                            st.write(f"**➡️ Next Steps:** {data.get('next_steps')}")
                        
                        if data.get('escalation_needed'):
                            st.warning("🚨 **Escalation Required**")
                    
                    elif content["type"] == "technical_response":
                        data = content["data"]
                        st.warning("🔧 **Technical Support Response**")
                        st.write(f"**Issue Type:** {data.get('issue_type', 'N/A')}")
                        st.write(f"**Diagnosis:** {data.get('diagnosis', 'N/A')}")
                        
                        if data.get('solution_steps'):
                            st.write("**Solution Steps:**")
                            for i, step in enumerate(data.get('solution_steps', []), 1):
                                st.write(f"{i}. {step}")
                        
                        if data.get('equipment_involved'):
                            st.write(f"**Equipment:** {', '.join(data.get('equipment_involved', []))}")
                        
                        if data.get('estimated_resolution_time'):
                            st.write(f"**Est. Resolution:** {data.get('estimated_resolution_time')}")
                        
                        st.write(f"**Instructions:** {data.get('customer_instructions', '')}")
                        st.write(f"**Escalation Level:** {data.get('escalation_level', 'Level 1')}")
                        
                        if data.get('requires_technician'):
                            st.error("🚨 **Technician Required**")
                        
                        if data.get('follow_up_needed'):
                            st.info("📞 **Follow-up Required**")
                    
                    elif content["type"] == "complaint_ticket":
                        data = content["data"]
                        st.error("🎫 **Complaint Ticket Created**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Ticket ID:** {data.get('ticket_id', 'N/A')}")
                            st.write(f"**Customer:** {data.get('customer_name', 'N/A')}")
                            st.write(f"**Priority:** {data.get('priority', 'Medium')}")
                        
                        with col2:
                            st.write(f"**Category:** {data.get('category', 'General')}")
                            st.write(f"**Assigned Agent:** {data.get('assigned_agent', 'Unassigned')}")
                            st.write(f"**Status:** {data.get('status', 'Open')}")
                        
                        st.write(f"**Description:** {data.get('complaint_description', 'N/A')}")
                    
                    else:  # text type
                        st.write(content["data"])
                else:
                    # Fallback for plain text
                    st.write(content)
                
                st.caption(message["timestamp"])

# User input
user_input = st.chat_input("Ask about your service, report an issue, or get help...")
if user_input:
    handle_user_message(user_input)
    st.rerun()

# Process message if needed
if st.session_state.processing_message:
    user_input = st.session_state.processing_message
    st.session_state.processing_message = None
    
    with st.spinner("Thinking..."):
        try:
            # Build conversation context from previous messages (excluding the current one we just added)
            previous_messages = st.session_state.chat_history[:-1]  # Exclude the last message (current user input)
            conversation_context = build_conversation_context(previous_messages)
            
            # Create enhanced input with conversation history
            if conversation_context:
                enhanced_input = f"""Previous conversation:
{conversation_context}

Current customer message: {user_input}

Please respond considering the full conversation history above. Reference previous interactions when relevant."""
            else:
                # First message in conversation
                enhanced_input = user_input
            
            # Send enhanced input with conversation context to agent
            result = asyncio.run(Runner.run(
                customer_support_agent, 
                enhanced_input,  # Input with conversation history
                context=st.session_state.user_context
            ))
            
            # Format and add response
            response_content = format_agent_response(result.final_output)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": {"type": "text", "data": error_message},
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
        
        st.rerun()

# Footer
st.divider()
st.caption("Customer Support AI Agent | Powered by OpenAI Agents SDK | Built with Streamlit")