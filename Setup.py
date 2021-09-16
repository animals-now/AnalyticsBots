"""
This section manage all necessary files' path.
"""
import argparse

##### Default Paths #####
DEFAULT_SERVICE_ACCOUNTS_CREDS_PATH = "/home/maor/PycharmProjects/creds/credentials-ServiceAccounts.json"
DEFAULT_OAUTH2CLIENT_IDS_CREDS_PATH = "/home/maor/PycharmProjects/creds/credentials-OAuth2ClientIDs.json"
DEFAULT_GMAIL_TOKEN_PATH = "/home/maor/PycharmProjects/creds/token.pickle"

parser = argparse.ArgumentParser()


parser.add_argument("--ServiceAccountCreds", default=[DEFAULT_SERVICE_ACCOUNTS_CREDS_PATH],
					nargs=1, help="Please Enter Service Account creds path")

parser.add_argument("--Oauth2ClientCreds", default=[DEFAULT_OAUTH2CLIENT_IDS_CREDS_PATH],
					nargs=1, help="Please Enter Oauth2Client creds path")

parser.add_argument("--GmailToken", default=[DEFAULT_GMAIL_TOKEN_PATH],
					nargs=1, help="Please Enter token.pickle path")


args = parser.parse_args()

##### Define the paths #####
SERVICE_ACCOUNTS_CREDS_PATH = args.ServiceAccountCreds[0]
OAUTH2CLIENT_IDS_CREDS_PATH = args.Oauth2ClientCreds[0]
GMAIL_TOKEN_PATH = args.GmailToken[0]

##### Analytics Views ID #####
VEG_VIEW_ID = "224062040"
ALL_CHALLENGES_VIEW_ID = "226152220"
ANIMALS_VIEW_ID = "180688649"
ETGAR22_VIEW_ID = "136470000"
CHALLENGE22_VIEW_ID = "110660708"


