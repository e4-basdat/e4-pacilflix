from django.shortcuts import render
from utils.query import query
from django.http import JsonResponse


def login(request):
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
            return JsonResponse({
                "message": "Gagal gan"
            })
    return render(request, "login.html", {})
