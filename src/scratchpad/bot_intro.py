""" Basic operations using Slack_sdk """
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

""" We need to pass the 'Bot User OAuth Token' """
slack_token = os.environ.get("SLACK_BOT_API_TOKEN")
signing_secret = os.environ.get("SLACK_BOT_SIGNING_SECRET")
print(f"hi {slack_token}")

# Creating an instance of the Webclient class
client = WebClient(token=slack_token)

try:
    # Posting a message in #random channel
    target_channel = "new-channel"
    response = client.chat_postMessage(
        channel=target_channel,
        text="Bot's first message"
    )

    # Sending a message to a particular user
    response = client.chat_postEphemeral(
        channel=target_channel,
        text="Hello USERID0000",
        user="U092VDAKQG0"
    )

    # Get basic information of the channel where our Bot has access
    response = client.conversations_info(
        channel="C09279HS51S"
    )
    print(response)

    # Get a list of conversations
    response = client.conversations_list()
    print(response["channels"])

except SlackApiError as e:
    assert e.response["error"]

print("done")
