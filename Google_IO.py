import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

#### Open, read and print some information from the google sheet template ##
def SheetUI():
    scope= ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    gc =gspread.authorize(credentials)
    testsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dvLDvf-J56HYPAiU5qJ0YUp_JbgkloYZ3HHHWg1bIXo/edit?usp=sharing").sheet1
    test=testsheet.col_values(2)
    print(test)


##Some useful links for later, possibly
## https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
## https://github.com/gsuitedevs/PyDrive
## https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

#### Authenticate only as needed ###
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycred.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
elif gauth.access_token_expired:
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
else:
    gauth.Authorize() #Just run because everything is loaded properly
gauth.SaveCredentialsFile("mycred.txt")
drive=GoogleDrive(gauth)


def DriveCreateFolder(title1):
    tgt_folder_id='13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B' ##Target Folder remains constant (for now)
#    print("Target: %s" % tgt_folder_id)
    file_metadata = {
        'title': title1,
        "parents": [{"kind": "drive#fileLink","id": tgt_folder_id}],
        'mimeType': 'application/vnd.google-apps.folder'   ## mimetype sets the type of object to a folder type
    }
    file = drive.CreateFile(file_metadata)
    file.Upload()
    print("Directory Created: " + "%s" %(title1))
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % tgt_folder_id}).GetList()
    for file1 in file_list:       
        if file1['title']==title1:
            return(file1['id'])
        else:
            pass

def DriveAddTemplates(opdir, RunID):
#    template_folder='1OxuxqfumIpg3MPr3rgtRxwcOgCfetkIu'  ##Hardcoded as this template doesn't change
    template_folder='1OxuxqfumIpg3MPr3rgtRxwcOgCfetkIu'  ##Hardcoded as this template doesn't change
#    print("Template: %s" % template_folder)
    file_template_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % template_folder}).GetList()
    for templatefile in file_template_list:       
            basename=templatefile['title']
            drive.auth.service.files().copy(fileId=templatefile['id'], body={"parents": [{"kind": "drive#fileLink", "id": opdir}], 'title': '%s_%s' %(RunID,basename)}).execute()
            print("File Created: " + "%s_%s" %(RunID,basename))