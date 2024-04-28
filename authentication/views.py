from django.shortcuts import render
from utils.query import query
from django.http import JsonResponse


def login(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        data = query(
            "SELECT username, password FROM pengguna WHERE username = %s AND password = %s", (username, password))
        print(data)
        if len(data) == 1:
            request.session["username"] = username
            return JsonResponse({
                "message": "berhasil gan"
            })
        else:
            context["message"] = "Login failed. Make sure you've inputted the correct credentials."
    return render(request, "login.html", context)
