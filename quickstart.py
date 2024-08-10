import json
import os.path
import base64
import re
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MAX_URI_LENGTH

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/gmail.settings.basic"]
# reg_mail = r'\b[mailto]+:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
# reg_mob = r'[l:](?<!=)(\+?\(?\d{1,3}\)?)?[-.]?(?<!=)\d{10}'
# reg_mob = r'\+?\(?91\)?-?\d{10}'
reg_mob=r'(?<!=)\+?\(?\d{1,3}\)?[-.]?(?<!=)\d{10}'

def clean_mails(mail_list):
    remove = ["mailto:customercare@indiamart.com", "mailto:buyleads@indiamart.com"]
    for indiamart_mail in remove:
        if indiamart_mail in mail_list:
            mail_list.remove(indiamart_mail)
    for index, mail in enumerate(mail_list):
        mail_list[index] = mail[7:]
    return mail_list

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API


    service = build("gmail", "v1", credentials=creds)
    user_id =  'me'
    # label_id_one = 'INBOX'
    # label_id_two = 'UNREAD'
    from_himank= service.users().messages().list(userId='me',q="from:indiamart.com after:1721200500").execute()
    messages = from_himank['messages']
    print(len(messages))
    for  msg in messages:
        m_id = msg['id']
        message = service.users().messages().get(userId=user_id, id=m_id).execute() 
        payld = message['payload'] # get payload of the message 
        # headr = payld['headers'] # get header of the payload
        # json_str = json.dumps(message, indent=1)
        mssg_parts = payld['parts'] # fetching the message parts
        part_one  = mssg_parts[1] # fetching first element of the part 
        part_body = part_one['body'] # fetching body of the message
        part_data = part_body['data'] # fetching data from the body
        clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
        clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
        clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
        soup = BeautifulSoup(clean_two , "lxml" )
        mssg_body = soup.prettify()
        # mssg_body = soup.body()
        # print(mssg_body)
        # print("\n\n\nEMAIL\n\n\n")
        # mailto_mails = re.findall(reg_mail, mssg_body)
        mob = re.findall(reg_mob, mssg_body)
        # mailto_mails = clean_mails(mailto_mails)


        # print("EMAIL")
        # print(mailto_mails)
        print("MOBILE")
        print(mob)
        # print(mssg_body)
        print("\n\n**************************************************************************************************************************************************\n\n")
 
  

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
