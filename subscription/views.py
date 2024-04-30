from django.shortcuts import render, redirect
from utils.query import query
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
import datetime
import json
from django.views.decorators.csrf import csrf_exempt

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
                t.metode_pembayaran,
                t.timestamp_pembayaran,
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
                t.timestamp_pembayaran,
                t.metode_pembayaran
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

def get_package_details_by_name(request, package_name):
    context = {}
    
    if request.method == "GET":
        package_details = query(
            """
            SELECT 
                p.nama, 
                p.harga, 
                p.resolusi_layar, 
                STRING_AGG(dp.dukungan_perangkat, ', ') AS dukungan_perangkat 
            FROM 
                paket AS p 
            JOIN 
                dukungan_perangkat AS dp ON p.nama = dp.nama_paket 
            WHERE 
                p.nama = %s 
            GROUP BY 
                p.nama, 
                p.harga, 
                p.resolusi_layar;
            """,
            (package_name,)
        )

        message = ""
        if len(package_details) == 0:
            message = f"Package {package_name} not found."
            context["package"] = {}
        else:
            message = f"Package {package_name} found."
            context["package"] = package_details[0]

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
                STRING_AGG(dp.dukungan_perangkat, ', ') AS dukungan_perangkat 
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
        SELECT DISTINCT
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
                t.username = %s
            ORDER BY
                t.timestamp_pembayaran DESC;
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
    
@csrf_exempt
def add_subscription(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == "POST":
        data = json.loads(request.body)
        package_name = data["package_name"]
        payment_method = data["payment_method"]

        # Mengambil data transaksi terakhir pengguna
        last_transaction = query(
            """
            SELECT MAX(start_date_time) 
            FROM transaction 
            WHERE username = %s
            """,
            (request.session["username"],)
        )
        
        if last_transaction and last_transaction[0]['max'] and datetime.datetime.combine(last_transaction[0]['max'], datetime.datetime.min.time()) > datetime.datetime.now() - datetime.timedelta(days=1):
            return JsonResponse({"status": "error", "message": "You already have an active subscription. Please wait for one day before updating."}, status=400)

        start_date_time = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date_time = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        payment_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        query(
            """
            INSERT INTO transaction (
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


@csrf_exempt
def update_subscription(request):
    context = {}

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    if request.method == "PUT":
        data = json.loads(request.body)
        start_date_time = data["start_date_time"]
        new_end_date = data["new_end_date"]
        username = request.session["username"]
        metode_pembayaran = data["metode_pembayaran"]
        nama_paket = data["nama_paket"]
        timestamp_pembayaran = data["timestamp_pembayaran"]
        print(new_end_date)

        data = query(
            """
            UPDATE transaction
            SET 
                end_date_time = %s,
                nama_paket = %s,
                metode_pembayaran = %s,
                timestamp_pembayaran = %s
            WHERE 
                username = %s AND 
                start_date_time = %s
            """,
            (new_end_date, 
             nama_paket, 
             metode_pembayaran,
             timestamp_pembayaran,
             username, 
             start_date_time)
        )

        return JsonResponse({"status": "success", "message": "Subscription status updated successfully."}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def check_subscription_eligibility(request):
    if 'username' not in request.session:
        return redirect('authentication:login')

    last_transaction = query(
        """
        SELECT MAX(start_date_time) 
        FROM transaction 
        WHERE username = %s
        """,
        (request.session["username"],)
    )

    if last_transaction and last_transaction[0]['max'] and datetime.datetime.combine(last_transaction[0]['max'], datetime.datetime.min.time()) > datetime.datetime.now() - datetime.timedelta(days=1):
        return JsonResponse({"status": "error", "message": "You already have an active subscription. Please wait for one day before purchasing a new one."}, status=400)
    else:
        return JsonResponse({"status": "success", "message": "You are eligible to purchase a new subscription."}, status=200)
    
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

def render_subscription_purchase(request, package_name):
    context = {
        "is_logged_in": False,
    }

    if 'username' not in request.session:
        return redirect('authentication:login')
    
    context["is_logged_in"] = True
    context["username"] = request.session["username"]

    if request.method == "GET":
        package_details = query(
            """
            SELECT 
                p.nama, 
                p.harga, 
                p.resolusi_layar, 
                STRING_AGG(dp.dukungan_perangkat, ', ') AS dukungan_perangkat 
            FROM 
                paket AS p 
            JOIN 
                dukungan_perangkat AS dp ON p.nama = dp.nama_paket 
            WHERE 
                p.nama = %s 
            GROUP BY 
                p.nama, 
                p.harga, 
                p.resolusi_layar;
            """,
            (package_name,)
        )

        if len(package_details) == 0:
            return redirect("subscription:render_subscription_manager")
        else:
            context["package"] = package_details[0]
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
    return render(request, "purchase_subscription.html", context)