# Copyright (c) 2019 Sean Vig

from pywayland.server import Display

from . import ffi, lib
from wlroots.backend import Backend


class Renderer:
    def __init__(self, backend: Backend, display: Display) -> None:
        """Obtains the renderer this backend is using

        The renderer is automatically destroyed as the backend is destroyed.

        :param backend:
            The wlroots backend to get the renderer for.
        :param display:
            The Wayland display to initialize the renderer against.
        """
        self._ptr = lib.wlr_backend_get_renderer(backend._ptr)
        lib.wlr_renderer_init_wl_display(self._ptr, display._ptr)

    def begin(self, width: int, height: int) -> None:
        """Begin rendering with the given height and width"""
        lib.wlr_renderer_begin(self._ptr, width, height)

    def clear(self, color) -> None:
        """Clear the renderer to the given RGBA color"""
        color_ptr = ffi.new("float[4]", color)
        lib.wlr_renderer_clear(self._ptr, color_ptr)

    def end(self):
        """Finish rendering"""
        lib.wlr_renderer_end(self._ptr)
