from django.conf.urls.defaults import *


urlpatterns = patterns('esp.users.views',
                       (r'^ajax_login/?', 'ajax_login'),
                       (r'^register/?$', 'user_registration',),
                       (r'^activate/?$', 'registration.activate_account',),
                       (r'^emaillist/?$', 'join_emaillist',),                   
                       (r'^passwdrecover/(success)?/?$', 'initial_passwd_request',),
                       (r'^passwdrecover/?$', 'initial_passwd_request',),
                       (r'^recoveremail/(success)?/?$', 'email_passwd_followup',),
                       (r'^recoveremail/?$', 'email_passwd_followup',),
                       (r'^cancelrecover/?$', 'email_passwd_cancel',),
                       (r'^signedout/?$', 'signed_out_message',),
                       (r'^login/?$',   'login_checked',),
                       (r'^disableaccount/?$', 'disable_account'),
                       )
