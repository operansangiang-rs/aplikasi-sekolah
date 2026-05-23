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
    # Tabel Informasi
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
    # Tabel Kelas Aktif (Dinamis Baru)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS kelas_aktif (
        nama_kelas TEXT PRIMARY KEY
    )
    """)
    # Tabel Jadwal Pelajaran
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
    # Tabel PPDB
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ppdb (
        id INTEGER PRIMARY KEY,
        status TEXT,
        syarat TEXT,
        biaya TEXT,
        kontak TEXT
    )
    """)
    # Tabel Profil Sekolah
    conn.execute("""
    CREATE TABLE IF NOT EXISTS profil (
        id INTEGER PRIMARY KEY,
        nama_sekolah TEXT,
        visi_misi TEXT,
        fasilitas TEXT,
        alamat_kontak TEXT
    )
    """)
    # Tabel Nilai Siswa
    conn.execute("""
    CREATE TABLE IF NOT EXISTS nilai (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nisn TEXT,
        nama_siswa TEXT,
        kelas TEXT,
        mata_pelajaran TEXT,
        nilai_tugas REAL,
        nilai_uts REAL,
        nilai_uas REAL,
        nilai_akhir REAL,
        keterangan TEXT
    )
    """)
    # Tabel E-Book Pelajaran
    conn.execute("""
    CREATE TABLE IF NOT EXISTS ebook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kelas TEXT,
        mata_pelajaran TEXT,
        judul_buku TEXT,
        link_download TEXT,
        pengunggah TEXT
    )
    """)
    # Tabel Keuangan / SPP Siswa
    conn.execute("""
    CREATE TABLE IF NOT EXISTS keuangan (
        nisn TEXT PRIMARY KEY,
        nama_siswa TEXT,
        kelas TEXT,
        total_biaya REAL,
        sudah_dibayar REAL,
        status_bayar TEXT,
        keterangan_lunas TEXT
    )
    """)
    
    c = conn.cursor()
    # Data Default Kelas Aktif jika kosong
    c.execute("SELECT COUNT(*) FROM kelas_aktif")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO kelas_aktif (nama_kelas) VALUES (?)", [
            ('KELAS 1',), ('KELAS 2',), ('KELAS 3',), ('KELAS 4',), ('KELAS 5',), ('KELAS 6',)
        ])
    # Data Default PPDB
    c.execute("SELECT COUNT(*) FROM ppdb")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO ppdb (id, status, syarat, biaya, kontak)
            VALUES (1, 'DIBUKA', '1. Mengisi Formulir\n2. Fotokopi Akta Kelahiran & KK\n3. Pas Foto 3x4', 'Pendaftaran Gratis', 'Hubungi Tata Usaha (021-xxxxxx)')
        """)
    # Data Default Profil Sekolah
    c.execute("SELECT COUNT(*) FROM profil")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO profil (id, nama_sekolah, visi_misi, fasilitas, alamat_kontak)
            VALUES (1, 'SDN SINDANGSARI', 'VISI:\nUnggul dalam Prestasi, Berkarakter, dan Berbudaya Lingkungan.\n\nMISI:\n1. Menyelenggarakan pendidikan yang berkualitas.\n2. Menanamkan nilai keimanan dan ketakwaan.\n3. Mengembangkan potensi minat dan bakat siswa.', '1. Ruang Kelas Nyaman\n2. Lapangan Olahraga\n3. Perpustakaan Digital\n4. Laboratorium Komputer', 'Alamat: Jl. Raya Sindangsari\nNo. HP / WA: 08xx-xxxx-xxxx\nEmail: info@sdnsindangsari.sch.id')
        """)
    # Data Sampel E-Book jika kosong
    c.execute("SELECT COUNT(*) FROM ebook")
    if c.fetchone()[0] == 0:
        c.executemany("""
            INSERT INTO ebook (kelas, mata_pelajaran, judul_buku, link_download, pengunggah)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ('KELAS 3', 'MATEMATIKA', 'Buku Siswa Matematika Kelas 3 SD - Kurikulum Merdeka', 'https://drive.google.com', 'Guru Kelas 3'),
            ('KELAS 3', 'IPA', 'Buku Paket Ilmu Pengetahuan Alam Semester 1 Kelas 3', 'https://drive.google.com', 'Guru IPA')
        ])
    # Data Sampel Keuangan jika kosong
    c.execute("SELECT COUNT(*) FROM keuangan")
    if c.fetchone()[0] == 0:
        c.executemany("""
            INSERT INTO keuangan (nisn, nama_siswa, kelas, total_biaya, sudah_dibayar, status_bayar, keterangan_lunas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ('12345', 'ALDI PRATAMA', 'KELAS 3', 1200000, 1200000, 'LUNAS', 'Lunas sampai bulan Juni 2026'),
            ('54321', 'SITI AMINAH', 'KELAS 3', 1200000, 800000, 'BELUM LUNAS', 'Baru bayar sampai bulan April 2026')
        ])
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()

# Ambil list kelas terupdate untuk dropdown form
c.execute("SELECT nama_kelas FROM kelas_aktif ORDER BY nama_kelas ASC")
list_kelas_db = [row[0] for row in c.fetchall()]
if not list_kelas_db:
    list_kelas_db = ["KELAS 1"] # Pengaman jika data kosong total

# ==========================================
# 🗂️ FUNCTION UNTUK MENAMPILKAN EKSKUL & UNGGULAN
# ==========================================
def tampilkan_ekskul_dan_unggulan():
    st.markdown("---")
    col_unggul, col_ekskul = st.columns(2)
    with col_unggul:
        st.markdown("### 🏆 Program & Prestasi Unggulan")
        with st.container(border=True):
            st.markdown("⭐ **Pembiasaan Karakter & Imtaq**")
            st.caption("Sholat berjamaah rutin, hafalan Juz Amma, dan pembentukan akhlak mulia sejak dini.")
        with st.container(border=True):
            st.markdown("⭐ **Juara Kompetisi Sains & Digitalisasi**")
            st.caption("Pemanfaatan sistem digital belajar pintar terpadu dan juara kompetisi cerdas cermat.")
    with col_ekskul:
        st.markdown("### 🏹 Kegiatan Ekstrakurikuler (Ekskul)")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.info("⚽ Futsal & Sepakbola")
            st.info("⛺ Pramuka Inti")
            st.info("🤖 Klub IT / Robotik")
        with col_e2:
            st.success("🥋 Pencak Silat")
            st.success("🎨 Seni Tari & Musik")
            st.success("🩺 Dokter Kecil / UKS")

# ==========================================
# 🔐 LOGIKA HAK AKSES DAN PASSWORD
# ==========================================
st.sidebar.title("🔑 Akses Pengguna")
status_login = st.sidebar.selectbox(
    "Masuk Sebagai:", 
    ["🌐 UMUM (PROFIL & PPDB)", "👨‍👩‍👧 ORANG TUA / SISWA", "👨‍🏫 GURU / STAFF", "🛠️ ADMIN UTAMA"]
)

is_ortu_siswa = False
is_admin = False
is_guru = False
akses_sukses = False

if status_login == "👨‍👩‍👧 ORANG TUA / SISWA":
    pass_ortu = st.sidebar.text_input("Masukkan Password Ortu/Siswa", type="password")
    if pass_ortu == "2222":
        st.sidebar.success("🔓 Akses Ortu & Siswa Terbuka!")
        is_ortu_siswa = True
        akses_sukses = True
    else:
        if pass_ortu != "":
            st.sidebar.error("❌ Password Salah!")

elif status_login == "👨‍🏫 GURU / STAFF":
    pass_guru = st.sidebar.text_input("Masukkan Password Guru", type="password")
    if pass_guru == "3333":
        st.sidebar.success("🔓 Akses Guru Aktif!")
        is_guru = True
        akses_sukses = True
    else:
        if pass_guru != "":
            st.sidebar.error("❌ Password Salah!")

elif status_login == "🛠️ ADMIN UTAMA":
    password = st.sidebar.text_input("Masukkan Password Admin", type="password")
    if password == "1234":
        st.sidebar.success("🔓 Mode Admin Aktif!")
        is_admin = True
        akses_sukses = True
    else:
        if password != "":
            st.sidebar.error("❌ Password Salah!")

else:
    st.sidebar.info("Silakan ganti status login jika Anda adalah Wali Murid, Guru, atau Admin.")

st.sidebar.divider()
st.sidebar.write(f"⏱️ **Waktu Sistem:** {waktu_sekarang}")

# ==========================================
# 📱 STRUKTUR TABS MENU UTAMA (DINAMIS)
# ==========================================
if is_ortu_siswa:
    daftar_tab = ["📊 Transkrip Nilai Siswa", "📚 E-Book Pelajaran Digital", "💰 Status Pembayaran Sekolah", "📅 Jadwal Pelajaran", "📢 Informasi & Ekskul Sekolah"]
elif is_admin or is_guru:
    daftar_tab = ["🏫 Profil Sekolah", "📝 Pendaftaran Siswa Baru (PPDB)", "📢 Informasi & Pengumuman", "📅 Master Jadwal Pelajaran Sekolah", "📊 Database Nilai Global", "📚 Management E-Book", "💰 Rekap Kas Keuangan SPP", "🗂️ Daftar Kelas Aktif"]
else:
    daftar_tab = ["🏫 Profil Sekolah", "📝 Pendaftaran Siswa Baru (PPDB)"]

daftar_tab.append("🛠️ Menu Kelola Data")
menu_utama = st.tabs(daftar_tab)


# ==========================================
# CONDITIONAL RENDERING KONTEN TAB
# ==========================================

# --- KONDISI A: TAMPILAN KHUSUS ORANG TUA / SISWA ---
if is_ortu_siswa:
    # 1. TAB NILAI SISWA
    with menu_utama[0]:
        st.subheader("📊 Pusat Informasi Nilai Perkembangan Siswa")
        input_nisn = st.text_input("🔎 Input NISN Siswa (Contoh ketik: 12345)", placeholder="Masukkan nomor induk siswa...")
        if input_nisn.strip():
            df_nilai_siswa = pd.read_sql_query(f"SELECT mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas, nilai_akhir, keterangan FROM nilai WHERE nisn='{input_nisn.strip()}'", conn)
            if df_nilai_siswa.empty:
                st.warning("⚠️ Data nilai tidak ditemukan.")
            else:
                c.execute(f"SELECT nama_siswa, kelas FROM nilai WHERE nisn='{input_nisn.strip()}' LIMIT 1")
                n_nama, n_kelas = c.fetchone()
                with st.container(border=True):
                    st.write(f"👤 **Nama Siswa:** {n_nama} | 🏫 **Kelas:** {n_kelas}")
                st.dataframe(df_nilai_siswa, use_container_width=True, hide_index=True)
                st.metric(label="📈 Nilai Rata-Rata Akhir", value=f"{df_nilai_siswa['nilai_akhir'].mean():.2f}")

    # 2. TAB E-BOOK PELAJARAN
    with menu_utama[1]:
        st.subheader("📚 Perpustakaan E-Book Pelajaran Digital")
        df_book = pd.read_sql_query("SELECT kelas, mata_pelajaran, judul_buku, link_download FROM ebook", conn)
        if df_book.empty:
            st.info("Belum ada materi e-book yang diunggah oleh bapak/ibu guru.")
        else:
            list_kelas_buku = ["Semua Kelas"] + sorted(list(df_book['kelas'].unique()))
            filter_kelas_buku = st.selectbox("Filter Kelas Buku:", list_kelas_buku)
            query_buku = df_book.copy()
            if filter_kelas_buku != "Semua Kelas":
                query_buku = query_buku[query_buku['kelas'] == filter_kelas_buku]
            if query_buku.empty:
                st.warning("E-book untuk kelas ini belum tersedia.")
            else:
                for _, b in query_buku.iterrows():
                    with st.container(border=True):
                        col_b1, col_b2 = st.columns([4, 1])
                        with col_b1:
                            st.markdown(f"### 📖 {b['judul_buku']}")
                            st.caption(f"📁 Mata Pelajaran: **{b['mata_pelajaran']}** | 🏫 Untuk Kelas: {b['kelas']}")
                        with col_b2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.link_button("📥 Download E-Book", b['link_download'], use_container_width=True)

    # 3. TAB STATUS PEMBAYARAN SEKOLAH
    with menu_utama[2]:
        st.subheader("💰 Cek Administrasi & Biaya Sekolah Siswa")
        input_nisn_keu = st.text_input("🔎 Masukkan NISN Anda untuk Cek Keuangan:", placeholder="Contoh ketik: 12345 atau 54321")
        if input_nisn_keu.strip():
            c.execute("SELECT nama_siswa, kelas, total_biaya, sudah_dibayar, status_bayar, keterangan_lunas FROM keuangan WHERE nisn=?", (input_nisn_keu.strip(),))
            data_keu = c.fetchone()
            if not data_keu:
                st.warning("⚠️ Data administrasi keuangan untuk NISN tersebut belum terdaftar di sistem Bendahara.")
            else:
                k_nama, k_kelas, k_total, k_bayar, k_status, k_ket = data_keu
                sisa_tunggakan = max(0.0, k_total - k_bayar)
                with st.container(border=True):
                    st.markdown(f"### 👤 Informasi Siswa: **{k_nama}** ({k_kelas})")
                    st.divider()
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric(label="💵 Total Biaya Wajib (Rp)", value=f"{k_total:,.0f}")
                    col_m2.metric(label="✅ Sudah Dibayar (Rp)", value=f"{k_bayar:,.0f}")
                    if sisa_tunggakan > 0:
                        col_m3.metric(label="🚨 Sisa Tunggakan (Rp)", value=f"{sisa_tunggakan:,.0f}", delta=f"- Belum Lunas", delta_color="inverse")
                    else:
                        col_m3.metric(label="🎉 Sisa Tunggakan (Rp)", value="0", delta=f"Bersih / Lunas", delta_color="normal")
                if k_status == "LUNAS":
                    st.success(f"🟢 **STATUS PEMBAYARAN: LUNAS**\n\n📌 **Catatan Bendahara:** {k_ket}")
                else:
                    st.error(f"🔴 **STATUS PEMBAYARAN: BELUM LUNAS**\n\n📌 **Catatan Pembayaran Terakhir:** {k_ket}")

    # 4. TAB JADWAL PELAJARAN
    with menu_utama[3]:
        st.subheader("📅 Jadwal Pelajaran Aktif")
        df_jadwal = pd.read_sql_query("SELECT hari, kelas, jam_mulai, jam_selesai, mata_pelajaran, guru_pengajar FROM jadwal ORDER BY hari, jam_mulai ASC", conn)
        if not df_jadwal.empty:
            list_kelas = ["Semua Kelas"] + sorted(list(df_jadwal['kelas'].unique()))
            filter_kelas = st.selectbox("Pilih Ruang Kelas Anda:", list_kelas)
            query_filter = df_jadwal.copy()
            if filter_kelas != "Semua Kelas":
                query_filter = query_filter[query_filter['kelas'] == filter_kelas]
            st.dataframe(query_filter, use_container_width=True, hide_index=True)

    # 5. TAB INFORMASI
    with menu_utama[4]:
        st.subheader("📢 Informasi & Pengumuman Internal Sekolah")
        df_info = pd.read_sql_query("SELECT * FROM informasi ORDER BY tanggal DESC", conn)
        if df_info.empty:
            st.info("Belum ada pengumuman tertulis dari guru.")
        else:
            for _, r in df_info.iterrows():
                with st.container(border=True):
                    st.markdown(f"### {r['judul']}")
                    st.caption(f"📅 {r['tanggal']} | Kategori: {r['kategori']}")
                    st.markdown(r['konten'])
        
        # Pengumuman Ekstrakurikuler Statis Siswa
        tampilkan_ekskul_dan_unggulan()


# --- KONDISI B: TAMPILAN DEFAULT UMUM / ADMIN / GURU / STAFF ---
else:
    # 1. TAB PROFIL SEKOLAH
    with menu_utama[0]:
        c.execute("SELECT nama_sekolah, visi_misi, fasilitas, alamat_kontak FROM profil WHERE id=1")
        p_nama, p_visimisi, p_fasilitas, p_kontak_sekolah = c.fetchone()
        st.subheader(f"✨ Selamat Datang di {p_nama}")
        col_prof1, col_prof2 = st.columns(2)
        with col_prof1:
            with st.container(border=True):
                st.markdown("### 🎯 Visi & Misi")
                st.write(p_visimisi)
            with st.container(border=True):
                st.markdown("### 📞 Alamat & Kontak Resmi")
                st.info(p_kontak_sekolah)
        with col_prof2:
            with st.container(border=True):
                st.markdown("### 🧪 Fasilitas Sekolah")
                st.write(p_fasilitas)

        # Ekskul dan Unggulan di halaman Publik/Admin
        tampilkan_ekskul_dan_unggulan()

    # 2. TAB PPDB
    with menu_utama[1]:
        st.subheader("📝 Penerimaan Peserta Didik Baru (PPDB)")
        c.execute("SELECT status, syarat, biaya, kontak FROM ppdb WHERE id=1")
        p_status, p_syarat, p_biaya, p_kontak = c.fetchone()
        if p_status == "DIBUKA":
            st.success("🟢 STATUS PPDB: **PENDAFTARAN SEDANG DIBUKA**")
        else:
            st.error("🔴 STATUS PPDB: **PENDAFTARAN SUDAH DITUTUP**")
        st.write(p_syarat)

    # Menu Tambahan Pemantauan Data Internal Khusus Admin/Guru/Staff
    if is_admin or is_guru:
        with menu_utama[2]:
            st.subheader("📢 Manajemen Berita & Pengumuman")
            st.dataframe(pd.read_sql_query("SELECT * FROM informasi ORDER BY tanggal DESC", conn), use_container_width=True, hide_index=True)
        with menu_utama[3]:
            st.subheader("📅 Master Jadwal Pelajaran Sekolah (Seluruh Kelas)")
            st.dataframe(pd.read_sql_query("SELECT * FROM jadwal ORDER BY hari, jam_mulai ASC", conn), use_container_width=True, hide_index=True)
        with menu_utama[4]:
            st.subheader("📊 Master Rekap Nilai Seluruh Siswa")
            st.dataframe(pd.read_sql_query("SELECT * FROM nilai", conn), use_container_width=True, hide_index=True)
        with menu_utama[5]:
            st.subheader("📚 Master Data E-Book Pelajaran")
            st.dataframe(pd.read_sql_query("SELECT * FROM ebook", conn), use_container_width=True, hide_index=True)
        with menu_utama[6]:
            st.subheader("💰 Master Data Rekap Kas Keuangan SPP Siswa")
            st.dataframe(pd.read_sql_query("SELECT nisn AS NISN, nama_siswa AS Nama_Siswa, kelas AS Kelas, total_biaya AS Total_Tagihan, sudah_dibayar AS Sudah_Dibayar, status_bayar AS Status, keterangan_lunas AS Catatan_Lunas FROM keuangan", conn), use_container_width=True, hide_index=True)
        with menu_utama[7]:
            st.subheader("🗂️ Daftar Kelas Aktif Terdaftar")
            st.caption("Berikut adalah list master kelas yang aktif digunakan di sistem penginputan data saat ini.")
            st.dataframe(pd.read_sql_query("SELECT nama_kelas AS 'Nama Kelas Aktif' FROM kelas_aktif ORDER BY nama_kelas ASC", conn), use_container_width=True, hide_index=True)


# --- TAB PALING UJUNG: PANEL KELOLA / MANAJEMEN DATA (MASTER UPDATE) ---
idx_terakhir = len(daftar_tab) - 1
with menu_utama[idx_terakhir]:
    if not (is_admin or is_guru):
        st.warning("🔒 **Akses Terbatas!** Menu Kelola ini dikunci. Silakan masuk sebagai **GURU/STAFF** atau **ADMIN UTAMA** di sidebar.")
    else:
        st.subheader("🛠️ Panel Input & Pembaruan Data Sekolah")
        
        # Opsi menu input dasar untuk Guru dan Admin
        opsi_kelola = ["📝 Tulis Informasi", "📅 Atur Jadwal Pelajaran Baru", "📊 Input Nilai Siswa", "📚 Upload E-Book Baru", "💰 Update Pembayaran Siswa"]
        if is_admin:
            opsi_kelola.extend(["🗂️ Tambah/Hapus Kelas", "⚙️ Atur PPDB", "🏫 Edit Profil"])
            
        sub_menu = st.radio("Pilih Operasi Kelola:", opsi_kelola, horizontal=True)
        st.divider()
        
        # 1. FORM INPUT INFORMASI
        if sub_menu == "📝 Tulis Informasi":
            with st.form("form_info_adm", clear_on_submit=True):
                st.write("### 📝 Tulis Pengumuman / Informasi Sekolah Baru")
                t_judul = st.text_input("Judul Informasi")
                t_kat = st.selectbox("Kategori", ["Akademik", "Kegiatan Sekolah", "Umum"])
                t_konten = st.text_area("Konten Berita")
                t_penulis = "STAFF / GURU" if is_guru else "ADMIN"
                
                if st.form_submit_button("Publish Informasi"):
                    if not (t_judul.strip() and t_konten.strip()):
                        st.error("❌ Judul dan Konten tidak boleh kosong!")
                    else:
                        c.execute("INSERT INTO informasi (tanggal, judul, konten, kategori, penulis) VALUES (?,?,?,?,?)", (waktu_sekarang, t_judul, t_konten, t_kat, t_penulis))
                        conn.commit()
                        st.success("Sukses mempublikasikan informasi terbaru!")
                        time.sleep(1)
                        st.rerun()

        # 2. FORM INPUT JADWAL (Sudah pakai Dropdown Kelas Aktif)
        elif sub_menu == "📅 Atur Jadwal Pelajaran Baru":
            with st.form("form_jadwal_adm", clear_on_submit=True):
                st.write("### 📅 Tambah/Susun Jadwal Pelajaran Baru")
                col_j1, col_j2 = st.columns(2)
                with col_j1:
                    j_hari = st.selectbox("Pilih Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
                    # SEKARANG: Berubah jadi selectbox tinggal klik list dari database
                    j_kelas = st.selectbox("Untuk Kelas", list_kelas_db)
                    j_mapel = st.text_input("Mata Pelajaran")
                with col_j2:
                    j_mulai = st.text_input("Jam Mulai (Contoh: 07:30)")
                    j_selesai = st.text_input("Jam Selesai (Contoh: 09:00)")
                    j_guru = st.text_input("Nama Guru Pengajar")
                
                if st.form_submit_button("Simpan Jadwal Pelajaran"):
                    if not j_mapel.strip():
                        st.error("❌ Kolom Mata Pelajaran wajib diisi!")
                    else:
                        c.execute("INSERT INTO jadwal (hari, kelas, jam_mulai, jam_selesai, mata_pelajaran, guru_pengajar) VALUES (?,?,?,?,?,?)",
                                  (j_hari, j_kelas, j_mulai.strip(), j_selesai.strip(), j_mapel.strip().upper(), j_guru.strip().upper()))
                        conn.commit()
                        st.success(f"Jadwal pelajaran {j_mapel.upper()} untuk {j_kelas} berhasil disimpan!")
                        time.sleep(1)
                        st.rerun()

        # 3. FORM INPUT NILAI (Sudah pakai Dropdown Kelas Aktif)
        elif sub_menu == "📊 Input Nilai Siswa":
            with st.form("form_nilai", clear_on_submit=True):
                st.write("### 📊 Input Rekap Nilai Siswa Baru")
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    v_nisn = st.text_input("NISN Siswa")
                    v_nama = st.text_input("Nama Lengkap Siswa")
                    # SEKARANG: Memilih kelas tinggal klik, anti typo
                    v_kelas = st.selectbox("Kelas Siswa", list_kelas_db)
                    v_mapel = st.text_input("Mata Pelajaran")
                with col_v2:
                    v_tugas = st.number_input("Nilai Tugas", min_value=0.0, max_value=100.0, value=80.0)
                    v_uts = st.number_input("Nilai UTS", min_value=0.0, max_value=100.0, value=80.0)
                    v_uas = st.number_input("Nilai UAS", min_value=0.0, max_value=100.0, value=80.0)
                
                if st.form_submit_button("Simpan & Hitung"):
                    if not (v_nisn.strip() and v_nama.strip() and v_mapel.strip()):
                        st.error("❌ NISN, Nama, dan Mapel wajib diisi!")
                    else:
                        n_akhir = (v_tugas * 0.3) + (v_uts * 0.3) + (v_uas * 0.4)
                        ket = "TUNTAS" if n_akhir >= 75 else "REMEDIAL"
                        c.execute("INSERT INTO nilai (nisn, nama_siswa, kelas, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas, nilai_akhir, keterangan) VALUES (?,?,?,?,?,?,?,?,?)",
                                  (v_nisn.strip(), v_nama.strip().upper(), v_kelas, v_mapel.strip().upper(), v_tugas, v_uts, v_uas, n_akhir, ket))
                        conn.commit()
                        st.success(f"Nilai {v_mapel.upper()} {v_nama.upper()} ({v_kelas}) Berhasil Disimpan!")
                        time.sleep(1)
                        st.rerun()

        # 4. FORM UPLOAD E-BOOK (Sudah pakai Dropdown Kelas Aktif)
        elif sub_menu == "📚 Upload E-Book Baru":
            with st.form("form_upload_ebook", clear_on_submit=True):
                st.write("### 📤 Upload / Tambah E-Book Pelajaran Baru")
                col_eb1, col_eb2 = st.columns(2)
                with col_eb1:
                    # SEKARANG: Memilih kelas dari selectbox dinamis
                    eb_kelas = st.selectbox("Untuk Kelas", list_kelas_db)
                    eb_mapel = st.text_input("Mata Pelajaran")
                with col_eb2:
                    eb_judul = st.text_input("Judul / Nama File E-Book")
                    eb_link = st.text_input("Tautan / Link Download E-Book")
                eb_pengunggah = "GURU / STAFF" if is_guru else "ADMIN UTAMA"
                
                if st.form_submit_button("Simpan & Publish E-Book"):
                    if not (eb_mapel.strip() and eb_judul.strip() and eb_link.strip()):
                        st.error("❌ Semua kolom wajib diisi lengkap!")
                    else:
                        c.execute("INSERT INTO ebook (kelas, mata_pelajaran, judul_buku, link_download, pengunggah) VALUES (?,?,?,?,?)",
                                  (eb_kelas, eb_mapel.strip().upper(), eb_judul.strip(), eb_link.strip(), eb_pengunggah))
                        conn.commit()
                        st.success("E-Book berhasil diterbitkan!")
                        time.sleep(1)
                        st.rerun()

        # 5. FORM UPDATE KEUANGAN (Sudah pakai Dropdown Kelas Aktif)
        elif sub_menu == "💰 Update Pembayaran Siswa":
            with st.form("form_update_keuangan", clear_on_submit=True):
                st.write("### ⚙️ Edit & Sinkronisasi Kas Pembayaran Siswa")
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    f_nisn = st.text_input("NISN Siswa Terdaftar")
                    f_nama = st.text_input("Nama Lengkap Siswa")
                    # SEKARANG: Berubah jadi pilihan klik
                    f_kelas = st.selectbox("Kelas Siswa", list_kelas_db)
                with col_k2:
                    f_total = st.number_input("Total Kewajiban Tagihan Sekolah (Rp)", min_value=0, value=1200000, step=50000)
                    f_bayar = st.number_input("Jumlah Uang yang Sudah Dibayar (Rp)", min_value=0, value=0, step=50000)
                    f_status = st.selectbox("Status Pembayaran saat ini:", ["BELUM LUNAS", "LUNAS"])
                
                f_ket = st.text_input("Keterangan Tambahan / Lunas Sampai Kapan:")
                
                submit_keu = st.form_submit_button("Simpan Perubahan Data Keuangan")
                if submit_keu:
                    if not (f_nisn.strip() and f_nama.strip()):
                        st.error("❌ Data NISN dan Nama Siswa wajib diisi!")
                    else:
                        c.execute("""
                            INSERT INTO keuangan (nisn, nama_siswa, kelas, total_biaya, sudah_dibayar, status_bayar, keterangan_lunas)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(nisn) DO UPDATE SET
                                nama_siswa=excluded.nama_siswa,
                                kelas=excluded.kelas,
                                total_biaya=excluded.total_biaya,
                                sudah_dibayar=excluded.sudah_dibayar,
                                status_bayar=excluded.status_bayar,
                                keterangan_lunas=excluded.keterangan_lunas
                        """, (f_nisn.strip(), f_nama.strip().upper(), f_kelas, f_total, f_bayar, f_status, f_ket.strip()))
                        conn.commit()
                        st.success(f"🎉 Data keuangan siswa {f_nama.upper()} berhasil diperbarui!")
                        time.sleep(1)
                        st.rerun()

        # 6. FORM MANAJEMEN TAMBAH/HAPUS KELAS (Khusus Admin Utama)
        elif is_admin and sub_menu == "🗂️ Tambah/Hapus Kelas":
            st.write("### 🗂️ Manajemen Master Kelas Aktif")
            
            col_k_in1, col_k_in2 = st.columns(2)
            
            with col_k_in1:
                with st.form("form_tambah_kelas", clear_on_submit=True):
                    st.markdown("**➕ Tambah Kelas Baru**")
                    input_kelas_baru = st.text_input("Nama Kelas Baru (Contoh: KELAS 1-A)", placeholder="Ketik nama kelas...")
                    if st.form_submit_button("Simpan Kelas"):
                        if input_kelas_baru.strip():
                            try:
                                c.execute("INSERT INTO kelas_aktif (nama_kelas) VALUES (?)", (input_kelas_baru.strip().upper(),))
                                conn.commit()
                                st.success(f"Berhasil menambahkan {input_kelas_baru.upper()}!")
                                time.sleep(1)
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("❌ Nama kelas sudah terdaftar!")
                        else:
                            st.error("❌ Nama kelas tidak boleh kosong!")
                            
            with col_k_in2:
                with st.form("form_hapus_kelas"):
                    st.markdown("**❌ Hapus Kelas Terdaftar**")
                    kelas_dihapus = st.selectbox("Pilih Kelas Yang Ingin Dihapus", list_kelas_db)
                    st.caption("⚠️ Peringatan: Menghapus kelas hanya menghapus opsi dari daftar pilihan dropdown.")
                    if st.form_submit_button("Hapus Kelas", type="secondary"):
                        c.execute("DELETE FROM kelas_aktif WHERE nama_kelas = ?", (kelas_dihapus,))
                        conn.commit()
                        st.success(f"Berhasil menghapus {kelas_dihapus} dari sistem!")
                        time.sleep(1)
                        st.rerun()

        # 7. CONFIG PPDB (Hanya Admin)
        elif is_admin and sub_menu == "⚙️ Atur PPDB":
            c.execute("SELECT status, syarat, biaya, kontak FROM ppdb WHERE id=1")
            cs, csy, cb, ck = c.fetchone()
            with st.form("form_ppdb_adm"):
                as_stat = st.selectbox("Status", ["DIBUKA", "DITUTUP"], index=0 if cs == "DIBUKA" else 1)
                as_syar = st.text_area("Syarat", value=csy)
                as_biay = st.text_area("Biaya", value=cb)
                as_kont = st.text_area("Kontak", value=ck)
                if st.form_submit_button("Update PPDB"):
                    c.execute("UPDATE ppdb SET status=?, syarat=?, biaya=?, kontak=? WHERE id=1", (as_stat, as_syar, as_biay, as_kont))
                    conn.commit()
                    st.success("PPDB Updated!")
                    time.sleep(1)
                    st.rerun()

        # 8. CONFIG PROFIL (Hanya Admin)
        elif is_admin and sub_menu == "🏫 Edit Profil":
            c.execute("SELECT nama_sekolah, visi_misi, fasilitas, alamat_kontak FROM profil WHERE id=1")
            cn, cv, cf, ca = c.fetchone()
            with st.form("form_prof_adm"):
                an_nama = st.text_input("Nama Sekolah", value=cn)
                an_visi = st.text_area("Visi Misi", value=cv)
                an_fasi = st.text_area("Fasilitas", value=cf)
                an_alam = st.text_area("Alamat", value=ca)
                if st.form_submit_button("Update Profil"):
                    c.execute("UPDATE profil SET nama_sekolah=?, visi_misi=?, fasilitas=?, alamat_kontak=? WHERE id=1", (an_nama.upper(), an_visi, p_fasilitas, an_alam))
                    conn.commit()
                    st.success("Profil Updated!")
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
