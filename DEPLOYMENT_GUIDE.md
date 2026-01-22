# Deployment Guide for Streamlit Cloud

This project is now ready to be deployed to Streamlit Cloud.

## Prerequisites
- A GitHub account.
- A [Streamlit Cloud](https://share.streamlit.io/) account.
- Your Google Gemini API Key.

## Steps
1. **Push Changes**: Ensure all the files in this folder (including `requirements.txt` and the updated `frontend.py`) are pushed to your GitHub repository.
2. **New App**: Go to Streamlit Cloud and click "New app".
3. **Select Repository**: Choose the repository containing this code.
4. **Main File**: Set the "Main file path" to `frontend.py`.
5. **Advanced Settings (Secrets)**:
   - Click on "Advanced settings" -> "Secrets".
   - Add your API keys in TOML format:
     ```toml
     GOOGLE_API_KEY = "your_actual_api_key_here"
     GITHUB_TOKEN = "your_github_token_here" # Optional but recommended
     ```
6. **Deploy**: Click the "Deploy!" button.

## Troubleshooting
- If the app fails to start, check the logs on the right side of the Streamlit Cloud dashboard.
- Ensure `requirements.txt` is present in the root.
- Ensure the API keys are correct in the Secrets section, NOT in a `.env` file (Streamlit Cloud uses Secrets instead of `.env`).
