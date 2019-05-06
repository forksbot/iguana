#!/usr/local/bin/python
from os import path, symlink, system, sep, chown, setgid, setuid, environ, stat, walk
from distutils.dir_util import copy_tree, remove_tree
from pwd import getpwuid


IGUANA_DIR = path.join(sep, "iguana")
IGUANA_FILES_DIR = path.join(IGUANA_DIR, "files")
FILES_DIR = path.join(sep, "files")

IGUANA_PUID = int(environ.get("PUID"))
IGUANA_PGID = int(environ.get("PGID"))


# move /iguana/files to /files directory and symlink to it
if not path.islink(IGUANA_FILES_DIR):
    print("Creating default files on the volume.")
    copy_tree(IGUANA_FILES_DIR, FILES_DIR)
    remove_tree(IGUANA_FILES_DIR)
    symlink(FILES_DIR, IGUANA_FILES_DIR)


# create Iguana user
try:
    # check if it exists
    getpwuid(IGUANA_PUID)
    print("User 'iguana' already exists.")
except Exception:
    print("Creating user 'iguana'.")
    system("addgroup --gid " + str(IGUANA_PGID) + " iguana")
    system("adduser --disabled-password --no-create-home --gecos '' --uid " + str(IGUANA_PUID) + " -G iguana iguana")


# chown the application path to the Iguana user
print('Setting file permissions.')
for dir in [IGUANA_DIR, FILES_DIR]:
    if stat(dir).st_uid != IGUANA_PUID or \
            stat(dir).st_gid != IGUANA_PGID:
        # recursive chown
        for root, dirs, files in walk(dir):
            for d in dirs:
                chown(path.join(root, d), IGUANA_PUID, IGUANA_PGID, follow_symlinks=False)
            for f in files:
                chown(path.join(root, f), IGUANA_PUID, IGUANA_PGID, follow_symlinks=False)

        # don't forget the root directory
        chown(dir, IGUANA_PUID, IGUANA_PGID, follow_symlinks=False)


# start Iguana
print("Starting Iguana.")
setgid(IGUANA_PGID)
setuid(IGUANA_PUID)
system("python ./src/make.py run 0.0.0.0:8000")