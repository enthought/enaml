#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

magic_numbers = {
    b'%PNG': 'image/png',
    b'\xFF\xD8\xFF': 'image/jpeg',
    b'GIF87a': 'image/gif',
    b'GIF89a': 'image/gif',
    b'BM': 'image/bmp',
    b'P1': 'image/x-portable-bitmap',
    b'P2': 'image/x-portable-graymap',
    b'P3': 'image/x-portable-pixmap',
    b'P4': 'image/x-portable-bitmap',
    b'P5': 'image/x-portable-graymap',
    b'P6': 'image/x-portable-pixmap',
    b'/* XPM */': 'image/x-xpixmap',
    b'! XPM2': 'image/x-xpixmap'
}

def infer_mimetype(data):
    """ Attempt to infer the image mimetype from the binary data
    
    """
    for magic_number, format in magic_numbers.items():
        if data.startswith(magic_number):
            return format
