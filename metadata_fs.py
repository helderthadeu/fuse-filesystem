#!/usr/bin/env python

from __future__ import print_function, absolute_import, division

import logging
import errno
from stat import S_IFDIR, S_IFREG
from time import time
import argparse

from fuse import FUSE, FuseOSError, Operations

# Constant for systems that may not define ENODATA
try:
    from errno import ENODATA
except ImportError:
    ENODATA = errno.ENOENT


class MetadataFS(Operations):
    """
    A simple in-memory filesystem that supports extended attributes (xattrs).
    This is implemented using FUSE and can be mounted as a virtual filesystem.

    Attributes:
        files (dict): Stores file metadata like size, timestamps, and permissions.
        data (dict): Stores the actual file contents as bytes.
        xattrs (dict): Stores extended attributes for each file and directory.
        fd (int): File descriptor counter used during file creation and opening.
    """

    def __init__(self):
        """
        Initializes the virtual filesystem with a root directory and
        one sample file that includes extended attributes.
        """
        self.files = {}
        self.data = {}
        self.xattrs = {}
        self.fd = 0
        now = time()

        # Create root directory with basic metadata
        self.files['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.xattrs['/'] = {}  # Initialize xattrs for root directory

        # Create a sample file
        file_path = '/exemplo.txt'
        file_content = b'This file has metadata!\n'
        self.files[file_path] = dict(st_mode=(S_IFREG | 0o644), st_nlink=1,
                                     st_size=len(file_content), st_ctime=now,
                                     st_mtime=now, st_atime=now)
        self.data[file_path] = file_content

        # Add sample extended attributes to the file
        self.xattrs[file_path] = {
            'user.category': b'documents',
            'user.tags': b'sample,python',
            'user.classification': b'important'
        }
        logging.info("Filesystem initialized in memory.")

    # --- Standard Virtual Filesystem Methods ---

    def getattr(self, path, fh=None):
        """Retrieve metadata for a given path."""
        logging.info('getattr(path=%s)', path)
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        return self.files[path]

    def readdir(self, path, fh):
        """Return a list of files in the directory."""
        logging.info('readdir(path=%s)', path)
        return ['.', '..'] + [x[1:] for x in self.files if x != '/']

    def read(self, path, size, offset, fh):
        """Read a slice of file data from the given offset."""
        logging.info('read(path=%s, size=%d, offset=%d)', path, size, offset)
        return self.data[path][offset:offset + size]

    def create(self, path, mode):
        """Create a new empty file with the specified mode."""
        logging.info('create(path=%s, mode=%o)', path, mode)
        self.files[path] = dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                 st_size=0, st_ctime=time(), st_mtime=time(),
                                 st_atime=time())
        self.data[path] = b''
        self.xattrs[path] = {}  # Initialize xattrs for new file
        self.fd += 1
        return self.fd

    def unlink(self, path):
        """Remove a file and its associated data and xattrs."""
        logging.info('unlink(path=%s)', path)
        self.files.pop(path)
        self.data.pop(path)
        self.xattrs.pop(path)

    def open(self, path, flags):
        """Called when a file is opened."""
        logging.info('open(path=%s, flags=%s)', path, flags)
        self.fd += 1
        return self.fd

    def truncate(self, path, length, fh=None):
        """Called to change the size of a file."""
        logging.info('truncate(path=%s, length=%d)', path, length)
        # Make the file content the desired length
        self.data[path] = self.data[path][:length]
        # Update the file size attribute
        self.files[path]['st_size'] = length

    def write(self, path, data, offset, fh):
        """Called to write data to a file."""
        logging.info('write(path=%s, offset=%d, bytes=%d)', path, offset, len(data))
        # Insert new data at the correct offset
        self.data[path] = self.data[path][:offset] + data
        # Update the file size attribute
        self.files[path]['st_size'] = len(self.data[path])
        # Return the number of bytes written
        return len(data)

    # --- Extended Attributes (xattr) Support ---

    def getxattr(self, path, name, position=0):
        """Retrieve the value of an extended attribute for the given path."""
        logging.info('getxattr(path=%s, name=%s)', path, name)
        if path not in self.xattrs:
            raise FuseOSError(errno.ENOATTR)

        attrs = self.xattrs.get(path, {})
        try:
            return attrs[name]
        except KeyError:
            raise FuseOSError(ENODATA)

    def setxattr(self, path, name, value, options, position=0):
        """Set or update an extended attribute for the given path."""
        logging.info('setxattr(path=%s, name=%s)', path, name)
        if path not in self.xattrs:
            raise FuseOSError(errno.ENOATTR)

        attrs = self.xattrs.setdefault(path, {})
        attrs[name] = value

    def listxattr(self, path):
        """List all extended attribute names for the given path."""
        logging.info('listxattr(path=%s)', path)
        if path not in self.xattrs:
            raise FuseOSError(errno.ENOATTR)

        attrs = self.xattrs.get(path, {})
        return list(attrs.keys())

    def removexattr(self, path, name):
        """Remove a specific extended attribute from the given path."""
        logging.info('removexattr(path=%s, name=%s)', path, name)
        if path not in self.xattrs:
            raise FuseOSError(errno.ENOATTR)

        attrs = self.xattrs.get(path, {})
        try:
            del attrs[name]
        except KeyError:
            raise FuseOSError(ENODATA)


if __name__ == '__main__':
    # Parse mount point argument
    parser = argparse.ArgumentParser(
        description="An in-memory filesystem with extended attribute support using FUSE.")
    parser.add_argument('mount', help='Mount point for the filesystem')
    args = parser.parse_args()

    # Enable logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting FUSE filesystem...")
    
    # Launch the FUSE filesystem
    fuse = FUSE(MetadataFS(), args.mount, foreground=True)

