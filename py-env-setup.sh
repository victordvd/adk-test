python -m venv .venv

source .venv/bin/activate # Mac / Linux
.venv\Scripts\Activate.ps1 # Windows PowerShell

pip install google-adk 
pip install streamlit

# Set the environment variable for Google Application Credentials
export GOOGLE_APPLICATION_CREDENTIALS="application_default_credentials.json" # Mac / Linux
$env:GOOGLE_APPLICATION_CREDENTIALS="application_default_credentials.json" # Windows PowerShell: