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

##Creating template directory for later copying of relevant files
def DriveCreateFolder(title1):
    tgt_folder_id='13xmOpwh-uCiSeJn8pSktzMlr7BaPDo7B' #Target Folder remains constant (for now)
    file_metadata = {
        'title': title1,
        "parents": [{"kind": "drive#fileLink","id": tgt_folder_id}],
        'mimeType': 'application/vnd.google-apps.folder'  #mimetype sets the type of object to a folder type
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

##Copies all files from template directory into the new directory
##Returns a referenced dictionary of files (title, Gdrive ID)
def DriveAddTemplates(opdir, RunID):
    template_folder='1OxuxqfumIpg3MPr3rgtRxwcOgCfetkIu'  #Hardcoded as this template doesn't change
    file_template_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % template_folder}).GetList()
    for templatefile in file_template_list:       
            basename=templatefile['title']
            drive.auth.service.files().copy(fileId=templatefile['id'], body={"parents": [{"kind": "drive#fileLink", "id": opdir}], 'title': '%s_%s' %(RunID,basename)}).execute(),
    newdir_list = drive.ListFile({'q': "'%s' in parents and trashed=false" %opdir}).GetList()
    ExpDataFile="%s_ExpDataEntry"%(RunID)
    new_dict={}
    for file1 in newdir_list:
        new_dict[file1['title']]=file1['id']
    return(new_dict)

def GDLFile(GdriveFileTitle, GdriveFileID):
    testing = drive.CreateFile({'id': GdriveFileID})
    testing.GetContentFile(GdriveFileTitle)
    return(GdriveFileTitle)
    