
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
copyright (c) 2007 MIT ESP

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
from esp.web.util import render_to_response
from esp.qsd.models import QuasiStaticData
from esp.qsd.forms import QSDMoveForm, QSDBulkMoveForm
from esp.datatree.models import *
from django.http import HttpResponseRedirect, Http404
from django.core.mail import send_mail
from esp.users.models import ESPUser, UserBit, GetNodeOrNoBits, admin_required

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models.query import Q
from django.core.mail import mail_admins
from django.core.cache import cache

from esp.program.models import Program, TeacherBio
from esp.program.forms import ProgramCreationForm
from esp.program.setup import prepare_program, commit_program
from esp.accounting_docs.models import Document
from esp.middleware import ESPError
from esp.accounting_core.models import LineItemType, CompletedTransactionException

import pickle
import operator

def find_user(userstr):
    """
    Do a best-guess effort at finding a user based on a string identifying that user.
    The string may be a user ID, username, or some permuation of the user's real name.
    Will return a list of users if the string is not a username and more than one
    name approximately matches.
    Will return something that evaluates to False iff no matching users are found.
    """
    # First, is this a User ID?
    try:
        found_user = ESPUser.objects.get(id=int(userstr))
        return found_user
    except ValueError:
        pass # Well, that wasn't even an integer; can't be an ID
    except ESPUser.DoesNotExist:
        pass # Well, maybe it is an integer, but it's not a valid user ID.

    # Second, is it a username?
    try:
        found_user = ESPUser.objects.get(username=userstr)
        return found_user
    except ESPUser.DoesNotExist:
        pass # Well, not a username either.  Oh well.

    # Third, try e-mail?
    if '@' in userstr:  # but don't even bother hitting the DB if it doesn't even have an '@'
        try:
            found_user = ESPUser.objects.get(email=userstr)
            return found_user
        except ESPUser.DoesNotExist:
            pass # Well, not a username either.  Oh well.

    # Maybe it's a name?
    # Let's do some playing.

    # Is it multipart?        
    # If so, we don't know which parts got filed under first name and
    # which under last name.
    # So, try them all!
    # First, try for an exact match (ie., all parts of the firstname, lastname pair are somewhere in the given string)
    userstr_parts = userstr.split(' ')

    # First, try single-part, since it's easier
    if len(userstr_parts) == 1:
        found_users = ESPUser.objects.filter(Q(first_name__iexact=userstr) | Q(last_name__iexact=userstr))
        if len(found_users) == 1:
            return found_users[0]
        elif len(found_users) > 1:
            return found_users

        found_users = ESPUser.objects.filter(Q(first_name__icontains=userstr) | Q(last_name__icontains=userstr))
        if len(found_users) == 1:
            return found_users[0]
        elif len(found_users) > 1:
            return found_users
        
    q_list = []
    for i in xrange(len(userstr_parts) + 1):
        q_list.append( Q( first_name__iexact = ' '.join(userstr_parts[:i]), last_name__iexact = ' '.join(userstr_parts[i:]) ) )

    # Allow any of the above permutations
    q = reduce(operator.or_, q_list)
    found_users = ESPUser.objects.filter( q )
    if len(found_users) == 1:
        return found_users[0]
    elif len(found_users) > 1:
        return found_users
    # else, we found no one.  Oops.

    # Now, repeat the same thing, but with "contains" so we match some nicknames and whatnot
    
    q_list = []
    for i in xrange(len(userstr_parts)):
        q_list.append( Q( first_name__icontains = ' '.join(userstr_parts[:i]), last_name__icontains = ' '.join(userstr_parts[i:]) ) )
    # Allow any of the above permutations
    q = reduce(operator.or_, q_list)
    found_users = ESPUser.objects.filter( q )
    if len(found_users) == 1:
        return found_users[0]
    elif len(found_users) > 1:
        return found_users
    # else, we found no one.  Oops.

    # Well, we fail.  Sorry.
    return None

def isiterable(i):
    """ returns true iff i is iterable """
    try:
        for x in i:
            return True
    except TypeError:
        return False

@admin_required
def usersearch(request):
    """
    Given a string that's somehow associated with a user,
    do our best to find that user.
    Either redirect to that user's "userview" page, or
    display a list of users to pick from."""
    if not request.GET.has_key('userstr'):
        raise ESPError(False), "You didn't specify a user to search for!"
                               
    userstr = request.GET['userstr']
    found_users = find_user(userstr)

    if not found_users:
        raise ESPError(False), "No user found by that name!"

    if isiterable(found_users):
        return render_to_response('users/userview_search.html', request, GetNode("Q/Web"), { 'found_users': found_users })
    else:
        from urllib import urlencode
        return HttpResponseRedirect('/manage/userview?%s' % urlencode({'username': found_users.username}))

@admin_required
def userview(request):
    """ Render a template displaying all the information about the specified user """
    try:
        user = ESPUser.objects.get(username=request.GET['username'])
    except:
        raise ESPError(False), "Sorry, can't find anyone with that username."

    teacherbio = TeacherBio.getLastBio(user)
    if not teacherbio.picture:
        teacherbio.picture = 'uploaded/not-available.jpg'
    
    return render_to_response("users/userview.html", request, GetNode("Q/Web"), { 'user': user, 'teacherbio': teacherbio } )
    
def programTemplateEditor(request):
    """ Generate and display a listing of all QSD pages in the Programs template
    (QSD pages that are created automatically when a new program is created) """
    qsd_pages = []

    template_node = GetNode('Q/Programs/Template')

    for qsd in template_node.quasistaticdata_set.all():
        qsd_pages.append( { 'edit_url': qsd.name + ".edit.html",
                            'view_url': qsd.name + ".html",
                            'page': qsd } )

    have_create = UserBit.UserHasPerms(request.user, template_node, GetNode('V/Administer/Edit'))

    return render_to_response('display/qsd_listing.html', request, GetNode('Q/Web'), {'qsd_pages': qsd_pages, 'have_create': have_create })

def classTemplateEditor(request, program, session):
    """ Generate and display a listing of all QSD pages in the Class template within the specified program
    (QSD pages that are created automatically when a new class is created) """
    qsd_pages = []

    try:
        template_node = GetNodeOrNoBits('Q/Programs/' + program + '/' + session + '/Template', request.user)
    except DataTree.NoSuchNodeException:
        raise Http404

    for qsd in template_node.quasistaticdata_set.all():
        qsd_pages.append( { 'edit_url': qsd.name + ".edit.html",
                            'view_url': qsd.name + ".html",
                            'page': qsd } )

    have_create = UserBit.UserHasPerms(request.user, template_node, GetNode('V/Administer/Edit'))

    return render_to_response('display/qsd_listing.html', request, program, {'qsd_pages': qsd_pages,
                                                            'have_create': have_create })

@admin_required
def manage_programs(request):
    admPrograms = ESPUser(request.user).getEditable(Program).order_by('-id')

    return render_to_response('program/manage_programs.html', request, GetNode('Q/Web/myesp'), {'admPrograms': admPrograms})

@admin_required
def newprogram(request):
    template_prog = None

    if 'template_prog' in request.GET:
        #try:
        tprogram = Program.objects.get(id=int(request.GET["template_prog"]))

        template_prog = {}
        template_prog.update(tprogram.__dict__)
        del template_prog["id"]
        
        template_prog["program_modules"] = tprogram.program_modules.all().values_list("id", flat=True)
        template_prog["class_categories"] = tprogram.class_categories.all().values_list("id", flat=True)
        template_prog["term"] = tprogram.anchor.name
        template_prog["term_friendly"] = tprogram.anchor.friendly_name
        template_prog["anchor"] = tprogram.anchor.parent.id
        
        # aseering 5/18/2008 -- List everyone who was granted V/Administer on the specified program
        template_prog["admins"] = User.objects.filter(userbit__verb=GetNode("V/Administer"), userbit__qsc=tprogram.anchor).values_list("id", flat=True)

        # aseering 5/18/2008 -- More aggressively list everyone who was an Admin
        #template_prog["admins"] = [ x.id for x in UserBit.objects.bits_get_users(verb=GetNode("V/Administer"), qsc=tprogram.anchor, user_objs=True) ]
        
        program_visible_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Flags/Public"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
        if len(program_visible_bits) > 0:
            newest_bit = program_visible_bits[0]
            oldest_bit = program_visible_bits[-1]

            template_prog["publish_start"] = oldest_bit.startdate
            template_prog["publish_end"] = newest_bit.enddate

        student_reg_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Deadline/Registration/Student"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
        if len(student_reg_bits) > 0:
            newest_bit = student_reg_bits[0]
            oldest_bit = student_reg_bits[-1]

            template_prog["student_reg_start"] = oldest_bit.startdate
            template_prog["student_reg_end"] = newest_bit.enddate

        teacher_reg_bits = list(UserBit.objects.bits_get_users(verb=GetNode("V/Deadline/Registration/Teacher"), qsc=tprogram.anchor).filter(user__isnull=True).order_by("-startdate"))
        if len(teacher_reg_bits) > 0:
            newest_bit = teacher_reg_bits[0]
            oldest_bit = teacher_reg_bits[-1]

            template_prog["teacher_reg_start"] = oldest_bit.startdate
            template_prog["teacher_reg_end"] = newest_bit.enddate

        
        line_items = LineItemType.objects.filter(anchor__name="Required", anchor__parent__parent=tprogram.anchor).values("amount", "finaid_amount")

        template_prog["base_cost"] = int(-sum([ x["amount"] for x in line_items]))
        template_prog["finaid_cost"] = int(-sum([ x["finaid_amount"] for x in line_items ]))

    if 'checked' in request.GET:
        # Our form's anchor is wrong, because the form asks for the parent of the anchor that we really want.
        # Don't bother trying to fix the form; just re-set the anchor when we're done.
        context = pickle.loads(request.session['context_str'])
        pcf = ProgramCreationForm(context['prog_form_raw'])
        if pcf.is_valid():
            # Fix the anchor friendly name right away, otherwise in-memory caches cause (mild) issues later on
            anchor = GetNode(pcf.cleaned_data['anchor'].get_uri() + "/" + pcf.cleaned_data["term"])
            anchor.friendly_name = pcf.cleaned_data['term_friendly']
            anchor.save()

            new_prog = pcf.save(commit = False) # don't save, we need to fix it up:
            new_prog.anchor = anchor
            new_prog.save()
            pcf.save_m2m()
            
            commit_program(new_prog, context['datatrees'], context['userbits'], context['modules'], context['costs'])
            
            manage_url = '/manage/' + new_prog.url() + '/resources'
            return HttpResponseRedirect(manage_url)
        else:
            raise ESPError(False), "Improper form data submitted."
          

    #   If the form has been submitted, process it.
    if request.method == 'POST':
        form = ProgramCreationForm(request.POST)

        if form.is_valid():
            temp_prog = form.save(commit=False)
            datatrees, userbits, modules = prepare_program(temp_prog, form.cleaned_data)
            #   Save the form's raw data instead of the form itself, or its clean data.
            #   Unpacking of the data happens at the next step.

            context_pickled = pickle.dumps({'prog_form_raw': form.data, 'datatrees': datatrees, 'userbits': userbits, 'modules': modules, 'costs': ( form.cleaned_data['base_cost'], form.cleaned_data['finaid_cost'] )})
            request.session['context_str'] = context_pickled
            
            return render_to_response('program/newprogram_review.html', request, GetNode('Q/Programs/'), {'prog': temp_prog, 'datatrees': datatrees, 'userbits': userbits, 'modules': modules})
        
    else:
        #   Otherwise, the default view is a blank form.
        if template_prog:
            form = ProgramCreationForm(template_prog)
        else:
            form = ProgramCreationForm()

    return render_to_response('program/newprogram.html', request, GetNode('Q/Programs/'), {'form': form, 'programs': Program.objects.all().order_by('-id')})

@login_required
def submit_transaction(request):
    #   We might also need to forward post variables to http://shopmitprd.mit.edu/controller/index.php?action=log_transaction
    
    if request.POST.has_key("decision") and request.POST["decision"] != "REJECT":

        try:
            from decimal import Decimal
            post_locator = request.POST['merchantDefinedData1']
            post_amount = Decimal(request.POST['orderAmount'])
            post_id = request.POST['requestID']
            
            document = Document.receive_creditcard(request.user, post_locator, post_amount, post_id)
        except CompletedTransactionException:
            from django.conf import settings
            invoice = Document.get_by_locator(post_locator)
            # Look for duplicate payment by checking old receipts for different cc_ref.
            cc_receipts = invoice.docs_next.filter(cc_ref__isnull=False).exclude(cc_ref=post_id)
            # Prepare to send e-mail notification of duplicate postback.
            # This should be cleaned up sometime. And we shouldn't hardcode esp-treasurer@mit.edu.
            recipient_list = [contact[1] for contact in settings.ADMINS]
            refs = 'Cybersource request ID: %s' % post_id
            if cc_receipts:
                recipient_list.append('esp-treasurer@mit.edu')
                subject = 'DUPLICATE PAYMENT'
                refs += '\n\nPrevious payments\' Cybersource IDs: ' + ( u', '.join([x.cc_ref for x in cc_receipts]) )
            else:
                subject = 'Duplicate Postback'
            # Send mail!
            send_mail('[ ESP CC ] ' + subject + ' for #' + post_locator + ' by ' + invoice.user.first_name + ' ' + invoice.user.last_name, \
                  """%s Notification\n--------------------------------- \n\nDocument: %s\n\n%s\n\nUser: %s %s (%s)\n\nCardholder: %s, %s\n\nProgram anchor: %s\n\nRequest: %s\n\n""" % \
                  (subject, invoice.locator, refs, invoice.user.first_name, invoice.user.last_name, invoice.user.id, request.POST.get('billTo_lastName', '--'), request.POST.get('billTo_firstName', '--'), invoice.anchor.get_uri(), request) , \
                  settings.SERVER_EMAIL, recipient_list, True)
            # Get the document that would've been created instead
            document = invoice.docs_next.all()[0]
        except:
            raise ESPError(), "Your credit card transaction was successful, but a server error occurred while logging it.  The transaction has not been lost (please do not try to pay again!); this just means that the green Credit Card checkbox on the registration page may not be checked off.  Please <a href=\"mailto:nw-websupport@lists.learningu.org\">e-mail us</a> and ask us to correct this manually.  We apologize for the inconvenience."

        one = document.anchor.parent.name
        two = document.anchor.name

        return HttpResponseRedirect("http://%s/learn/%s/%s/confirmreg" % (request.META['HTTP_HOST'], one, two))
        
    return render_to_response( 'accounting_docs/credit_rejected.html', request, GetNode('Q/Accounting'), {} )

# This really should go in qsd
@admin_required
def manage_pages(request):
    if request.method == 'POST':
        data = request.POST
        if request.GET['cmd'] == 'bulk_move':
            if data.has_key('confirm'):
                form = QSDBulkMoveForm(data)
                #   Handle submission of bulk move form
                if form.is_valid():
                    form.save_data()
                    return HttpResponseRedirect('/manage/pages')

            #   Create and display the form
            qsd_id_list = []
            for key in data.keys():
                if key.startswith('check_'):
                    qsd_id_list.append(int(key[6:]))
            if len(qsd_id_list) > 0:
                form = QSDBulkMoveForm()
                qsd_list = QuasiStaticData.objects.filter(id__in=qsd_id_list)
                anchor = form.load_data(qsd_list)
                if anchor:
                    return render_to_response('qsd/bulk_move.html', request, DataTree.get_by_uri('Q/Web'), {'common_anchor': anchor, 'qsd_list': qsd_list, 'form': form})
        
        qsd = QuasiStaticData.objects.get(id=request.GET['id'])
        if request.GET['cmd'] == 'move':
            #   Handle submission of move form
            form = QSDMoveForm(data)
            if form.is_valid():
                form.save_data()
            else:
                return render_to_response('qsd/move.html', request, DataTree.get_by_uri('Q/Web'), {'qsd': qsd, 'form': form})
        elif request.GET['cmd'] == 'delete':
            #   Mark as inactive all QSD pages matching the one with ID request.GET['id']
            if data['sure'] == 'True':
                all_qsds = QuasiStaticData.objects.filter(path=qsd.path, name=qsd.name)
                for q in all_qsds:
                    q.disabled = True
                    q.save()
        return HttpResponseRedirect('/manage/pages')

    elif request.GET.has_key('cmd'):
        qsd = QuasiStaticData.objects.get(id=request.GET['id'])
        if request.GET['cmd'] == 'delete':
            #   Show confirmation of deletion
            return render_to_response('qsd/delete_confirm.html', request, DataTree.get_by_uri('Q/Web'), {'qsd': qsd})
        elif request.GET['cmd'] == 'undelete':
            #   Make all the QSDs enabled and return to viewing the list
            all_qsds = QuasiStaticData.objects.filter(path=qsd.path, name=qsd.name)
            for q in all_qsds:
                q.disabled = False
                q.save()
        elif request.GET['cmd'] == 'move':
            #   Show move form
            form = QSDMoveForm()
            form.load_data(qsd)
            return render_to_response('qsd/move.html', request, DataTree.get_by_uri('Q/Web'), {'qsd': qsd, 'form': form})
            
    #   Show QSD listing 
    qsd_ids = []
    qsds = QuasiStaticData.objects.all().order_by('-create_date').values_list('id', 'path', 'name')
    seen_keys = set()
    for id, path, name in qsds:
        key = path, name
        if key not in seen_keys:
            qsd_ids.append(id)
            seen_keys.add(key)
    qsd_list = list(QuasiStaticData.objects.filter(id__in=qsd_ids))
    qsd_list.sort(key=lambda q: q.url())
    return render_to_response('qsd/list.html', request, DataTree.get_by_uri('Q/Web'), {'qsd_list': qsd_list})

@admin_required
def flushcache(request):
    context = {}
    if request.POST:
        if request.POST.has_key("reason") and len(request.POST['reason']) > 5:
            reason = request.POST['reason']
            _cache = cache
            while hasattr(_cache, "_wrapped_cache"):
                _cache = _cache._wrapped_cache
            if hasattr(_cache, "flush_all"):
                _cache.flush_all()
                mail_admins("Cache Flushed on server '%s'!" % request.META['SERVER_NAME'], "The cache was flushed!  The following reason was given:\n\n%s" % reason)
                context['success'] = "Cache Cleared."
            else:
                context['error'] = "Error: This cache backend doesn't support the 'flush_all' method.  Sorry; you'll have to flush this one manually."
        else:
            context['error'] = "Sorry, that doesn't count as a reason."

    return render_to_response('admin/cache_flush.html', request, DataTree.get_by_uri('Q/Web'), context)
                         
