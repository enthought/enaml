#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum


#: A dialog's result (depending on how it was closed)
#:
#: ============ ===============================================
#: value        description
#: ============ ===============================================
#: ``accepted`` The user accepted the dialog.
#: ``rejected`` (default) The user declined the default result.
#: ============ ===============================================
DialogResult = Enum(('rejected', 'accepted'))

#: Generic orientation values.
#:
#: ============== ======================
#: value          description
#: ============== ======================
#: ``horizontal`` Horizontal orientation
#: ``vertical``   Vertical orientation
#: ============== ======================
Orientation = Enum(('horizontal', 'vertical'))

#: The position of the tabs in a Tabbed container.
#:
#: ========== =====================================================
#: value      description
#: ========== =====================================================
#: ``top``    (default) Place tabs above the main content.
#: ``bottom`` Place tabs below the main content.
#: ``left``   Place tabs to the left of the main content.
#: ``right``  Place tabs to the right of the main content.
#: ========== =====================================================
TabPosition = Enum(('top', 'bottom', 'left', 'right'))


#: Horizontal alingment.
#:
#: ========== =====================================================
#: value      description
#: ========== =====================================================
#: ``left``   (default) Align left
#: ``right``  Align right
#: ``center`` Align center
#: ========== =====================================================
HorizontalAlign = Enum(('left', 'right', 'center'))


#: A container's layout style, based on the order of insertion.
#:
#: ================= ===============================================
#: value             description
#: ================= ===============================================
#: ``left_to_right`` (default) Position children from left to right.
#: ``right_to_left`` Position children from right to left.
#: ``top_to_bottom`` Position children from top to bottom.
#: ``bottom_to_top`` Position children from bottom to top.
#: ================= ===============================================
Direction = Enum(('left_to_right', 'right_to_left', 
                  'top_to_bottom', 'bottom_to_top'))

#: A window's modality specifies whether it captures focus.
#:
#: ===================== =================================================
#: value                 description
#: ===================== =================================================
#: ``non_modal``         (default) The window is not modal.
#: ``window_modal``      The window blocks input to its parent, and all
#:                       ancestor windows.
#: ``application_modal`` The window blocks input to all other windows in
#:                       the application.
#: ===================== =================================================
Modality = Enum(('application_modal', 'window_modal'))

#: The position of ticks for a control.
#:
#: ============= =========================================================
#: value         description
#: ============= =========================================================
#: ``not_ticks`` (default) Do not display ticks.
#: ``left``      Display ticks to the left of the element.
#: ``right``     Display ticks to the right of the element.
#: ``top``       Display ticks above the element.
#: ``bottom``    Display ticks below the element.
#: ``both``      Display ticks both above the element and below it, or to
#:               both the left and the right. This might vary with
#:               :attr:`Orientation`.
#: ============= =========================================================
TickPosition = Enum(('no_ticks', 'left', 'right', 'top', 'bottom', 'both'))

#: The ordering of a sort.
#:
#: ============== =====================================
#: value          description
#: ============== =====================================
#: ``ascending``  Elements will be in ascending order.
#: ``descending`` Elements will be in descending order.
#: ============== =====================================
Sorted = Enum(('ascending', 'descending'))

#: The result of a validation function.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``invalid``      The input was clearly invalid.
#: ``indermediate`` The input is invalid, but further input could make it
#:                  valid.
#: ``acceptable``   The input is valid.
#: ================ ======================================================
Validity = Enum(('invalid', 'indermediate', 'acceptable'))

#: The strength of widget expand and clip preferences for hug and resist_clip.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``ignore``       No constraint shuld be created.
#: ``weak``         The constraint should be created, but is weak.
#: ``strong``       The constraint should be created, but is strong.
#: ``required``     The constraint should be created, and is required.
#: ================ ======================================================
PolicyEnum = Enum(('ignore', 'weak', 'strong', 'required'))

#: The selection mode for item views.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``extended``     Same as contiguous except that the Cmd key can be
#:                  used to start multiple non-contiguous selection
#:                  regions.
#: ``single``       A single item may be selection.
#: ``contiguous``   A contiguous range of items may be selected using the
#:                  Shift key.
#: ``multi``        Clicking on an item toggles its selection.
#: ``none``         No selection allowed.
#: ================ ======================================================
SelectionMode = Enum(('extended', 'contiguous', 'single', 'multi', 'none'))

#: What kind of items may be selected in item views.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``items``        Individual items, like table cells.
#: ``rows``         Only whole rows, not individual table cells.
#: ``columns``      Only whole columns, not individual table cells.
#: ================ ======================================================
SelectionBehavior = Enum(('items', 'rows', 'columns'))


#: Exactly what actions to do when programmatically setting the selection in
#: item views.
#:
#: ==================== ======================================================
#: value                description
#: ==================== ======================================================
#: ``no_update``        Make no selection.
#: ``clear``            Clear the complete selection.
#: ``select``           Select the specified indices.
#: ``deselect``         Deselect the specified indices.
#: ``toggle``           Toggle the selection of the specified indices.
#: ``current``          Update the "current" index.
#: ``rows``             Expand the selection to span rows.
#: ``columns``          Expand the selection to span columns.
#: ``select_current``   Select the given selection and update the "current"
#:                      index.
#: ``toggle_current``   Toggle the given selection and update the "current"
#:                      index.
#: ``clear_select``     Clear the whole selection and select the given
#:                      indices.
#: ==================== ======================================================
SelectionCommand = Enum((
    'clear_select', 'no_update', 'clear', 'select', 'deselect', 'toggle', 
    'current', 'rows', 'columns', 'select_current', 'toggle_current',
))

