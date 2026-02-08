import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LLM Security Helper",
    layout="wide"
)

# Title and description
st.title("LLM Security Helper")
st.markdown("""
1. **Code Security Analysis** - Find vulnerabilities in code snippets
2. **GenAI App Spec Analysis** - Identify OWASP LLM Top 10 and ATLAS vulnerabilities
""")

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sidebar info
st.sidebar.header("Configuration")
st.sidebar.success("✅ Using Google Gemini API")

# Check if API key is set
if not GEMINI_API_KEY or GEMINI_API_KEY == "":
    st.error("⚠️ **API Key Not Configured!**")
    st.warning("""
    Please configure your Gemini API key:
    """)
    st.stop()

# Initialize Gemini client
try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try different model names in order of preference
    model = None
    model_name = None
    
    # List of models to try (in order of preference)
    models_to_try = [
        'gemini-pro',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-1.0-pro',
        'models/gemini-pro',
        'models/gemini-1.5-pro',
        'models/gemini-1.5-flash'
    ]
    
    # Try to find an available model
    for model_attempt in models_to_try:
        try:
            test_model = genai.GenerativeModel(model_attempt)
            # Try a simple test to see if it works
            test_response = test_model.generate_content("Hi")
            if test_response:
                model = test_model
                model_name = model_attempt
                break
        except Exception as e:
            continue
    
    # If no model worked, list available models and use the first one
    if model is None:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if available_models:
            # Use the first available model
            model_name = available_models[0]
            model = genai.GenerativeModel(model_name)
            st.sidebar.warning(f"Auto-selected model: {model_name}")
        else:
            raise Exception("No compatible models found")
    
    st.sidebar.success("✅ Gemini API connected successfully")
    st.sidebar.info(f"Using model: {model_name}")
    
except Exception as e:
    st.error(f"Error initializing Gemini API: {str(e)}")
    st.sidebar.error("❌ Failed to connect to Gemini API")
    
    # Show available models for debugging
    st.info("**Available models:**")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.write(f"- {m.name}")
    except:
        pass
    
    st.info("""
    Troubleshooting:
    1. Check your API key is correct in the .env file
    2. Make sure you have internet connection
    3. Verify your API key at: https://aistudio.google.com/app/apikey
    4. Try generating a new API key
    """)
    st.stop()

# Tabs for two different functionalities
tab1, tab2 = st.tabs(["Code Security Analysis", "GenAI Spec Vulnerability Analysis"])

# ==================== PART 1: Code Security Analysis ====================
with tab1:
    st.header("Security Fixes")
    st.markdown("Paste your code below to identify security vulnerabilities and get recommended fixes.")
    
    # Code input
    code_input = st.text_area(
        "Enter your code here:",
        height=300,
        placeholder="""Example:
def login(username, password):
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()
""",
        key="code_input"
    )
    
    # Language selector
    language = st.selectbox(
        "Select programming language:",
        ["Python", "JavaScript", "Java", "C#", "PHP", "Ruby", "Go", "SQL", "Other"]
    )
    
    if st.button("🔍 Analyze Code Security", key="analyze_code"):
        if not code_input.strip():
            st.warning("Please enter some code to analyze.")
        else:
            with st.spinner("Analyzing code for security vulnerabilities..."):
                try:
                    # Create the prompt for code analysis
                    prompt = f"""You are a security expert analyzing code for vulnerabilities. 

Analyze the following {language} code and identify ALL security vulnerabilities:

```{language.lower()}
{code_input}
```

Provide your analysis in the following format:

## Security Vulnerabilities Found

For each vulnerability:
### [Vulnerability Number]. [Vulnerability Name]
- **Severity**: [Critical/High/Medium/Low]
- **Description**: [Detailed explanation of the vulnerability]
- **Attack Vector**: [How an attacker could exploit this]
- **Impact**: [What could happen if exploited]

## Recommended Fixes

For each vulnerability, provide:
### Fix for [Vulnerability Name]
- **Solution**: [Detailed explanation of how to fix it]
- **Secure Code Example**:
```{language.lower()}
[Provide the corrected, secure version of the code]
```
- **Additional Best Practices**: [Any related security recommendations]

Focus ONLY on security issues, not general code quality or refactoring suggestions."""

                    # Call Gemini API
                    response = model.generate_content(prompt)
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("Please check your API key and internet connection.")

# ==================== PART 2: GenAI Spec Analysis ====================
with tab2:
    st.header("OWASP LLM & ATLAS Vulnerabilities")
    st.markdown("Describe your GenAI/Agentic application to identify potential security vulnerabilities.")
    
    # Spec input
    spec_input = st.text_area(
        "Describe your GenAI/Agentic application:",
        height=300,
        placeholder="""Example:
We are building a customer support chatbot that:
- Accesses our customer database to retrieve order information
- Allows users to update their shipping addresses
- Can process refund requests up to $500 without human approval
- Uses RAG to search internal knowledge base documents
- Integrates with our payment processing API
- Stores conversation history for quality monitoring
""",
        key="spec_input"
    )
    
    # App type selector
    app_type = st.selectbox(
        "Application Type:",
        ["Chatbot/Virtual Assistant", "Code Generation Tool", "Content Generator", 
         "Data Analysis Agent", "RAG-based System", "Multi-Agent System", "Other"]
    )
    
    if st.button("🔍 Analyze Vulnerabilities", key="analyze_spec"):
        if not spec_input.strip():
            st.warning("Please enter your application specifications.")
        else:
            with st.spinner("Analyzing for OWASP LLM Top 10 and ATLAS vulnerabilities..."):
                try:
                    # Create the prompt for spec analysis
                    prompt = f"""You are a GenAI security expert specializing in OWASP LLM Top 10 and ATLAS (Adversarial Threat Landscape for AI Systems) frameworks.

Analyze the following {app_type} specification for security vulnerabilities:

APPLICATION SPECIFICATION:
{spec_input}

Provide a comprehensive security analysis using BOTH frameworks:

## OWASP LLM Top 10 Vulnerabilities Analysis

For each applicable vulnerability from the OWASP LLM Top 10, provide:

### [OWASP-XX]: [Vulnerability Name]
- **Risk Level**: [Critical/High/Medium/Low]
- **Specific to this application**: [Explain exactly how this vulnerability applies to the described app]
- **Attack Scenario**: [Concrete example of how an attacker could exploit this in THIS specific application]
- **Mitigation Strategies**: [Specific, actionable steps to address this vulnerability]

The OWASP LLM Top 10 includes:
1. LLM01: Prompt Injection
2. LLM02: Insecure Output Handling
3. LLM03: Training Data Poisoning
4. LLM04: Model Denial of Service
5. LLM05: Supply Chain Vulnerabilities
6. LLM06: Sensitive Information Disclosure
7. LLM07: Insecure Plugin Design
8. LLM08: Excessive Agency
9. LLM09: Overreliance
10. LLM10: Model Theft

## ATLAS Framework Analysis

Analyze using the ATLAS (Adversarial Threat Landscape for AI Systems) perspective:

### Data Poisoning Threats
[Specific risks and mitigations]

### Evasion Attacks
[Specific risks and mitigations]

### Model Inversion/Extraction
[Specific risks and mitigations]

### Adversarial Examples
[Specific risks and mitigations]

## Priority Action Items

List the top 5 most critical vulnerabilities to address first, ranked by:
1. [Vulnerability name] - [Why it's critical for this app] - [Quick win mitigation]
2. ...

Be specific, actionable, and clear. Every recommendation should be directly applicable to the described application."""

                    # Call Gemini API
                    response = model.generate_content(prompt)
                    
                    # Display results
                    st.success("✅ Analysis Complete!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.info("Please check your API key and internet connection.")
