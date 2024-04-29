from django.shortcuts import render, redirect
from utils.query import query
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
import datetime
import json

# Create your views here.
def get_user_active_package(request):
    context = {}
    if 'username' not in request.session:
        return redirect('authentication:login')
    
    active_username = request.session["username"]

    if request.method == "GET":
        active_transaction = query(
            """
            SELECT 
                t.nama_paket, 
                t.start_date_time, 
                t.end_date_time, 
                p.harga, 
                p.resolusi_layar, 
                STRING_AGG(dp.dukungan_perangkat, ', ') AS dukungan_perangkat 
            FROM 
                transaction AS t 
            JOIN 
                paket AS p ON t.nama_paket = p.nama 
            JOIN 
                dukungan_perangkat AS dp ON p.nama = dp.nama_paket 
            WHERE 
                t.username = %s 
                AND (t.end_date_time IS NULL OR t.end_date_time > CURRENT_DATE) 
            GROUP BY 
                t.nama_paket, 
                t.start_date_time, 
                t.end_date_time, 
                p.harga, 
                p.resolusi_layar, 
                t.timestamp_pembayaran 
            ORDER BY 
                t.timestamp_pembayaran DESC 
            LIMIT 1;
            """, 
            (active_username,)
        )
        
        message = ""
        if len(active_transaction) == 0:
            message = f"User {active_username} doesn't have any active subscription."
            context["transaction"] = {}
        else:
            message = f"User {active_username} has an active subscription."
            context["transaction"] = active_transaction[0]
        
        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_all_packages(request):
    context = {}
    
    if request.method == "GET":
        all_packages = query(
            """
            SELECT 
                p.nama, 
                p.harga, 
                p.resolusi_layar, 
                STRING_AGG(dp.dukungan_perangkat, ', ') 
            FROM 
                paket AS p 
            JOIN 
                dukungan_perangkat AS dp ON p.nama = dp.nama_paket 
            GROUP BY 
                p.nama, 
                p.harga, 
                p.resolusi_layar;
            """
        )

        message = ""
        if len(all_packages) == 0:
            message = "No packages available."
            context["packages"] = []
        else:
            message = "Packages available."
            context["packages"] = all_packages

        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_transaction_history(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    active_username = request.session["username"]

    if request.method == "GET":
        all_transaction = query(
            """
            SELECT 
                t.nama_paket, 
                t.start_date_time, 
                t.end_date_time, 
                t.metode_pembayaran, 
                p.harga, 
                t.timestamp_pembayaran 
            FROM 
                transaction AS t 
            JOIN 
                paket AS p ON t.nama_paket = p.nama 
            JOIN 
                dukungan_perangkat AS dp ON p.nama = dp.nama_paket 
            WHERE 
                t.username = %s;
            """, 
            (active_username,)
        )
        
        message = ""
        if len(all_transaction) == 0:
            message = f"User {active_username} doesn't have any transaction history."
            context["transaction"] = {}
        else:
            message = f"Transaction history found for user {active_username}."
            context["transaction"] = all_transaction
        
        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

def add_subscription(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == "POST":
        data = json.loads(request.body)
        package_name = data["package_name"]
        payment_method = data["payment_method"]

        start_date_time = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        payment_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = query(
            """
            INSERT INTO
                transaction (
                    username, 
                    nama_paket, 
                    start_date_time,
                    end_date_time, 
                    metode_pembayaran, 
                    timestamp_pembayaran
                )
            VALUES 
                (%s, %s, %s, %s, %s, %s);
            """,
            (
                request.session["username"], 
                package_name, 
                start_date_time, 
                end_date_time, 
                payment_method, 
                payment_timestamp
            )
        )

        return JsonResponse({"status": "success", "message": "Subscription added successfully."}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def update_active_subscription_status(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == "PUT":
        data = json.loads(request.body)
        start_date_time = data["start_date_time"]
        new_end_date = data["new_end_date"]
        username = request.session["username"]

        data = query(
            """
            UPDATE
                transaction
            SET
                end_date_time = %s
            WHERE
                username = %s
                AND start_date_time = %s;
            """,
            (new_end_date, username, start_date_time)
        )

        return JsonResponse({"status": "success", "message": "Subscription status updated successfully."}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def render_subscription_manager(request):
    context = {
        "is_logged_in": False
    }

    if 'username' not in request.session:
        return redirect('authentication:login')
    else:
        context["is_logged_in"] = True
        context["username"] = request.session["username"]

    return render(request, "manage_subscription.html", context)

def render_purchase_subscription(request):
    context = {
        "is_logged_in": False
    }

    if 'username' not in request.session:
        return redirect('authentication:login')
    else:
        context["is_logged_in"] = True
        context["username"] = request.session["username"]