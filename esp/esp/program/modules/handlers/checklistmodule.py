
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
from esp.program.modules.base import ProgramModuleObj, needs_teacher, needs_student, needs_admin, usercheck_usetl, main_call, aux_call
from esp.program.modules import module_ext
from esp.program.models  import Program, ProgramCheckItem
from esp.web.util        import render_to_response
from esp.datatree.models import *
from django.contrib.auth.decorators import login_required
from django.db.models.query import Q
from esp.datatree.models import *
from esp.users.models import ESPUser, User
from django.http import HttpResponseRedirect

class CheckListModule(ProgramModuleObj):
    doc = """
    If you want to manage those checklists that your program sees, come here.
    """

    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Managing Checklist Items",
            "link_title": "CheckList Management",
            "module_type": "manage",
            "seq": 1000
            }

    @main_call
    @needs_admin
    def managecheckitems(self, request, tl, one, two, module, extra, prog):
        return HttpResponseRedirect('/admin/program/programcheckitem/')


    def teachers(self, QObject = False):
        teaching = GetNode('V/Flags/Registration/Teacher')

        finish_dict = {}

        for check_item in self.program.checkitems.all():
            finish_dict['checkitem_%s' % check_item.id] = \
                     Q(userbit__qsc__classsubject__checklist_progress = check_item) &\
                     Q(userbit__verb = teaching) & \
                     Q(userbit__qsc__classsubject__parent_program = self.program)

        if QObject:
            return finish_dict

        for k,v in finish_dict.items():
            finish_dict[k] = User.objects.filter(v)

        return finish_dict

    def teacherDesc(self):
        finish_dict = {}

        for check_item in self.program.checkitems.all():
            finish_dict['checkitem_%s' % check_item.id] = \
                     "Teachers teaching a class flagged with '%s'" % check_item.title

        return finish_dict
