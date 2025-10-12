"""
Google Sheets Tool for Customer Support AI Agent
Handles logging complaint information to Google Sheets for tracking
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from agents import function_tool
import gspread
from google.oauth2.service_account import Credentials

def authenticate_google_sheets():
    """
    Authenticate with Google Sheets using service account credentials.
    
    Returns:
        gspread.Client: Authenticated Google Sheets client
    """
    try:
        # Get credentials path from environment
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'google_service_account.json')
        
        # Define the scope for Google Sheets API
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Load credentials and authenticate
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        
        return client
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets: {str(e)}")

@function_tool
def log_to_google_sheets(
    ticket_id: str,
    customer_name: str,
    complaint_description: str,
    priority: str,
    assigned_agent: str,
    category: str
) -> str:
    """
    Log complaint information to Google Sheets for tracking and management.
    
    Args:
        ticket_id: Unique ticket identifier
        customer_name: Name of the customer
        complaint_description: Description of the complaint
        priority: Priority level (Low, Medium, High)
        assigned_agent: Assigned support agent
        category: Complaint category (Technical, Billing, Service, General)
    
    Returns:
        JSON string confirming successful logging
    """
    
    # Mock implementation - in real usage, this would connect to Google Sheets API
    
    # Prepare data for Google Sheets
    sheet_data = {
        "timestamp": datetime.now().isoformat(),
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "complaint_description": complaint_description,
        "priority": priority,
        "assigned_agent": assigned_agent,
        "category": category,
        "status": "Open",
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "created_time": datetime.now().strftime("%H:%M:%S")
    }
    
    # Mock successful logging
    # In real implementation, you would:
    # 1. Authenticate with Google Sheets API
    # 2. Open the designated spreadsheet
    # 3. Append the new row with complaint data
    # 4. Return confirmation of successful logging
    
    response = {
        "logging_successful": True,
        "sheet_name": "Customer_Complaints_Log",
        "row_added": True,
        "data_logged": sheet_data,
        "google_sheets_url": "https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
        "message": f"Complaint {ticket_id} successfully logged to Google Sheets",
        "next_steps": [
            "Complaint data available for manager review",
            "Automatic notifications sent to assigned agent",
            "Tracking dashboard updated with new case",
            "Performance metrics updated"
        ]
    }
    
    return json.dumps(response, indent=2)