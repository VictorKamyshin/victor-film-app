from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from models import Film, Appraisal, Profile, Comment, User
from django.db.models import Avg
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from forms import RegistrationForm, EditProfileForm, AuthorisationForm, CreateFilmForm, FilmCommentForm, FilmVoteForm, \
    EditFilmForm, EditFilmCommentForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate as dj_authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout
import json
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import datetime
import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.


def api_film_card(request):
    if request.method:
        param = request.GET.get('film_id')
        try:
            film_id = int(param)
        except ValueError:
            return HttpResponseBadRequest("Id is not a number")
        film = Film.objects.get(id=film_id)
        appraisals = Appraisal.customManager.film_appraisal(film_id)
        appraisals_json = []
        for appraisal in appraisals:
            appraisals_json.append(appraisal.json_format())
        film_json = film.json_format()
        return HttpResponse(json.dumps({'film': film_json, 'appraisals': appraisals_json}, 2),
                            content_type='application/json')
    else:
        return HttpResponseBadRequest("Method not supported")


def api_film_list(request):
    if request.method == 'GET':
        sort = request.GET.get('sort_by')
        if (sort is None) or (sort not in ['rating', 'popularity', 'date', 'title']):
            return HttpResponseBadRequest('unexpected sort type')
        order = request.GET.get('order')
        if (order is None) or (order not in ['asc', 'desc']):
            order = 'asc'
        films = []
        if sort == 'rating':
            if order == 'asc':
                films = list(Film.objects.all().order_by('rating'))
            else:
                films = list(Film.objects.all().order_by('-rating'))
        if sort == 'popularity':
            if order == 'asc':
                films = list(Film.objects.all().order_by('count_of_comments'))
            else:
                films = list(Film.objects.all().order_by('-count_of_comments'))
        if sort == 'date':
            if order == 'asc':
                films = list(Film.objects.all().order_by('date_of_addition'))
            else:
                films = list(Film.objects.all().order_by('-date_of_addition'))
        if sort == 'title':
            if order == 'asc':
                films = list(Film.objects.all().order_by('title'))
            else:
                films = list(Film.objects.all().order_by('-title'))
        json_films = []
        for film in films:
            json_films.append(film.json_format())
        return HttpResponse(json.dumps(json_films, 2), content_type='application/json')
    else:
        return HttpResponseBadRequest("Method not supported")


def main_page(request):
    if request.method == 'GET':
        sort = request.GET.get('sort')
        if (sort is None) or (sort not in ['rating', 'popularity', 'date', 'title']):
            sort = 'title'
        films = []
        is_moderator = check_is_moderator(request.user)
        if is_moderator:
            if sort == 'rating':
                films = list(Film.objects.all().order_by('rating'))
            if sort == 'popularity':
                films = list(Film.objects.all().order_by('count_of_comments'))
            if sort == 'date':
                films = list(Film.objects.all().order_by('date_of_addition'))
            if sort == 'title':
                films = list(Film.objects.all().order_by('title'))
        else:
            if sort == 'rating':
                films = list(Film.objects.filter(isDeleted=False).order_by('rating'))
            if sort == 'popularity':
                films = list(Film.objects.filter(isDeleted=False).order_by('count_of_comments'))
            if sort == 'date':
                films = list(Film.objects.filter(isDeleted=False).order_by('date_of_addition'))
            if sort == 'title':
                films = list(Film.objects.filter(isDeleted=False).order_by('title'))
        films = paginate(films, request)
        last_comments = Comment.customManager.get_last()
        username = request.user.username
        return render(request, 'main-page.html', {'films': films, 'last_comments': last_comments, 'username': username,
                                                  'sort': sort, 'isModerator': is_moderator})
    else:
        return HttpResponse('Method does not allowed')


def profile_view_page(request):
    if not request.method == 'GET':
        return HttpResponseRedirect('/main/')
    try:
        profile = Profile.objects.get(user__username=request.GET.get('username'))
    except ObjectDoesNotExist:
        return HttpResponse('That user doesnt exist')
    appraisal_distr = get_appraisal_distribution_by_user(profile.user)
    last_comments = Comment.customManager.get_last()
    username = request.user.username
    can_edit = request.user.username == request.GET.get('username')
    return render(request, 'profile-view.html', {'profile': profile, 'appraisals_distr': appraisal_distr,
                                                 'last_comments': last_comments, 'username': username,
                                                 'can_edit': can_edit})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/main/')


def film_card_page(request):
    param = request.GET.get('film_id')
    try:
        film_id = int(param)
    except ValueError:
        return HttpResponse("Not a number")
    film_card = Film.objects.get(id=film_id)
    if film_card is None:
        return HttpResponse("There are no such film")
    is_moderator = check_is_moderator(request.user)
    if film_card.isDeleted and not is_moderator:
        return HttpResponse("This film was deleted")
    comments = Comment.customManager.filter(film_id=film_card.id).order_by('material_path')
    user = request.user.username
    last_comments = Comment.customManager.get_last()
    appraisal_distr = get_appraisal_distr(film_id)
    comment_form = FilmCommentForm
    film_vote_form = FilmVoteForm
    return render(request, 'film-card.html', {'film_card': film_card, 'comments': comments,
                                              'last_comments': last_comments, 'comment_form': comment_form,
                                              'film_vote': film_vote_form, 'username': user,
                                              'appraisals_distr': appraisal_distr, 'isModerator': is_moderator})


def register_confirm(request):
    if request.user.is_authenticated():
        HttpResponseRedirect('/main_page/')
    if request.method == 'GET':
        activation_key = request.GET.get('activation_key')
    else:
        return HttpResponseBadRequest('Method not supported')

    user_profile = get_object_or_404(Profile, activation_key=activation_key)

    if user_profile.key_expires < timezone.now():
        user_profile.delete()
        request.user.delete()
        last_comments = Comment.customManager.get_last()
        return render(request, 'confirm_expired.html', {'last_comments': last_comments})
    else:
        last_comments = Comment.customManager.get_last()
        user = user_profile.user
        user.is_active = True
        user.save()
        return render(request, 'registration_confirm.html', {'last_comments': last_comments})


def registration_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            patronymic = form.cleaned_data.get('patronymic')
            password = form.cleaned_data.get('password1')
            avatar = form.cleaned_data.get('avatar')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt + email).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            Profile.objects.create(user=user, email=email, name=name, surname=surname, patronymic=patronymic,
                                   activation_key=activation_key, key_expires=key_expires)

            email_subject = u'Registration confirm'
            email_body = u"Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours https://victor-film-app.herokuapp.com/registration_confirm/?activation_key=%s" % (username, activation_key)
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            last_comments = Comment.customManager.get_last()
            return render(request, 'registration_success.html', {'last_comments': last_comments})
    else:
        form = RegistrationForm
        user = request.user.username
        last_comments = Comment.customManager.get_last()
        return render(request, 'registration.html', {'last_comments': last_comments, 'form': form, 'username': user})


def profile_edit_page(request):
    if request.method == 'POST':
        new_username = request.POST.get('username', '')
        new_name = request.POST.get('name', '')
        new_surname = request.POST.get('surname', '')
        new_patronymic = request.POST.get('patronymic', '')
        profile = Profile.objects.get(user=request.user)
        if new_username:
            profile.user.username = new_username
        if new_name:
            profile.name = new_name
        if new_surname:
            profile.surname = new_surname
        if new_patronymic:
            profile.patronymic = new_patronymic
        profile.save()
    last_comments = Comment.customManager.get_last()
    form = EditProfileForm
    user = request.user.username
    appraisal_distr = get_appraisal_distribution_by_user(request.user)
    return render(request, 'profile.html', {'last_comments': last_comments, 'form': form, 'username': user,
                                            'appraisals_distr': appraisal_distr})


def authorisation_page(request):
    if request.method == 'POST':
        form = AuthorisationForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            try:
                username = Profile.objects.get(email=email).user.username
            except ObjectDoesNotExist:
                return HttpResponseBadRequest('This user does not exists')
            password = request.POST.get('password', '')
            user = dj_authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                return HttpResponseRedirect('/main/')
    else:
        form = AuthorisationForm
    last_comments = Comment.customManager.get_last()
    return render(request, 'authorisation.html', {'last_comments': last_comments, 'form': form})


def create_film(request):
    if not (check_user_rights(request.user)):
        return HttpResponseRedirect('/main/')
    if request.method == 'POST':
        form = CreateFilmForm(request.POST)
        if form.is_valid():
            title = request.POST.get('title', '')
            producer = request.POST.get('producer', '')
            country = request.POST.get('country', '')
            description = request.POST.get('description', '')
            premiere = request.POST.get('premiere', '')
            Film.objects.create(title=title, producer=producer, country=country, description=description,
                                premiere=premiere)
            return HttpResponseRedirect('/main/')
    else:
        form = CreateFilmForm
    last_comments = Comment.customManager.get_last()
    user = request.user.username
    return render(request, 'create-film.html', {'last_comments': last_comments, 'form': form, 'username': user})


def edit_film(request):
    if not (check_user_rights(request.user)):
        return HttpResponseRedirect('/main/')

    if request.method == 'GET':
        form = EditFilmForm(initial={'film_id': request.GET.get('film_id')})
        last_comments = Comment.customManager.get_last()
        return render(request, 'edit-film.html', {'form': form, 'username': request.user.username,
                                                  'last_comments': last_comments})

    if request.method == 'POST':
        film_id = request.POST.get('film_id')
        try:
            film = Film.objects.get(id=film_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('There are no such film')
        producer = request.POST.get('producer', '')
        country = request.POST.get('country', '')
        description = request.POST.get('description', '')
        premiere = request.POST.get('premiere', None)
        if producer:
            film.producer = producer
        if country:
            film.country = country
        if description:
            film.description = description
        if premiere:
            film.premiere = premiere
        film.save()
        return HttpResponseRedirect('/film_card/?film_id='+str(film.id))


def delete_film(request):
    if check_is_moderator(request.user):
        if request.method == 'GET':
            try:
                film = Film.objects.get(id=request.GET.get('film_id'))
            except ObjectDoesNotExist:
                return HttpResponseBadRequest('There are no such film')
            film.isDeleted = True
            film.save()
            return HttpResponseRedirect('/film_card/?film_id='+str(film.id))
        else:
            return HttpResponseBadRequest('Method not supported')
    else:
        return HttpResponse('You are not moderator')


def restore_film(request):
    if check_is_moderator(request.user):
        if request.method == 'GET':
            try:
                film = Film.objects.get(id=request.GET.get('film_id'))
            except ObjectDoesNotExist:
                return HttpResponseBadRequest('There are no such film')
            film.isDeleted = False
            film.save()
            return HttpResponseRedirect('/film_card/?film_id='+str(film.id))
        else:
            return HttpResponseBadRequest('Method not supported')
    else:
        return HttpResponse('You are not moderator')


def edit_comment(request):
    if not check_is_moderator(request.user):
        return HttpResponseBadRequest('You are not moderator')
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        comment = Comment.customManager.get(id=comment_id)
        form = EditFilmCommentForm(initial={'comment_id': comment_id})
        last_comments = Comment.customManager.get_last()
        return render(request, 'comment_edit.html', {'comment': comment, 'form': form,
                                                     'username': request.user.username, 'last_comments': last_comments})
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        try:
            comment = Comment.customManager.get(id=comment_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('There are no such comment')
        text = request.POST.get('new_text', '')
        comment.text = text
        comment.save()
        return HttpResponseRedirect('/film_card/?film_id='+str(comment.film.id))

    return HttpResponse('I see you request, but wouldnt anything right now')


def delete_comment(request):
    if not check_is_moderator(request.user):
        return HttpResponseBadRequest('You are not moderator')
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        try:
            comment = Comment.customManager.get(id=comment_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('There are no such comment')
        comment.isDeleted = True
        comment.save()
        return HttpResponseRedirect('/film_card/?film_id='+str(comment.film.id))
    else:
        return HttpResponseBadRequest('Method not supported')


def restore_comment(request):
    if not check_is_moderator(request.user):
        return HttpResponseBadRequest('You are not moderator')
    if request.method == 'GET':
        comment_id = request.GET.get('comment_id')
        try:
            comment = Comment.customManager.get(id=comment_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('There are no such comment')
        comment.isDeleted = False
        comment.save()
        return HttpResponseRedirect('/film_card/?film_id=' + str(comment.film.id))
    else:
        return HttpResponseBadRequest('Method not supported')


def film_card_appraisal(request):
    if request.method == 'POST':
        value = request.POST.get('appraisal')
        film_id = request.POST.get('film_id')
        user = request.user
        film = Film.objects.get(id=film_id)
        try:
            appraisal = Appraisal.customManager.get(author__user=user, film__id=film_id)
            appraisal.value = value
            appraisal.save()
        except ObjectDoesNotExist:
            author = Profile.objects.get(user=user)
            Appraisal.customManager.create(value=value, author=author, film=film)
        rating = Appraisal.customManager.film_appraisal(film_id).aggregate(Avg('value'))
        film.rating = rating.get('value__avg')
        film.save()
        return HttpResponse(json.dumps({'text': 'Got your appraisal', 'rating': film.rating}),
                            content_type='application/json')
    return HttpResponseBadRequest('Method not supported')


def film_comment(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Authorization requered')
    else:
        if request.method == 'POST':
            film_id = request.POST.get('film_id')
            comment_id = request.POST.get('commented_comment_id')
            text = request.POST.get('text')
            film = Film.objects.get(id=film_id)
            if comment_id is not None:
                if comment_id.isdigit():
                    parent_comment = Comment.customManager.get(id=comment_id)
                else:
                    parent_comment = None
            else:
                parent_comment = None
            author = Profile.objects.get(user=request.user)
            comment = Comment.customManager.create_comment(text=text, author=author, parent=parent_comment, film=film)
            print film.count_of_comments
            previous_comments = list(Comment.customManager.filter(material_path__lt=comment.material_path,
                                                                  film__id=film.id).order_by('material_path'))
            if len(previous_comments) > 0:
                previous_comment = previous_comments[-1]
                return HttpResponse(json.dumps({'text': 'Hello!', 'level': comment.level,
                                                'reverse_level': 12 - comment.level, 'comment_id': comment.id,
                                                'username': request.user.username,
                                                'prev_comment_id': previous_comment.id}),
                                    content_type='application/json')
            else:
                return HttpResponse(json.dumps({'text': 'Hello!', 'level': comment.level,
                                                'reverse_level': 12 - comment.level, 'comment_id': comment.id,
                                                'username': request.user.username, 'prev_comment_id': None}),
                                    content_type='application/json')
        else:
            return HttpResponseBadRequest('Unsupported request method')


def get_appraisal_distr(film_id):
    existing_appraisal_distr = Appraisal.customManager.filter(film__id=film_id).values('value')\
        .annotate(value_count=Count('value'))
    appraisal_distr = []
    j = 0
    for i in xrange(0, 11):
        if j < len(existing_appraisal_distr):
            if existing_appraisal_distr[j].get('value') == i:
                appraisal_distr.append({'value': i, 'count': existing_appraisal_distr[j].get('value_count')})
                j += 1
            else:
                appraisal_distr.append({'value': i, 'count': 0})
        else:
            appraisal_distr.append({'value': i, 'count': 0})
    return appraisal_distr


def get_appraisal_distribution_by_user(user):
    existing_appraisal_distr = Appraisal.customManager.filter(author__user=user, film__isDeleted=False).values('value')\
        .annotate(value_count=Count('value'))
    appraisal_distr = []
    j = 0
    for i in xrange(0, 11):
        if j < len(existing_appraisal_distr):
            if existing_appraisal_distr[j].get('value') == i:
                appraisal_distr.append({'value': i, 'count': existing_appraisal_distr[j].get('value_count')})
                j += 1
            else:
                appraisal_distr.append({'value': i, 'count': 0})
        else:
            appraisal_distr.append({'value': i, 'count': 0})
    return appraisal_distr


def check_user_rights(user):
    profile = Profile.objects.get(user=user)
    if profile.isModerator:
        return True
    else:
        return False


def check_is_moderator(user):
    if user.is_authenticated():
        try:
            return Profile.objects.get(user=user).isModerator
        except ObjectDoesNotExist:
            return False
    else:
        return False


def paginate(object_list, request):
    paginator = Paginator(object_list, 2)  # Show 2 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return contacts
