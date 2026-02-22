#!/usr/bin/env python3
import argparse
import datetime
import os

def log_audit(message: str, score: int = None, issues: str = None, log_file: str = "findings.md"):
    """Silently appends CTO mentoring notes to findings.md."""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if we are running in the context of the main project source 
    # to append to the correct findings.md
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    findings_path = os.path.join(project_root, log_file)
    
    # Create file if it doesn't exist
    if not os.path.exists(findings_path):
        with open(findings_path, "w") as f:
            f.write("# CTO Mentor Audit Findings\n\n")

    with open(findings_path, "a") as f:
        f.write(f"## Audit Log: {timestamp}\n")
        f.write(f"- **Action:** {message}\n")
        
        if score is not None:
            f.write(f"- **Technical Score:** {score}/100\n")
            
        if issues:
            f.write(f"- **Flagged Issues:**\n{issues}\n")
            
        f.write("\n---\n\n")
        
    print(f"✅ CTO Audit log successfully written to {log_file}")

def main():
    parser = argparse.ArgumentParser(description="CTO Mentor Audit Logger")
    parser.add_argument("--action", required=True, help="Description of the audit action or milestone.")
    parser.add_argument("--score", type=int, help="Optional numerical score (0-100) based on the rubric.")
    parser.add_argument("--issues", help="Optional bulleted string of flagged physical or architectural omissions.")
    parser.add_argument("--file", default="findings.md", help="Target markdown file to log to (default: findings.md).")
    
    args = parser.parse_args()
    
    try:
        log_audit(args.action, args.score, args.issues, args.file)
    except Exception as e:
        print(f"❌ Failed to write audit log: {str(e)}")

if __name__ == "__main__":
    main()
