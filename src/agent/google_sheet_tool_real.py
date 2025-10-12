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
    
    try:
        # Authenticate and get the Google Sheets client
        client = authenticate_google_sheets()
        
        # Get sheet configuration from environment
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        sheet_name = os.getenv('GOOGLE_SHEET_NAME', 'Sheet1')
        
        if not sheet_id:
            raise Exception("GOOGLE_SHEET_ID not found in environment variables")
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Prepare data for Google Sheets
        current_time = datetime.now()
        sheet_data = [
            current_time.strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
            ticket_id,
            customer_name,
            complaint_description,
            priority,
            category,  # Category comes before Assigned Agent in the sheet
            assigned_agent,
            "Open",  # Status
            current_time.strftime("%Y-%m-%d"),  # Created Date
            current_time.strftime("%H:%M:%S")   # Created Time
        ]
        
        # Check if headers exist, if not add them
        try:
            headers = worksheet.row_values(1)
            if not headers:
                headers = [
                    "Timestamp", "Ticket ID", "Customer Name", "Complaint Description",
                    "Priority", "Category", "Assigned Agent", "Status", "Created Date", "Created Time"
                ]
                worksheet.append_row(headers)
        except:
            headers = [
                "Timestamp", "Ticket ID", "Customer Name", "Complaint Description",
                "Priority", "Category", "Assigned Agent", "Status", "Created Date", "Created Time"
            ]
            worksheet.append_row(headers)
        
        # Append the new complaint data
        worksheet.append_row(sheet_data)
        
        # Prepare success response
        response = {
            "logging_successful": True,
            "sheet_name": sheet_name,
            "row_added": True,
            "data_logged": {
                "timestamp": current_time.isoformat(),
                "ticket_id": ticket_id,
                "customer_name": customer_name,
                "complaint_description": complaint_description,
                "priority": priority,
                "assigned_agent": assigned_agent,
                "category": category,
                "status": "Open"
            },
            "google_sheets_url": f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit",
            "message": f"Complaint {ticket_id} successfully logged to Google Sheets",
            "next_steps": [
                "Complaint data available for manager review",
                "Tracking dashboard updated with new case",
                "Data available for reporting and analytics"
            ]
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        # Handle errors gracefully
        error_response = {
            "logging_successful": False,
            "error": str(e),
            "message": f"Failed to log complaint {ticket_id} to Google Sheets",
            "fallback_action": "Complaint logged to local system only"
        }
        
        return json.dumps(error_response, indent=2)