from pyrogram import Client, filters
import requests
import os
from urllib.parse import urlparse

api_id = "10471716"
api_hash = "f8a1b21a13af154596e2ff5bed164860"
bot_token = "6680585225:AAEXQVe8voeIvCJ6ebzVN8cGdi4hmzKkkq4"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


# Start command handler
@app.on_message(filters.command("start"))
def start_command(client, message):
    message.reply_text("Hello! I am your file downloader bot. Send me a link, and I'll download and upload the file for you.")


# Link handler
@app.on_message(filters.text & filters.regex(r'http[s]?://[^\s]+'))
def link_handler(client, message):
    try:
        # Download the file to the current working directory
        link = message.text

        # Make a HEAD request to get the headers without downloading the entire file
        response = requests.head(link)

        # Try to extract filename from Content-Disposition header
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            file_name = content_disposition.split("filename=")[1].strip('";')
        else:
            # Extract filename from URL if Content-Disposition is not available
            parsed_url = urlparse(link)
            file_name = os.path.basename(parsed_url.path)

        # Ensure a valid filename
        if not file_name or "." not in file_name:
            raise ValueError("Invalid filename")

        downloaded_file_path = os.path.join(os.getcwd(), file_name)

        # Download the file
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(downloaded_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        # Upload the file to Telegram
        message.reply_document(document=downloaded_file_path)

        # Remove the downloaded file from the local storage
        os.remove(downloaded_file_path)

    except Exception as e:
        # Handle errors
        app.send_message(chat_id=message.chat.id, text=f"An error occurred: {str(e)}")


# Run the bot
app.run()
