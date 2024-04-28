from django.shortcuts import render
from utils.query import query


def show_main(request):
    context = {}
    username = request.session["username"]
    print(username)
    context["is_guest"] = not username
    if not context["is_guest"]:
        context["username"] = username

    return render(request, "main.html", context)
