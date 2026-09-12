"""
tools/knowledge_tools.py
Built-in troubleshooting knowledge base for hardware, technical, access, and HR queries.
Enables agents to retrieve standard operating procedures (SOP) before escalating.
"""

from typing import Dict, Any, List
import re

try:
    from langchain_core.tools import tool
except ImportError:
    def tool(func):
        return func


# Standard Operating Procedures & Troubleshooting Knowledge Base
TROUBLESHOOTING_KB = {
    "hardware": [
        {
            "keywords": ["laptop", "not turning on", "won't boot", "dead", "power", "turn on", "black screen"],
            "title": "Laptop Power & Boot Diagnostics",
            "steps": [
                "1. Connect the original OEM charger and check if the charging LED indicator lights up.",
                "2. If no light appears, test with another known-working power outlet or compatible adapter.",
                "3. Perform a hard reset: Unplug the charger, hold the power button down firmly for 30 seconds, then reconnect and try turning it on.",
                "4. If connected to a docking station, disconnect all peripherals and attempt to power on directly.",
                "5. If the laptop still does not respond, a hardware inspection or battery replacement ticket is required."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        },
        {
            "keywords": ["printer", "printing", "paper jam", "offline", "toner", "cartridge", "print"],
            "title": "Office Printer Troubleshooting",
            "steps": [
                "1. Check if the printer display screen shows any error codes or 'Offline' status.",
                "2. Verify paper trays are properly seated and clear any visible jammed paper from Tray 1 and Tray 2.",
                "3. Ensure the printer is connected to the office LAN or company Wi-Fi network (SSID: IBM-Corp).",
                "4. Restart the printer using the physical power switch, wait 60 seconds, and turn back on.",
                "5. On your computer, open Printers & Scanners, remove the device, and click 'Add device' to re-sync drivers.",
                "6. If the printer remains in error state or requires toner replacement, raise a support ticket."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        },
        {
            "keywords": ["monitor", "screen", "display", "flicker", "blank", "hdmi", "cable"],
            "title": "External Monitor & Display Diagnostics",
            "steps": [
                "1. Confirm the monitor power cable is firmly seated and the power LED is illuminated.",
                "2. Check the video cable (HDMI / DisplayPort / USB-C) connection on both monitor and laptop.",
                "3. Press Windows Key + P on your laptop and ensure 'Duplicate' or 'Extend' display mode is selected.",
                "4. Use the monitor's physical buttons to cycle the input source to match your cable (e.g. HDMI 1).",
                "5. If the panel has physical cracks, severe lines, or does not power on, request hardware replacement."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": True
        },
        {
            "keywords": ["keyboard", "mouse", "headset", "bluetooth", "peripheral", "keys"],
            "title": "Peripheral Devices (Keyboard / Mouse / Headset)",
            "steps": [
                "1. If wireless, replace or recharge the batteries and verify the power switch is in the 'ON' position.",
                "2. For USB dongle devices, remove and plug the USB receiver into a different USB port.",
                "3. For Bluetooth devices, open Windows Bluetooth settings, remove the device, and re-pair.",
                "4. Test the peripheral on another workstation if available to isolate hardware failure.",
                "5. If a key is mechanically stuck or damaged, request peripheral replacement."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        },
        {
            "keywords": ["battery", "charger", "draining", "adapter", "charging", "replace laptop", "new laptop"],
            "title": "Battery & Charger Replacement Diagnostics",
            "steps": [
                "1. Check battery health report in Windows (cmd: `powercfg /batteryreport`).",
                "2. Inspect the charger cable for any fraying, bending, or physical damage.",
                "3. Ensure the laptop is not running heavy background tasks causing thermal throttling.",
                "4. For equipment replacement (laptop, high-value components), manager approval is required."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": True
        }
    ],
    "technical": [
        {
            "keywords": ["crash", "crashes", "payroll", "application", "software", "error code", "fails", "freeze"],
            "title": "Application Crash & Error Resolution",
            "steps": [
                "1. Open Windows Task Manager (Ctrl + Shift + Esc) and terminate any lingering background instances of the application.",
                "2. Clear application temporary cache files located in %LOCALAPPDATA% or %TEMP%.",
                "3. Verify that your system has the latest mandatory security patches installed via Software Center.",
                "4. Restart your workstation to release locked memory handles.",
                "5. If the error code persists (e.g., 0x8004), provide the exact error message and raise a technical support ticket."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        },
        {
            "keywords": ["wi-fi", "wifi", "network", "internet", "connecting", "disconnect", "lan", "dns"],
            "title": "Network & Wi-Fi Connectivity Guide",
            "steps": [
                "1. Verify that Airplane Mode is turned OFF and Wi-Fi adapter is toggled ON.",
                "2. Disconnect from the current Wi-Fi network and select 'IBM-Corp-Secure' or 'IBM-Guest'.",
                "3. In Windows Command Prompt, run: `ipconfig /flushdns` followed by `ipconfig /renew`.",
                "4. If using Cisco AnyConnect / GlobalProtect VPN, disconnect and reconnect to re-establish tunnel.",
                "5. If other colleagues also experience connectivity drops in your wing, alert the Network Operations team."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        },
        {
            "keywords": ["install", "installation", "admin rights", "software center", "permission to install"],
            "title": "Software Installation & Updates",
            "steps": [
                "1. Open the company 'Software Center' or 'Self-Service Portal' from your Start Menu.",
                "2. Search for approved software (e.g. VS Code, Slack, Zoom, Docker) which can be installed without admin elevation.",
                "3. If the software is not listed in the catalog, submit a Software License & Security Approval request.",
                "4. Do not download executable installers from unverified public web sources."
            ],
            "requires_ticket_if_unresolved": False,
            "is_expensive": False
        },
        {
            "keywords": ["blue screen", "bsod", "os error", "operating system", "windows update", "corrupt"],
            "title": "Operating System & BSOD Diagnostics",
            "steps": [
                "1. Record the stop code displayed on screen (e.g., CRITICAL_PROCESS_DIED, DPC_WATCHDOG_VIOLATION).",
                "2. Allow Windows to complete memory dump generation (reaches 100%) and reboot.",
                "3. Disconnect any newly attached external hardware docks or USB drives.",
                "4. If the machine loops into Automatic Repair, technical desktop support intervention is mandatory."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False
        }
    ],
    "access": [
        {
            "keywords": ["password", "forgot password", "reset password", "change password", "expired"],
            "title": "Password Reset Protocol",
            "steps": [
                "1. Navigate to the self-service Identity Management Portal at https://identity.ibm-internal.corp/reset.",
                "2. Enter your Employee ID and complete the Multi-Factor Authentication (MFA) push on Duo / Microsoft Authenticator.",
                "3. Ensure the new password meets security requirements: minimum 14 characters, uppercase, lowercase, numeric, and symbol.",
                "4. NOTE: For security policies, automated agents cannot directly view, generate, or send passwords over chat.",
                "5. If MFA is unavailable or your account is hard-locked, an authenticated IT Administrator must approve and process the reset."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False,
            "requires_human_approval": True
        },
        {
            "keywords": ["access", "permission", "portal", "attendance system", "payroll portal", "jira", "github"],
            "title": "Application Access & Permission Requests",
            "steps": [
                "1. Identify the specific application (e.g. Workday Attendance, SAP Payroll, JIRA Cloud).",
                "2. Access permissions require managerial approval and departmental role verification.",
                "3. Submit an Access Request ticket specifying: Employee ID, Target System, and Business Justification.",
                "4. Once your reporting manager approves in the workflow, privileges are provisioned within 4 business hours."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False,
            "requires_human_approval": True
        },
        {
            "keywords": ["lock", "locked", "account locked", "too many attempts", "unlock"],
            "title": "Account Lockout Recovery",
            "steps": [
                "1. Company security policies automatically lock accounts for 15 minutes after 5 consecutive failed attempts.",
                "2. Wait 15 minutes without typing credentials to allow automatic security counter reset.",
                "3. Verify caps lock is disabled and mobile email sync has the updated password stored.",
                "4. If emergency access is needed, an IT security specialist must verify your identity to unlock."
            ],
            "requires_ticket_if_unresolved": True,
            "is_expensive": False,
            "requires_human_approval": True
        }
    ],
    "general": [
        {
            "keywords": ["leave", "apply for leave", "sick leave", "casual leave", "vacation", "pto"],
            "title": "Leave Application Guidelines",
            "steps": [
                "1. Log in to the HR Self-Service Portal at https://hr.internal.corp/leave.",
                "2. Navigate to 'Time Off' > 'Request Leave'.",
                "3. Select the leave type (Casual, Sick, Privilege, or Bereavement) and specify start/end dates.",
                "4. Attach medical certificates if sick leave exceeds 3 consecutive days.",
                "5. Click 'Submit' to route the notification to your reporting manager for approval."
            ],
            "requires_ticket_if_unresolved": False,
            "is_expensive": False
        },
        {
            "keywords": ["attendance", "swipe", "working hours", "timing", "shift", "regularization"],
            "title": "Working Hours & Attendance Regularization",
            "steps": [
                "1. Standard core working hours are 09:00 AM to 06:00 PM (Monday through Friday).",
                "2. Employees must record at least 8.5 active hours per day including lunch breaks.",
                "3. If you forgot your swipe card or worked off-site, navigate to HR Portal > Attendance > 'Regularize'.",
                "4. Attendance regularizations must be submitted before the 25th of each calendar month for payroll sync."
            ],
            "requires_ticket_if_unresolved": False,
            "is_expensive": False
        },
        {
            "keywords": ["contact", "hr contact", "policy", "handbook", "benefits", "insurance"],
            "title": "General HR Policies & Support Channels",
            "steps": [
                "1. Employee handbook and benefits details are accessible at https://hr.internal.corp/handbook.",
                "2. For medical insurance coverage or claims queries, contact insurance-desk@company.com.",
                "3. For payroll or tax-deduction queries, email payroll-helpdesk@company.com.",
                "4. General HR Helpdesk operational hours: 09:00 AM - 05:00 PM IST (Ext: 4455)."
            ],
            "requires_ticket_if_unresolved": False,
            "is_expensive": False
        }
    ]
}


def search_troubleshooting(query: str, category: str = "general") -> Dict[str, Any]:
    """
    Searches the troubleshooting knowledge base for procedures matching the query and category.

    Args:
        query: The user's question or problem description.
        category: The category ('hardware', 'technical', 'access', 'general').

    Returns:
        A dictionary containing matched SOP title, diagnostic steps, and recommendation on whether a ticket is needed.
    """
    query_lower = query.lower()
    cat_lower = category.lower().strip()

    # Determine which categories to search
    cats_to_search = [cat_lower] if cat_lower in TROUBLESHOOTING_KB else ["hardware", "technical", "access", "general"]

    best_match = None
    highest_score = 0

    for cat in cats_to_search:
        for article in TROUBLESHOOTING_KB.get(cat, []):
            score = sum(1 for kw in article["keywords"] if kw in query_lower)
            if score > highest_score:
                highest_score = score
                best_match = article

    if best_match and highest_score > 0:
        return {
            "found": True,
            "category": cat_lower,
            "title": best_match["title"],
            "steps": best_match["steps"],
            "requires_ticket_if_unresolved": best_match.get("requires_ticket_if_unresolved", False),
            "is_expensive": best_match.get("is_expensive", False),
            "requires_human_approval": best_match.get("requires_human_approval", False)
        }

    # Fallback standard response if no direct SOP matched
    return {
        "found": False,
        "category": cat_lower,
        "title": f"General {cat_lower.capitalize()} Support Guidance",
        "steps": [
            "1. Gather detailed information regarding the issue, including timestamps and error messages.",
            "2. Ensure any relevant systems or hardware have been safely restarted.",
            "3. If the problem impedes daily work, request a support ticket with high priority."
        ],
        "requires_ticket_if_unresolved": True,
        "is_expensive": False,
        "requires_human_approval": False
    }


# Export LangChain Tool instance
search_troubleshooting_tool = tool(search_troubleshooting)
