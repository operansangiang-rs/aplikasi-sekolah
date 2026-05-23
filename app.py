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
    # Buat tabel informasi/pengumuman
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
    # Buat tabel jadwal pelajaran
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
    # Buat tabel pengaturan PPDB
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ppdb (
        id INTEGER PRIMARY KEY,
        status TEXT,
        syarat TEXT,
        biaya TEXT,
        kontak TEXT
    )
    """)
    # Buat tabel profil sekolah
    conn.execute("""
    CREATE TABLE IF NOT EXISTS profil (
        id INTEGER PRIMARY KEY,
        nama_sekolah TEXT,
        visi_misi TEXT,
        fasilitas TEXT,
        alamat_kontak TEXT
    )
    """)
    
    c = conn.cursor()
    # Isi data default PPDB jika kosong
    c.execute("SELECT COUNT(*) FROM ppdb")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO ppdb (id, status, syarat, biaya, kontak)
            VALUES (1, 'DIBUKA', '1. Mengisi Formulir\n2. Fotokopi Akta Kelahiran & KK\n3. Pas Foto 3x4', 'Pendaftaran Gratis', 'Hubungi Tata Usaha (021-xxxxxx)')
        """)
    # Isi data default Profil Sekolah jika kosong
    c.execute("SELECT COUNT(*) FROM profil")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO profil (id, nama_sekolah, visi_misi, fasilitas, alamat_kontak)
            VALUES (1, 'SDN SINDANGSARI', 'VISI:\nUnggul dalam Prestasi, Berkarakter, dan Berbudaya Lingkungan.\n\nMISI:\n1. Menyelenggarakan pendidikan yang berkualitas.\n2. Menanamkan nilai keimanan dan ketakwaan.\n3. Mengembangkan potensi minat dan bakat siswa.', '1. Ruang Kelas Nyaman\n2. Lapangan Olahraga\n3. Perpustakaan Digital\n4. Laboratorium Komputer', 'Alamat: Jl. Raya Sindangsari\nNo. HP / WA: 08xx-xxxx-xxxx\nEmail: info@sdnsindangsari.sch.id')
        """)
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# ==========================================
# 🔐 LOGIKA HAK AKSES DAN PASSWORD
# ==========================================
st.sidebar.title("🔑 Akses Pengguna")
status_login = st.sidebar.selectbox(
    "Masuk Sebagai:", 
    ["🌐 UMUM (PROFIL & PPDB)", "👨‍👩‍👧 ORANG TUA / SISWA", "👨‍🏫 GURU / STAFF", "🛠️ ADMIN UTAMA"]
)

# Status default hak akses menu internal (Jadwal & Pengumuman)
buka_menu_internal = False
is_admin = False
is_guru = False

if status_login == "👨‍👩‍👧 ORANG TUA / SISWA":
    pass_ortu = st.sidebar.text_input("Masukkan Password Ortu/Siswa", type="password")
    if pass_ortu == "2222":
        st.sidebar.success("🔓 Akses Ortu & Siswa Terbuka!")
        buka_menu_internal = True
    else:
        if pass_ortu != "":
            st.sidebar.error("❌ Password Salah!")

elif status_login == "🛠️ ADMIN UTAMA":
    password = st.sidebar.text_input("Masukkan Password Admin", type="password")
    if password == "1234":
        st.sidebar.success("🔓 Mode Admin Aktif!")
        is_admin = True
        buka_menu_internal = True  # Admin otomatis bisa melihat semua tab
    else:
        if password != "":
            st.sidebar.error("❌ Password Salah!")

elif status_login == "👨‍🏫 GURU / STAFF":
    st.sidebar.info("Akses Guru aktif otomatis.")
    is_guru = True
    buka_menu_internal = True

else:
    st.sidebar.info("Gunakan menu ini jika Anda ingin masuk sebagai Wali Murid, Guru, atau Admin.")

st.sidebar.divider()
st.sidebar.write(f"⏱️ **Waktu Sistem:** {waktu_sekarang}")

# ==========================================
# 📱 STRUKTUR TABS MENU UTAMA (DINAMIS)
# ==========================================
# Profil Sekolah dan PPDB sekarang SELALU BISA diakses oleh Publik/Umum saat pertama buka
daftar_tab = ["🏫 Profil Sekolah", "📝 Pendaftaran Siswa Baru (PPDB)"]

# Jika login sukses (Admin/Guru/Ortu), sisipkan menu internal di tengah-tengah
if buka_menu_internal:
    daftar_tab.insert(1, "📢 Informasi & Pengumuman")
    daftar_tab.insert(2, "📅 Jadwal Pelajaran")

# Selalu tampilkan tab Kelola Admin di paling ujung (terkunci jika bukan admin)
daftar_tab.append("🛠️ Menu Kelola Admin")

menu_utama = st.tabs(daftar_tab)

# --- TAB 0: PROFIL SEKOLAH (SELALU AKTIF) ---
with menu_utama[0]:
    c.execute("SELECT nama_sekolah, visi_misi, fasilitas, alamat_kontak FROM profil WHERE id=1")
    p_nama, p_visimisi, p_fasilitas, p_kontak_sekolah = c.fetchone()
    
    st.subheader(f"✨ Selamat Datang di {p_nama}")
    st.write("Mengenal lebih dekat lingkungan, visi misi, dan fasilitas pendidikan di sekolah kami.")
    
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        with st.container(border=True):
            st.markdown("### 🎯 Visi & Misi")
            st.write(p_visimisi)
            
        with st.container(border=True):
            st.markdown("### 📞 Hubungi & Alamat Kami")
            st.info(p_kontak_sekolah)
            
    with col_prof2:
        with st.container(border=True):
            st.markdown("### 🧪 Fasilitas Sekolah")
            st.write(p_fasilitas)

# Index pelacak tab dinamis
index_skrg = 1

# --- KONTEN JIKA USER SUDAH LOGIN (MENU INTERNAL) ---
if buka_menu_internal:
    # --- TAB 1: INFORMASI SEKOLAH ---
    with menu_utama[index_skrg]:
        st.subheader("📢 Informasi & Pengumuman Sekolah")
        df_info = pd.read_sql_query("SELECT * FROM informasi ORDER BY tanggal DESC", conn)
        
        if df_info.empty:
            st.info("Belum ada pengumuman atau informasi terbaru yang diterbitkan oleh Admin.")
        else:
            for _, r in df_info.iterrows():
                with st.container(border=True):
                    st.markdown(f"### {r['judul']}")
                    st.caption(f"📅 Ditulis pada: {r['tanggal']} | Kategori: **{r['kategori']}** | Oleh: {r['penulis']}")
                    st.markdown(f"{r['konten']}")
    index_skrg += 1

    # --- TAB 2: JADWAL PELAJARAN ---
    with menu_utama[index_skrg]:
        st.subheader("📅 Jadwal Pelajaran Interaktif")
        df_jadwal = pd.read_sql_query("SELECT * FROM jadwal ORDER BY hari, jam_mulai ASC", conn)
        
        if df_jadwal.empty:
            st.info("Jadwal pelajaran belum dimasukkan oleh Admin.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                list_hari = ["Semua Hari", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                filter_hari = st.selectbox("Filter Hari", list_hari)
            with col_f2:
                list_kelas = ["Semua Kelas"] + sorted(list(df_jadwal['kelas'].unique()))
                filter_kelas = st.selectbox("Filter Kelas", list_kelas)
                
            query_filter = df_jadwal.copy()
            if filter_hari != "Semua Hari":
                query_filter = query_filter[query_filter['hari'] == filter_hari]
            if filter_kelas != "Semua Kelas":
                query_filter = query_filter[query_filter['kelas'] == filter_kelas]
                
            if query_filter.empty:
                st.warning("Tidak ada jadwal pelajaran yang cocok dengan filter terpilih.")
            else:
                st.dataframe(query_filter, use_container_width=True, hide_index=True)
    index_skrg += 1

# --- TAB PPDB (SELALU AKTIF UNTUK UMUM) ---
with menu_utama[index_skrg]:
    st.subheader("📝 Informasi Penerimaan Peserta Didik Baru (PPDB)")
    c.execute("SELECT status, syarat, biaya, kontak FROM ppdb WHERE id=1")
    p_status, p_syarat, p_biaya, p_kontak = c.fetchone()
    
    if p_status == "DIBUKA":
        st.success("🟢 STATUS PPDB: **%s**" % p_status)
    else:
        st.error("🔴 STATUS PPDB: **%s**" % p_status)
        
    col_ppdb1, col_ppdb2 = st.columns(2)
    with col_ppdb1:
        with st.container(border=True):
            st.markdown("### 📋 Persyaratan Dokumen")
            st.write(p_syarat)
    with col_ppdb2:
        with st.container(border=True):
            st.markdown("### 💰 Informasi Biaya & Investasi Pendidikan")
            st.write(p_biaya)
            
    with st.container(border=True):
        st.markdown("### 📞 Alur Pendaftaran & Kontak Informasi")
        st.info(p_kontak)
index_skrg += 1

# --- TAB TERAKHIR: PANEL CONTROL ADMIN ---
with menu_utama[index_skrg]:
    if not is_admin:
        st.warning("🔒 **Akses Terbatas!** Menu Kelola Admin ini dikunci. Silakan pilih status login sebagai **ADMIN UTAMA** di sidebar dan masukkan password yang benar untuk membukanya.")
    else:
        st.subheader("🛠️ Dashboard Manajemen Admin")
        st.markdown("Selamat datang di panel kontrol sekolah. Silakan pilih menu di bawah ini untuk mengubah data aplikasi secara global.")
        
        sub_menu = st.radio(
            "Pilih Objek Kelola:", 
            ["📝 Tulis Informasi Baru", "📅 Atur Jadwal Pelajaran", "⚙️ Atur Info Pendaftaran (PPDB)", "🏫 Edit Profil Sekolah"], 
            horizontal=True
        )
        st.divider()
        
        # --- FORM INPUT INFORMASI ---
        if sub_menu == "📝 Tulis Informasi Baru":
            with st.form("form_tambah_info", clear_on_submit=True):
                st.write("### Buat Pengumuman Baru")
                t_judul = st.text_input("Judul Informasi / Pengumuman")
                t_kat = st.selectbox("Kategori", ["Akademik", "Kegiatan Sekolah", "Keuangan", "PPDB / Kelulusan", "Umum"])
                t_konten = st.text_area("Isi Konten Informasi", height=150)
                t_penulis = st.text_input("Nama Penulis/Bagian")
                
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
                    j_kelas = st.text_input("Kelas (Contoh: 1-A, X-RPL-1)")
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

        # --- FORM EDIT CONFIG PPDB ---
        elif sub_menu == "⚙️ Atur Info Pendaftaran (PPDB)":
            st.write("### ⚙️ Edit Halaman Informasi Pendaftaran Siswa Baru")
            c.execute("SELECT status, syarat, biaya, kontak FROM ppdb WHERE id=1")
            curr_status, curr_syarat, curr_biaya, curr_kontak = c.fetchone()
            
            with st.form("form_edit_ppdb"):
                adm_status = st.selectbox("Status Pembukaan PPDB", ["DIBUKA", "DITUTUP"], index=0 if curr_status == "DIBUKA" else 1)
                adm_syarat = st.text_area("Syarat Pendaftaran", value=curr_syarat, height=150)
                adm_biaya = st.text_area("Rincian Biaya Masuk", value=curr_biaya, height=150)
                adm_kontak = st.text_area("Alur Pendaftaran / Kontak Panitia", value=curr_kontak, height=120)
                
                submit_ppdb = st.form_submit_button("Simpan Perubahan PPDB")
                
                if submit_ppdb:
                    c.execute("""
                        UPDATE ppdb SET status=?, syarat=?, biaya=?, kontak=? WHERE id=1
                    """, (adm_status, adm_syarat.strip(), adm_biaya.strip(), adm_kontak.strip()))
                    conn.commit()
                    st.success("🎉 Informasi PPDB berhasil diperbarui secara global!")
                    time.sleep(1)
                    st.rerun()

        # --- FORM EDIT PROFIL SEKOLAH ---
        elif sub_menu == "🏫 Edit Profil Sekolah":
            st.write("### 🏫 Edit Ruang Informasi Profil Sekolah")
            c.execute("SELECT nama_sekolah, visi_misi, fasilitas, alamat_kontak FROM profil WHERE id=1")
            curr_nama, curr_visimisi, curr_fasilitas, curr_alamat = c.fetchone()
            
            with st.form("form_edit_profil"):
                adm_nama = st.text_input("Nama Resmi Sekolah", value=curr_nama)
                adm_visimisi = st.text_area("Visi & Misi Sekolah", value=curr_visimisi, height=150)
                adm_fasilitas = st.text_area("Fasilitas Unggulan Sekolah", value=curr_fasilitas, height=150)
                adm_alamat = st.text_area("Alamat Lengkap & Kontak Resmi", value=curr_alamat, height=120)
                
                submit_prof = st.form_submit_button("Simpan Pembaruan Profil")
                
                if submit_prof:
                    if not adm_nama.strip():
                        st.error("❌ Nama sekolah tidak boleh dikosongkan!")
                    else:
                        c.execute("""
                            UPDATE profil 
                            SET nama_sekolah=?, visi_misi=?, fasilitas=?, alamat_kontak=? 
                            WHERE id=1
                        """, (adm_nama.strip().upper(), adm_visimisi.strip(), adm_fasilitas.strip(), adm_alamat.strip()))
                        conn.commit()
                        st.success("🎉 Profil sekolah berhasil diperbarui secara global!")
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
