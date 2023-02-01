'''
Follow these steps to configure the webhook in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Incoming WebHooks".

  3. Choose the default channel where messages will be sent and click "Add Incoming WebHooks Integration".

  4. Copy the webhook URL from the setup instructions and use it in the next section.

To encrypt your secrets use the following steps:

  1. Create or use an existing KMS Key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html

  2. Expand "Encryption configuration" and click the "Enable helpers for encryption in transit" checkbox

  3. Paste <SLACK_CHANNEL> into the slackChannel environment variable

  Note: The Slack channel does not contain private info, so do NOT click encrypt

  4. Paste <SLACK_HOOK_URL> into the kmsEncryptedHookUrl environment variable and click "Encrypt"

  Note: You must exclude the protocol from the URL (e.g. "hooks.slack.com/services/abc123").

  5. Give your function's role permission for the `kms:Decrypt` action using the provided policy template
'''

import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


SLACK_CHANNEL = os.environ['slackChannel'] #환경변수: slack channel 명 가져오기
HOOK_URL = os.environ['hookUrl'] #환경변수: webhook url 가져오기

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    deploy_status = message['status']
    application_name = message['applicationName']
    deployment_id = message['deploymentId']
    complete_time = message['completeTime']
    
    color = "#30db3f"
    if deploy_status == "SUCCEEDED":
      status_text = ":white_check_mark: *SUCCEEDED*"
      if "dev" in application_name:
        website_url = "http://13.124.38.72/"
      else:
        website_url = "https://www.claboutside.com/"
      result_component = {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": ":link: " + website_url 
          },
          "style": "primary",
          "url": website_url
        }
      ]
    }
    else:
      status_text = ":x: *FAILED*"
      error_message = message['errorInformation']
      color = "#eb4034"
      result_component = {
        "type": "context",
        "elements": [
          {
            "type": "mrkdwn",
            "text": error_message
          }  
        ]
      }
      
    slack_message = {
        "channel": SLACK_CHANNEL,
        "attachments": [{
          "color": color,
          "blocks": [
            {
              "type": "section",
              "fields": [
                {
                  "type": "mrkdwn",
                  "text": "*배포 결과:*\n" + status_text
                },
                {
                  "type": "mrkdwn",
                  "text": "*배포 애플리케이션:*\n" + application_name
                },
                {
                  "type": "mrkdwn",
                  "text": "*배포 ID:*\n" + deployment_id
                },
                {
                  "type": "mrkdwn",
                  "text": "*배포 완료 시간:*\n" + complete_time
                },
              ]
            },
            {
              "type": "actions",
              "elements": [
                {
                  "type": "button",
                  "text": {
                    "type": "plain_text",
                    "text": "CodeDeploy :eyes:"
                  },
                  "style": "primary",
                  "url": "https://ap-northeast-2.console.aws.amazon.com/codesuite/codedeploy/deployments/"+ deployment_id +"?region=ap-northeast-2"
                }
              ]
            }
          ]
        }],
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": ":female_fairy: 안녕? 난 AWS 요정이야 배포 결과를 알려주러 왔어!"
            }
          },
          {
            "type": "divider"
          },
          result_component
        ]
    }
    
    
    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

