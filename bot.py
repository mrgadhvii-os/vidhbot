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
✨ <b>Welcome to SmartURL Bot</b> ✨

I transform your educational links into organized, accessible formats.

<b>What I can do:</b>
• Convert PDF links to viewer-friendly formats
• Format YouTube links for easy access
• Process multiple URLs in one message
• Share formatted links with friends
• Set chapter names with /set command

<b>Try me!</b> Just send any PDF or YouTube link...

<i>Created by @MrGadhvii</i>
"""

# Help message with examples
HELP_MESSAGE = """
📚 <b>How to Use This Bot</b> 📚

Simply send messages containing URLs:

<b>PDF Link Example:</b>
<code>Chapter Notes https://contents.classx.co.in/file.pdf</code>

<b>YouTube Link Example:</b>
<code>Tutorial Video https://youtube.com/watch?v=example</code>

<b>Multiple URLs Example:</b>
<code>Practice PDF https://notes.example.com/notes.pdf
Reference Video https://youtube.com/watch?v=example</code>

<b>Set Chapter Name:</b>
<code>/set Chapter Name</code> - All files will be prefixed with this name

You can share formatted PDF and YouTube links with the Share button.

<i>Send /about to learn more about this bot</i>
"""

# About message
ABOUT_MESSAGE = """
🤖 <b>About SmartURL Bot</b> 🤖

This bot was created to help easily format educational content URLs for viewing and sharing.

<b>Features:</b>
• Modern interface with sharing functionality
• Support for multiple URL types
• Clean, clickable formatting
• Specialized PDF viewers for different sources
• Chapter name setting with /set command
• "@MrGadhvii" attribution included with all links

<b>Version:</b> 3.1
<b>Developer:</b> @MrGadhvii

<i>Send /help to learn how to use this bot</i>
"""

def generate_final_url(file_url, website_link="https://tempnewwebsite.classx.co.in", save_flag="1", key="undefined"):
    if file_url.startswith("https://appx"):
        if "https://tempnewwebsite.classx.co.in/pdfjs/web/viewer.html?file=" in file_url:
            return file_url
        return (f"{website_link}/pdfjs/web/viewer.html?file={file_url}"
                f"&save_flag={save_flag}"
                f"&is_encrypted={'0' if key=='undefined' else '1'}"
                f"&encryption_key=encryptedSecret"
                f"&encryption_version=1"
                f"&phone=NjM4dWRoMzgyOTE2MjAxOHhsc3JkMDM4Y3l5Z3Rramg5NDI2MTE3NDg4")
    else:
        # Use Google Docs viewer for non-appx URLs.
        return f"https://docs.google.com/viewer?url={file_url}"

def format_file_name(file_name, chapter_name=None):
    """Format file name by replacing spaces with underscores and removing special characters.
    Include chapter name as prefix if provided."""
    # Remove any special characters that might cause issues in filenames
    formatted_name = re.sub(r'[^\w\s-]', '', file_name)
    # Replace spaces with underscores
    formatted_name = formatted_name.replace(' ', '_')
    
    # Add chapter name prefix if provided
    if chapter_name:
        return f"{chapter_name}_{formatted_name}"
    return formatted_name

def extract_file_name(text_before_url):
    """Extract file name from text before URL."""
    # Clean up the filename by removing extra spaces
    cleaned_text = text_before_url.strip()
    
    # If the filename is empty, use a default
    if not cleaned_text:
        return "file"
    
    return cleaned_text

def extract_and_format_urls(text, chapter_name=None):
    """Extract and format URLs from the text with optional chapter name."""
    # Initialize formatted output
    formatted_output = []
    video_urls_formatted = []
    pdf_urls_formatted = []
    youtube_urls_formatted = []
    zip_urls_formatted = []
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
        # Pattern for ZIP URLs
        zip_pattern = r'(https?://[^\s]+\.zip)'
        # Pattern for other URLs
        other_url_pattern = r'(https?://\S+)'
        
        # Find video URL in this line
        video_matches = re.findall(video_pattern, line)
        if video_matches:
            for url in video_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                
                # Format with chapter name in bold if available for display name
                displayed_name = file_name
                if chapter_name:
                    displayed_name = f"<b>{chapter_name}</b> - {file_name}"
                
                # Format the safe_file_name with just bold tags as requested
                safe_file_name = file_name
                if chapter_name:
                    # Just use the chapter name without any HTML tags
                    safe_file_name = f"{chapter_name} = {file_name}"
                
                # Split URL and key
                parts = url.split('*')
                if len(parts) == 2:
                    base_url, key = parts
                    formatted_url = f"/yl https://664f78cd-28f0-4020-8e22-64c4aa497a9e.deepnoteproject.com/ffmpeg-stream?url={base_url}*{key} -n {safe_file_name} • Downloaded By @MrGadhvii"
                    video_urls_formatted.append((displayed_name, formatted_url, "video"))
            continue
                
        # Find PDF URL in this line
        pdf_matches = re.findall(pdf_pattern, line)
        if pdf_matches:
            for url in pdf_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                
                # Apply chapter name if present
                safe_file_name = format_file_name(file_name, chapter_name)
                
                # Format with chapter name in bold if available
                displayed_name = file_name
                if chapter_name:
                    displayed_name = f"<b>{chapter_name}</b> - {file_name}"
                
                # Generate final URL using the new function
                final_url = generate_final_url(url)
                formatted_url = f"{final_url} • Downloaded By @MrGadhvii"
                pdf_urls_formatted.append((displayed_name, formatted_url, "pdf"))
            continue
        
        # Find YouTube URL in this line
        youtube_matches = re.findall(youtube_pattern, line)
        if youtube_matches:
            for url in youtube_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                
                # Format with chapter name in bold if available
                displayed_name = file_name
                if chapter_name:
                    displayed_name = f"<b>{chapter_name}</b> - {file_name}"
                
                formatted_url = f"/yl {url} • Downloaded By @MrGadhvii"
                youtube_urls_formatted.append((displayed_name, formatted_url, "youtube"))
            continue
        
        # Find ZIP URL in this line
        zip_matches = re.findall(zip_pattern, line)
        if zip_matches:
            for url in zip_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                
                # Format with chapter name in bold if available
                displayed_name = file_name
                if chapter_name:
                    displayed_name = f"<b>{chapter_name}</b> - {file_name}"
                
                formatted_url = f"{url} • Downloaded By @MrGadhvii"
                zip_urls_formatted.append((displayed_name, formatted_url, "zip"))
            continue
        
        # Find other URLs in this line
        if not video_matches and not pdf_matches and not youtube_matches and not zip_matches:
            other_matches = re.findall(other_url_pattern, line)
            for url in other_matches:
                # Get everything before the URL to extract file name
                text_before_url = line.split(url)[0]
                file_name = extract_file_name(text_before_url)
                
                # Format with chapter name in bold if available
                displayed_name = file_name
                if chapter_name:
                    displayed_name = f"<b>{chapter_name}</b> - {file_name}"
                
                other_urls_formatted.append((displayed_name, f"{url} • Downloaded By @MrGadhvii", "other"))
    
    # Combine all URLs in the specified order: videos first, then PDFs, then YouTube, then zips, then others
    all_urls = []
    all_urls.extend(video_urls_formatted)
    all_urls.extend(pdf_urls_formatted)
    all_urls.extend(youtube_urls_formatted)
    all_urls.extend(zip_urls_formatted)
    all_urls.extend(other_urls_formatted)
    
    # Return the data for building the inline keyboard
    return all_urls

def create_sharable_content(urls):
    """Create text that's sharable with only PDF, ZIP and YouTube URLs, optimized for sharing."""
    if not urls:
        return ["No sharable URLs found."]
    
    formatted_parts = []
    
    # First, filter to keep only PDF, ZIP and YouTube URLs in the desired order
    video_urls = [(name, url, url_type) for name, url, url_type in urls if url_type == "video"]
    pdf_urls = [(name, url, url_type) for name, url, url_type in urls if url_type == "pdf"]
    youtube_urls = [(name, url, url_type) for name, url, url_type in urls if url_type == "youtube"]
    zip_urls = [(name, url, url_type) for name, url, url_type in urls if url_type == "zip"]
    
    # Combine in the desired order
    sharable_urls = []
    sharable_urls.extend(video_urls)
    sharable_urls.extend(pdf_urls)
    sharable_urls.extend(youtube_urls)
    sharable_urls.extend(zip_urls)
    
    if not sharable_urls:
        return ["No sharable URLs found."]
    
    # Add a header to the shared content
    formatted_parts.append("<b>📚 Educational Resources 📚</b>\nShared via @MrGadhvii")
    
    # Format each URL for sharing
    for name, url, url_type in sharable_urls:
        if url_type == "pdf":
            icon = "📄"
            # Format PDF URLs with blockquote for easy clicking
            formatted_parts.append(f"{icon} {name}\n<blockquote>{url}</blockquote>")
        elif url_type == "zip":
            icon = "🗃️"
            # Format ZIP URLs with blockquote like PDFs
            formatted_parts.append(f"{icon} {name}\n<blockquote>{url}</blockquote>")
        elif url_type == "youtube":
            icon = "🎬"
            # Remove /yl prefix for sharing YouTube links and attribution
            clean_url = url.replace("/yl ", "")
            if "•" in clean_url:
                clean_url = clean_url.split("•")[0].strip()
            formatted_parts.append(f"{icon} {name}\n{clean_url}")
        elif url_type == "video":
            icon = "📹"  # Video camera emoji
            # Use code tag for monospaced font for video URLs
            formatted_parts.append(f"{icon} {name}\n<code>{url}</code>")
    
    # Return the parts as a list
    return formatted_parts

def split_text_into_chunks(text_parts, max_chunk_size=4000):
    """Split text into chunks respecting Telegram's message size limit."""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for part in text_parts:
        part_length = len(part)
        
        # If this part alone exceeds the limit, we need to split it further
        if part_length > max_chunk_size:
            # If we have content in current_chunk, add it as a chunk first
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # Now handle the oversized part by splitting it
            remaining_text = part
            while remaining_text:
                # Find a good splitting point (preferably at a line break)
                split_point = max_chunk_size
                if len(remaining_text) > max_chunk_size:
                    # Try to find a newline to split at
                    newline_pos = remaining_text[:max_chunk_size].rfind('\n')
                    if newline_pos > max_chunk_size // 2:  # Only use if it's reasonably far in
                        split_point = newline_pos + 1  # Include the newline
                
                chunks.append(remaining_text[:split_point])
                remaining_text = remaining_text[split_point:]
        
        # If adding this part would exceed the limit, start a new chunk
        elif current_length + part_length + (2 if current_chunk else 0) > max_chunk_size:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [part]
            current_length = part_length
        
        # Otherwise, add to the current chunk
        else:
            current_chunk.append(part)
            current_length += part_length + (2 if current_chunk else 0)  # +2 for "\n\n"
    
    # Add the last chunk if there's anything left
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks

def create_formatted_text(urls):
    """Create formatted text from URLs."""
    if not urls:
        return "No valid URLs found."
    
    formatted_parts = []
    
    for i, (name, url, url_type) in enumerate(urls):
        # Add icon based on URL type
        if url_type == "video":
            icon = "📹"  # Video camera emoji
            # Use code tag for monospaced font for video URLs
            formatted_parts.append(f"{icon} {name}\n<code>{url}</code>")
            continue
        elif url_type == "pdf":
            icon = "📄"
            # Format PDF URLs with blockquote and clickable link
            formatted_parts.append(f"{icon} {name}\n<blockquote>{url}</blockquote>")
            continue
        elif url_type == "youtube":
            icon = "🎬"
        elif url_type == "zip":
            icon = "🗃️"
            # Format ZIP URLs with blockquote like PDFs
            formatted_parts.append(f"{icon} {name}\n<blockquote>{url}</blockquote>")
            continue
        else:
            icon = "🔗"
        
        # Format each URL entry (non-PDF/ZIP)
        formatted_parts.append(f"{icon} {name}\n<code>{html.escape(url)}</code>")
    
    # Join all parts with separators
    return formatted_parts

def build_inline_keyboard(urls):
    """Build an inline keyboard with share button."""
    keyboard = []
    
    # Add share button if there are any URLs
    if urls:
        # Create a proper share button that will open Telegram's native share menu
        keyboard.append([
            InlineKeyboardButton("📤 Share with Friends", callback_data="share")
        ])
    
    return InlineKeyboardMarkup(keyboard) if keyboard else None

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # Modern animated greeting with the user's name
    greeting = f"Hi {user.first_name}! 👋"
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greeting + "\n" + WELCOME_MESSAGE,
        parse_mode=ParseMode.HTML
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HELP_MESSAGE,
        parse_mode=ParseMode.HTML
    )

def about_command(update: Update, context: CallbackContext) -> None:
    """Send information about the bot."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ABOUT_MESSAGE,
        parse_mode=ParseMode.HTML
    )

def set_chapter_name(update: Update, context: CallbackContext) -> None:
    """Set the chapter name for future URL formatting."""
    args = context.args
    
    if not args:
        update.message.reply_text(
            "Please provide a chapter name after the /set command. For example: /set Chapter1",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Join all arguments to create the chapter name
    chapter_name = ' '.join(args)
    
    # Store the chapter name in user_data
    context.user_data['chapter_name'] = chapter_name
    
    update.message.reply_text(
        f"✅ Chapter name set to: <b>{chapter_name}</b>\n\nThis will be applied to all future files you process.",
        parse_mode=ParseMode.HTML
    )

def button_callback(update: Update, context: CallbackContext) -> None:
    """Handle button callback queries."""
    query = update.callback_query
    query.answer()
    
    if query.data == "help":
        query.edit_message_text(
            text=HELP_MESSAGE,
            parse_mode=ParseMode.HTML
        )
    elif query.data == "share":
        # Generate sharable content with only PDF and YouTube URLs
        if 'urls' in context.user_data:
            urls = context.user_data['urls']
            sharable_parts = create_sharable_content(urls)
            
            # Split into chunks if needed
            chunks = split_text_into_chunks(sharable_parts)
            
            # Create a new message specifically designed for sharing
            main_message = "<b>✅ Ready to share!</b>\n\nHere are your formatted resources. To share them:\n1. <b>Long-press</b> on a message below\n2. Select <b>Forward</b>\n3. Choose the chat"
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=main_message,
                parse_mode=ParseMode.HTML
            )
            
            # Send each chunk as a separate, shareable message
            for chunk in chunks:
                # Use forward-friendly format that works well in group chats
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False  # Allow link previews for better UX
                )
            
            query.answer("Content ready to share!")
        else:
            query.answer("Nothing to share!")

def process_message(update: Update, context: CallbackContext) -> None:
    """Process the user message and format URLs with inline buttons."""
    text = update.message.text
    
    # Store the original message for potential use
    context.user_data['original_message'] = text
    
    # Get chapter name if it has been set
    chapter_name = context.user_data.get('chapter_name', None)
    
    # Extract and format URLs with chapter name if available
    urls = extract_and_format_urls(text, chapter_name)
    
    # Store URLs for sharing functionality
    context.user_data['urls'] = urls
    
    if not urls:
        update.message.reply_text(
            "No valid URLs found in your message. Please check and try again.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Create formatted text parts and inline keyboard
    formatted_parts = create_formatted_text(urls)
    reply_markup = build_inline_keyboard(urls)
    
    # Split into chunks if needed
    chunks = split_text_into_chunks(formatted_parts)
    
    # Send the first chunk with the inline keyboard
    update.message.reply_text(
        text=chunks[0],
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    # Send any additional chunks without the keyboard
    for chunk in chunks[1:]:
        update.message.reply_text(
            text=chunk,
            parse_mode=ParseMode.HTML
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
    dispatcher.add_handler(CommandHandler("set", set_chapter_name))
    
    # Callback query handler for inline buttons
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_message))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
