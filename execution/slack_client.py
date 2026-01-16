import os
import requests
import logging

def send_slack_message(channel, text):
    """
    Sends a message to Slack.
    Uses SLACK_WEBHOOK_URL if available (ignores channel arg in that case usually),
    or SLACK_BOT_TOKEN if available.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if webhook_url:
        try:
            # Webhook payload is simple
            payload = {"text": text}
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Slack webhook: {e}")
            return False

    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("Warning: Neither SLACK_WEBHOOK_URL nor SLACK_BOT_TOKEN found.")
        return False

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            print(f"Slack API Error: {data.get('error')}")
            return False
        return True
    except Exception as e:
        print(f"Failed to send Slack message: {e}")
        return False
