from django.shortcuts import render, redirect
from utils.query import query
from django.http import JsonResponse
import datetime
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def get_active_subscription(request):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
    username = request.session['username']

    if request.method == 'GET':
        active_subscription = query(
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
            (username,)
        )

        message = ""
        if len(active_subscription) == 0:
            message = f"User {username} does not have any active subscription"
            context['active_subscription'] = None
        else:
            message = f"User {username} has active subscription"
            context['active_subscription'] = active_subscription[0]
        
        return JsonResponse({'status': 'success', 'data': context, 'message': message}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
def get_subscription_details_by_name(request, package_name):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
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
            context["package"] = None
        else:
            message = f"Package {package_name} found."
            context["package"] = package_details[0]

        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
    
def get_all_subscription_details(request):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
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
                p.resolusi_layar
            ORDER BY
                p.harga ASC;
            """
        )

        message = ""
        if len(all_packages) == 0:
            message = "No packages available."
            context["packages"] = None
        else:
            message = "Packages available."
            context["packages"] = all_packages

        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

def get_transaction_history(request):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
    username = request.session["username"]

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
            (username,)
        )
        
        message = ""
        if len(all_transaction) == 0:
            message = f"User {username} doesn't have any transaction history."
            context["transactions"] = None
        else:
            message = f"Transaction history found for user {username}."
            context["transactions"] = all_transaction
        
        return JsonResponse({"status": "success", "data": context, "message": message}, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

def is_eligible_to_subscribe(username):
    last_transaction = query(
        """
        SELECT MAX(start_date_time) 
        FROM transaction 
        WHERE username = %s
        """,
        (username,)
    )

    if last_transaction \
          and last_transaction[0]['max'] \
              and datetime.datetime.combine(last_transaction[0]['max'], datetime.datetime.min.time()) \
                > datetime.datetime.now() - datetime.timedelta(days=1):
        return False
    
    return True

def get_subscription_eligibilty(request):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
    username = request.session['username']

    if request.method == "GET":
        eligibilty = is_eligible_to_subscribe(username)
        context['is_eligible'] = eligibilty
        if eligibilty == True:
            return JsonResponse({'status': 'success', 'data': context, 'message': 'You are eligible to subscribe.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'data': context, 'message': 'You are not eligible to subscribe. You already have an active subscription. Please wait for one day before purchasing.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def purchase_subscription(request):
    context = {}
    if 'username' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in'}, status=403)
    
    username = request.session['username']

    if request.method == "POST":
        data = json.loads(request.body)
        package_name = data["package_name"]
        payment_method = data["payment_method"]

        if is_eligible_to_subscribe(username) == False:
            return JsonResponse({'status': 'error', 'message': 'You are not eligible to subscribe. You already have an active subscription. Please wait for one day before purchasing.'}, status=403)
        
        query(
            """
            INSERT INTO transaction (
                username, 
                nama_paket, 
                metode_pembayaran
            )
            VALUES 
                (%s, %s, %s);
            """,
            (
                username, 
                package_name, 
                payment_method
            )
        )

        return JsonResponse({'status': 'success', 'message': 'Subscription purchased successfully.'}, status=201)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
def render_subscription_details(request):
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
        "is_logged_in": False
    }

    if 'username' not in request.session:
        return redirect('authentication:login')
    else:
        context["is_logged_in"] = True
        context["username"] = request.session["username"]
        context["package_name"] = package_name

    return render(request, "purchase_subscription.html", context)