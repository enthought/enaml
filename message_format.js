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
// objects in an Enaml application. This message format is very similar
// to that used by the most recent version of IPython. This was done on
// purpose so that it will not be difficult to have the two communicate
// with each other.
//
// The basic requirement of message is that be serializable to JSON. 
// For applications which operate locally, they may choose to omit
// the serialization step, since it would be unnecessary.
//
// A message is an array with four elements. The details of each element
// are described in detail below:
[
  // The first element in the message is the message header. The header
  // contains information necessary for routing the message to the 
  // appropriate session object. The header of the message can never 
  // be null, and all keys are required. However, certain keys may be
  // null depending on the 'msg_type'.
  {
    // A unique identifier for the session which created the message.
    // This will be null when the client is establishing a session.
    "session": "<string>",

    // The username for the originator of the message. This should
    // never be null.
    "username": "<string>",
    
    // A unique identifier for this message. This should never be null.
    "msg_id": "<string>",
    
    // The type of this message. The supported message types are 
    // described individually below.
    "msg_type": "<string>",

    // The version of the message protocol being used. (still in flux)
    "version": "<string>",
  },

  // The second element in a message is the parent header. This is the 
  // header of the message which originated this particular message. 
  // This allows clients to track the progress of a particular request. 
  // This field may be an empty mapping for an original message.
  {},

  // The third element in a message is metadata. The metadata of a 
  // message is entirely implementation defined, but must be an object.
  {},

  // The fourth element in a message is the content. What exists in the
  // content will be dependent on, the "msg_type" and "metadata". The 
  // supported message types are listed below and describe what will be 
  // included in their metadata.
  {},
]


// For every request made by a client to the server. The server will
// respond with a standard reply message where the "msg_type" is the
// same as the original message and the content is as follows:



//-----------------------------------------------------------------------------
// Supported Message Types
//-----------------------------------------------------------------------------


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


// "enaml_discover"
// ----------------
// This type of message is used to discover what views are available
// on the server. The session field of the header for this type of
// message may be null.
//
// The metadata and content of this message should be null.
//
// The content of the reponse to this message is as follows:
{
  // The status of the request, either "ok" or "error"
  "status": "<ok | error",

  // The error message if the status is "error". If the status is
  // "ok", the message will be an empty string.
  "message": "<string>",

  // The available sessions that the client may run. This will only
  // be provided if the status is 'ok'.
  "sessions": [
    {
      // The name of the session. This will be unique amongst all 
      // available sessions.
      "name": "<string>",

      // The description of the session. This is a brief description
      // of what the session will peform when launched.
      "description": "<string>",
    }
  ]
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
  // The name of the session to start for this client. This must be
  // equal to one of the session names provided by 'enaml_discover'.
  "name": "<string>"
}
//
// The content of the response to this message is as follows
{
  // The status of the request, either "ok" or "error"
  "status": "<ok | error",

  // The error message if the status is "error". If the status is
  // "ok", the message will be an empty string.
  "message": "<string>",

  // The session identifier to use for communicating with the 
  // session object on the server. This will only be provided if
  // the status is 'ok'.
  "session": "<string>",
}


// "enaml_end_session"
// -------------------
// This message is used by a client to end its session.
// 
// Both the "metadata" and the "content" are null.
//
// The content of the response to this message is as follows;
{
  // The status of the request, either "ok" or "error"
  "status": "<ok | error",

  // The error message if the status is "error". If the status is
  // "ok", the message will be an empty string.
  "message": "<string>",
}

