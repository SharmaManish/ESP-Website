
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

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
from esp.users.models import ESPUser
from django.template import Context, Template, loader, RequestContext
import django.shortcuts
from django.conf import settings
from django.http import HttpResponse
from esp.program.models import Program
from esp.qsd.models import ESPQuotations
from esp.middleware import ESPError

def get_from_id(id, module, strtype = 'object', error = True):
    """ This function will get an object from its id, and return an appropriate error if need be. """
    from esp.users.models import ESPUser

    try:
        newid    = int(id)
        foundobj = module.objects.get(id = newid)
        if module == ESPUser:
            foundobj = ESPUser(foundobj)
    except:
        if error:
            raise ESPError(False), 'Could not find the %s with id %s.' % (strtype, id)
        return None
    return foundobj
    

def render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return django.shortcuts.render_to_response(*args, **kwargs)


def render_to_response(template, requestOrContext, prog = None, context = None):
    from esp.web.views.navBar import makeNavBar


    # if there are only two arguments
    if context is None and prog is None:
        return django.shortcuts.render_to_response(template, requestOrContext, Context({'navbar_list': []}))
    
    if context is not None:
        request = requestOrContext

        section = ''

        if type(prog) == tuple:
            section = prog[1]
            prog = prog[0]

        if not context.has_key('program'):  
            if type(prog) == Program:
                context['program'] = prog
                
        # create nav bar list
        if not context.has_key('navbar_list'):
            category = None
            if context.has_key('nav_category'):
                category = context['nav_category']
            if prog is None:
                context['navbar_list'] = []
            elif type(prog) == Program:
                context['navbar_list'] = makeNavBar(request.user, prog.anchor, section, category)
            else:
                context['navbar_list'] = makeNavBar(request.user, prog, section, category)

        return render_response(request, template, context)
        
    assert False, 'render_to_response expects 2 or 4 arguments.'

