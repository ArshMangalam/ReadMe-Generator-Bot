import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

# Initialize Gemini client
client = genai.Client()

def generate_readme_from_repo(repo_info):
    """
    Generate a professional README.md using Google Gemini AI
    """
    
    # Enhanced prompt for better README generation
    prompt = f"""
You are an expert technical writer and software documentation specialist. Generate a comprehensive, professional README.md file for the following GitHub repository:

**Repository Details:**
- Name: {repo_info['name']}
- Owner: {repo_info['owner']}
- Description: {repo_info['description'] or 'No description provided'}
- Primary Language: {repo_info['language'] or 'Not specified'}
- Stars: {repo_info['stars']}
- Topics/Tags: {', '.join(repo_info.get('topics', [])) or 'None'}

**Requirements:**
Create a professional README with the following structure:

1. **Project Title** - Eye-catching with emojis
2. **Description** - Compelling project overview
3. **Features** - Key highlights and capabilities
4. **Technologies Used** - Tech stack with badges
5. **Installation** - Step-by-step setup instructions
6. **Usage** - Code examples and demonstrations
7. **API Documentation** - If applicable
8. **Contributing** - Guidelines for contributors
9. **License** - License information
10. **Contact** - Author/maintainer info

**Style Guidelines:**
- Use modern markdown formatting
- Include relevant emojis for visual appeal
- Add GitHub badges for technologies
- Provide clear, actionable instructions
- Include code examples where appropriate
- Make it scannable with proper headings
- Add a table of contents for longer READMEs

**Output Format:**
Provide only the markdown content, no additional text or explanations.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            }
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"🚨 [ERROR] Gemini API Request Failed: {e}")
        return None