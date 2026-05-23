import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import pytz
import time

# ==========================================
# CONFIG Halaman Utama Aplikasi Sekolah
# ==========================================
st.set_page_config(
    page_title="Sistem Informasi Aplikasi Sekolah",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 Sistem Informasi & Aplikasi Sekolah")
st.markdown("---")

# ==========================================
# ⏱️ TIMEZONE INDONESIA
# ==========================================
jakarta = pytz.timezone("Asia/Jakarta")
waktu_sekarang = datetime.now(jakarta).strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# 💾 KONEKSI & PEMBUATAN DATABASE OTOMATIS
# ==========================================
@st.cache_resource
def init_db():
    conn = sqlite3.connect("sekolah.db", check_same_thread=False)
    # Buat tabel informasi/pengumuman jika belum ada
    conn.execute("""
    CREATE TABLE IF NOT EXISTS informasi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        judul TEXT,
        konten TEXT,
        kategori TEXT,
        penulis TEXT
    )
    """)
    # Buat tabel jadwal pelajaran jika belum ada
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jadwal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hari TEXT,
        kelas TEXT,
        jam_mulai TEXT,
        jam_selesai TEXT,
        mata_pelajaran TEXT,
        guru_pengajar TEXT
    )
    """)
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# ==========================================
# 🔐 HAK AKSES / LOGIN SIMPEL DI SIDEBAR
# ==========================================
st.sidebar.title("🔑 Akses Pengguna")
status_login = st.sidebar.selectbox(
    "Masuk Sebagai:", 
    ["👨‍👩‍👧 GUEST / ORANG TUA", "👨‍🏫 GURU / STAFF", "🛠️ ADMIN UTAMA"]
)

is_admin = False
is_guru = False

if status_login == "🛠️ ADMIN UTAMA":
    password = st.sidebar.text_input("Masukkan Password Admin", type="password")
    if password == "adminsekolah2026":  # Password admin utama aplikasi
        st.sidebar.success("🔓 Mode Admin Aktif!")
        is_admin = True
    else:
        if password != "":
            st.sidebar.error("❌ Password Salah!")

elif status_login == "👨‍🏫 GURU / STAFF":
    st.sidebar.info("Akses Guru: Anda dapat melihat seluruh data dan menginput presensi/catatan harian.")
    is_guru = True
else:
    st.sidebar.info("Akses Orang Tua/Umum: Hanya dapat melihat Informasi Sekolah dan Jadwal Pelajaran.")

st.sidebar.divider()
st.sidebar.write(f"⏱️ **Waktu Sistem:** {waktu_sekarang}")

# ==========================================
# 📱 STRUKTUR MENU UTAMA (TABS)
# ==========================================
menu_utama = st.tabs(["📢 Informasi & Pengumuman", "📅 Jadwal Pelajaran", "🛠️ Menu Kelola Admin"])

# --- TAB 1: INFORMASI SEKOLAH ---
with menu_utama[0]:
    st.subheader("📢 Informasi & Pengumuman Sekolah")
    st.write("Halaman ini menampilkan pengumuman resmi dari pihak sekolah untuk orang tua murid dan guru.")
    
    # Ambil data informasi dari database
    df_info = pd.read_sql_query("SELECT * FROM informasi ORDER BY tanggal DESC", conn)
    
    if df_info.empty:
        st.info("Belum ada pengumuman atau informasi terbaru yang diterbitkan oleh Admin.")
    else:
        for _, r in df_info.iterrows():
            with st.container(border=True):
                st.markdown(f"### {r['judul']}")
                st.caption(f"📅 Ditulis pada: {r['tanggal']} | Kategori: **{r['kategori']}** | Oleh: {r['penulis']}")
                st.markdown(f"{r['konten']}")

# --- TAB 2: JADWAL PELAJARAN ---
with menu_utama[1]:
    st.subheader("📅 Jadwal Pelajaran Interaktif")
    
    # Ambil semua data jadwal pelajaran
    df_jadwal = pd.read_sql_query("SELECT * FROM jadwal ORDER BY hari, jam_mulai ASC", conn)
    
    if df_jadwal.empty:
        st.info("Jadwal pelajaran belum dimasukkan oleh Admin.")
    else:
        # Filter interaktif untuk memudahkan pencarian kelas atau hari
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            list_hari = ["Semua Hari", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
            filter_hari = st.selectbox("Filter Hari", list_hari)
        with col_f2:
            list_kelas = ["Semua Kelas"] + sorted(list(df_jadwal['kelas'].unique()))
            filter_kelas = st.selectbox("Filter Kelas", list_kelas)
            
        # Logika pemfilteran data dataframe
        query_filter = df_jadwal.copy()
        if filter_hari != "Semua Hari":
            query_filter = query_filter[query_filter['hari'] == filter_hari]
        if filter_kelas != "Semua Kelas":
            query_filter = query_filter[query_filter['kelas'] == filter_kelas]
            
        if query_filter.empty:
            st.warning("Tidak ada jadwal pelajaran yang cocok dengan filter terpilih.")
        else:
            st.dataframe(query_filter, use_container_width=True, hide_index=True)

# --- TAB 3: KELOLA DATA (HANYA UNTUK ADMIN) ---
with menu_utama[2]:
    if not is_admin:
        st.warning("🔒 **Akses Terbatas!** Menu Kelola Admin ini dikunci. Silakan pilih status login sebagai **ADMIN UTAMA** di sidebar dan masukkan password yang benar untuk membukanya.")
    else:
        st.subheader("🛠️ Dashboard Manajemen Admin")
        st.markdown("Selamat datang di panel kontrol sekolah. Silakan pilih menu di bawah ini untuk menambah atau mengubah informasi.")
        
        sub_menu = st.radio(
            "Pilih Objek Kelola:", 
            ["📝 Tulis Informasi Baru", "📅 Atur Jadwal Pelajaran"], 
            horizontal=True
        )
        st.divider()
        
        # --- FORM INPUT INFORMASI ---
        if sub_menu == "📝 Tulis Informasi Baru":
            with st.form("form_tambah_info", clear_on_submit=True):
                st.write("### Buat Pengumuman Baru")
                t_judul = st.text_input("Judul Informasi / Pengumuman")
                t_kat = st.selectbox("Kategori", ["Akademik", "Kegiatan Sekolah", "Keuangan", "Umum"])
                t_konten = st.text_area("Isi Konten Informasi", height=150)
                t_penulis = st.text_input("Nama Penulis/Bagian (Contoh: Humas / Kepala Sekolah)")
                
                submit_info = st.form_submit_button("Publish Pengumuman")
                
                if submit_info:
                    if not (t_judul.strip() and t_konten.strip() and t_penulis.strip()):
                        st.error("❌ Gagal mempublikasikan! Semua kolom wajib diisi.")
                    else:
                        c.execute("""
                            INSERT INTO informasi (tanggal, judul, konten, kategori, penulis)
                            VALUES (?, ?, ?, ?, ?)
                        """, (waktu_sekarang, t_judul.strip(), t_konten.strip(), t_kat, t_penulis.strip()))
                        conn.commit()
                        st.success("🎉 Pengumuman baru berhasil diterbitkan secara global!")
                        time.sleep(1)
                        st.rerun()
                        
        # --- FORM INPUT JADWAL ---
        elif sub_menu == "📅 Atur Jadwal Pelajaran":
            with st.form("form_tambah_jadwal", clear_on_submit=True):
                st.write("### Tambah Jadwal Pelajaran")
                col_j1, col_j2 = st.columns(2)
                with col_j1:
                    j_hari = st.selectbox("Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
                    j_kelas = st.text_input("Kelas (Contoh: 1-A, X-RPL-1, 7-B)")
                    j_mapel = st.text_input("Mata Pelajaran")
                with col_j2:
                    j_mulai = st.text_input("Jam Mulai (Contoh: 07:00)")
                    j_selesai = st.text_input("Jam Selesai (Contoh: 08:30)")
                    j_guru = st.text_input("Nama Guru Pengajar")
                    
                submit_jadwal = st.form_submit_button("Simpan Jadwal")
                
                if submit_jadwal:
                    if not (j_kelas.strip() and j_mapel.strip() and j_mulai.strip() and j_selesai.strip() and j_guru.strip()):
                        st.error("❌ Gagal menyimpan jadwal! Pastikan seluruh data input telah terisi.")
                    else:
                        c.execute("""
                            INSERT INTO jadwal (hari, kelas, jam_mulai, jam_selesai, mata_pelajaran, guru_pengajar)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (j_hari, j_kelas.strip().upper(), j_mulai.strip(), j_selesai.strip(), j_guru.strip()))
                        conn.commit()
                        st.success("🎉 Jadwal pelajaran berhasil disimpan ke sistem!")
                        time.sleep(1)
                        st.rerun()

# ==========================================
# FOOTER APLIKASI
# ==========================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px;'>"
    "🏫 Aplikasi Sistem Informasi Sekolah Global<br>"
    "Developed by Mas Lian © All Rights Reserved"
    "</div>",
    unsafe_allow_html=True
)
