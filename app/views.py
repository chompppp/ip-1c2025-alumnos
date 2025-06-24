# capa de vista/presentación

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .layers.services import services
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from .models import Favourite
import json

def index_page(request):
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")

        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error="usuario o contraseña incorrectos"
            return render (request, "registration/login.html", {"error":error})
        
    return render(request, 'registration/login.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def card_color(types):
    if "fire" in types:
        return "border-danger"
    elif "water" in types:
        return "border-primary"
    elif "grass" in types:
        return "border-success"
    else:
        return "border-warning"
    
def home(request):
    images = services.getAllImages()
    favourite_list = []

    for img in images:
        img.border_class = card_color(img.types)

    return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })

# función utilizada en el buscador.
def search(request):
    name = request.POST.get('query', '')

    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if (name != ''):
        images = services.filterByCharacter(name)
        for img in images:
            img.border_class=card_color(img.types)

        favourite_list = []

        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })
    else:
        return redirect('home')

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request):
    type_filter = request.POST.get('type', '').lower()

    if type_filter != '':
        images = services.filterByType(type_filter) # debe traer un listado filtrado de imágenes, segun si es o contiene ese tipo.
        favourite_list = []
        for img in images:
            img.border_class = card_color(img.types)        
        return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })

    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    user = request.user
    favourite_list=Favourite.objects.filter(user=user)
    return render(request, "favourites.html", {"favourite_list": favourite_list})

@login_required
def saveFavourite(request):
    if request.method == "POST":
        user= request.user
        poke_id= request.POST.get('id')
        name= request.POST.get('name')
        height= request.POST.get('height')
        weight= request.POST.get('weight')
        base_exp= request.POST.get('base_experience')
        types= request.POST.get("types")
        image= request.POST.get("image")
        
        try:
            types=json.loads(types)
        except Exception:
            types=[]
        
        if not Favourite.objects.filter(user=user, name=name).exists():
            Favourite.objects.create(
                id=poke_id,
                user=user,
                name=name,
                height=height,
                weight=weight,
                base_experience=base_exp,
                types=types,
                image=image
            )
    return redirect("home")

@login_required
def deleteFavourite(request):
    if request.method=="POST":
        fav_id= request.POST.get("id")
        Favourite.objects.filter(id=fav_id, user=request.user).delete()
    return redirect("favoritos")

@login_required
def exit(request):
    logout(request)
    return redirect('home')

from django.core.mail import EmailMessage

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            subject = 'Registro exitoso'
            message = 'Bienvenido a la Pokédex!'
            recipient = user.email
            from django.core.mail import EmailMessage
            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [recipient])
            email.content_subtype = "plain"
            email.encoding = "utf-8"
            email.send(fail_silently=False)

            messages.success(request, 'Usuario registrado correctamente. Revisa tu correo.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
