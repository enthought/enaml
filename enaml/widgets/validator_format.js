//-----------------------------------------------------------------------------
// Copyright (c) 2012, Enthought, Inc.
// All rights reserved.
//-----------------------------------------------------------------------------
//
//     JSON does not allow comments, so this file is marked as js.
//     However, it is describing a JSON specification
//
//-----------------------------------------------------------------------------
// Validator Format
//-----------------------------------------------------------------------------
// This describes the format for specifying a validator which validates
// user text input. The format is intentionally loose so that it may
// scale with new requirements as dictated by future use cases.
{
  // The type of this validator. The validator type largely dictate what
  // other properties are supported by the validator. This field is
  // required.
  "type": "<string>",

  // The message which should be displayed by the control when the 
  // validator fails. The means by which this message is displayed,
  // or whether it is displayed at all, is implementation defined.
  // This field is optional. If a message is provided, it must be a 
  // string.
  "message": "<string>",

  // The behaviors which should cause the control to run the validator.
  // This field is optional. If triggers are provided, they should be
  // an array of strings. The acceptable trigger strings are defined by
  // a given control. If no triggers are provided, it is assumed that 
  // the control has provided another method of running the validator.
  "triggers": ["<string>"],

  // XXX calling it a stylesheet for now, unless we decide against them.
  // The style overrides to apply to the control when validation fails.
  // This field is optional. If a stylesheet is provided, it must be
  // a string. 
  "stylesheet": "<string>",

  // XXX calling it a stylesheet for now, unless we decide against them.
  // The style to apply to the failure message display. The styles 
  // supported by the message are control and implementation defined.
  // This field is optional. If a stylesheet is provided, it must be
  // a string.
  "message_stylesheet": "<string>",
}


//-----------------------------------------------------------------------------
// Currently Supported Validators
//-----------------------------------------------------------------------------
{
  // The null validator accepts all input as valid.
  "type": "null",
}


{
  // The regexp validator uses a regex for validation.
  "type": "regexp",

  // The regex string to use for validating the text. The regex format
  // follows Python's regex rules. Only text which matches the regex
  // is considered valid. This field is required.
  "regexp": "<string>",
}

