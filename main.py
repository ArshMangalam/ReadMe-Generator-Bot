import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from dotenv import load_dotenv
from typing import Optional
from github_utils import extract_repo_info
from gemini_utils import generate_readme_from_repo
import asyncio
from flask import Flask
import threading

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("🚨 BOT_TOKEN environment variable is not set")

TOKEN: str = BOT_TOKEN

# Define states for conversation
WAITING_FOR_LINK = 1

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    # Characters that need to be escaped in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    # Escape each character by adding a backslash before it
    escaped_text = ""
    for char in text:
        if char in escape_chars:
            escaped_text += f"\\{char}"
        else:
            escaped_text += char
    
    return escaped_text

def safe_markdown_format(text: str) -> str:
    """Safely format text for Telegram, removing problematic characters"""
    # Remove or replace problematic markdown characters
    text = text.replace('*', '•')  # Replace asterisks with bullet points
    text = text.replace('_', '-')  # Replace underscores with dashes
    text = text.replace('`', "'")  # Replace backticks with single quotes
    text = text.replace('[', '(')  # Replace square brackets
    text = text.replace(']', ')')
    text = text.replace('#', 'No.')  # Replace hash symbols
    
    return text

# Enhanced start handler with professional styling
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return ConversationHandler.END
    
    welcome_message = """
🚀 **Welcome to ReadMe Generator Bot** 🚀

✨ *Your AI-Powered README Creation Assistant* ✨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **What I Do:**
• Generate professional README files instantly
• Analyze your GitHub repositories 
• Create comprehensive documentation
• Powered by Google's Gemini AI

📝 **How It Works:**
1. Share your GitHub repository link
2. I'll analyze your project structure
3. Generate a professional README
4. Download your custom README file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 **Ready to get started?**
Send me your GitHub repository link now!

*Example: https://github.com/username/repository*
"""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    return WAITING_FOR_LINK

# Enhanced GitHub link handler with better UX
async def handle_github_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message:
        return WAITING_FOR_LINK
    
    if not update.message.text:
        await update.message.reply_text("❌ Please send a valid GitHub repository link.")
        return WAITING_FOR_LINK
    
    repo_url = update.message.text.strip()
    
    # Validate GitHub URL format
    if not ("github.com" in repo_url and "/" in repo_url):
        await update.message.reply_text(
            "⚠️ **Invalid GitHub URL**\n\n"
            "Please provide a valid GitHub repository link.\n"
            "📝 *Format: https://github.com/username/repository*",
            parse_mode="Markdown"
        )
        return WAITING_FOR_LINK
    
    # Show processing message with animation
    processing_msg = await update.message.reply_text("🔍 **Analyzing repository...**", parse_mode="Markdown")
    
    # Simulate processing steps for better UX
    await asyncio.sleep(1)
    await processing_msg.edit_text("📊 **Fetching repository data...**", parse_mode="Markdown")
    
    repo_data = extract_repo_info(repo_url)
    
    if not repo_data:
        await processing_msg.edit_text(
            "❌ **Repository Analysis Failed**\n\n"
            "🔧 **Possible Issues:**\n"
            "• Repository might be private\n"
            "• Invalid repository URL\n"
            "• Network connectivity issues\n\n"
            "Please verify the link and try again.",
            parse_mode="Markdown"
        )
        return WAITING_FOR_LINK
    
    # Store repository info
    if context.user_data is None:
        context.user_data = {}
    context.user_data["repo_info"] = repo_data
    
    # Show repository summary with enhanced formatting
    repo_summary = f"""
📦 **Repository Analysis Complete!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ **Name:** `{repo_data['name']}`
👤 **Owner:** `{repo_data['owner']}`
📝 **Description:** {repo_data['description'] or 'No description available'}
🌟 **Stars:** {repo_data['stars']:,}
💻 **Language:** {repo_data['language'] or 'Not specified'}
🏷️ **Topics:** {', '.join(repo_data.get('topics', [])) or 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    await processing_msg.edit_text(repo_summary, parse_mode="Markdown")
    
    # Start README generation
    await asyncio.sleep(2)
    generation_msg = await update.message.reply_text("🤖 **Generating README with Gemini AI...**", parse_mode="Markdown")
    
    await asyncio.sleep(1)
    await generation_msg.edit_text("⚡ **Processing repository structure...**", parse_mode="Markdown")
    
    await asyncio.sleep(1)
    await generation_msg.edit_text("📝 **Crafting professional documentation...**", parse_mode="Markdown")
    
    readme_content = generate_readme_from_repo(repo_data)
    
    if not readme_content:
        await generation_msg.edit_text(
            "❌ **README Generation Failed**\n\n"
            "🔧 **Error Details:**\n"
            "• AI service temporarily unavailable\n"
            "• Please try again in a few moments\n\n"
            "If the issue persists, contact support.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    context.user_data["readme"] = readme_content
    
    # Show preview with enhanced formatting - FIXED VERSION
    preview_lines = readme_content.splitlines()[:5]  # Reduced to 5 lines to avoid issues
    preview = "\n".join(preview_lines)
    
    # Safely format the preview to avoid markdown parsing issues
    safe_preview = safe_markdown_format(preview)
    
    # Keep preview short to avoid parsing issues
    if len(safe_preview) > 150:
        safe_preview = safe_preview[:150] + "..."
    
    success_message = f""""""


    # Use a safer approach for the message
    try:
        await generation_msg.edit_text(success_message, parse_mode="Markdown")
    except Exception as e:
        # If markdown parsing fails, send without formatting
        simple_message = """
✅ README Generated Successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your professional README is ready!
Use /download to get your README file.

The generated README includes installation instructions, usage examples, and project documentation.
"""
        await generation_msg.edit_text(simple_message)
    
    return ConversationHandler.END

# Enhanced file export function
async def export_readme_to_file(readme_text: str, repo_name: str = "project") -> str:
    filename = f"{repo_name}_README.md"
    filepath = os.path.join("generated", filename)
    
    # Ensure directory exists
    os.makedirs("generated", exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(readme_text)
    
    return filepath

# Enhanced download handler
async def download_readme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        message = update.message
    elif update.callback_query and update.callback_query.message:
        message = update.callback_query.message
    else:
        return
    
    # Type assertion to help the linter
    from telegram import Message
    if not isinstance(message, Message):
        return
    
    if context.user_data is None:
        context.user_data = {}
    
    readme = context.user_data.get("readme")
    repo_info = context.user_data.get("repo_info")
    
    if not readme:
        await message.reply_text(
            "⚠️ **No README Found**\n\n"
            "Please generate a README first by sending a GitHub repository link.\n"
            "Use /start to begin the process.",
            parse_mode="Markdown"
        )
        return
    
    repo_name = repo_info.get("name", "project") if repo_info else "project"
    
    try:
        filepath = await export_readme_to_file(readme, repo_name)
        
        with open(filepath, "rb") as file:
            await message.reply_document(
                document=file,
                filename=f"{repo_name}_README.md",
                caption=f"""
📄 **README File Generated Successfully!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **Features Included:**
• Project overview and description
• Installation instructions
• Usage examples and documentation
• Technology stack information
• Professional formatting

🎯 **Ready to use in your repository!**

Thanks for using ReadMe Generator Bot! 🚀
""",
                parse_mode="Markdown"
            )
        
        # Clean up the file after sending
        os.remove(filepath)
        
    except Exception as e:
        await message.reply_text(
            f"❌ **Download Failed**\n\n"
            f"Error: {str(e)}\n"
            f"Please try again or contact support.",
            parse_mode="Markdown"
        )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    help_text = """
🆘 **ReadMe Generator Bot - Help Guide**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **Commands:**
• `/start` - Start the README generation process
• `/help` - Show this help message
• `/download` - Download your generated README

📝 **How to Use:**
1. Send `/start` to begin
2. Share your GitHub repository link
3. Wait for AI analysis and generation
4. Download your professional README

🔗 **Supported URLs:**
• Public GitHub repositories
• Format: https://github.com/username/repository

⚡ **Features:**
• AI-powered content generation
• Professional formatting
• Comprehensive documentation
• Instant download

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Need more help? Contact the developer! 👨‍💻
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Handle button callbacks
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.callback_query:
        return
        
    query = update.callback_query
    await query.answer()
    
    if query.data == "download":
        await download_readme(update, context)

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "✅ Bot is alive!", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))  # ⬅️ Key fix here
    app_flask.run(host="0.0.0.0", port=port)  # ⬅️ Must bind to public IP and Railway port
    
def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# Main function
def main():
    keep_alive()  # 👈 Add this line to start the web server
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_github_link)],
        },
        fallbacks=[CommandHandler("help", help_command)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("download", download_readme))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🚀 ReadMe Generator Bot is running...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Bot Status: Online")
    print("🤖 AI Engine: Google Gemini")
    print("📝 Ready to generate professional READMEs!")
    
    app.run_polling()

if __name__ == "__main__":
    main()
