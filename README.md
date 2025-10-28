# 🤖 Customer Support AI Agent System

A comprehensive, production-ready customer support AI agent built with OpenAI Agents SDK, featuring advanced RAG capabilities, real-time complaint logging, and intelligent conversation management.

## ✨ Key Features

### 🧠 **Advanced AI Agent Framework**
- **OpenAI Agents SDK Integration**: Professional-grade agent orchestration with function tool decorators
- **Multi-Tool Coordination**: Intelligent tool selection and sequential execution for complex workflows
- **Context-Aware Responses**: Maintains conversation history and customer context across interactions
- **Structured Output Models**: Type-safe responses using Pydantic v2 models

### 🔍 **RAG-Powered Knowledge Base**
- **Vector Similarity Search**: FAISS-powered semantic search with 235+ document chunks
- **HuggingFace Embeddings**: Advanced all-MiniLM-L6-v2 model for accurate information retrieval
- **Comprehensive Dataset**: Rich knowledge base covering:
  - 6 Internet packages (Basic to Ultra Gigabit)
  - Business hours and contact information
  - Detailed company policies (refund, cancellation, privacy)
  - Service coverage areas and technical support guides
  - Billing information and payment policies

### 📊 **Real-Time Google Sheets Integration**
- **Automated Complaint Logging**: Seamless integration with Google Sheets API
- **Service Account Authentication**: Secure, scalable authentication using JSON credentials
- **Structured Data Tracking**: Automatic complaint categorization and agent assignment
- **Real-Time Updates**: Instant logging of complaint tickets with timestamp and priority

### 🌐 **Modern Web Interface**
- **Streamlit-Powered UI**: Professional, responsive web interface
- **Real-Time Chat**: Live conversation with typing indicators and message history
- **Customer Identification System**: Flexible ID management (existing, new, or generated)
- **Rich Response Formatting**: Structured display of service responses, technical support, and complaint tickets
- **Context Management**: Visual conversation memory tracking

### 📋 **Intelligent Complaint Management**
- **Automatic Ticket Generation**: Smart ticket creation with unique IDs
- **Priority Assessment**: AI-powered priority assignment based on complaint content
- **Category Classification**: Automatic categorization (Technical, Billing, Service, General)
- **Agent Assignment**: Intelligent routing to specialized support agents
- **Dual Logging System**: Both internal tracking and Google Sheets logging

### 🔧 **Technical Excellence**
- **Production-Ready Architecture**: Modular design with clear separation of concerns
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Environment Configuration**: Secure configuration management with .env files
- **Logging & Monitoring**: Logfire integration for observability and tracing
- **Type Safety**: Full Pydantic model validation throughout the system

## 🏗️ Architecture Overview

```
Customer_Support_AI_Agent/
├── src/
│   ├── agent/                    # Core AI agent components
│   │   ├── agent.py             # Main customer support agent
│   │   ├── knowledge_base_tool.py # RAG-powered search tool
│   │   ├── complaint_ticket_tool.py # Complaint processing tool
│   │   ├── google_sheet_tool_real.py # Google Sheets integration
│   │   └── knowledge_base.py    # Comprehensive knowledge dataset
│   ├── interfaces/              # User interfaces
│   │   ├── streamlit_demo.py    # Web interface
│   │   └── customer_support_cli.py # CLI interface
│   ├── data/                    # Data models and schemas
│   │   └── models.py           # Pydantic models for type safety
│   ├── agents/                  # Specialized agent modules
│   │   ├── customer_support_main.py
│   │   ├── complaint_specialist.py
│   │   └── technical_support.py
│   └── guardrails/             # AI safety and ethics
│       └── budget_guardrails.py
├── database/                   # Database schemas
│   ├── mysql_schema.sql       # MySQL schema for persistence
│   └── sqlite_to_mysql.sql    # Migration scripts
├── requirements.txt           # Python dependencies (178 packages)
├── .env                      # Environment configuration
└── google_service_account.json # Google API credentials
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API access (GitHub Models or OpenAI)
- Google Cloud Platform account (for Sheets integration)
- MySQL server (for conversation persistence)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-repo/customer-support-ai-agent
cd customer-support-ai-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Configure Google Sheets**
- Create a Google Cloud project
- Enable Google Sheets API
- Download service account JSON
- Place as `google_service_account.json`

5. **Run the application**
```bash
# Web interface (recommended)
streamlit run src/interfaces/streamlit_demo.py

# CLI interface
python src/interfaces/customer_support_cli.py
```

## ⚙️ Configuration

### Environment Variables
```env
# AI Model Configuration
BASE_URL="https://models.github.ai/inference/v1"
API_KEY="your-api-key"
MODEL_NAME="openai/gpt-4.1-nano"

# Monitoring
LOGFIRE_API_KEY="your-logfire-token"

# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS_PATH="google_service_account.json"
GOOGLE_SHEET_ID="your-sheet-id"
GOOGLE_SHEET_NAME="Customer Support Complaints"

```

## 🎯 Usage Examples

### Web Interface
1. Navigate to the Streamlit interface
2. Identify yourself (existing customer, new customer, or generate ID)
3. Ask questions like:
   - "What internet packages do you offer?"
   - "I'm having slow internet speeds"
   - "I want to file a complaint about my service"

### Programmatic Usage
```python
from src.agent.agent import customer_support_agent
from src.data.models import UserContext
from agents import Runner

# Create user context
user_context = UserContext(
    user_id="CUST-12345678",
    user_name="John Doe",
    current_plan="Standard"
)

# Run agent
result = await Runner.run(
    customer_support_agent,
    "What are your business hours?",
    context=user_context
)

print(result.final_output)
```

## 🔍 Core Capabilities

### 1. Service Information Queries
- Internet package details and pricing
- Business hours and contact information
- Coverage area verification
- Policy explanations (refund, cancellation, privacy)

### 2. Technical Support
- Connectivity troubleshooting
- Speed optimization guidance
- Equipment setup instructions
- Network configuration help

### 3. Complaint Resolution
- Intelligent complaint categorization
- Automatic priority assignment
- Specialized agent routing
- Real-time tracking in Google Sheets

### 4. Advanced Features
- Conversation memory across sessions
- Context-aware responses
- Multi-tool coordination
- Structured data output

## 📊 Data Models

### ServiceResponse
```python
class ServiceResponse(BaseModel):
    response_type: ResponseType  # information, complaint_resolution, technical_support
    content: str                 # Main response content
    actions_taken: List[str]     # Actions performed
    ticket_id: Optional[str]     # Complaint ticket ID if created
    next_steps: Optional[str]    # What happens next
    escalation_needed: bool      # Whether human escalation required
```

### ComplaintTicket
```python
class ComplaintTicket(BaseModel):
    ticket_id: str              # Unique identifier
    customer_name: str          # Customer name
    complaint_description: str  # Issue description
    priority: Priority          # Low, Medium, High
    assigned_agent: str         # Responsible agent
    category: Category          # Technical, Billing, Service, General
    status: Status             # Open, In Progress, Resolved, Closed
    created_at: datetime       # Creation timestamp
```

## 🛡️ Security & Privacy

- **Data Encryption**: AES-256 encryption for sensitive data
- **API Security**: Secure API key management with environment variables
- **Privacy Compliance**: GDPR-compliant data handling
- **Access Control**: Service account authentication for Google Sheets
- **Input Validation**: Comprehensive Pydantic model validation

## 📈 Monitoring & Analytics

- **Logfire Integration**: Real-time performance monitoring
- **Error Tracking**: Comprehensive error logging and alerting
- **Usage Analytics**: Conversation tracking and analysis
- **Performance Metrics**: Response time and accuracy monitoring

## 🔮 Future Enhancements

### Planned Features
- **Long-Term Memory**: MySQL-based conversation persistence
- **Advanced Analytics**: Customer satisfaction tracking
- **Multi-Language Support**: International customer support
- **Voice Integration**: Voice-to-text and text-to-voice capabilities
- **Mobile App**: Native mobile application
- **Advanced Security**: Multi-factor authentication and encryption

### Expansion Possibilities
- **CRM Integration**: Salesforce, HubSpot integration
- **Ticketing Systems**: JIRA, ServiceNow integration
- **Payment Processing**: Stripe, PayPal integration
- **SMS/WhatsApp**: Multi-channel communication
- **Video Support**: Screen sharing and video calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our GitHub Discussions for questions
- **Email**: sabitsiraji@gmail.com

## 🏆 Acknowledgments

- **OpenAI Agents SDK**: Core agent framework
- **LangChain**: RAG implementation components
- **Streamlit**: Web interface framework
- **Google Sheets API**: Real-time data logging
- **HuggingFace**: Embedding models for semantic search

---

**Built with ❤️ by the Customer Support AI Team**

*Transforming customer service with intelligent automation*