from django.shortcuts import render
from utils.query import query


def show_main(request):
    context = {
        "is_authenticated": False
    }
    return render(request, "main.html", context)
