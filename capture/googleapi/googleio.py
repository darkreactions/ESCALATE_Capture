#Copyright (c) 2018 Ian Pendleton - MIT License
#### Some useful links for later, possibly
########################################################################################
### https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
### https://github.com/gsuitedevs/PyDrive
### https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

import logging
import os
import time

import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from capture.googleapi import googleio
from capture.devconfig import template_folder

modlog = logging.getLogger('initialize.googleio')

##############################################################################################
### Authentication for pydrive, designed globally to minimally generate token (a slow process)
##  TODO discuss where this should happen or if this google auth really should be global

gauth = GoogleAuth()

# We have to check this path here, rather than in runme.py, if this is global because
# global code gets executed when a module is imported
if not os.path.exists('./localfiles'):
    os.mkdir('./localfiles')

# TODO put this in a config
GOOGLE_CRED_FILE = "./localfiles/mycred.txt"
if not os.path.exists(GOOGLE_CRED_FILE):
    open(GOOGLE_CRED_FILE, 'w+').close()

gauth.LoadCredentialsFile(GOOGLE_CRED_FILE)
if gauth.credentials is None or gauth.access_token_expired:
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
else:
    gauth.Authorize()  # Just run because everything is loaded properly
gauth.SaveCredentialsFile(GOOGLE_CRED_FILE)
drive = GoogleDrive(gauth)

##############################################################################################


def DriveCreateFolder(title, tgt_folder_id):
    """Create template directory for later copying of relevant files
    :param title: title of the new folder
    :param tgt_folder_id: ID of the parent folder in which to create the new folder
    :return: ID of new folder
    """

    file_metadata = {
        'title': title,
        "parents": [{"kind": "drive#fileLink", "id": tgt_folder_id}],
        'mimeType': 'application/vnd.google-apps.folder'  # mimeType here specifies that the new file will be a folder
    }

    file = drive.CreateFile(file_metadata)
    file.Upload()
    time.sleep(2)
    print("Directory Created: " + "%s" % title)

    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % tgt_folder_id}).GetList()
    for file in file_list:
        if file['title'] == title:
            return file['id']

    raise ValueError('Run folder not found in GDrive. Possible server error: try again.')


def DriveAddTemplates(opdir, RunID, includedfiles):
    """Copy template gdrive files into gdrive directory for this run

    :param opdir: gdrive directory for this run
    :param RunID: ID of this run
    :param includedfiles: files to be copied from template gdrive directory
    :return: a referenced dictionary of files (title, Gdrive ID)
    """

#    template_folder='1HneaSFzgJgHImDAL-8OgQfSx1ioFJp6S'  # Debugging target folder
    template_folder = '131G45eK7o9ZiDb4a2yV7l2E1WVQrz16d'  # New template 11/5/2018
    file_template_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % template_folder}).GetList()
    for templatefile in file_template_list:       
            basename = templatefile['title']
            if basename in includedfiles:
                drive.auth.service.files().copy(fileId=templatefile['id'],
                                                body={"parents": [{"kind": "drive#fileLink", "id": opdir}],
                                                      'title': '%s_%s' % (RunID, basename)}).execute()

    newdir_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % opdir}).GetList()
    new_dict = {}
    for file1 in newdir_list:
        new_dict[file1['title']] = file1['id']
    return new_dict


def GupFile(opdir, secdir, secfilelist, filelist, runID, eclogfile):
    """Upload files to Google Drive

    :param opdir: main google drive directory to upload to
    :param secdir: subdirectory in opdir in which logfiles and executables are written
    :param secfilelist: files to be written to secdir
    :param filelist: files that go in opdir
    :param runID: the ID of this run of ESCALATE
    :param eclogfile: local path to logfile for the run
    :return: None
    """

    for file in filelist:
        outfile = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": opdir}]})
        outfile.SetContentFile(file)
        outfile['title'] = file.split('/')[1]
        outfile.Upload()

    #  Data files that need to be stored but are not crucial for performers
    for secfile in secfilelist:
        outfile = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": secdir}]})
        outfile.SetContentFile(secfile)
        outfile['title'] = secfile.split('/')[1]
        outfile.Upload()

    logfile = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": opdir}]})
    logfile.SetContentFile(eclogfile)
    logfile['title'] = '%s.log' % runID
    logfile.Upload()
    wdir = drive.CreateFile({'id': opdir})
    swdir = drive.CreateFile({'id': secdir})
    modlog.info('%s successfully uploaded to %s' % (logfile['title'], swdir['title']))

    for item in filelist:
        modlog.info('%s successfully uploaded to %s' % (item, wdir['title']))
    for item in secfilelist:
        modlog.info('%s successfully uploaded to %s' % (item, swdir['title']))
    print('File Upload Complete')


def genddirectories(rxndict, targetfolder, includedfiles):
    """Generate the primary and secondary gdrive directories for this run

    :param rxndict: the rxndict
    :param targetfolder: Parent gdrive folder in which to create the primary run directory
    :param includedfiles: gdrive template files to copy from grdive template directory
    :return: a triple: (primary directory, secondary directory, dictionary of template files)
    """
    tgt_folder_id = targetfolder
    PriDir = googleio.DriveCreateFolder(rxndict['RunID'], tgt_folder_id)
    file_dict = googleio.DriveAddTemplates(PriDir, rxndict['RunID'], includedfiles)
    secfold_name = "%s_subdata" % rxndict['RunID']
    secdir = googleio.DriveCreateFolder(secfold_name, PriDir)
    return PriDir, secdir, file_dict


def gsheettarget(file_dict):
    """Iterate through gdrive file_dict to find experimental data entry form

    :param file_dict: dictionary representing a gdrive folder
    :return: tuple containing filename and gspread credental object for experimental data entry form
    """
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) 
    gc = gspread.authorize(credentials)

    for key, val in file_dict.items():
        if "ExpDataEntry" in key:  # Experimentalsheet = gc.open_bysearches for ExpDataEntry Form to get id
            target = val
            return target, gc

    raise ValueError('No ExpDataEntry file in file dictionary')
