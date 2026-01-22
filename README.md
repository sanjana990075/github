# GitHub Issue Analyzer
A Streamlit application that analyzes GitHub issues using Google's Gemini AI. It provides a summary, classification, priority score, and suggested labels for any public GitHub issue.

## Features
- **Summary**: Concise summary of the issue.
- **Classification**: Categorizes issues (Bug, Feature Request, etc.).
- **Priority Scoring**: Assigns a priority score (1-5) with justification.
- **Label Suggestions**: Suggests relevant labels for the issue.

## Local Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file (see `.env.example` if available, or just set them):
   - `GOOGLE_API_KEY`: Your Google Gemini API Key.
   - `GITHUB_TOKEN` (Optional): For higher rate limits.
4. Run the application:
   ```bash
   streamlit run frontend.py
   ```

## Deployment to Streamlit Cloud
1. Push this code to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. Set "Main file path" to `frontend.py`.
5. In "Advanced Settings", add your secrets:
   ```toml
   GOOGLE_API_KEY = "your-key-here"
   GITHUB_TOKEN = "your-token-here"
   ```
6. Click **Deploy**!