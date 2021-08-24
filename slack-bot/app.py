import slack_bolt
import os
from nlcc import openai

# Initialize the app
#app = Flask(__name__)

# Initialize Bolt
bolt_client = slack_bolt.App(
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    token=os.environ["SLACK_BOT_TOKEN"],
)

@bolt_client.event("message")
def handle_message_events(body, logger):
    print(body)
    logger.info(body)

# Initialize the Bolt app
@bolt_client.event("app_mention")
def handle_mention(body, say, logger):
    print(body)
    request_full = body['event']['text']
    try:
        code_request = "|".join(request_full.split("|")[1:])
    except IndexError:
        say("Request a Codex translation by mentioning @nlcc and then putting a | before your request") 
        return
    
    response = openai.code_engine(code_request)
    say("You asked:")
    say(code_request)
    say(response[0])

@bolt_client.command("/nlcc")
def code_generation(ack, respond, command):
    # Acknowledge command request
    ack()
    code_request = command['text']
    print(code_request)
    print()
    response = openai.code_engine(code_request)
    respond("You asked:")
    respond(code_request)
    respond(response[0])

# Start the app
if __name__ == "__main__":
    bolt_client.start(port=3000)
