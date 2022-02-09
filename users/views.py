from django.http.response import HttpResponse
import json
from sawo import createTemplate, getContext, verifyToken
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}.')
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Account has been updated.')
            return redirect('profile')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'uform': uform, 'pform': pform})


@login_required
def SearchView(request):
    if request.method == 'POST':
        kerko = request.POST.get('search')
        print(kerko)
        results = User.objects.filter(username__contains=kerko)
        context = {
            'results': results
        }
        return render(request, 'users/search_result.html', context)


load = ''
loaded = 0


def setPayload(payload):
    global load
    load = payload


def setLoaded(reset=False):
    global loaded
    if reset:
        loaded = 0
    else:
        loaded += 1


createTemplate("users/templates/partials")


def index(request):
    return render(request, "index.html")


def LoginView(request):
    setLoaded()
    setPayload(load if loaded < 2 else '')
    configuration = {
        "auth_key": "cdd9093a-fad6-41a8-831b-b7f6520832d1",
        "identifier": "email",
        "to": "receive/"
    }
    context = {"sawo": configuration, "load": load, "title": "Home"}

    return render(request, "users/login.html", context)


def receive(request):
    if request.method == 'POST':
        payload = json.loads(request.body)["payload"]
        setLoaded(True)
        setPayload(payload)
        print(payload)

        status = 200 if verifyToken(payload) else 404
        print(status)
        response_data = {"status": status}
        # return HttpResponse(json.dumps(response_data), content_type="application/json")
        request.session['payload'] = payload
        return redirect('/')

def LogoutView(request):
    setPayload(None)
    del request.session['payload']
    return redirect('/login/')
