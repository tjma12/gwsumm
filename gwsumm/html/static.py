# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2016)
#
# This file is part of GWSumm.
#
# GWSumm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWSumm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWSumm.  If not, see <http://www.gnu.org/licenses/>.

"""HTML <head> helphers

This module mainly declares the resources used by standard on HTML pages
"""

from collections import OrderedDict

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__credits__ = 'Alex Urban <alexander.urban@ligo.org>'


STATICDIR = 'html/static'

# build collection of CSS resources
CSS = OrderedDict((
    ('font-awesome', 'https://cdnjs.cloudflare.com/ajax/libs/'
                     'font-awesome/5.11.2/css/fontawesome.min.css'),
    ('font-awesome-solid', 'https://cdnjs.cloudflare.com/ajax/libs/'
                           'font-awesome/5.11.2/css/solid.min.css'),
    ('gwbootstrap', 'https://cdn.jsdelivr.net/npm/gwbootstrap@1.2.1/'
                    'lib/gwbootstrap.min.css'),
))

# build collection of javascript resources
JS = OrderedDict((
    ('jquery', 'https://code.jquery.com/jquery-3.4.1.min.js'),
    ('jquery-ui', 'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js'),
    ('moment', 'https://cdnjs.cloudflare.com/ajax/libs/'
               'moment.js/2.24.0/moment.min.js'),
    ('bootstrap', 'https://stackpath.bootstrapcdn.com/bootstrap/'
                  '4.4.1/js/bootstrap.bundle.min.js'),
    ('fancybox', 'https://cdnjs.cloudflare.com/ajax/libs/'
                 'fancybox/3.5.7/jquery.fancybox.min.js'),
    ('datepicker', 'https://cdnjs.cloudflare.com/ajax/libs/'
                   'bootstrap-datepicker/1.9.0/js/'
                   'bootstrap-datepicker.min.js'),
    ('gwbootstrap', 'https://cdn.jsdelivr.net/npm/gwbootstrap@1.2.1/'
                    'lib/gwbootstrap-extra.min.js'),
))


# -- utilities ----------------------------------------------------------------

def get_css():
    """Return a `dict` of CSS files to link in the HTML <head>
    """
    return CSS


def get_js():
    """Return a `dict` of javascript files to link in the HTML <head>
    """
    return JS
