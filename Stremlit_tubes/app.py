"""
app.py
Aplikasi utama Streamlit untuk Dashboard Perpustakaan Seperlima.
Mengatur tata letak halaman, pemanggilan data, dan pemanggilan fungsi grafik.
"""

import streamlit as st

from db import load_peminjaman_detail, load_anggota, load_buku
from charts import (
    chart_tren_bulanan_status,
    chart_peminjaman_per_fakultas,
    chart_heatmap_fakultas_kategori,
    chart_durasi_rata_per_fakultas,
    chart_peminjaman_per_status,
    chart_top5_judul,
    chart_boxplot_durasi_per_status,
    chart_anggota_per_status,
    chart_anggota_per_fakultas_treemap,
    chart_buku_per_kategori,
    chart_buku_per_tahun,
)

# ======================================================
# KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="Seperlima",
    page_icon="📚",
    layout="wide"
)

# CSS sederhana untuk header dan kartu ringkasan
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #6366F1, #22C55E);
        padding: 18px 24px;
        border-radius: 18px;
        color: white;
        margin-bottom: 18px;
    }
    .metric-card {
        padding: 16px 18px;
        border-radius: 16px;
        background: #0F172A;
        border: 1px solid #1F2937;
        box-shadow: 0 10px 30px rgba(15,23,42,0.6);
    }
    .metric-label {
        font-size: 0.8rem;
        color: #9CA3AF;
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
        color: #6B7280;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header utama dashboard
st.markdown(
    """
    <div class="main-header">
        <h2 style="margin-bottom: 4px;">Seperlima</h2>
        <span>Sistem Informasi Perpustakaan Kelompok 5</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ======================================================
# SIDEBAR NAVIGASI & INFORMASI
# ======================================================
st.sidebar.title("🧭 Navigasi")
page = st.sidebar.radio(
    "Pilih halaman",
    ["Ringkasan umum", "Data peminjaman", "Data anggota", "Data buku"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("Tentang aplikasi")
st.sidebar.caption(
    "Dashboard ini terhubung ke database MySQL `seperlima` sebagai sumber data "
    "peminjaman, keanggotaan, dan koleksi perpustakaan."
)


def show_empty_message():
    """
    Menampilkan pesan standar ketika hasil filter data kosong.
    """
    st.info("Data tidak tersedia untuk kombinasi filter yang dipilih.")


# ======================================================
# HALAMAN: RINGKASAN UMUM
# ======================================================
if page == "Ringkasan umum":
    try:
        with st.spinner("Memuat data peminjaman..."):
            df_pinjam = load_peminjaman_detail()
    except Exception as e:
        st.error("Gagal memuat data peminjaman dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
        st.stop()

    st.write(
        "Halaman ini menyajikan ringkasan aktivitas perpustakaan berdasarkan data "
        "peminjaman, anggota, dan koleksi buku."
    )

    # ----------------- Kartu ringkasan (KPI) -----------------
    total_peminjaman = len(df_pinjam)
    total_anggota = df_pinjam["id_anggota"].nunique()
    total_buku = df_pinjam["id_buku"].nunique()
    total_denda = int(df_pinjam["denda_buku"].sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total peminjaman</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_peminjaman}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Jumlah seluruh transaksi peminjaman</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Anggota aktif</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_anggota}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Pernah melakukan peminjaman</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Judul dipinjam</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_buku}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Berdasarkan ID buku yang tercatat</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total denda</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">Rp {total_denda:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Akumulasi dari seluruh transaksi</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Ikhtisar grafik")
    st.write(
        "Bagian berikut menampilkan grafik-grafik untuk melihat pola peminjaman "
        "dari sisi waktu, fakultas, kategori buku, dan durasi peminjaman."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Perkembangan peminjaman", "Per fakultas", "Per kategori buku", "Durasi peminjaman"]
    )

    # Tab 1: Perkembangan peminjaman dari waktu ke waktu
    with tab1:
        st.subheader("Perkembangan peminjaman dari waktu ke waktu")
        st.caption(
            "Grafik ini memperlihatkan perkembangan jumlah peminjaman setiap bulan, "
            "yang dikelompokkan berdasarkan status peminjaman."
        )

        fig_tren = chart_tren_bulanan_status(df_pinjam)
        st.plotly_chart(fig_tren, use_container_width=True)

        # Insight otomatis: bulan dengan peminjaman tertinggi
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
        st.caption(
            "Grafik ini digunakan untuk membandingkan intensitas peminjaman "
            "antar fakultas."
        )
        fig_fak, per_fak = chart_peminjaman_per_fakultas(df_pinjam)
        st.plotly_chart(fig_fak, use_container_width=True)

        if not per_fak.empty:
            fak_tertinggi = per_fak.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"Fakultas dengan peminjaman tertinggi adalah {fak_tertinggi['nama_fakultas']} "
                f"dengan {fak_tertinggi['jumlah']} transaksi."
            )

    # Tab 3: Pola peminjaman berdasarkan fakultas dan kategori buku
    with tab3:
        st.subheader("Peminjaman berdasarkan fakultas dan kategori buku")
        st.caption(
            "Grafik ini menampilkan pola peminjaman berdasarkan kombinasi fakultas "
            "dan kategori buku. Warna yang lebih gelap menunjukkan jumlah peminjaman yang lebih besar."
        )
        fig_heat, per_fak_kat = chart_heatmap_fakultas_kategori(df_pinjam)
        if fig_heat is not None:
            st.plotly_chart(fig_heat, use_container_width=True)

            # Insight otomatis: kombinasi fakultas-kategori tertinggi
            baris_tertinggi = per_fak_kat.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"Kombinasi paling sering adalah Fakultas {baris_tertinggi['nama_fakultas']} "
                f"dengan kategori {baris_tertinggi['kategori_buku']} "
                f"sebanyak {baris_tertinggi['jumlah']} peminjaman."
            )
        else:
            show_empty_message()

    # Tab 4: Rata-rata durasi peminjaman per fakultas
    with tab4:
        st.subheader("Rata-rata durasi peminjaman per fakultas")
        st.caption(
            "Grafik ini digunakan untuk melihat kecenderungan lama peminjaman di setiap "
            "fakultas."
        )
        fig_durasi, durasi_fak = chart_durasi_rata_per_fakultas(df_pinjam)

        if fig_durasi is not None:
            st.plotly_chart(fig_durasi, use_container_width=True)
            fak_durasi_top = durasi_fak.sort_values("rata_durasi", ascending=False).iloc[0]
            st.caption(
                f"Fakultas dengan rata-rata durasi peminjaman paling lama adalah "
                f"{fak_durasi_top['nama_fakultas']} "
                f"dengan rata-rata {fak_durasi_top['rata_durasi']:.1f} hari."
            )
        else:
            show_empty_message()

# ======================================================
# HALAMAN: DATA PEMINJAMAN
# ======================================================
elif page == "Data peminjaman":
    st.subheader("Data peminjaman buku")
    st.write(
        "Halaman ini menampilkan data peminjaman yang dapat difilter berdasarkan "
        "rentang tanggal, fakultas, dan status peminjaman."
    )

    try:
        with st.spinner("Memuat data peminjaman..."):
            df = load_peminjaman_detail()
    except Exception as e:
        st.error("Gagal memuat data peminjaman dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
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
        max_value=max_date
    )

    if isinstance(date_range, (tuple, list)):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    fakultas_list = ["(Semua)"] + sorted(df["nama_fakultas"].dropna().unique().tolist())
    status_list = ["(Semua)"] + sorted(df["status_peminjaman"].dropna().unique().tolist())

    fakultas_pilih = st.sidebar.selectbox("Fakultas", fakultas_list)
    status_pilih = st.sidebar.selectbox("Status peminjaman", status_list)

    # Terapkan filter ke DataFrame
    df_filtered = df[
        (df["tgl_pinjam"].dt.date >= start_date) &
        (df["tgl_pinjam"].dt.date <= end_date)
    ].copy()

    if fakultas_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["nama_fakultas"] == fakultas_pilih]

    if status_pilih != "(Semua)":
        df_filtered = df_filtered[df_filtered["status_peminjaman"] == status_pilih]

    df_filtered = df_filtered.sort_values("tgl_pinjam", ascending=False)

    # Ringkasan kondisi filter yang sedang aktif
    st.caption(
        f"Data ditampilkan untuk periode {start_date} sampai {end_date}"
        + (f", Fakultas {fakultas_pilih}" if fakultas_pilih != "(Semua)" else ", semua fakultas")
        + (f", status {status_pilih}." if status_pilih != "(Semua)" else ", semua status.")
    )

    # ----------------- Tabel dan tombol unduh -----------------
    with st.expander("Tabel data peminjaman (setelah filter)"):
        st.dataframe(df_filtered, use_container_width=True, height=350)

    csv_peminjaman = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh data peminjaman (CSV)",
        data=csv_peminjaman,
        file_name="peminjaman_filtered.csv",
        mime="text/csv"
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
            st.metric("Rata-rata durasi", f"{rata_durasi:.1f} hari")
        else:
            st.metric("Rata-rata durasi", "-")

    # ----------------- Grafik per status dan lima judul teratas -----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Peminjaman per status peminjaman")
        st.caption(
            "Grafik ini digunakan untuk melihat komposisi status peminjaman, "
            "misalnya berapa banyak yang masih dipinjam, hilang, atau sudah kembali."
        )
        fig_status, per_status = chart_peminjaman_per_status(df_filtered)
        if fig_status is not None:
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            show_empty_message()

    with col2:
        st.subheader("Lima judul buku paling sering dipinjam")
        st.caption(
            "Grafik ini menampilkan lima judul buku dengan frekuensi peminjaman tertinggi "
            "pada kombinasi filter yang dipilih."
        )
        fig_top, top_judul = chart_top5_judul(df_filtered)
        if fig_top is not None:
            st.plotly_chart(fig_top, use_container_width=True)

            judul_top = top_judul.iloc[0]
            st.caption(
                f"Judul dengan peminjaman tertinggi adalah "
                f"\"{judul_top['judul']}\" sebanyak {judul_top['jumlah']} kali."
            )
        else:
            show_empty_message()

    # ----------------- Boxplot durasi per status -----------------
    st.subheader("Sebaran durasi peminjaman per status peminjaman")
    st.caption(
        "Grafik ini digunakan untuk melihat sebaran lama peminjaman untuk setiap status, "
        "sehingga tampak apakah ada status tertentu dengan durasi peminjaman yang cenderung lebih lama."
    )
    fig_box = chart_boxplot_durasi_per_status(df_filtered)

    if fig_box is not None:
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        show_empty_message()

# ======================================================
# HALAMAN: DATA ANGGOTA
# ======================================================
elif page == "Data anggota":
    st.subheader("Data anggota perpustakaan")
    st.write(
        "Halaman ini menampilkan data anggota perpustakaan dan ringkasan berdasarkan "
        "status dan fakultas."
    )

    try:
        with st.spinner("Memuat data anggota..."):
            df_anggota = load_anggota()
    except Exception as e:
        st.error("Gagal memuat data anggota dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
        st.stop()

    # Pencarian nama anggota
    search_nama = st.text_input(
        "Pencarian nama anggota",
        placeholder="Ketik nama atau sebagian nama anggota..."
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
        mime="text/csv"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jumlah anggota per status")
        st.caption(
            "Grafik ini digunakan untuk melihat komposisi jenis anggota yang terdaftar "
            "di perpustakaan."
        )
        fig_status = chart_anggota_per_status(df_anggota_view)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.subheader("Jumlah anggota per fakultas")
        st.caption(
            "Grafik ini menampilkan sebaran anggota perpustakaan berdasarkan fakultas asal."
        )
        fig_fak = chart_anggota_per_fakultas_treemap(df_anggota_view)
        st.plotly_chart(fig_fak, use_container_width=True)

# ======================================================
# HALAMAN: DATA BUKU
# ======================================================
elif page == "Data buku":
    st.subheader("Data koleksi buku")
    st.write(
        "Halaman ini menampilkan data koleksi buku dan ringkasan berdasarkan kategori "
        "serta tahun terbit."
    )

    try:
        with st.spinner("Memuat data buku..."):
            df_buku = load_buku()
    except Exception as e:
        st.error("Gagal memuat data buku dari database. Periksa koneksi ke MySQL.")
        st.exception(e)
        st.stop()

    # Pencarian judul buku
    search_judul = st.text_input(
        "Pencarian judul buku",
        placeholder="Ketik judul atau sebagian judul buku..."
    )
    df_buku_view = df_buku.copy()
    if search_judul:
        df_buku_view = df_buku_view[
            df_buku_view["judul"].str.contains(search_judul, case=False, na=False)
        ]

    with st.expander("Tabel data buku"):
        st.dataframe(df_buku_view, use_container_width=True, height=350)

    csv_buku = df_buku_view.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh data buku (CSV)",
        data=csv_buku,
        file_name="buku.csv",
        mime="text/csv"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Jumlah buku per kategori")
        st.caption(
            "Grafik ini digunakan untuk melihat sebaran koleksi buku berdasarkan kategori buku."
        )
        fig_kat = chart_buku_per_kategori(df_buku_view)
        st.plotly_chart(fig_kat, use_container_width=True)

    with col2:
        st.subheader("Jumlah buku per tahun terbit")
        st.caption(
            "Grafik ini memperlihatkan perkembangan jumlah koleksi berdasarkan tahun terbit buku."
        )
        fig_th = chart_buku_per_tahun(df_buku_view)
        st.plotly_chart(fig_th, use_container_width=True)
