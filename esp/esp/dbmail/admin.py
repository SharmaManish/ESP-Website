
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
Email: nw-websupport@lists.learningu.org
"""
from django.contrib import admin

from esp.dbmail.models import MessageVars, EmailList, PlainRedirect, MessageRequest, TextOfEmail


class MessageVarsAdmin(admin.ModelAdmin):
    pass
admin.site.register(MessageVars, MessageVarsAdmin)

class EmailListAdmin(admin.ModelAdmin):
    list_display = ('description', 'regex')
    pass
admin.site.register(EmailList, EmailListAdmin)
    
class PlainRedirectAdmin(admin.ModelAdmin):
    list_display = ('original', 'destination')
    pass
admin.site.register(PlainRedirect, PlainRedirectAdmin)

class MessageRequestAdmin(admin.ModelAdmin):
    pass
admin.site.register(MessageRequest, MessageRequestAdmin)

class TextOfEmailAdmin(admin.ModelAdmin):
    pass
admin.site.register(TextOfEmail, TextOfEmailAdmin)
