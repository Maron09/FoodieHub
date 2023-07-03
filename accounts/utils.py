

#send_verification_email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from django.core import mail
from django.conf import settings

def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendor-dashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'customer-dashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl
    


def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL # gets the default name
    current_site = get_current_site(request)
    message = render_to_string(email_template, {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)), #to encode user primary key
        'token': default_token_generator.make_token(user), # generates a token for each user
    })
    to_email = user.email
    with mail.get_connection() as connection:
        mail.EmailMessage(mail_subject, message, from_email, to=[to_email], connection=connection).send(fail_silently=False)


def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(
        mail_template,
        context,
    )
    to_email = context['user'].email
    with mail.get_connection() as connection:
        mail.EmailMessage(mail_subject, message, from_email, to=[to_email], connection=connection).send(fail_silently=False)
