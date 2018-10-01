# -*- coding: utf-8 -*-

"""Tools for interacting with GCS infrastructure."""

import os
from os.path import join, isdir, basename, exists
from google.cloud import storage
from google.oauth2 import service_account
from glob import glob
from datetime import datetime as dt
import subprocess, shlex

def get_bucket(cred_path):
    '''Return a bucket object from Rhg's GCS system.
    
    Parameters
    ----------
    cred_path : str
        Path to credentials file. Default is the default location on Rhg workers.
        
    Returns
    -------
    bucket : :py:class:`google.cloud.storage.Bucket`
    '''

    credentials = service_account.Credentials.from_service_account_file(
            cred_path)
    sclient = storage.Client(credentials=credentials)
    bucket = sclient.get_bucket('rhg-data')
    
    return bucket


def _cp_dir_to_gcs(bucket,src,dest):
    '''Recursively copy a directory from local path to GCS'''
    
    files_loc = glob(join(src,'*'))
    if src[-1] != '/': src += '/'

    # upload directory blob
    if bucket.get_blob(dest) is None:
        newblob = bucket.blob(dest)
        newblob.upload_from_string('')

    # upload file blobs
    for f_loc in files_loc:
        fname = basename(f_loc)
        this_dest = join(dest,fname)
        if isfile(f_loc):
            newblob = bucket.blob(this_dest)
            newblob.upload_from_filename(f_loc)
        # if directory, call this recursively
        else:
            _cp_dir_to_gcs(bucket,f_loc,this_dest)


def cp_to_gcs(src, dest, cred_path='/opt/gcsfuse_tokens/rhg-data.json'):
    '''Copy a file or recursively copy a directory from local
    path to GCS.
    
    Parameters
    ----------
    src : str
        The local path to either a file (single copy) or a directory (recursive copy).
    dest : str
        If copying a directory, this is the path of the directory blob on GCS.
        If copying a file, this is the path of the file blob on GCS.
        This path begins with e.g. 'impactlab-rhg/...'.
    cred_path (optional) : str
        Path to credentials file. Default is the default location on Rhg workers.
        
    Returns
    -------
    :py:class:`datetime.timedelta`
        Time it took to copy file(s).
    '''
        
    st_time = dt.now()
    
    # construct cp command
    if dest[0] == '/':
        dest_gs = dest.replace('/gcs/','gs://')
        dest_gcs = dest
    elif dest[0] == 'g':
        dest_gs = dest
        dest_gcs = dest.replace('gs://','/gcs/')
    cmd = 'gsutil '
    if isdir(src):
        cmd += '-m cp -r '
    cmd += '{} {}'.format(src,dest_gs)
    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    # now make directory blob on gcs so that gcsfuse recognizes it
    if not exists(dest_gcs):
        os.mkdir(dest_gcs)
        
    return stdout, stderr, dt.now() - st_time
        
        