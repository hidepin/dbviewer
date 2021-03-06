#!/usr/bin/env python

import argparse
import sys
import os
import dropbox

# OAuth2 access token.  TODO: login etc.
TOKEN = ''

parser = argparse.ArgumentParser(description='View Dropbox')
parser.add_argument('folder', type=str, nargs='?', default='download',
                    help='Folder name in your Dropbox')
parser.add_argument('--token', type=str, default=TOKEN,
                    help='Access token '
                    '(see https://www.dropbox.com/developers/apps)')
parser.add_argument('--size', '-s', action='store_true',
                    help='Display sum of file size.')
parser.add_argument('--quiet', '-q', action='store_true',
                    help='quiet mode.')

def main():
    args = parser.parse_args()
    if not args.token:
        print('--token is mandatory')
        sys.exit(2)

    folder = args.folder

    if not args.quiet:
        print('Dropbox folder name:', folder)

    dbx = dropbox.Dropbox(args.token)

    if args.size:
        disk_usage(dbx, folder);
    else:
        list_folder(dbx, folder, '')

def disk_usage(dbx, folder):
    path = '/%s' % (folder)
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        if _stopwatch('disk_usage'):
            res = dbx.files_list_folder(path, recursive=True)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumed empty:', err)
        return {}
    else:
        size = _disk_usage_recursive(dbx, res)
        print(folder, 'size = ', size/1024/1024)

def list_folder(dbx, folder, subfolder):
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        if _stopwatch('list_folder'):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumed empty:', err)
        return {}
    else:
        _list_folder_recursive(dbx, res)

def _stopwatch(message):
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))

def _disk_usage_recursive(dbx, res):
    size = 0
    for entry in res.entries:
        if type(entry) is dropbox.files.FileMetadata:
            size += entry.size

    if (res.has_more):
        res_continue = dbx.files_list_folder_continue(res.cursor)
        size += _disk_usage_recursive(dbx, res_continue)

    return size

def _list_folder_recursive(dbx, res):
    for entry in res.entries:
        if type(entry) is dropbox.files.FileMetadata:
            print(entry.name, ",", entry.size)

    if (res.has_more):
        res_continue = dbx.files_list_folder_continue(res.cursor)
        _list_folder_recursive(dbx, res_continue)

if __name__ == '__main__':
    main()
