import json
from django.http import JsonResponse
from django.shortcuts import redirect, render

from utils.query import query

# Create your views here.
def render_contributors(request):
    context = {
        "is_logged_in": False,
    }

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    context["is_logged_in"] = True
    context["username"] = request.session["username"]
    
    return render(request, 'contributors.html', context)

def get_writers(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == 'GET':
        writers = query(
            """
            SELECT c.nama, 
                CASE 
                    WHEN c.jenis_kelamin = 0 THEN 'Laki-laki'
                    WHEN c.jenis_kelamin = 1 THEN 'Perempuan'
                    ELSE 'Tidak diketahui'
                END AS jenis_kelamin,
                c.kewarganegaraan,
                'Screenwriter' AS role
            FROM penulis_skenario ps
            JOIN contributors c ON ps.id = c.id;
            """
        )

        message = ""
        if len(writers) == 0:
            message = "No writers found."
            context["contributors"] = {}
        else:
            message = "Writers found."
            context["contributors"] = writers
        
        return JsonResponse({"status": "success", "message": message, "data": context}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_actors(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == 'GET':
        actors = query(
            """
            SELECT c.nama, 
                CASE 
                    WHEN c.jenis_kelamin = 0 THEN 'Laki-laki'
                    WHEN c.jenis_kelamin = 1 THEN 'Perempuan'
                    ELSE 'Tidak diketahui'
                END AS jenis_kelamin,
                c.kewarganegaraan,
                'Actor' AS role
            FROM pemain p
            JOIN contributors c ON p.id = c.id;
            """
        )

        message = ""
        if len(actors) == 0:
            message = "No actors found."
            context["contributors"] = {}
        else:
            message = "Actors found."
            context["contributors"] = actors
        
        return JsonResponse({"status": "success", "message": message, "data": context}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_directors(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == 'GET':
        directors = query(
            """
            SELECT c.nama, 
                CASE 
                    WHEN c.jenis_kelamin = 0 THEN 'Laki-laki'
                    WHEN c.jenis_kelamin = 1 THEN 'Perempuan'
                    ELSE 'Tidak diketahui'
                END AS jenis_kelamin,
                c.kewarganegaraan,
                'Director' AS role
            FROM sutradara s
            JOIN contributors c ON s.id = c.id;
            """
        )

        message = ""
        if len(directors) == 0:
            message = "No directors found."
            context["contributors"] = {}
        else:
            message = "Directors found."
            context["contributors"] = directors
        
        return JsonResponse({"status": "success", "message": message, "data": context}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)