python -m venv .venv
# Mac / Linux
source .venv/bin/activate

# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install google-adk 
pip install streamlit

# Set the environment variable for Google Application Credentials
export GOOGLE_APPLICATION_CREDENTIALS="application_default_credentials.json"
$env:GOOGLE_APPLICATION_CREDENTIALS="application_default_credentials.json"