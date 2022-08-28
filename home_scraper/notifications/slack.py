from slack_sdk import WebClient

from home_scraper.config import settings


def send_message(message: str, channel: str):
    client = WebClient(token=settings.slack.bot_token)
    client.chat_postMessage(channel=channel, text=message)
