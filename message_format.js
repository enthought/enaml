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
  // dependent upon the "msg_type". The supported message types,
  // listed below, describe what will be included in the content.
  "content": {},
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
// The "content" of this message type is as follows:
{
  // The target of the message. This uniquely identifies the receiver of
  // the message in an Enaml application.
  "target_id": "<string>",

  // The action that should be performed by the receiver the target.
  // The types of actions supported are defined by a given receiver.
  "action": "<string>",

  // Additional keys can be present in this content dict, and will
  // be defined by the given action and receiver.
}

// "enaml_request"
// ---------------
// This type of message is created when an object needs to request data
// from another object. The originator of the message expects to receive
// an "enaml_reply" message at some point in the future. 
//
// The "content" of this message type is as follows.
{
  // The target of the message. This uniquely identifies the receiver of
  // the message in an Enaml application.
  "target_id": "<string>",

  // The requestor of the message. This uniquely identifies the object
  // which originated the action. This value must be used as the "target_id"
  // in the content of the corresponding "enaml_reply" message.
  "originator_id": "<string>",

  // The action that should be performed by the receiver the target.
  // The types of actions supported are defined by a given receiver.
  "action": "<string>",

  // Additional keys can be present in this content dict, and will
  // be defined by the given action and receiver.
}


// "enaml_reply"
// -------------
// This type of message is created in response to an "enaml_request". It
// is used to deliver a response to the object which made the original
// request. The order in which messages of this type are generated is
// not guaranteed.
//
// The "content" of this message type is as follows:
{
  // The target of the message. This will be the same as the value for
  // "originator_id" in the associated "enaml_request" message.
  "target_id": "<string>",

  // This will be the same value as the "action" field in the
  // associated "enaml_request".
  "action": "<string>",
  
  // Additional keys can be present in this content dict, and will
  // be defined by the reciever and action in the associated
  // "enaml_request" which generated this reply.
}

