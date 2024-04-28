from django.shortcuts import render, redirect
from utils.query import query
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse

# Create your views here.
def get_user_active_package(request):
    context = {}
    if 'username' not in request.session:
        return redirect('authentication:login')
    
    active_username = request.session["username"]

    if request.method == "GET":
        active_transaction = query(
            "SELECT t.nama_paket, t.start_date_time, t.end_date_time, p.harga, p.resolusi_layar, dp.dukungan_perangkat FROM transaction AS t JOIN paket AS p ON t.nama_paket = p.nama JOIN dukungan_perangkat AS dp ON p.nama = dp.nama_paket WHERE t.username = %s AND (t.end_date_time IS NULL OR t.end_date_time > CURRENT_DATE) ORDER BY t.timestamp_pembayaran DESC LIMIT 1", (active_username,))
        
        context["status"] = "success"
        context["username"] = active_username

        if len(active_transaction) == 0:
            context["message"] = "You don't have any active subscription."
            context["transaction"] = {}
        else:
            context["message"] = "You have an active subscription."
            context["transaction"] = active_transaction[0]
        
        return JsonResponse(context, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_all_packages(request):
    context = {}
    
    if request.method == "GET":
        all_packages = query("SELECT p.nama, p.harga, p.resolusi_layar, dp.dukungan_perangkat FROM paket AS p JOIN dukungan_perangkat AS dp ON p.nama = dp.nama_paket")

        context["status"] = "success"

        if len(all_packages) == 0:
            context["message"] = "No packages available."
            context["packages"] = []
        else:
            context["message"] = "Packages available."
            context["packages"] = all_packages

        return JsonResponse(context, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_transaction_history(request):
    context = {}
    if 'username' not in request.session:
        return redirect('authentication:login')
    
    active_username = request.session["username"]

    if request.method == "GET":
        all_transaction = query(
            "SELECT t.nama_paket, t.start_date_time, t.end_date_time, t.metode_pembayaran, p.harga, t.timestamp_pembayaran FROM transaction AS t JOIN paket AS p ON t.nama_paket = p.nama JOIN dukungan_perangkat AS dp ON p.nama = dp.nama_paket WHERE t.username = %s", (active_username,))
        
        context["status"] = "success"
        context["username"] = active_username

        if len(all_transaction) == 0:
            context["message"] = "You don't have any transaction history."
            context["transaction"] = []
        else:
            context["message"] = "Transaction history found."
            context["transaction"] = all_transaction
        
        return JsonResponse(context, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
