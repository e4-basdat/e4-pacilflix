from django.shortcuts import redirect, render
from utils.query import query
from django.http import JsonResponse


def login(request):
    if "username" in request.session:
        return redirect("main:show_main")
    context = {}
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
