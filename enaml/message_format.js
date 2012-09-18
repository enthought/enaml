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
  // null depending on the "msg_type".
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


//-----------------------------------------------------------------------------
// discover 
//-----------------------------------------------------------------------------
// This type of message is used to discover the available server sessions,
// which represent the various views that can be run on the client.
[ 
  // Header
  {
    "msg_type": "discover"
    "session": null,
    // ...
  },
  // Parent Header
  {},
  // Metadata
  {},
  // Content
  {}
]


//-----------------------------------------------------------------------------
// discover_response 
//-----------------------------------------------------------------------------
// This is the server"s response to a message of type "discover"
[
  // Header
  {
    "msg_type": "discover_response",
    "session": null,
    // ...
  },
  // Parent Header
  {
    // The original header for the "discover" message
  },
  // Metadata
  {},
  // Content
  {
    // The status of the request, either "ok" or "error"
    "status": "<ok | error",
    // The status message if the status is "error". If the status is
    // "ok", the status message will be an empty string.
    "status_msg": "<string>",
    // The available sessions that the client may run. This will only
    // be provided if the status is "ok".
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
]


//-----------------------------------------------------------------------------
// start_session
//-----------------------------------------------------------------------------
// This message is used by a client to start an Enaml session.
[
  // Header
  {
    "msg_type": "start_session",
    "session": null,
    //...
  },
  // Parent Header
  {},
  // Metadata
  {},
  // Content
  {
    // The name of the session to start for this client. This must be
    // equal to one of the session names provided by "discover_response".
    "name": "<string>"
  }
]


//-----------------------------------------------------------------------------
// start_session_response
//-----------------------------------------------------------------------------
// This is the server"s response to a message of type "start_session".
[
  // Header
  {
    "msg_type": "start_session_response",
    "session": null,
    // ...
  },
  // Parent Header
  {
    // The original header for the "start_session" message.
  },
  // Metadata
  {},
  // Content
  {
    // The status of the start_session request, either "ok" or "error"
    "status": "<ok | error",
    // The error message if the status is "error". If the status is
    // "ok", the message will be an empty string.
    "status_msg": "<string>",
    // The session identifier to use for communicating with the 
    // session object on the server. This will only be provided if
    // the status is "ok".
    "session": "<string>",
  }
]


//-----------------------------------------------------------------------------
// end_session
//-----------------------------------------------------------------------------
// This message is used by a client to terminate a session.
[
  // Header
  {
    "msg_type": "end_session",
    // The identifier for the session
    "session": "<string>",
    // ...
  }
  // Parent Header
  {},
  // Metadata
  {},
  // Content
  {}
]


//-----------------------------------------------------------------------------
// end_session_response
//-----------------------------------------------------------------------------
// This is server"s reponse to a message of type "end_session". After this
// message is sent by the server, the session id will no longer be valid.
[
  // Header
  {
    "msg_type": "end_session_response",
    // The identifier for the session
    "session": "<string>",
  }
  // Parent Header
  {
    // The original header for the "end_session" message.
  },
  // Metadata
  {},
  // Content
  {
    // The status of the request, either "ok" or "error"
    "status": "<ok | error",
    // The error message if the status is "error". If the status is
    // "ok", the message will be an empty string.
    "status_msg": "<string>",
  }
]


//-----------------------------------------------------------------------------
// "snapshot"
//-----------------------------------------------------------------------------
// This message is used by a client to request a snapshot of the session. 
// A snap is serialized version of the entire UI tree and is used for 
// assembling the UI on the client side.
[
  // Header
  {
    "msg_type": "snapshot",
    // The session identifier
    "session": "<string>",
    // ...
  },
  // Parent Header
  {},
  // Metadata
  {},
  // Content
  {},
]


//-----------------------------------------------------------------------------
// "snapshot_response"
//-----------------------------------------------------------------------------
// This is the server's response to a message of type "snapshot".
[
  // Header
  {
    "msg_type": "snapshot_response",
    // The session identifier
    "session": "<string>",
    // ...
  },
  // Parent Header
  {
    // The original header for the "snapshot" message.
  },
  // Metadata
  {},
  // Content
  {
    // The status of the request, either "ok" or "error"
    "status": "<ok | error",
    // The error message if the status is "error". If the status is
    // "ok", the message will be an empty string.
    "status_msg": "<string>",
    // The snapshot of the session state. This is only provided if
    // the "status" is "ok". This will be an array of objects, with
    // each object representing a UI tree belonging to the session.
    "snapshot": ["<object>"]
  }
]


//-----------------------------------------------------------------------------
// "widget_action"
//-----------------------------------------------------------------------------
// This message is used by both the client and server to request an action
// to be performed by the other part. This is the most common message type
// used in Enaml applications and is chief means of synchronizing widget
// state and sharing widget data between the client and server.
[
  // Header
  {
    "msg_type": "widget_action",
    // The identifier for the session
    "session": "<string>",
    // ...
  },
  // Parent Header
  {},
  // Metadata
  {
    // The identifier of the widget that should perform the action.
    "widget_id": "<string>".
    // The action that the widget should perform.
    "action": "<string>"
  },
  // Content
  {
    // The data required to perform the action. It is dependent upon
    // the "action" being performed by the widget.
  }
]


//-----------------------------------------------------------------------------
// "widget_action_response"
//-----------------------------------------------------------------------------
// This message is the reponse the "widget_action" message type. It it used
// by both the client and the server.
[
  // Header
  {
    "msg_type": "widget_action_response",
    // The identifier for the session
    "session": "<string>"
  },
  // Parent Header
  {
    // The original header for the "widget_action" message.
  },
  // Metadata
  {
    // The original Metadata for the "widget_action" message.
  },
  // Content
  {
    // The status of the request, either "ok" or "error"
    "status": "<ok | error",
    // The error message if the status is "error". If the status is
    // "ok", the message will be an empty string.
    "message": "<string>",
    // Other content related to the response of the action. This is 
    // dependent upon the "action" that was requested of the widget.
  }
]

