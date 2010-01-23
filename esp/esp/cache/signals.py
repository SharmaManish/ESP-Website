
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2008 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: nu-websupport@lists.learningu.org
"""
__all__ = ['table_dirty', 'cache_deleted']


from django.dispatch import Signal

### not used
### # TODO: Is it worth it making it specify changed fields? How common is this sort of thing?
### """ Emitted when the entire table should be considered dirty. i.e. every field of every row could potentially be changed. """
### table_dirty = Signal()

""" Emitted when a cache is deleted. """
cache_deleted = Signal(providing_args=[]) # DON'T FORGOT TO SPECIFY THESE AT SOME POINT...

""" Emitted when an M2M entry is added. """
m2m_added = Signal(providing_args=['instance', 'field', 'object'])

""" Emitted when an M2M entry is removed. """
m2m_removed = Signal(providing_args=['instance', 'field', 'object'])
