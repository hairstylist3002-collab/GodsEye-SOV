import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import traceback
import google.generativeai as genai

# Load environment variables
load_dotenv()

def summarize_error(error, error_context="", api_key=None):
    """
    Generate AI-powered error summary using Google Gemini 1.5 Pro.
    Falls back to simple text if AI generation fails.
    
    Args:
        error: The exception object
        error_context: Additional context about where the error occurred
        api_key: Optional Google API key (uses GEMINI_API_KEY env var if not provided)
    
    Returns:
        Dictionary with 'summary' and 'is_ai_generated' keys
    """
    error_type = type(error).__name__
    error_message = str(error)
    stack_trace = traceback.format_exc()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Try AI-powered summarization
    try:
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-pro')
            
            prompt = f"""
            Generate a brief, professional incident report for a development team.
            
            **Server Name:** GodsEye SOV Server
            **Error Type:** {error_type}
            **Timestamp:** {timestamp}
            **Error Context:** {error_context if error_context else 'No additional context'}
            **Error Message:** {error_message}
            
            **Stack Trace:**
            {stack_trace}
            
            Write a concise 2-3 sentence summary that:
            1. Clearly states what failed
            2. Indicates severity/impact
            3. Suggests potential next steps (if obvious)
            
            Be professional, urgent, and technical.
            """
            
            response = model.generate_content(prompt)
            ai_summary = response.text.strip()
            
            return {
                "summary": ai_summary,
                "is_ai_generated": True,
                "timestamp": timestamp,
                "error_type": error_type
            }
    except Exception as e:
        print(f"⚠️ AI summarization failed: {e}. Using fallback.")
    
    # Fallback: Simple text summary
    fallback_summary = f"""
Server: GodsEye SOV Server
Error Type: {error_type}
Error Message: {error_message}
Context: {error_context if error_context else 'No additional context'}
Time: {timestamp}
    """
    
    return {
        "summary": fallback_summary,
        "is_ai_generated": False,
        "timestamp": timestamp,
        "error_type": error_type
    }

def send_error_email(error, error_context="", api_key=None):
    """
    Send error notification email with AI-powered error analysis.
    
    Args:
        error: The exception object
        error_context: Additional context about where the error occurred
        api_key: Optional Google API key for AI summarization
    """
    # Get SMTP configuration from environment variables
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    to_email = os.getenv('ERROR_NOTIFICATION_EMAIL', smtp_user)
    
    if not smtp_user or not smtp_pass:
        print("ERROR: SMTP credentials not configured in environment variables")
        return False
    
    # Get AI-powered error summary
    error_data = summarize_error(error, error_context, api_key)
    error_summary = error_data['summary']
    is_ai = error_data['is_ai_generated']
    stack_trace = traceback.format_exc()
    ai_badge = "✨ AI-Analyzed" if is_ai else "⚙️ Fallback"
    
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'🚨 GodsEye SOV Server Error Alert: {error_data["error_type"]}'
    msg['From'] = from_email
    msg['To'] = to_email
    
    # HTML email body
    html_body = f"""
    <div style="background:#f4f6fb;padding:40px 0;min-height:100vh;font-family:Arial,sans-serif;">
        <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);padding:36px 32px 28px 32px;">
            <div style="text-align:center;margin-bottom:28px;">
                <div style="font-size:24px;font-weight:700;color:#dc3545;letter-spacing:1px;margin-bottom:8px;">⚠️ GodsEye SOV Server</div>
                <div style="font-size:18px;font-weight:600;color:#222;margin-bottom:8px;">Error Incident Report</div>
                <div style="font-size:12px;color:#aaa;">{ai_badge} • {error_data['timestamp']}</div>
            </div>
            
            <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:16px;margin-bottom:24px;border-radius:4px;">
                <div style="font-size:16px;color:#856404;font-weight:600;margin-bottom:8px;">Incident Summary</div>
                <div style="font-size:14px;color:#856404;white-space:pre-line;line-height:1.6;">{error_summary}</div>
            </div>
            
            {f'<div style="background:#e7f3ff;border-left:4px solid #0066cc;padding:16px;margin-bottom:24px;border-radius:4px;"><div style="font-size:14px;color:#004085;"><strong>Context:</strong> {error_context}</div></div>' if error_context else ''}
            
            <div style="background:#f8f9fa;border-left:4px solid #6c757d;padding:16px;margin-bottom:24px;border-radius:4px;">
                <div style="font-size:14px;color:#495057;font-weight:600;margin-bottom:8px;">Stack Trace</div>
                <div style="font-size:12px;color:#495057;font-family:monospace;white-space:pre-wrap;overflow-x:auto;">{stack_trace}</div>
            </div>
            
            <div style="text-align:center;font-size:13px;color:#aaa;margin-top:24px;">
                — GodsEye AI Error Monitoring System
            </div>
        </div>
    </div>
    """
    
    # Attach HTML body
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f"✅ Error notification sent to {to_email}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send error notification: {e}")
        return False


def main():
    """
    Test function with a demo error
    """
    print("=" * 60)
    print("GodsEye SOV Server - Error Notification System - Testing")
    print("=" * 60)
    
    # Demo error for testing
    try:
        print("\n🧪 Simulating a database connection error...")
        
        # Simulate an error
        def connect_to_database():
            raise ConnectionError("Unable to connect to database at localhost:5432")
        
        connect_to_database()
        
    except Exception as e:
        print(f"\n❌ Error caught: {e}")
        print("\n📧 Sending error notification email...")
        
        # Send error email with context
        success = send_error_email(
            error=e,
            error_context="Failed to connect to PostgreSQL database during startup"
        )
        
        if success:
            print("\n✅ Test completed successfully! Check your email.")
        else:
            print("\n⚠️ Test completed but email sending failed. Please check your SMTP configuration.")
    
    print("\n" + "=" * 60)
    print("Make sure to set up your .env file with:")
    print("SMTP_HOST=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USER=your-email@gmail.com")
    print("SMTP_PASS=your-app-password")
    print("ERROR_NOTIFICATION_EMAIL=admin@example.com")
    print("GEMINI_API_KEY=your-gemini-api-key")
    print("=" * 60)


if __name__ == "__main__":
    main()