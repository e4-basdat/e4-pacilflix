from django.shortcuts import render,redirect
from utils.query import query


def show_main(request):
    context = {
        "is_logged_in": False
    }
    if "username" in request.session:
        context["is_logged_in"] = True
        context["username"] = request.session["username"]
        return redirect('shows:tayangan')
    else :
        return render(request, "main.html", context)
