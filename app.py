"""
app.py
Aplikasi utama Streamlit untuk Dashboard Perpustakaan Seperlima.

Fitur utama:
- Halaman Ringkasan: KPI dan grafik utama aktivitas perpustakaan.
- Halaman Peminjaman: tabel + filter + grafik tren dan durasi.
- Halaman Anggota: distribusi anggota per status dan fakultas.
- Halaman Buku: kondisi koleksi buku dan kategori.
- Halaman Referensi data: menampilkan tabel-tabel referensi (fakultas, prodi, dll.).

Seluruh data diambil dari database MySQL 'seperlima' melalui modul db.py.
"""

import streamlit as st

from db import (
    load_peminjaman_detail,
    load_anggota,
    load_buku,
    load_fakultas,
    load_program_studi,
    load_pengarang,
    load_buku_pengarang,
    load_petugas,
    load_judul,
    load_klasifikasi,
)

from charts import (
    chart_tren_bulanan_status,
    chart_peminjaman_per_fakultas,
    chart_peminjaman_per_kategori,
    chart_durasi_rata_per_fakultas,
    chart_peminjaman_per_status,
    chart_top5_judul,
    chart_hist_durasi,
    chart_anggota_per_status,
    chart_anggota_per_fakultas,
    chart_buku_per_kategori,
    chart_buku_per_status,
    chart_buku_per_tahun,
)

# ======================================================
# KONFIGURASI HALAMAN
# ======================================================

st.set_page_config(
    page_title="Seperlima",
    page_icon="📚",
    layout="wide",
)

# CSS header dan kartu ringkasan
st.markdown(
    """
    <style>
    .main-header {
        /* rak buku hangat: gelap → medium roast → leather */
        background: linear-gradient(90deg, #090201, #381F08, #8C663E);
        padding: 18px 24px;
        border-radius: 18px;
        color: #F9FAFB;
        margin-bottom: 18px;
    }
    .metric-card {
        padding: 16px 18px;
        border-radius: 16px;
        background: #200E03;              /* Super black cokelat */
        border: 1px solid #8C663E;        /* Cambridge Leather */
        box-shadow: 0 10px 30px rgba(0,0,0,0.7);
    }
    .metric-label {
        font-size: 0.8rem;
        color: #D1B38A;                   /* warm beige, mudah dibaca */
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #C7CED6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Header utama dashboard
st.markdown(
    """
    <div class="main-header">
        <h2 style="margin-bottom: 4px;">Seperlima</h2>
        <span>Sistem Informasi Perpustakaan Kelompok 5</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======================================================
# SIDEBAR NAVIGASI & INFORMASI
# ======================================================

st.sidebar.title("🧭 Navigasi")
page = st.sidebar.radio(
    "Pilih halaman",
    ["Ringkasan", "Peminjaman", "Anggota", "Buku", "Referensi data"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("Tentang aplikasi")
st.sidebar.caption(
    "Dashboard ini menggunakan database MySQL `seperlima` sebagai sumber data "
    "anggota, petugas, buku, dan transaksi peminjaman."
)


def show_empty_message():
    """Pesan standar ketika hasil filter data kosong."""
    st.info("Data tidak tersedia untuk kombinasi filter yang dipilih.")


# ======================================================
# HALAMAN: RINGKASAN
# ======================================================

if page == "Ringkasan":
    try:
        with st.spinner("Memuat data peminjaman..."):
            df_pinjam = load_peminjaman_detail()
    except Exception as e:
        st.error("Gagal memuat data peminjaman dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
        st.stop()

    if df_pinjam.empty:
        st.warning("Belum ada data peminjaman pada database.")
        st.stop()

    st.write(
        "Halaman ini menampilkan gambaran umum aktivitas perpustakaan berdasarkan "
        "data peminjaman, anggota, dan koleksi buku."
    )

    # ----------------- Kartu ringkasan (KPI) -----------------
    total_peminjaman = len(df_pinjam)
    total_anggota_aktif = df_pinjam["id_anggota"].nunique()
    total_buku_dipinjam = df_pinjam["id_buku"].nunique()
    total_denda = int(df_pinjam["denda_buku"].sum())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total peminjaman</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_peminjaman}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Seluruh transaksi peminjaman</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Anggota aktif</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_anggota_aktif}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Pernah melakukan peminjaman</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Buku yang dipinjam</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_buku_dipinjam}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Berdasarkan variasi ID buku</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total denda</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">Rp {total_denda:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Akumulasi dari seluruh transaksi</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Ikhtisar grafik")
    st.write(
        "Grafik di bawah ini membantu melihat pola peminjaman berdasarkan waktu, fakultas, "
        "kategori buku, dan durasi peminjaman."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Perkembangan peminjaman",
            "Peminjaman per fakultas",
            "Peminjaman per kategori buku",
            "Durasi peminjaman per fakultas",
        ]
    )

    # Tab 1: Perkembangan peminjaman dari waktu ke waktu
    with tab1:
        st.subheader("Perkembangan peminjaman dari waktu ke waktu")
        fig_tren = chart_tren_bulanan_status(df_pinjam)
        st.plotly_chart(fig_tren, use_container_width=True)

        df_bulan = df_pinjam.copy()
        df_bulan["bulan"] = df_bulan["tgl_pinjam"].dt.to_period("M").astype(str)
        per_bulan = df_bulan.groupby("bulan").size().reset_index(name="jumlah")
        if not per_bulan.empty:
            puncak = per_bulan.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"Periode dengan jumlah peminjaman tertinggi adalah {puncak['bulan']} "
                f"dengan {puncak['jumlah']} transaksi."
            )

    # Tab 2: Peminjaman per fakultas
    with tab2:
        st.subheader("Peminjaman per fakultas")
        fig_fak, per_fak = chart_peminjaman_per_fakultas(df_pinjam)
        st.plotly_chart(fig_fak, use_container_width=True)

        if not per_fak.empty:
            fak_tertinggi = per_fak.iloc[0]
            st.caption(
                f"Fakultas dengan jumlah peminjaman tertinggi adalah "
                f"{fak_tertinggi['nama_fakultas']} dengan {fak_tertinggi['jumlah']} transaksi."
            )

    # Tab 3: Peminjaman per kategori buku
    with tab3:
        st.subheader("Peminjaman per kategori buku")
        fig_kat, per_kat = chart_peminjaman_per_kategori(df_pinjam)
        st.plotly_chart(fig_kat, use_container_width=True)

        if not per_kat.empty:
            kat_tertinggi = per_kat.iloc[0]
            st.caption(
                f"Kategori buku dengan peminjaman tertinggi adalah "
                f"{kat_tertinggi['kategori_buku']} dengan {kat_tertinggi['jumlah']} transaksi."
            )

    # Tab 4: Durasi peminjaman per fakultas
    with tab4:
        st.subheader("Rata-rata durasi peminjaman per fakultas")
        fig_durasi, durasi_fak = chart_durasi_rata_per_fakultas(df_pinjam)
        st.plotly_chart(fig_durasi, use_container_width=True)

        if not durasi_fak.empty:
            fak_durasi_top = durasi_fak.iloc[0]
            st.caption(
                f"Fakultas dengan rata-rata durasi peminjaman paling lama adalah "
                f"{fak_durasi_top['nama_fakultas']} "
                f"dengan rata-rata {fak_durasi_top['rata_durasi']:.1f} hari."
            )

# ======================================================
# HALAMAN: PEMINJAMAN
# ======================================================

elif page == "Peminjaman":
    st.subheader("Data peminjaman buku")
    st.write(
        "Halaman ini menampilkan data peminjaman yang dapat difilter berdasarkan tanggal, "
        "fakultas, program studi, status anggota, status peminjaman, dan kategori buku."
    )

    try:
        with st.spinner("Memuat data peminjaman..."):
            df = load_peminjaman_detail()
    except Exception as e:
        st.error("Gagal memuat data peminjaman dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
        st.stop()

    if df.empty:
        st.warning("Belum ada data peminjaman pada database.")
        st.stop()

    # ----------------- Filter di sidebar -----------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filter peminjaman")

    min_date = df["tgl_pinjam"].min().date()
    max_date = df["tgl_pinjam"].max().date()

    date_range = st.sidebar.date_input(
        "Rentang tanggal peminjaman",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, (tuple, list)):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    fakultas_list = ["(Semua)"] + sorted(df["nama_fakultas"].dropna().unique().tolist())
    prodi_list = ["(Semua)"] + sorted(df["nama_prodi"].dropna().unique().tolist())
    status_anggota_list = ["(Semua)"] + sorted(df["status_anggota"].dropna().unique().tolist())
    status_pinjam_list = ["(Semua)"] + sorted(df["status_peminjaman"].dropna().unique().tolist())
    kategori_list = ["(Semua)"] + sorted(df["kategori_buku"].dropna().unique().tolist())

    fakultas_pilih = st.sidebar.selectbox("Fakultas", fakultas_list)
    prodi_pilih = st.sidebar.selectbox("Program studi", prodi_list)
    status_anggota_pilih = st.sidebar.selectbox("Status anggota", status_anggota_list)
    status_peminjaman_pilih = st.sidebar.selectbox("Status peminjaman", status_pinjam_list)
    kategori_pilih = st.sidebar.selectbox("Kategori buku", kategori_list)

    # Terapkan filter ke DataFrame
    df_filtered = df[
        (df["tgl_pinjam"].dt.date >= start_date)
        & (df["tgl_pinjam"].dt.date <= end_date)
    ].copy()

    if fakultas_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["nama_fakultas"] == fakultas_pilih]
    if prodi_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["nama_prodi"] == prodi_pilih]
    if status_anggota_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["status_anggota"] == status_anggota_pilih]
    if status_peminjaman_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["status_peminjaman"] == status_peminjaman_pilih]
    if kategori_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["kategori_buku"] == kategori_pilih]

    df_filtered = df_filtered.sort_values("tgl_pinjam", ascending=False)

    # Ringkasan kondisi filter
    st.caption(
        f"Data ditampilkan untuk periode {start_date} sampai {end_date}"
        + (f", fakultas {fakultas_pilih}" if fakultas_pilih != "(Semua)" else ", semua fakultas")
        + (f", program studi {prodi_pilih}" if prodi_pilih != "(Semua)" else ", semua program studi")
        + (f", status anggota {status_anggota_pilih}" if status_anggota_pilih != "(Semua)" else ", semua status anggota")
        + (f", status peminjaman {status_peminjaman_pilih}" if status_peminjaman_pilih != "(Semua)" else ", semua status peminjaman")
        + (f", kategori {kategori_pilih}." if kategori_pilih != "(Semua)" else ", semua kategori buku.")
    )

    # ----------------- Tabel dan tombol unduh -----------------
    with st.expander("Tabel data peminjaman (setelah filter)"):
        st.dataframe(df_filtered, use_container_width=True, height=350)

    csv_peminjaman = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh data peminjaman (CSV)",
        data=csv_peminjaman,
        file_name="peminjaman_filtered.csv",
        mime="text/csv",
    )

    # ----------------- Angka ringkasan sesuai filter -----------------
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.metric("Jumlah peminjaman", len(df_filtered))
    with col_k2:
        st.metric("Total denda", f"Rp {int(df_filtered['denda_buku'].sum()):,}")
    with col_k3:
        if df_filtered["durasi_peminjaman"].notna().any():
            rata_durasi = df_filtered["durasi_peminjaman"].mean()
            st.metric("Rata-rata durasi peminjaman", f"{rata_durasi:.1f} hari")
        else:
            st.metric("Rata-rata durasi peminjaman", "-")

    # ----------------- Grafik per status dan lima judul teratas -----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Peminjaman per status peminjaman")
        fig_status, per_status = chart_peminjaman_per_status(df_filtered)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.subheader("Lima judul buku paling sering dipinjam")
        fig_top, top_judul = chart_top5_judul(df_filtered)
        st.plotly_chart(fig_top, use_container_width=True)

        if not top_judul.empty:
            judul_top = top_judul.iloc[0]
            st.caption(
                f"Judul dengan peminjaman tertinggi adalah "
                f"\"{judul_top['judul']}\" sebanyak {judul_top['jumlah']} kali."
            )

    # ----------------- Histogram durasi peminjaman -----------------
    st.subheader("Distribusi durasi peminjaman")
    st.caption(
        "Grafik ini menunjukkan sebaran lama peminjaman dalam satuan hari, "
        "sehingga terlihat apakah mayoritas peminjaman masih dalam batas waktu yang wajar."
    )
    fig_hist, _ = chart_hist_durasi(df_filtered)
    st.plotly_chart(fig_hist, use_container_width=True)

    # ----------------- Penjelasan logika durasi dan denda -----------------
    with st.expander("Penjelasan singkat logika durasi dan denda"):
        st.write(
            "- Kolom **durasi_peminjaman** menyimpan lama peminjaman dalam satuan hari.\n"
            "- Pada implementasi nyata, perpustakaan biasanya menetapkan batas hari tertentu (misalnya 7 hari).\n"
            "- Jika peminjaman melewati batas tersebut, maka dikenakan denda per hari keterlambatan.\n"
            "- Kolom **denda_buku** pada tabel ini berisi nilai denda yang sudah dihitung sesuai skenario dummy."
        )

    # ----------------- Contoh query SQL -----------------
    with st.expander("Contoh query SQL (JOIN beberapa tabel)"):
        st.code(
            """
SELECT
    p.id_peminjaman,
    a.nama_anggota,
    j.judul,
    f.nama_fakultas,
    p.tgl_pinjam,
    p.tgl_kembali,
    p.denda_buku
FROM peminjaman p
JOIN anggota a ON p.id_anggota = a.id_anggota
LEFT JOIN program_studi ps ON a.id_prodi = ps.id_prodi
LEFT JOIN fakultas f ON ps.id_fakultas = f.id_fakultas
JOIN buku b ON p.id_buku = b.id_buku
JOIN judul j ON b.id_judul = j.id_judul
ORDER BY p.tgl_pinjam DESC;
            """,
            language="sql",
        )
        st.caption(
            "Query ini menggabungkan tabel peminjaman, anggota, program studi, fakultas, "
            "buku, dan judul untuk menampilkan riwayat peminjaman beserta identitas anggota "
            "dan informasi buku."
        )

# ======================================================
# HALAMAN: ANGGOTA
# ======================================================

elif page == "Anggota":
    st.subheader("Data anggota perpustakaan")
    st.write(
        "Halaman ini menampilkan data anggota perpustakaan serta ringkasan berdasarkan "
        "status keanggotaan dan fakultas asal."
    )

    try:
        with st.spinner("Memuat data anggota..."):
            df_anggota = load_anggota()
    except Exception as e:
        st.error("Gagal memuat data anggota dari database.")
        st.exception(e)
        st.stop()

    if df_anggota.empty:
        st.warning("Belum ada data anggota pada database.")
        st.stop()

    # Pencarian nama anggota
    search_nama = st.text_input(
        "Pencarian nama anggota",
        placeholder="Ketik nama atau sebagian nama anggota...",
    )
    df_anggota_view = df_anggota.copy()
    if search_nama:
        df_anggota_view = df_anggota_view[
            df_anggota_view["nama_anggota"].str.contains(search_nama, case=False, na=False)
        ]

    with st.expander("Tabel data anggota"):
        st.dataframe(df_anggota_view, use_container_width=True, height=350)

    csv_anggota = df_anggota_view.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh data anggota (CSV)",
        data=csv_anggota,
        file_name="anggota.csv",
        mime="text/csv",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jumlah anggota per status")
        fig_status = chart_anggota_per_status(df_anggota_view)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.subheader("Jumlah anggota per fakultas")
        fig_fak = chart_anggota_per_fakultas(df_anggota_view)
        st.plotly_chart(fig_fak, use_container_width=True)

# ======================================================
# HALAMAN: BUKU
# ======================================================

elif page == "Buku":
    st.subheader("Data koleksi buku")
    st.write(
        "Halaman ini menampilkan data koleksi buku beserta status ketersediaan, "
        "kategori, dan tahun terbit."
    )

    try:
        with st.spinner("Memuat data buku..."):
            df_buku = load_buku()
    except Exception as e:
        st.error("Gagal memuat data buku dari database.")
        st.exception(e)
        st.stop()

    if df_buku.empty:
        st.warning("Belum ada data buku pada database.")
        st.stop()

    # Pencarian judul buku
    search_judul = st.text_input(
        "Pencarian judul buku",
        placeholder="Ketik judul atau sebagian judul buku...",
    )
    df_buku_view = df_buku.copy()
    if search_judul:
        df_buku_view = df_buku_view[
            df_buku_view["judul"].str.contains(search_judul, case=False, na=False)
        ]

    # Urutan kolom: tampilkan kode_* sebelum eksemplar
    cols_order = [
        "id_buku",
        "kode_judul",
        "judul",
        "kode_klasifikasi",
        "kategori_buku",
        "kode_pengarang",
        "tahun_terbit",
        "isbn",
        "status_buku",
        "eksemplar",
    ]
    existing_cols = [c for c in cols_order if c in df_buku_view.columns]
    df_buku_view = df_buku_view[existing_cols]

    # Filter kategori dan status buku
    kategori_list = ["(Semua)"] + sorted(df_buku["kategori_buku"].dropna().unique().tolist())
    status_buku_list = ["(Semua)"] + sorted(df_buku["status_buku"].dropna().unique().tolist())

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        kategori_pilih = st.selectbox("Kategori buku", kategori_list)
    with col_filter2:
        status_buku_pilih = st.selectbox("Status buku", status_buku_list)

    if kategori_pilih != "(Semua)":
        df_buku_view = df_buku_view[df_buku_view["kategori_buku"] == kategori_pilih]
    if status_buku_pilih != "(Semua)":
        df_buku_view = df_buku_view[df_buku_view["status_buku"] == status_buku_pilih]

    with st.expander("Tabel data buku"):
        st.dataframe(df_buku_view, use_container_width=True, height=350)

    csv_buku = df_buku_view.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh data buku (CSV)",
        data=csv_buku,
        file_name="buku.csv",
        mime="text/csv",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jumlah buku per kategori")
        fig_kat = chart_buku_per_kategori(df_buku_view)
        st.plotly_chart(fig_kat, use_container_width=True)

    with col2:
        st.subheader("Komposisi status koleksi buku")
        fig_status_buku, _ = chart_buku_per_status(df_buku_view)
        st.plotly_chart(fig_status_buku, use_container_width=True)

    st.subheader("Jumlah buku per tahun terbit")
    fig_th = chart_buku_per_tahun(df_buku_view)
    st.plotly_chart(fig_th, use_container_width=True)

# ======================================================
# HALAMAN: REFERENSI DATA
# ======================================================

elif page == "Referensi data":
    st.subheader("Referensi data perpustakaan")
    st.write(
        "Halaman ini menampilkan data referensi yang digunakan oleh sistem, yaitu "
        "fakultas, program studi, pengarang, relasi buku-pengarang, dan petugas."
    )

    tab_fak, tab_prodi, tab_peng, tab_bupeng, tab_petugas, tab_judul, tab_klasifikasi = st.tabs(
        ["Fakultas", "Program studi", "Pengarang", "Buku-pengarang", "Petugas", "Judul", "Klasifikasi"]
    )

    with tab_fak:
        df_fak = load_fakultas()
        st.markdown("**Tabel fakultas**")
        st.dataframe(df_fak, use_container_width=True)

    with tab_prodi:
        df_prodi = load_program_studi()
        st.markdown("**Tabel program studi**")
        st.dataframe(df_prodi, use_container_width=True)

    with tab_peng:
        df_peng = load_pengarang()
        st.markdown("**Tabel pengarang**")
        st.dataframe(df_peng, use_container_width=True)

    with tab_bupeng:
        df_bupeng = load_buku_pengarang()
        st.markdown("**Tabel relasi buku-pengarang**")
        st.dataframe(df_bupeng, use_container_width=True)

    with tab_petugas:
        df_pt = load_petugas()
        st.markdown("**Tabel petugas**")
        st.dataframe(df_pt, use_container_width=True)


    with tab_judul:
        df_pt = load_judul()
        st.markdown("**Tabel judul**")
        st.dataframe(df_pt, use_container_width=True)

    with tab_klasifikasi:
        df_pt = load_klasifikasi()
        st.markdown("**Tabel klasifikasi**")
        st.dataframe(df_pt, use_container_width=True)