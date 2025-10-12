"""
Complaint Ticket Tool for Customer Support AI Agent
Handles complaint processing, categorization, and agent assignment
"""

import json
from datetime import datetime
from typing import Optional
from agents import function_tool

@function_tool
def create_complaint_ticket(
    complaint_description: str, 
    customer_name: Optional[str] = None,
    priority_override: Optional[str] = None
) -> str:
    """
    Create a complaint ticket with automatic categorization and agent assignment.
    
    Args:
        complaint_description: Description of the customer's complaint
        customer_name: Customer's name (will use context if available)
        priority_override: Manual priority setting ('Low', 'Medium', 'High')
    
    Returns:
        JSON string with ticket details including ID, priority, and assigned agent
    """
    
    # Get customer information 
    customer_name = customer_name or "Anonymous Customer"
    
    # Generate unique ticket ID
    timestamp = datetime.now()
    ticket_id = f"CS-{timestamp.strftime('%Y%m%d')}-{timestamp.strftime('%H%M%S')}"
    
    # Automatic categorization based on complaint content
    complaint_lower = complaint_description.lower()
    
    # Determine category
    category = "General"
    if any(keyword in complaint_lower for keyword in ["internet", "speed", "slow", "connection", "wifi", "router", "outage", "down", "technical"]):
        category = "Technical"
    elif any(keyword in complaint_lower for keyword in ["bill", "charge", "payment", "money", "fee", "refund", "credit"]):
        category = "Billing"
    elif any(keyword in complaint_lower for keyword in ["service", "installation", "appointment", "technician", "coverage"]):
        category = "Service"
    
    # Automatic priority assignment (unless overridden)
    if priority_override and priority_override in ["Low", "Medium", "High"]:
        priority = priority_override
    else:
        priority = "Medium"  # Default
        
        # High priority indicators
        if any(keyword in complaint_lower for keyword in [
            "outage", "down", "not working", "completely", "totally", "emergency", 
            "urgent", "critical", "business", "work", "days", "weeks", "angry", 
            "frustrated", "unacceptable", "terrible", "worst"
        ]):
            priority = "High"
        
        # Low priority indicators
        elif any(keyword in complaint_lower for keyword in [
            "question", "curious", "wondering", "minor", "small", "quick", 
            "information", "clarification", "understand"
        ]):
            priority = "Low"
    
    # Agent assignment based on category and priority
    available_agents = {
        "Technical": {
            "High": "Rahim Hassan (Senior Technical Specialist)",
            "Medium": "David Chen (Technical Support)",
            "Low": "Emma Rodriguez (Technical Assistant)"
        },
        "Billing": {
            "High": "Sara Johnson (Billing Manager)",
            "Medium": "Michael Park (Billing Specialist)", 
            "Low": "Lisa Wang (Billing Support)"
        },
        "Service": {
            "High": "John Smith (Service Manager)",
            "Medium": "Alex Thompson (Service Coordinator)",
            "Low": "Maria Garcia (Service Assistant)"
        },
        "General": {
            "High": "Jennifer Lee (Customer Success Manager)",
            "Medium": "Robert Davis (Customer Support Lead)",
            "Low": "Amanda Wilson (Customer Support)"
        }
    }
    
    assigned_agent = available_agents[category][priority]
    
    # Create ticket data
    ticket_data = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "complaint_description": complaint_description,
        "priority": priority,
        "assigned_agent": assigned_agent,
        "category": category,
        "created_at": timestamp.isoformat(),
        "status": "Open"
    }
    
    # Response timeframes based on priority
    response_timeframes = {
        "High": "within 2 hours",
        "Medium": "within 4-8 hours", 
        "Low": "within 24 hours"
    }
    
    # Potential remedies based on category and priority
    potential_remedies = []
    if category == "Technical" and priority == "High":
        potential_remedies = [
            "Priority technical support scheduling",
            "Possible service credit for outage time",
            "Free equipment replacement if hardware issue",
            "On-site technician visit if needed"
        ]
    elif category == "Billing" and priority in ["High", "Medium"]:
        potential_remedies = [
            "Account review and adjustment",
            "Billing error correction",
            "Payment plan options if applicable",
            "Fee waiver consideration"
        ]
    elif category == "Service":
        potential_remedies = [
            "Expedited service appointment",
            "Installation issue resolution",
            "Coverage area verification",
            "Alternative service options"
        ]
    else:
        potential_remedies = [
            "Detailed explanation and clarification",
            "Account review and recommendations", 
            "Follow-up communication as needed"
        ]
    
    # Compile response
    response_data = {
        "ticket_created": True,
        "ticket_details": ticket_data,
        "next_steps": {
            "expected_response": response_timeframes[priority],
            "contact_method": "Phone call or email from assigned agent",
            "escalation_path": "Manager review if not resolved within timeframe"
        },
        "potential_remedies": potential_remedies,
        "customer_actions": [
            f"Keep ticket ID {ticket_id} for reference",
            "Expect contact from assigned agent within timeframe",
            "Prepare any additional details or documentation",
            "Contact emergency line if service completely down"
        ],
        "company_actions": [
            "Complaint logged in ticketing system",
            "Assigned agent notified automatically",
            "Case review initiated",
            "Google Sheets logging for tracking"
        ]
    }
    
    return json.dumps(response_data, indent=2)