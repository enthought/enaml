//-----------------------------------------------------------------------------
// Copyright (c) 2012, Enthought, Inc.
// All rights reserved.
//-----------------------------------------------------------------------------
//
//     JSON does not allow comments, so this file is marked as js.
//     However, it is describing a JSON specification
//
//-----------------------------------------------------------------------------
// Message Format
//-----------------------------------------------------------------------------
// This describes the message object that is sent to represent an image. 
{
    // A string of raw image data that is in encoded in base64 format to ensure
    // that it is JSON-serializable. Required
    "data": "<string>",

    // A string representation of the image format. Currently indexed 8-bit, 
    // RGB32 and RGBA32 are supported. Required
    "format": "<string>",

    // A tuple with the width and height of the image. Required
    "size": "<tuple>",

    // A list of RGB tuples. This is only used by the indexed 8-bit format.
    // Optional
    "color_table": "<list of tuples>"
}