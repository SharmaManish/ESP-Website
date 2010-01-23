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

# Configure Django to support ESP
from django_settings import *

# Import system-specific settings
from local_settings import *

############################################

# compute some derived settings
MEDIA_ROOT = PROJECT_ROOT + MEDIA_ROOT_DIR

MANAGERS = ADMINS

TEMPLATE_DIRS = (
    PROJECT_ROOT+'templates',
)

#CACHE_BACKEND = "esp.utils.memcached_multikey://174.129.184.116:11211/?timeout=%d" % DEFAULT_CACHE_TIMEOUT
CACHE_BACKEND = "esp.utils.memcached_multikey://127.0.0.1:11211/?timeout=%d" % DEFAULT_CACHE_TIMEOUT

MIDDLEWARE_CLASSES = [pair[1] for pair in sorted(MIDDLEWARE_GLOBAL + MIDDLEWARE_LOCAL)]

# set tempdir so that we don't have to worry about collision
import tempfile
import os
if not getattr(tempfile, 'alreadytwiddled', False): # Python appears to run this multiple times
    tempdir = os.path.join(tempfile.gettempdir(), "esptmp__" + CACHE_PREFIX)
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    tempfile.tempdir = tempdir
    tempfile.alreadytwiddled = True
