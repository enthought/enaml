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
// This describes the message object that is used to communicate between
// objects in an Enaml application. This message format is the same as
// that used by the most recent version of IPython.
//
// The basic requirement of message is that be serializable to JSON. 
// For applications which operate locally, they may choose to omit
// the serialization step, since it would be unnecessary.
//
// Once messages are created and posted to the dispatcher, they should
// be treated as read-only. Thus, it is safe for applications to read
// messages from mutiple threads without locking.
{
  // The header of the message. The header contains information about
  // the message sender, and the type of the message. The header is
  // mainly useful for application level objects.
  "header":
    {
      // A unique identifier for the session which created the message.
      "session": "<string>",

      // The username for the originator of the message.
      "username": "<string>",
      
      // A unique identifier for this message.
      "msg_id": "<string>",
      
      // The type of this message. Supported message types are 
      // enumerated below.
      "msg_type": "<string>",

      // The version of the message structure in use.
      "version": "<string>",
    }

  // The parent header for this message. This may be null for an 
  // original message. For a response message, this will be the
  // header of the original message.
  "parent_header": null,

  // The metadata supplied by the implementations. There is formally
  // no requirement for what must be placed in this object. It is 
  // entirely implementation defined and may be null.
  "metadata": null,

  // The content of the message. What exists in the content will be
  // dependent upon the "msg_type" and "metadata". The supported message
  // types are listed below and describe what will be included in their
  // metadata.
  "content": {},
}


// For every request made by a client to the server. The server will
// respond with a standard reply message where the "msg_type" is the
// same as the original message and the content is as follows:
{
  // The status of the request, either "ok" or "error"
  "status": "<ok | error",

  // The error message if the status is "error". If the status is
  // "ok", the message will be an empty string.
  "message": "<string>",
}


//-----------------------------------------------------------------------------
// Supported Message Types
//-----------------------------------------------------------------------------
//
// These are the message types currently supported by an Enaml application
//
//
// "enaml_message"
// ---------------
// This is the most common message type passed around in Enaml applications.
// It is used to post and action and or data to a specific receiver. The
// originator of the message does not expect a reply.
//
// The "metadata" of this message type is as follows:
{
  // The target of the message. This uniquely identifies the receiver of
  // the message in an Enaml application.
  "target_id": "<string>",

  // The action that should be performed by the receiver the target.
  // The types of actions supported are defined by a given receiver.
  "action": "<string>",
}

// "enaml_request"
// ---------------
// This type of message is created when an object needs to request data
// from another object. The originator of the message expects to receive
// an "enaml_reply" message at some point in the future. 
//
// The "metadata" of this message type is as follows.
{
  // The target of the message. This uniquely identifies the receiver of
  // the message in an Enaml application.
  "target_id": "<string>",

  // The action that should be performed by the receiver the target.
  // The types of actions supported are defined by a given receiver.
  "action": "<string>",
}


// "enaml_reply"
// -------------
// This type of message is created in response to an "enaml_request". It
// is used to deliver a response to the object which made the original
// request. The order in which messages of this type are generated is
// not guaranteed.
//
// The "metadata" of this message type is as follows:
{
  // The target of the message. This will be the same as the value for
  // "target_id" in the associated "enaml_request" message.
  "target_id": "<string>",

  // This will be the same value as the "action" field in the
  // associated "enaml_request".
  "action": "<string>",
}


// "enaml_begin_session"
// ---------------------
// This message is used by a client to start an Enaml session. This is
// the only message type in which the "session" field of the header
// may be null. The standard reply for this message type will have 
// a populated "session" field for the client.
//
// The "metadata" for this message type is null. 
//
// The content for this message type is as follows:
{
  // The version of the Enaml protocol to be used by the session.
  "version": "<string>",
}


// "enaml_end_session"
// -------------------
// This message is used by a client to end its session.
// 
// Both the "metadata" and the "content" are null.

