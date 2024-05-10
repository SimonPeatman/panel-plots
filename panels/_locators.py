"""Definitions of panel locators."""
# Copyright 2017 Andrew Dawson
#
# This file is part of panel-plots.
#
# panel-plots is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# panel-plots is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with panel-plots.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

from itertools import product
import warnings
import collections.abc

from ._units import convert_units


class PanelSizeLocator(object):
    """A panel locator based on panel size."""

    def __init__(self, rows, columns, panelwidth, panelheight,
                 hsep=0, vsep=0, padleft=0, padright=0, padtop=0,
                 padbottom=0, units='mm'):
        """
        Initialize a locator based on panel size. The sizes can be
        specified in arbitrary units of length specified via the `units`
        keyword.

        Arguments:

        * rows, columns: int
            The number of rows and columns making up the figure.

        * panelwidth, panelheight: float
            The width and height of the panels making up the figure.

        Keyword arguments:

        * hsep (default=0): float or sequence of floats
            The horizontal spacing between each panel and neighbouring
            panels in the same row. A sequence must have a length of one
            shorter than the number of columns.

        * vsep (default=0): float or sequence of floats
            The vertical spacing between each panel and neighbouring
            panels in the same column. A sequence must have a length of one
            shorter than the number of rows.

        * padleft (default=0): float
            The spacing between the left edge of the figure and the left
            edge of the first column of panels.

        * padright (default=0): float
            The spacing between the right edge of the figure and the
            right edge of the last column of panels.

        * padtop (default=0): float
            The spacing between the top edge of the figure and the top
            edge of the first row of panels.

        * padbottom (default=0): float
            The spacing between the bottom edge of the figure and the
            bottom edge of the last row of panels.

        * units (default='mm'): str
            The units of measure the other arguments are specified in.
            This can be one of 'mm', 'cm', or 'inches'.

        """
        self.rows, self.columns = rows, columns
        self.panelwidth = panelwidth
        self.panelheight = panelheight
        if isinstance(hsep, collections.abc.Sequence):
            if len(hsep) != columns - 1:
                raise ValueError('If hsep is a sequence, it must have one fewer'
                                 ' value than the number of columns')
            self.hsep = hsep
        else:
            self.hsep = [hsep] * (columns - 1)
        if isinstance(vsep, collections.abc.Sequence):
            if len(vsep) != rows - 1:
                raise ValueError('If vsep is a sequence, it must have one fewer'
                                 ' value than the number of rows')
            self.vsep = vsep
        else:
            self.vsep = [vsep] * (rows - 1)
        self.padleft = padleft
        self.padright = padright
        self.padtop = padtop
        self.padbottom = padbottom
        self.units = units
        self.figwidth = (self.padleft + self.columns * self.panelwidth +
                         sum(self.hsep) + self.padright)
        self.figheight = (self.padtop + self.rows * self.panelheight +
                          sum(self.vsep) + self.padbottom)
        self.panelwidth_fig = self.panelwidth / self.figwidth
        self.panelheight_fig = self.panelheight / self.figheight

    @property
    def figsize(self):
        """The figure size (width, height) in inches."""
        return self.figsize_in('inches')

    def figsize_in(self, units):
        """
        Returns the figure size (width, height) in a specified unit.

        Argument:

        * units: string
            The units of measure the figure size should be returned in.
            This can be one of 'mm', 'cm', or 'inches'.

        """
        return (convert_units(self.figwidth, self.units, units),
                convert_units(self.figheight, self.units, units))

    def panel_position_iterator(self, order='row'):
        """
        Returns a generator of panel positions.

        Keyword argument:

        * order (default='row'): str
            The order in which panels are iterated over. Accepted values
            are "row" for row-major order (columns then rows), or
            "column" for column-major order (rows then columns).

        """
        row_gen = range(self.rows)
        col_gen = range(self.columns)
        try:
            i0, i1, g0, g1 = {'row': (0, 1, row_gen, col_gen),
                              'column': (1, 0, col_gen, row_gen)}[order]
        except KeyError:
            raise ValueError('the order keyword must be either "row" or "column"')
        return (self.panel_position(x[i0], x[i1]) for x in product(g0, g1))

    def panel_position(self, row, column):
        """
        Returns the matplotlib-style (x, y, width, height) position of
        a panel in figure coordinates.

        Arguments:

        row, column: integer
           The row and column indices of the panel, where indices start at
           0 in the top-left.

        """
        x = self.padleft + self.panelwidth * column + sum(self.hsep[:column])
        y = (self.figheight - self.padtop -
             self.panelheight * (row + 1) - sum(self.vsep[:row]))
        x_fig = x / self.figwidth
        y_fig = y / self.figheight
        return (x_fig, y_fig, self.panelwidth_fig, self.panelheight_fig)


class FigureSizeLocator(PanelSizeLocator):
    """A panel locator based on total figure size."""

    def __init__(self, rows, columns, figwidth=None, figheight=None,
                 panelratio=None, hsep=0, vsep=0, padleft=0, padright=0,
                 padtop=0, padbottom=0, units='mm'):
        """
        Initialize a locator based on total figure size. The sizes can
        be specified in arbitrary units of length specified via the
        `units` keyword. You must at a minimum specify the width or the
        height of the figure.

        Arguments:

        * rows, columns: int
            The number of rows and columns making up the figure.

        Keyword arguments:

        * figwidth (no default): float
            The total width of the figure.

        * figheight (no default): float
            The total height of the figure.

        * panelratio (default=1): float
            The width/height ratio for panel sizes. This argument is
            used to determine the panel size when only one of the
            `figwidth` or `figheight` keyword arguments is present. If
            both the `figwidth` and `figheight` keyword arguments are
            given then `panelratio` will be ignored.

        * hsep (default=0): float or sequence of floats
            The horizontal spacing between each panel and neighbouring
            panels in the same row. A sequence must have a length of one
            shorter than the number of columns.

        * vsep (default=0): float or sequence of floats
            The vertical spacing between each panel and neighbouring
            panels in the same column. A sequence must have a length of one
            shorter than the number of rows.

        * padleft (default=0): float
            The spacing between the left edge of the figure and the left
            edge of the first column of panels.

        * padright (default=0): float
            The spacing between the right edge of the figure and the
            right edge of the last column of panels.

        * padtop (default=0): float
            The spacing between the top edge of the figure and the top
            edge of the first row of panels.

        * padbottom (default=0): float
            The spacing between the bottom edge of the figure and the
            bottom edge of the last row of panels.

        * units (default='mm'): str
            The units of measure the other arguments are specified in.
            This can be one of 'mm', 'cm', or 'inches'.

        """
        # Compute the panel size that fits with the figure size specification:
        panelwidth, panelheight = self.panel_size(
            rows, columns, figwidth=figwidth, figheight=figheight,
            panelratio=panelratio, hsep=hsep, vsep=vsep, padleft=padleft,
            padright=padright, padtop=padtop, padbottom=padbottom)
        # Call the PanelSizeLocator constructor:
        super(FigureSizeLocator, self).__init__(
            rows, columns, panelwidth, panelheight, hsep=hsep, vsep=vsep,
            padleft=padleft, padright=padright, padtop=padtop,
            padbottom=padbottom, units=units)

    @staticmethod
    def panel_size(rows, columns, figwidth=None, figheight=None,
                   panelratio=None, hsep=0, vsep=0, padleft=0, padright=0,
                   padtop=0, padbottom=0):
        """
        Determine panel sizes for a fixed figure size.

        Arguments:

        * rows, columns: int
            The number of rows and columns making up the figure.

        Keyword arguments:

        * figwidth (no default): float
            The total width of the figure.

        * figheight (no default): float
            The total height of the figure.

        * panelratio (default=1): float
            The width/height ratio for panel sizes. This argument is
            used to determine the panel size when only one of the
            `figwidth` or `figheight` keyword arguments is present. If
            both the `figwidth` and `figheight` keyword arguments are
            given then `panelratio` will be ignored.

        * hsep (default=0): float or sequence of floats
            The horizontal spacing between each panel and neighbouring
            panels in the same row. A sequence must have a length of one
            shorter than the number of columns.

        * vsep (default=0): float or sequence of floats
            The vertical spacing between each panel and neighbouring
            panels in the same column. A sequence must have a length of one
            shorter than the number of rows.

        * padleft (default=0): float
            The spacing between the left edge of the figure and the left
            edge of the first column of panels.

        * padright (default=0): float
            The spacing between the right edge of the figure and the
            right edge of the last column of panels.

        * padtop (default=0): float
            The spacing between the top edge of the figure and the top
            edge of the first row of panels.

        * padbottom (default=0): float
            The spacing between the bottom edge of the figure and the
            bottom edge of the last row of panels.

        """
        if figwidth is None and figheight is None:
            raise ValueError('one or both of the "figwidth" and "figheight" '
                             'keywords must be used')
        if isinstance(hsep, collections.abc.Sequence):
            if len(hsep) != columns - 1:
                raise ValueError('If hsep is a sequence, it must have one fewer'
                                 ' value than the number of columns')
        else:
            hsep = [hsep] * (columns - 1)
        if isinstance(vsep, collections.abc.Sequence):
            if len(vsep) != rows - 1:
                raise ValueError('If vsep is a sequence, it must have one fewer'
                                 ' value than the number of rows')
        else:
            vsep = [vsep] * (rows - 1)
        if figwidth is not None and figheight is not None:
            # Both width and height are prescribed, choose the panel size
            # appropriately (ignoring any specified aspect ratio):
            if panelratio is not None:
                msg = ('the "panelratio" keyword is ignored when both the '
                       '"figwidth" and "figheight" keywords are used')
                warnings.warn(msg)
            panelwidth = (figwidth - sum(hsep) - padleft -
                          padright) / float(columns)
            panelheight = (figheight - sum(vsep) - padtop -
                           padbottom) / float(rows)
            if panelwidth <=0 or panelheight <= 0:
                msg = ('the specified dimensions are not large enough to'
                       'locate panels with the desired separation and padding')
                raise ValueError(msg)
        elif figwidth is None:
            # Only the figure height is prescribed, choose the panel height
            # appropriately and determine the panel width from the aspect
            # ratio:
            panelheight = (figheight - sum(vsep) - padtop -
                           padbottom) / float(rows)
            if panelheight <= 0:
                msg = ('the specified figure height is not tall enough to '
                       'locate panels with the desired separation and padding')
                raise ValueError(msg)
            panelwidth = panelheight * (panelratio or 1.)
        elif figheight is None:
            # Only the figure width is prescribed, choose the panel width
            # appropriately and determine the panel height from the aspect
            # ratio:
            panelwidth = (figwidth - sum(hsep) - padleft -
                          padright) / float(columns)
            if panelwidth <= 0:
                msg = ('the specified figure width is not wide enough to '
                       'locate panels with the desired separation and padding')
                raise ValueError(msg)
            panelheight = panelwidth / (panelratio or 1.)
        return panelwidth, panelheight
