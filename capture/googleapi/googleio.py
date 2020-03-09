#Copyright (c) 2018 Ian Pendleton - MIT License
#### Some useful links for later, possibly
########################################################################################
### https://stackoverflow.com/questions/43865016/python-copy-a-file-in-google-drive-into-a-specific-folder
### https://github.com/gsuitedevs/PyDrive
### https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process

import logging
import os
import re
import time


import gspread
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from capture.googleapi import googleio
import capture.devconfig as config
from utils import globals
from utils.globals import lab_safeget

modlog = logging.getLogger('initialize.googleio')

def get_drive_auth():
    gauth = GoogleAuth(settings_file='settings.yaml')

    # We have to check this path here, rather than in runme.py, if this is global because
    # global code gets executed when a module is imported

    # TODO put this in a config
    GOOGLE_CRED_FILE = "./mycred.txt"
    if not os.path.exists(GOOGLE_CRED_FILE):
        open(GOOGLE_CRED_FILE, 'w+').close()

    gauth.LoadCredentialsFile(GOOGLE_CRED_FILE)
    if gauth.credentials is None or gauth.access_token_expired:
        gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
    else:
        gauth.Authorize()  # Just run because everything is loaded properly
    gauth.SaveCredentialsFile(GOOGLE_CRED_FILE)
    drive = GoogleDrive(gauth)
    return(drive)

def create_drive_folder(title, tgt_folder_id):
    """Create template directory for later copying of relevant files
    :param title: title of the new folder
    :param tgt_folder_id: ID of the parent folder in which to create the new folder
    :return: ID of new folder
    """
    drive = get_drive_auth()

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


def copy_drive_templates(opdir, RunID, includedfiles):
    """Copy template gdrive files into gdrive directory for this run

    :param opdir: gdrive directory for this run
    :param RunID: ID of this run
    :param includedfiles: files to be copied from template gdrive directory
    :return: a referenced dictionary of files (title, Gdrive ID)
    """
    drive = get_drive_auth()
    template_folder = lab_safeget(config.lab_vars, globals.get_lab(), 'template_folder')
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


def upload_files_to_gdrive(opdir, secdir, secfilelist, filelist, runID, eclogfile):
    """Upload files to Google Drive

    :param opdir: main google drive directory to upload to
    :param secdir: subdirectory in opdir in which logfiles and executables are written
    :param secfilelist: files to be written to secdir
    :param filelist: files that go in opdir
    :param runID: the ID of this run of ESCALATE
    :param eclogfile: local path to logfile for the run
    :return: None
    """
    drive = get_drive_auth()

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

    requested_folders = lab_safeget(config.lab_vars, globals.get_lab(), 'required_folders')
    if requested_folders:
        for folder in requested_folders:
            create_drive_folder(folder, opdir)

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


def create_drive_directories(rxndict, targetfolder, includedfiles):
    """Generate the primary and secondary gdrive directories for this run

    :param rxndict: the rxndict
    :param targetfolder: Parent gdrive folder in which to create the primary run directory
    :param includedfiles: gdrive template files to copy from grdive template directory
    :return: a triple: (primary directory, secondary directory, dictionary of template files)
    """
    tgt_folder_id = targetfolder
    PriDir = googleio.create_drive_folder(rxndict['RunID'], tgt_folder_id)
    file_dict = googleio.copy_drive_templates(PriDir, rxndict['RunID'], includedfiles)
    secfold_name = "%s_subdata" % rxndict['RunID']
    secdir = googleio.create_drive_folder(secfold_name, PriDir)
    return PriDir, secdir, file_dict


def get_uid_by_name(file_dict, name_pat):
    """Return the uid of the file from file dict whose name matches name_pat

    Returns the first matching name in order of dict hash.

    :param file_dict: dictionary representing a gdrive folder
    :param name_pat: a pattern to search for in the file_dict
    :return: uid of gdrive observation_interface file
    """

    for key, val in file_dict.items():
        if re.search(name_pat, key):
            target = val
            return target

    raise ValueError('Could not find {} in file_dict.keys'.format(name_pat))

def get_gdrive_client():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    gc = gspread.authorize(credentials)
    return gc


def upload_cp_files_to_drive(uploadlist, secfilelist, runID, logfile, targetfolder):
    tgt_folder_id = targetfolder
    PriDir = googleio.create_drive_folder(runID, tgt_folder_id)
    googleio.copy_drive_templates(PriDir, runID, []) # copies metadata from current template (leaves the rest)
    secfold_name = "%s_subdata" %runID
    secdir = googleio.create_drive_folder(secfold_name, PriDir)
    googleio.upload_files_to_gdrive(PriDir, secdir, secfilelist, uploadlist, runID, logfile)