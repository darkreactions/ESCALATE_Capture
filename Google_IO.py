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

def DriveCreateFolder(title1):
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
#    folder_id = '1qoQXcyhaK7KE-iIxFoEhdnC_8Tg01gPb'
    ## mimetype sets the type of object to a folder type
    file_metadata = {
        'title': title1,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = drive.CreateFile(file_metadata)
    file.Upload()
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:       
        if file1['title']==title1:
            print ('title: %s, id: %s' % (file1['title'], file1['id']))
        else:
            pass

#DriveCreateFolder('test1')

