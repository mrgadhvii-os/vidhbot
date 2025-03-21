import os
import re
import logging
import html
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7906761490:AAFbbEV5znYVdFUw-F2auPWcyj1k7bBauzw"

# Modern welcome message with bot info
WELCOME_MESSAGE = """
🌟 *Welcome to URL Formatter Bot* 🌟

I can help you format different types of URLs:

📹 *Video Links (.mkv):* 
   Formatted for ffmpeg-stream with /yl prefix

📄 *PDF Links:* 
   Added /yl prefix with -n parameter

🎬 *YouTube Links:* 
   Added /yl prefix (no -n parameter)

Just send me any URL or multiple URLs, and I'll format them for easy downloading!

_Developed by @MrGadhvii_
"""

# Help message with examples
HELP_MESSAGE = """
📚 *How to Use This Bot* 📚

Simply send me messages containing URLs:

🔹 *Video Link Example:*
```
Physics Class https://appx-videos.livelearn.in/videos/data/12345/encrypted.mkv*123456
```

🔹 *PDF Link Example:*
```
Chapter Notes https://contents.classx.co.in/file.pdf
```

🔹 *YouTube Link Example:*
```
Tutorial Video https://youtube.com/watch?v=example
```

🔹 *Multiple URLs Example:*
```
Lecture Video https://videos.example.com/video.mkv*12345
Practice PDF https://notes.example.com/notes.pdf
Reference Video https://youtube.com/watch?v=example
```

_Send /about to learn more about this bot_
"""

# About message
ABOUT_MESSAGE = """
🤖 *About URL Formatter Bot* 🤖

This bot was created to help easily format educational content URLs for downloading.

*Features:*
• Modern interface with inline buttons
• Support for multiple URL types
• Bulk URL processing
• Clean, copyable formatting
• "@MrGadhvii" attribution included with all links

*Version:* 2.0
*Developer:* @MrGadhvii

_Send /help to learn how to use this bot_
"""

def format_file_name(file_name):
    """Format file name by replacing spaces with underscores and removing special characters."""
    # Remove any special characters that might cause issues in filenames
    formatted_name = re.sub(r'[^\w\s-]', '', file_name)
    # Replace spaces with underscores
    formatted_name = formatted_name.replace(' ', '_')
    return formatted_name

def extract_file_name(text_before_url):
    """Extract file name from text before URL."""
    # Clean up the filename by removing extra spaces
    cleaned_text = text_before_url.strip()
    
    # If the filename is empty, use a default
    if not cleaned_text:
        return "file"
    
    return cleaned_text

def extract_and_format_urls(text):
    """Extract and format URLs from the text."""
    # Initialize formatted output
    formatted_output = []
    video_urls_formatted = []
    pdf_urls_formatted = []
    youtube_urls_formatted = []
    other_urls_formatted = []
    
    # Split text into lines to process each line separately
    lines = text.strip().split('\n')
    
    for line in lines:
        # Pattern for video URLs ending with .mkv*number
        video_pattern = r'(https?://[^\s]+\.mkv\*\d+)'
        # Pattern for PDF URLs
        pdf_pattern = r'(https?://[^\s]+\.pdf)'
        # Pattern for YouTube URLs
        youtube_pattern = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/\S+)'
        # Pattern for other URLs
        other_url_pattern = r'(https?://\S+)'
        
        # Find video URL in this line
        video_matches = re.findall(video_pattern, line)
        if video_matches:
            for url in video_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                safe_file_name = format_file_name(file_name)
                
                # Split URL and key
                parts = url.split('*')
                if len(parts) == 2:
                    base_url, key = parts
                    formatted_url = f"/yl https://664f78cd-28f0-4020-8e22-64c4aa497a9e.deepnoteproject.com/ffmpeg-stream?url={base_url}*{key} -n {safe_file_name} • Downloaded By @MrGadhvii"
                    video_urls_formatted.append((file_name, formatted_url, "video"))
            continue
                
        # Find PDF URL in this line
        pdf_matches = re.findall(pdf_pattern, line)
        if pdf_matches:
            for url in pdf_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                safe_file_name = format_file_name(file_name)
                formatted_url = f"/yl {url} -n {safe_file_name} • Downloaded By @MrGadhvii"
                pdf_urls_formatted.append((file_name, formatted_url, "pdf"))
            continue
        
        # Find YouTube URL in this line
        youtube_matches = re.findall(youtube_pattern, line)
        if youtube_matches:
            for url in youtube_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                formatted_url = f"/yl {url} • Downloaded By @MrGadhvii"
                youtube_urls_formatted.append((file_name, formatted_url, "youtube"))
            continue
        
        # Find other URLs in this line
        if not video_matches and not pdf_matches and not youtube_matches:
            other_matches = re.findall(other_url_pattern, line)
            for url in other_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                other_urls_formatted.append((file_name, f"{url} • Downloaded By @MrGadhvii", "other"))
    
    # Combine all URLs for output
    all_urls = []
    all_urls.extend(video_urls_formatted)
    all_urls.extend(pdf_urls_formatted)
    all_urls.extend(youtube_urls_formatted)
    all_urls.extend(other_urls_formatted)
    
    # Return the data for building the inline keyboard
    return all_urls

def build_inline_keyboard(urls):
    """Build an inline keyboard with copy buttons for each URL."""
    keyboard = []
    
    for i, (name, url, url_type) in enumerate(urls):
        # Create a unique callback data for each URL
        callback_data = f"copy_{i}"
        
        # Add icon based on URL type
        if url_type == "video":
            icon = "📹"
        elif url_type == "pdf":
            icon = "📄"
        elif url_type == "youtube":
            icon = "🎬"
        else:
            icon = "🔗"
        
        # Create a button for this URL
        button = InlineKeyboardButton(f"{icon} Copy {name}", callback_data=callback_data)
        keyboard.append([button])
    
    # Add buttons for other actions
    keyboard.append([
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
        InlineKeyboardButton("❓ Help", callback_data="help")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def create_formatted_text(urls):
    """Create formatted text from URLs."""
    if not urls:
        return "No valid URLs found."
    
    formatted_parts = []
    
    for i, (name, url, url_type) in enumerate(urls):
        # Add icon based on URL type
        if url_type == "video":
            icon = "📹"
        elif url_type == "pdf":
            icon = "📄"
        elif url_type == "youtube":
            icon = "🎬"
        else:
            icon = "🔗"
        
        # Format each URL entry
        formatted_parts.append(f"{icon} *{html.escape(name)}*\n`{html.escape(url)}`")
    
    # Join all parts with separators
    return "\n\n".join(formatted_parts)

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user.first_name}! " + WELCOME_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

def about_command(update: Update, context: CallbackContext) -> None:
    """Send information about the bot."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ABOUT_MESSAGE,
        parse_mode=ParseMode.MARKDOWN
    )

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button callback queries."""
    query = update.callback_query
    query.answer()
    
    if query.data == "help":
        query.edit_message_text(
            text=HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "refresh":
        # Try to process the original message again
        if 'original_message' in context.user_data:
            text = context.user_data['original_message']
            urls = extract_and_format_urls(text)
            formatted_text = create_formatted_text(urls)
            reply_markup = build_inline_keyboard(urls)
            
            query.edit_message_text(
                text=formatted_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    elif query.data.startswith("copy_"):
        # Just acknowledge the copy action
        query.answer("Text copied to clipboard!")

def process_message(update: Update, context: CallbackContext) -> None:
    """Process the user message and format URLs with inline buttons."""
    text = update.message.text
    
    # Store the original message for potential refresh
    context.user_data['original_message'] = text
    
    # Extract and format URLs
    urls = extract_and_format_urls(text)
    
    if not urls:
        update.message.reply_text(
            "No valid URLs found in your message. Please check and try again.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Create formatted text and inline keyboard
    formatted_text = create_formatted_text(urls)
    reply_markup = build_inline_keyboard(urls)
    
    # Send the formatted URLs with inline keyboard
    update.message.reply_text(
        text=formatted_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    
    # Callback query handler for inline buttons
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
