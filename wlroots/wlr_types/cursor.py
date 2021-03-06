# Copyright (c) Sean Vig 2019

from typing import Optional

from pywayland.server import Signal

from wlroots import ffi, lib
from .output_layout import OutputLayout
from .input_device import InputDevice, InputDeviceType
from .pointer import (
    PointerEventAxis,
    PointerEventButton,
    PointerEventMotion,
    PointerEventMotionAbsolute,
)


class Cursor:
    def __init__(self, output_layout: OutputLayout) -> None:
        """Manage a cursor attached to the given output layout

        Uses the given layout to establish the boundaries and movement
        semantics of this cursor. Cursors without an output layout allow
        infinite movement in any direction and do not support absolute input
        events.

        :param output_layout:
            The output layout to attach the cursor to and bound the cursor by.
        """
        ptr = lib.wlr_cursor_create()
        self._ptr = ffi.gc(ptr, lib.wlr_cursor_destroy)
        lib.wlr_cursor_attach_output_layout(self._ptr, output_layout._ptr)

        self.motion_event = Signal(
            ptr=ffi.addressof(self._ptr.events.motion), data_wrapper=PointerEventMotion
        )
        self.motion_absolute_event = Signal(
            ptr=ffi.addressof(self._ptr.events.motion_absolute),
            data_wrapper=PointerEventMotionAbsolute,
        )
        self.button_event = Signal(
            ptr=ffi.addressof(self._ptr.events.button), data_wrapper=PointerEventButton
        )
        self.axis_event = Signal(
            ptr=ffi.addressof(self._ptr.events.axis), data_wrapper=PointerEventAxis
        )
        self.frame_event = Signal(ptr=ffi.addressof(self._ptr.events.frame))

    def destroy(self) -> None:
        """Clean up the cursor"""
        if self._ptr is not None:
            ffi.release(self._ptr)
            self._ptr = None

    def attach_input_device(self, input_device: InputDevice) -> None:
        """Attaches this input device to this cursor

        The input device type must be one of:
            - InputDeviceType.POINTER
            - InputDeviceType.TOUCH
            - InputDeviceType.TABLET_TOOL

        :param input_device:
            The input device to attach to the cursor
        """
        allowed_device_types = (
            InputDeviceType.POINTER,
            InputDeviceType.TOUCH,
            InputDeviceType.TABLET_TOOL,
        )
        if input_device.device_type not in allowed_device_types:
            raise ValueError(
                "Input device must be one of pointer, touch, or tablet tool, got: {}".format(
                    input_device.device_type
                )
            )

        lib.wlr_cursor_attach_input_device(self._ptr, input_device._ptr)

    def warp_absolute(
        self, input_device: Optional[InputDevice], x: float, y: float
    ) -> None:
        """Warp the cursor to the given x and y in absolute coordinates

        If the given point is out of the layout boundaries or constraints, the
        closest point will be used. If one coordinate is NAN, it will be
        ignored.

        The `input_device` may be passed to respect device mapping constraints.
        If `input_device` is None, device mapping constraints will be ignored.
        """
        if input_device is None:
            input_device_ptr = ffi.NULL
        else:
            input_device_ptr = input_device._ptr

        lib.wlr_cursor_warp_absolute(self._ptr, input_device_ptr, x, y)

    def __enter__(self) -> "Cursor":
        """Context manager to clean up the cursor"""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Clean up the cursor when exiting the context"""
        self.destroy()
