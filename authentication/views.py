from django.shortcuts import redirect, render
import psycopg2
from utils.query import query
from django.http import JsonResponse
import random as r


def register(request):
    if "username" in request.session:
        # TODO: Ganti redirect jadi ke "Shows" (daftar tayangan)
        return redirect("shows:tayangan")
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        negara_asal = request.POST.get("country")

        data = query("INSERT INTO pengguna (username, password, negara_asal) VALUES (%s,%s,%s)",
                     (username, password, negara_asal))

        # If trigger is called, Postgres will raise error to psycopg2
        if isinstance(data, psycopg2.errors.RaiseException):
            error_msg = str(data).split("\n")[0]
            context["message"] = error_msg
        else:
            request.session["msg_color"] = "text-blue-500"
            request.session["message"] = "Account creation successful! You can log in now."
            return redirect("authentication:login")
    return render(request, "register.html", context)


def login(request):
    context = {}
    if "username" in request.session:
        # TODO: Ganti redirect jadi ke "Shows" (daftar tayangan)
        return redirect("shows:tayangan")
    if "message" in request.session:
        context["msg_color"] = request.session["msg_color"]
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
            return redirect("shows:tayangan")
        else:
            context["msg_color"] = "text-red-500"
            context["message"] = "Login failed. Make sure you've inputted the correct credentials."
    return render(request, "login.html", context)


def logout(request):
    del request.session["username"]
    return redirect("main:show_main")
