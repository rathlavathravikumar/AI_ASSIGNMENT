#!/usr/bin/env python3
"""
Run the Email Triage UI application.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit UI"""
    ui_path = os.path.join(os.path.dirname(__file__), 'ui.py')

    # Run streamlit
    cmd = [sys.executable, '-m', 'streamlit', 'run', ui_path, '--server.headless', 'true', '--server.port', '8501']
    subprocess.run(cmd)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">/home/rgukt-basar/email-triage-openenv/env/run_ui.py