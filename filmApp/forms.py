from django import forms
from filmApp.models import Profile, Film
from django.contrib.auth.models import User
from django.contrib.auth import authenticate as dj_authenticate
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


class RegistrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': 'basic-addon1', 'placeholder': 'Alex',
                                                             'class': 'form-control'}), label=u'Username',
                               required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'aria-describedby': 'basic-addon1',
                                                           'placeholder': 'example@mail.ru', 'class': "form-control"}),
                             label=u'E-mail', required=True)
    name = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                         'placeholder': "Alex", 'class': "form-control"}),
                           label=u'First name', required=True)
    surname = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1", 'placeholder': "Smith",
                                                            'class': "form-control"}), label=u'Surname', required=True)
    patronymic = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                               'placeholder': u'(o_o)?', 'class': "form-control"}),
                                 label=u'Patronymic', required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'aria-describedby': "basic-addon1",
                                                                  'placeholder': "qwer1234", 'class': "form-control"}),
                                label=u'Password', required=True)

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'aria-describedby': "basic-addon1",
                                                                  'placeholder': "qwer1234", 'class': "form-control"}),
                                label=u'Repeat password', required=True)

    avatar = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label='Avatar', required=False)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError(u'Too short password')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(u'Passwords does not match')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise forms.ValidationError(u'This email is already used')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(u'This username is already used')
        return username


class EditProfileForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1", 'placeholder': "Alex",
                                                             'class': "form-control"}), label=u'Username',
                               required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1", 'placeholder': "Alex",
                                                         'class': "form-control"}), label=u'First name', required=False)
    surname = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1", 'placeholder': "Smith",
                                                            'class': "form-control"}), label=u'Surname', required=False)
    patronymic = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                               'placeholder': u'(o_o)?', 'class': "form-control"}),
                                 label=u'Patronymic', required=False)

    Avatar = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label=u'avatar', required=False)


class AuthorisationForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                             'placeholder': "example@maol.ru", 'class': "form-control"}),
                               label=u'Email', required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'aria-describedby': "basic-addon1",
                                                                 'placeholder': "qwer1234", 'class': "form-control"}),
                               label=u'Password', required=True)

    def clean_password(self):
        email = self.cleaned_data.get('email')
        try:
            username = Profile.objects.get(email=email).user.username
        except ObjectDoesNotExist:
            raise forms.ValidationError("Sorry, wrong couple of login/password. Please try again.")
        password = self.cleaned_data.get('password')
        user = dj_authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Sorry, wrong couple of login/password. Please try again.")
        return self.cleaned_data


class CreateFilmForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                          'placeholder': "Awesome title", 'class': "form-control"}),
                            label=u'Title', required=True)
    producer = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                             'placeholder': "Awesome producer",
                                                             'class': "form-control"}),
                               label=u'Producer', required=True)
    country = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                            'placeholder': "Awesome country", 'class': "form-control"}),
                              label=u'Country', required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'aria-describedby': "basic-addon1",
                                                               'placeholder': "Enter film description here",
                                                               'class': "comment-input-field"}), label='Description',
                                  required=True)
    premiere = forms.DateTimeField(initial=datetime.now(), widget=forms.DateTimeInput())
    poster = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label=u'Poster', required=False)

    preview = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label=u'Preview', required=False)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        try:
            Film.objects.get(title=title)
            raise forms.ValidationError("Sorry, film with this title already exists. Please try another title.")
        except ObjectDoesNotExist:
            return self.cleaned_data


class EditFilmForm(forms.Form):
    film_id = forms.IntegerField(widget=forms.HiddenInput)

    producer = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                             'placeholder': "Awesome producer",
                                                             'class': "form-control"}),
                               label=u'Producer', required=False)
    country = forms.CharField(widget=forms.TextInput(attrs={'aria-describedby': "basic-addon1",
                                                            'placeholder': "Awesome country", 'class': "form-control"}),
                              label=u'Country', required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'aria-describedby': "basic-addon1",
                                                               'placeholder': "Enter film description here",
                                                               'class': "comment-input-field"}), label='Description',
                                  required=False)
    premiere = forms.DateField(initial=datetime.now(), widget=forms.DateInput(format='%Y-%m-%d'),
                               input_formats=('%Y-%m-%d'), required=False)
    poster = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label=u'Poster', required=False)

    preview = forms.ImageField(widget=forms.FileInput(attrs={'name': "avatar"}), label=u'Preview', required=False)


class FilmCommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'aria-describedby': "basic-addon1",
                                                        'placeholder': "Enter your comment here",
                                                        'class': "comment-input-field", 'rows': "4",
                                                        'name': 'comment', 'id': 'comment'}), required=True)


class EditFilmCommentForm(forms.Form):
    comment_id = forms.IntegerField(widget=forms.HiddenInput)

    new_text = forms.CharField(widget=forms.Textarea(attrs={'aria-describedby': "basic-addon1",
                                                            'placeholder': "Enter your comment here",
                                                            'class': "comment-input-field", 'rows': "4",
                                                            'name': 'comment', 'id': 'comment'}), label=u'New text',
                               required=True)


class FilmVoteForm(forms.Form):
    value = forms.ChoiceField(choices=[(x, x) for x in range(0, 11)], required=True)
