#### Some useful links for later, possibly
### https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
### https://github.com/gsuitedevs/PyDrive
### https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

##########################################################
#  _        ___           _                              #
# |_)    o   |   _. ._   |_) _  ._   _| |  _ _|_  _  ._  #
# |_) \/ o  _|_ (_| | |  |  (/_ | | (_| | (/_ |_ (_) | | #
#     /                                                  #
##########################################################

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json


##Authentication for pydrive, designed globally to minimally generate token (a slow process)
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycred.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth() #Creates local webserver and auto handles authentication.
elif gauth.access_token_expired:
    gauth.LocalWebserverAuth() #Creates local webserver and auto handles authentication.
else:
    gauth.Authorize() #Just run because everything is loaded properly
gauth.SaveCredentialsFile("mycred.txt")
drive=GoogleDrive(gauth)

scope= ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
gc =gspread.authorize(credentials)

###Returns a referenced dictionary of processed files as dictionaries {folder title SD2 ID, Gdrive UID}
def drivedatfold(opdir):
    test=open('test.json', 'w')
    datadir_list = drive.ListFile({'q': "'%s' in parents and trashed=false" %opdir}).GetList()
    dir_dict=[]
    Crys_dict={}
    Expdata_dict={}
    Robo_dict={}
    for f in datadir_list:
        if "Template" in f['title']:
            pass
        elif f['mimeType']=='application/vnd.google-apps.folder': # if folder
            dir_dict.append(f['title'])
            Exp_file_list =  drive.ListFile({'q': "'%s' in parents and trashed=false" %f['id']}).GetList()
            for f_sub in Exp_file_list:
                if "CrystalScoring" in f_sub['title']:
                    Crys_dict[f['title']]=f_sub['id']
                if "ExpDataEntry.json" in f_sub['title']:
                    Expdata_dict[f['title']]=f_sub['id']
                    #### NEed to write a helper function to export from gspread directly
                if "RobotInput" in f_sub['title']:
                    Robo_dict[f['title']]=f_sub['id']
    return(Crys_dict, Robo_dict, Expdata_dict, dir_dict)


def getalldata(crysUID, roboUID, expUID, workdir, runname):
    Crys_File = gc.open_by_key(crysUID)
    Crys_file_lists = Crys_File.sheet1.get_all_values()
    Crysout=open(workdir+runname+"_CrystalScoring.csv", "w")  
    print(Crys_file_lists, file=Crysout)
    exp_file = drive.CreateFile({'id': expUID}) 
    exp_file.GetContentFile(workdir+exp_file['title'])
    robo_file = drive.CreateFile({'id': roboUID}) 
    robo_file.GetContentFile(workdir+robo_file['title'])



