import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
import psycopg2


def show_tayangan(request):
    context = {
        "is_logged_in": False
    }
    if 'username' not in request.session:
        return redirect('authentication:login')

    context["is_logged_in"] = True
    context["username"] = request.session["username"]

    tayangan = query("""
        SELECT 
            judul,
            sinopsis_trailer, 
            url_video_trailer, 
            to_char(release_date_trailer, 'DD-MM-YYYY') as release_date_trailer
        FROM
            TAYANGAN
        """)

    top_ten = query("""
        SELECT
            TAYANGAN.id,
            TAYANGAN.judul,
            TAYANGAN.sinopsis_trailer,
            TAYANGAN.url_video_trailer,
            to_char(TAYANGAN.release_date_trailer, 'DD-MM-YYYY') as release_date_trailer,
            COALESCE(total_view_all_time.total_view_all_time, 0) AS total_view_all_time,
            COALESCE(total_view_7_days.total_view_7_days, 0) AS total_view_7_days
        FROM
            TAYANGAN
        LEFT JOIN (
            SELECT
                t.id AS id_tayangan,
                SUM(e.durasi) AS total_duration
            FROM
                TAYANGAN t
            LEFT JOIN
                episode e ON t.id = e.id_series
            GROUP BY
                t.id
        ) AS series_total_duration ON TAYANGAN.id = series_total_duration.id_tayangan
        LEFT JOIN (
            SELECT
                t.id AS id_tayangan,
                f.durasi_film AS total_duration
            FROM
                TAYANGAN t
            LEFT JOIN
                film f ON t.id = f.id_tayangan
        ) AS film_total_duration ON TAYANGAN.id = film_total_duration.id_tayangan
        LEFT JOIN (
            SELECT
                COALESCE(std.id_tayangan, ftd.id_tayangan) AS id_tayangan,
                COALESCE(std.total_duration, ftd.total_duration) AS total_duration
            FROM
                (
                    SELECT
                        t.id AS id_tayangan,
                        SUM(e.durasi) AS total_duration
                    FROM
                        TAYANGAN t
                    LEFT JOIN
                        episode e ON t.id = e.id_series
                    GROUP BY
                        t.id
                ) AS std
            FULL OUTER JOIN (
                SELECT
                    t.id AS id_tayangan,
                    f.durasi_film AS total_duration
                FROM
                    TAYANGAN t
                LEFT JOIN
                    film f ON t.id = f.id_tayangan
            ) AS ftd ON std.id_tayangan = ftd.id_tayangan
        ) AS combined_total_duration ON TAYANGAN.id = combined_total_duration.id_tayangan
        LEFT JOIN (
            SELECT
                rn.id_tayangan,
                COUNT(*) AS total_view_7_days
            FROM
                riwayat_nonton rn
            JOIN (
                SELECT
                    COALESCE(std.id_tayangan, ftd.id_tayangan) AS id_tayangan,
                    COALESCE(std.total_duration, ftd.total_duration) AS total_duration
                FROM
                    (
                        SELECT
                            t.id AS id_tayangan,
                            SUM(e.durasi) AS total_duration
                        FROM
                            TAYANGAN t
                        LEFT JOIN
                            episode e ON t.id = e.id_series
                        GROUP BY
                            t.id
                    ) AS std
                FULL OUTER JOIN (
                    SELECT
                        t.id AS id_tayangan,
                        f.durasi_film AS total_duration
                    FROM
                        TAYANGAN t
                    LEFT JOIN
                        film f ON t.id = f.id_tayangan
                ) AS ftd ON std.id_tayangan = ftd.id_tayangan
            ) AS ctd ON rn.id_tayangan = ctd.id_tayangan
            WHERE
                end_date_time >= NOW() - INTERVAL '7 days'
                AND EXTRACT(EPOCH FROM (end_date_time - start_date_time))/60 >= 0.7 * ctd.total_duration
            GROUP BY
                rn.id_tayangan
        ) AS total_view_7_days ON TAYANGAN.id = total_view_7_days.id_tayangan
        LEFT JOIN (
            SELECT
                rn.id_tayangan,
                COUNT(*) AS total_view_all_time
            FROM
                riwayat_nonton rn
            JOIN (
                SELECT
                    COALESCE(std.id_tayangan, ftd.id_tayangan) AS id_tayangan,
                    COALESCE(std.total_duration, ftd.total_duration) AS total_duration
                FROM
                    (
                        SELECT
                            t.id AS id_tayangan,
                            SUM(e.durasi) AS total_duration
                        FROM
                            TAYANGAN t
                        LEFT JOIN
                            episode e ON t.id = e.id_series
                        GROUP BY
                            t.id
                    ) AS std
                FULL OUTER JOIN (
                    SELECT
                        t.id AS id_tayangan,
                        f.durasi_film AS total_duration
                    FROM
                        TAYANGAN t
                    LEFT JOIN
                        film f ON t.id = f.id_tayangan
                ) AS ftd ON std.id_tayangan = ftd.id_tayangan
            ) AS ctd ON rn.id_tayangan = ctd.id_tayangan
            WHERE
                EXTRACT(EPOCH FROM (end_date_time - start_date_time))/60 >= 0.7 * ctd.total_duration
            GROUP BY
                rn.id_tayangan
        ) AS total_view_all_time ON TAYANGAN.id = total_view_all_time.id_tayangan
        ORDER BY
            total_view_7_days DESC,
            total_view_all_time DESC,
            TAYANGAN.release_date_trailer DESC
        LIMIT 10;
    """)

    film = query("""
        SELECT 
            id,
            judul,
            sinopsis_trailer, 
            url_video_trailer, 
            to_char(release_date_trailer, 'DD-MM-YYYY') as release_date_trailer
        FROM 
            TAYANGAN
        JOIN 
            FILM f ON f.id_tayangan = TAYANGAN.id
        GROUP BY 
            TAYANGAN.id
        ORDER BY
            TAYANGAN.judul ASC;
        """)

    series = query("""
        SELECT
            id, 
            judul,
            sinopsis_trailer, 
            url_video_trailer, 
            to_char(release_date_trailer, 'DD-MM-YYYY') as release_date_trailer
        FROM 
            TAYANGAN
        JOIN 
            SERIES s ON s.id_tayangan = TAYANGAN.id
        GROUP BY 
            TAYANGAN.id
        ORDER BY
            TAYANGAN.judul ASC;
        """)

    pengguna = query("""
        SELECT
            username,
            to_char(end_date_time, 'DD-MM-YYYY') as end_date_time
        FROM
            TRANSACTION
        WHERE end_date_time > NOW()
        ORDER BY
            username ASC;
        """)

    context.update({'tayangan': tayangan, 'trailers': top_ten,
                   'film': film, 'series': series, 'pengguna': pengguna})
    return render(request, "shows.html", context)


def tayangan_detail(request, id):
    context = {
        "is_logged_in": False
    }
    if 'username' not in request.session:
        return redirect('authentication:login')

    context["is_logged_in"] = True
    context["username"] = request.session["username"]

    # Tayangan
    tayangan = query("""
        SELECT 
            t.id,
            t.judul,
            t.sinopsis, 
            t.asal_negara, 
            COALESCE(total_view_all_time.total_view_all_time, 0) AS total_view_all_time,
            STRING_AGG(DISTINCT gt.genre, ', ') AS genre,
            ROUND(COALESCE(AVG(u.rating),0), 1) AS rating_rata_rata
        FROM
            TAYANGAN AS t
        LEFT JOIN (
            SELECT 
                id_tayangan, 
                COUNT(*) AS total_view_all_time
            FROM 
                riwayat_nonton
            GROUP BY 
                id_tayangan
        ) AS total_view_all_time ON t.id = total_view_all_time.id_tayangan
        LEFT JOIN genre_tayangan AS gt ON t.id = gt.id_tayangan
        LEFT JOIN ULASAN AS u ON t.id = u.id_tayangan
        WHERE
            id = %s
        GROUP BY
            t.id,t.judul, t.sinopsis, t.asal_negara, total_view_all_time.total_view_all_time;
        """, (id,))

    # Film
    film = query("""
        SELECT
            durasi_film,
            release_date_film,
            url_video_film
        FROM 
            FILM
        LEFT JOIN tayangan t ON t.id = film.id_tayangan
        WHERE
            id_tayangan = %s;
        """, (id,))

    release_film = query("""
        SELECT
            id_tayangan, release_date_film
        FROM film
        WHERE
            release_date_film <= CURRENT_DATE;
        """)

    pemain = query("""
        SELECT
            nama
        FROM 
            CONTRIBUTORS
        LEFT JOIN memainkan_tayangan mt ON mt.id_pemain = CONTRIBUTORS.id
        LEFT JOIN tayangan t ON t.id = mt.id_tayangan
        WHERE
            t.id = %s
        GROUP BY
            nama;
        """, (id,))

    penulis = query("""
        SELECT
            nama
        FROM 
            CONTRIBUTORS
        LEFT JOIN menulis_skenario_tayangan ms ON ms.id_penulis_skenario = CONTRIBUTORS.id
        LEFT JOIN tayangan t ON t.id = ms.id_tayangan
        WHERE
            t.id = %s
        GROUP BY
            nama;
        """, (id,))

    sutradara = query("""
        SELECT
            nama
        FROM 
            CONTRIBUTORS
        LEFT JOIN sutradara s ON s.id = CONTRIBUTORS.id
        LEFT JOIN tayangan t ON t.id_sutradara = s.id
        WHERE
            t.id = %s
        GROUP BY
            nama;
        """, (id,))

    episode = query("""
        SELECT
            t.id,
            e.sub_judul,
            t.judul
        FROM episode e
        LEFT JOIN tayangan t ON t.id= e.id_series
        WHERE
            t.id = %s
        ORDER BY
            e.sub_judul ASC;
        """, (id,))

    ulasan = query("""
        SELECT 
            username,
            deskripsi,
            rating
        FROM ULASAN
        LEFT JOIN tayangan t ON t.id = ULASAN.id_tayangan
        WHERE
            t.id = %s
        ORDER BY
            ulasan.timestamp DESC;
        """, (id,))

    # Query untuk mengecek apakah judul ada di tabel film
    is_film = query("""
        SELECT EXISTS (
            SELECT 1 FROM FILM WHERE id_tayangan = (
                SELECT id FROM TAYANGAN WHERE id = %s
            )
        )
    """, (id,))[0]

    context.update({'tayangan': tayangan})
    if pemain:
        context.update({'pemain': pemain})

    if penulis:
        context.update({'penulis': penulis})

    if sutradara:
        context.update({'sutradara': sutradara})

    if ulasan:
        context.update({'ulasan': ulasan})

    # Cek apakah Film atau Series
    if is_film['exists']:
        context.update({'film': film, 'release_film': release_film})
        template_name = 'film_detail.html'
    else:
        context.update({'episode': episode})
        template_name = 'series_detail.html'

    return render(request, template_name, context)


def episode_detail(request, id, sub_judul):
    context = {
        "is_logged_in": False
    }
    if 'username' not in request.session:
        return redirect('authentication:login')

    context["is_logged_in"] = True
    context["username"] = request.session["username"]

    episode_khusus = query("""
        SELECT
            e.sub_judul,
            t.judul,
            e.sinopsis,
            e.durasi,
            e.url_video,
            e.release_date
        FROM episode e
        LEFT JOIN tayangan t ON t.id= e.id_series
        WHERE
            t.id = %s AND
            e.sub_judul = %s
        ORDER BY
            e.sub_judul ASC;
        """, (id, sub_judul))

    episode = query("""
        SELECT
            t.id,
            e.sub_judul,
            t.judul
        FROM episode e
        LEFT JOIN tayangan t ON t.id= e.id_series
        WHERE
            t.id = %s
        ORDER BY
            e.sub_judul ASC;
        """, (id,))

    release_episode = query("""
        SELECT
            id_series,sub_judul,release_date
        FROM EPISODE e
        LEFT JOIN SERIES s ON s.id_tayangan = e.id_series
        WHERE 
            e.release_date <= CURRENT_DATE;
        """)
    context.update({'episode': episode, 'episode_khusus': episode_khusus,
                   'release_episode': release_episode})
    return render(request, "episode_detail.html", context)


@csrf_exempt
def save_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        deskripsi = data['deskripsi']
        rating = data['rating']
        id_tayangan = data['id_tayangan']
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lakukan penyisipan data ke dalam basis data
        try:
            data = query("""
                INSERT INTO ulasan (
                    id_tayangan,
                    username, 
                    timestamp, 
                    rating,
                    deskripsi
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                         (
                             id_tayangan,
                             request.session.get("username", ""),
                             timestamp,
                             rating,
                             deskripsi
                         )
                         )
            if isinstance(data, psycopg2.errors.RaiseException):
                error_msg = str(data).split("\n")[0]
                return JsonResponse({"status": "error", "message": error_msg}, status=400)
            else:
                return JsonResponse({"status": "success", "message": "Review added successfully."}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)


def update_review(request, id):
    ulasan = query("""
        SELECT username, deskripsi, rating
        FROM ULASAN
        LEFT JOIN tayangan t ON t.id = ULASAN.id_tayangan
        WHERE t.id = %s
        ORDER BY ulasan.timestamp DESC;
    """, (id,))

    return JsonResponse({'ulasan': ulasan}, content_type='application/json')


@csrf_exempt
def save_watching_history(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id_tayangan = data['id_tayangan']
        username = request.session.get("username", "")
        start_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        watching_percentage = float(data['watching_percentage'])

        try:
            film = query(
                "SELECT durasi_film AS durasi FROM FILM f WHERE f.id_tayangan = %s", (id_tayangan,))
            if film:
                durasi = film[0]['durasi']
            if not film:
                series = query(
                    "SELECT SUM(e.durasi) AS durasi FROM EPISODE e WHERE e.id_series = %s", (id_tayangan,))
                durasi = series[0]['durasi']

            watching_seconds = (watching_percentage / 100) * (durasi * 60)

            start_datetime = datetime.datetime.strptime(
                start_date_time, "%Y-%m-%d %H:%M:%S")
            end_datetime = start_datetime + \
                datetime.timedelta(seconds=watching_seconds)
            end_date_time = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

            query("""
                INSERT INTO riwayat_nonton (id_tayangan, username, start_date_time, end_date_time)
                VALUES (%s, %s, %s, %s);
                """,
                  (id_tayangan, username, start_date_time, end_date_time)
                  )
            return JsonResponse({"status": "success", "message": "Watching history saved successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
