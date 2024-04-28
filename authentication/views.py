from django.shortcuts import redirect, render
from utils.query import query
from django.http import JsonResponse
import random as r


def register(request):
    if "username" in request.session:
        # TODO: Ganti redirect jadi ke "Shows" (daftar tayangan)
        return redirect("main:show_main")
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        negara_asal = request.POST.get("country")

        # Select a random show to recommend to new user
        random_show = str(r.choice(query("SELECT id FROM tayangan"))["id"])

        # Validate user with the same username doesn't exist
        exists = query(
            "SELECT * FROM pengguna WHERE username = %s", (username,))
        if len(exists) > 0:
            context["message"] = "Username already taken. Please choose another username."
        else:
            data = query("INSERT INTO pengguna (username, password, id_tayangan, negara_asal) VALUES (%s,%s,%s,%s)",
                         (username, password, random_show, negara_asal))
            request.session["message"] = "Account creation successful! You can log in now."
            return redirect("authentication:login")
    return render(request, "register.html", context)


def login(request):
    context = {}
    if "username" in request.session:
        # TODO: Ganti redirect jadi ke "Shows" (daftar tayangan)
        return redirect("main:show_main")
    if "message" in request.session:
        context["message"] = request.session["message"]
        del request.session["message"]
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = query(
            "SELECT username, password FROM pengguna WHERE username = %s AND password = %s", (username, password))
        if len(data) == 1:
            request.session["username"] = username
            # TODO: Ganti redirect jadi ke "Shows" (daftar tayangan)
            return redirect("main:show_main")
        else:
            context["message"] = "Login failed. Make sure you've inputted the correct credentials."
    return render(request, "login.html", context)


def logout(request):
    del request.session["username"]
    return redirect("main:show_main")
