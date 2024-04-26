from django.shortcuts import render
from utils.query import query

def show_main(request):
    data = query("SELECT * FROM contributors")
    context = {"data": data}
    return render(request, "main.html", context)
# Create your views here.
