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
  
  // Different types of validators may require additional items to
  // be provided beyond these two.
  
  // Styling for invalid entries and the associated messages will be
  // specified by virtual states in the widget stylesheet, once they
  // are implemented.
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
  "type": "regex",

  // The regex string to use for validating the text. The regex format
  // follows Python's regex rules. Only text which matches the regex
  // is considered valid. This field is required.
  "regex": "<string>",
}

