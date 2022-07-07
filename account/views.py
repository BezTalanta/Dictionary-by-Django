from django.shortcuts import redirect, render
from django import views
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from dictionary.models import DictionarySetting, Word


class Login(views.View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'account/login_page.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        user_take = authenticate(request, username=username, password=password)

        if user_take is not None:
            login(request, user_take)
            return redirect('home')
        return render(request, 'account/login_page.html',
            {'err_msg': 'Your login or username are incorrect!'})


class Signup(views.View):
    def get(self, request):
        return render(request, 'account/signup_page.html')

    def post(self, request):
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']

        user_input = {'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email}

        if pass1 != pass2:
            user_input['err'] = "Your passwords don't match"
            return render(request, 'account/signup_page.html', user_input)
        elif len(pass1) < 11:
            user_input['err'] = \
                "Your password has to be more than 10 symbols and consist of digits and letters"
            return render(request, 'account/signup_page.html', user_input)
        elif User.objects.filter(username=username).count():
            user_input['err'] = \
                "The user with this username has already exist"
            user_input['username'] = ''
            return render(request, 'account/signup_page.html', user_input)

        user = User.objects.create_user(
            username=username,
            password=pass1,
            first_name=first_name,
            last_name=last_name,
            email=email)
        DictionarySetting.objects.create(user=user)
        login(request, user)

        return redirect('home')
