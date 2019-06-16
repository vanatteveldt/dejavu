import logging

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView, SuccessURLAllowedHostsMixin
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, is_safe_url, urlencode
from django.views import View
from django.views.generic import TemplateView, RedirectView

from django import forms


class VULoginForm(AuthenticationForm):
    """Subclass for authentication that can handle login/reset link sending"""

    def clean(self):
        if 'action-link' in self.data:
            self.action = "LINK"
        elif 'action-reset' in self.data:
            self.action = "RESET"
        else:
            self.action = "LOGIN"

        if self.action in ["LINK", "RESET"]:
            # don't need password, only check if username is filled in
            if not self.cleaned_data.get('username'):
                raise forms.ValidationError(
                    "Please enter a valid VUnetID",
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            return self.cleaned_data
        else:
            # Normal login, so defer to super

            return super().clean()


def send_email(user: User, action: str, next_url: str = None):
    # Mostly Copypasta from auth.forms.PasswordResetForm
    token = PasswordResetTokenGenerator().make_token(user)
    context = dict(user=user,
                   action=action,
                   uid=urlsafe_base64_encode(force_bytes(user.pk)),
                   token=token,
                   protocol="http",
                   domain="localhost:8000",
                   next=next_url,
                  )
    from_email = "vanatteveldt@gmail.com"
    to_email = "vanatteveldt@gmail.com" # replace with vunet-id
    subject = loader.render_to_string("registration/link_email_subject.txt", context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string("registration/link_email_body.txt", context)
    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    html_email = loader.render_to_string("registration/link_email_body.html", context)
    email_message.attach_alternative(html_email, 'text/html')
    email_message.send()


class VULoginView(LoginView):
    form_class = VULoginForm

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        if 'error' in self.request.GET:
            c['error'] = self.request.GET['error']
        return c

    def form_valid(self, form):
        print(form.action)
        if form.action in ["LINK", "RESET"]:
            return self.send_link(form.action, form.cleaned_data['username'])
        else:
            return super().form_valid(form)

    def send_link(self, action: str, username: str):
        response = TemplateResponse(self.request, template="registration/mail_sent.html",
                                    context=dict(username=username))
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            logging.warning(f"User {username} not found")
            return response
        if not user.is_active:
            logging.warning(f"User {username} not active")
            return response

        send_email(user, action, next_url = self.get_redirect_url())
        return response


def _token_login(uidb64: str, token: str) -> User:
    uid = urlsafe_base64_decode(uidb64).decode()
    user = User.objects.get(pk=uid)
    if not PasswordResetTokenGenerator().check_token(user, token):
        raise ValueError("Token invalid or expired")
    return user


class TokenLoginView(RedirectView, SuccessURLAllowedHostsMixin):
    def get_redirect_url(self, *args, **kwargs):
        try:
            user = _token_login(kwargs['uidb64'], kwargs['token'])
            login(self.request, user)
        except Exception as e:

            return f'{reverse("login")}?{urlencode(dict(error=str(e)))}'
        redirect_to = self.request.POST.get('next', self.request.GET.get('next', ''))
        if redirect_to and is_safe_url(url=redirect_to, allowed_hosts=self.get_success_url_allowed_hosts(),
                                       require_https=self.request.is_secure()):
            return redirect_to
        else:
            return reverse("index")
