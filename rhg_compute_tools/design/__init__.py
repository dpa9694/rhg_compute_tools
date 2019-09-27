
from __future__ import absolute_import

from rhg_compute_tools.design.colors import _load_colors
from rhg_compute_tools.design.plotting import (
    get_color_scheme,
    add_colorbar)

_load_colors()

# import matplotlib.font_manager as fm
#
# RHG_FONTS = [
#
#     # rhodium v1
#     # ('Univers LT', 'ttf'),
#     # ('Knockout', 'ttf'),
#
#     # rhodium 2019
#     ('Fira Sans', 'ttf'),
#     # ('DIN Pro', 'ttf'),
#     # ('CamingoDos', 'ttf'),
#     #
#     # # impactlab
#     # ('Chaparral Pro', 'ttf'),
#     # ('Merriweather', 'ttf'),
#     ]
#
# for (sysfont, ext) in RHG_FONTS:
#     fm.findfont(sysfont, fontext=ext, rebuild_if_missing=False)

from matplotlib.font_manager import _rebuild
_rebuild()

__all__ = ['get_color_scheme', 'add_colorbar']
