from django.shortcuts import render
from utils.query import query

def show_tayangan(request):
    context = {
        "is_logged_in": False
    }
    if "username" in request.session:
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
                id_tayangan, 
                COUNT(*) AS total_view_7_days
            FROM 
                riwayat_nonton
            WHERE 
                end_date_time >= NOW() - INTERVAL '7 days'
            GROUP BY 
                id_tayangan
        ) AS total_view_7_days ON TAYANGAN.id = total_view_7_days.id_tayangan
        LEFT JOIN (
            SELECT 
                id_tayangan, 
                COUNT(*) AS total_view_all_time
            FROM 
                riwayat_nonton
            GROUP BY 
                id_tayangan
        ) AS total_view_all_time ON TAYANGAN.id = total_view_all_time.id_tayangan
        ORDER BY 
            total_view_all_time DESC,
            TAYANGAN.release_date_trailer DESC
        LIMIT 10;
    """)
    
    film = query("""
        SELECT 
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
            end_date_time
        FROM
            TRANSACTION
        WHERE end_date_time > NOW()
        ORDER BY
            username ASC;
        """)
    
    
    context.update({'tayangan': tayangan, 'trailers': top_ten, 'film': film, 'series': series, 'pengguna': pengguna})
    return render(request, "shows.html", context)

def tayangan_detail(request):
    context = []
    return render(request, 'tayangan_detail.html', context)