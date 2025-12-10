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

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Seperlima Dashboard",
    page_icon="📚",
    layout="wide",
)

# ==========================================
# CSS CUSTOM UNTUK UI YANG LEBIH PROFESIONAL
# ==========================================
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #6366F1, #22C55E);
        padding: 18px 24px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
    }

    /* Kartu ringkasan */
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
        font-size: 1.7rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER UTAMA
# ==========================================

st.markdown("""
<div class="main-header">
    <h2 style="margin-bottom:4px;">📚 SEPERLIMA – Dashboard Perpustakaan</h2>
    <span>Sistem Informasi Perpustakaan Kelompok 5 • Institut Teknologi Kalimantan</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# NAVIGASI SIDEBAR
# ==========================================
st.sidebar.title("🧭 Navigasi")
page = st.sidebar.radio(
    "Pilih halaman",
    ["Ringkasan umum", "Data peminjaman", "Data anggota", "Data buku"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard ini menampilkan visualisasi real-time dari database `seperlima`.")

# ==========================================
# FUNGSI PESAN DATA KOSONG
# ==========================================
def show_empty_message():
    st.info("Tidak ada data yang cocok dengan filter yang dipilih.")

# ==========================================
# HALAMAN 1 — RINGKASAN UMUM
# ==========================================
if page == "Ringkasan umum":

    try:
        with st.spinner("Memuat data peminjaman..."):
            df_pinjam = load_peminjaman_detail()
    except Exception as e:
        st.error("Gagal memuat data. Pastikan MySQL berjalan.")
        st.exception(e)
        st.stop()

    st.write("Halaman ini menampilkan gambaran umum aktivitas perpustakaan.")

    # KPI CARD
    total_peminjaman = len(df_pinjam)
    total_anggota = df_pinjam["id_anggota"].nunique()
    total_buku = df_pinjam["id_buku"].nunique()
    total_denda = int(df_pinjam["denda_buku"].sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total peminjaman</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_peminjaman}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Seluruh transaksi tercatat</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Anggota unik</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_anggota}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Yang pernah meminjam</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total buku dipinjam</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_buku}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Judul / eksemplar unik</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total denda</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">Rp {total_denda:,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sub">Akumulasi seluruh transaksi</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Ikhtisar Grafik")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Perkembangan peminjaman", "Per fakultas", "Fakultas × kategori", "Durasi peminjaman"]
    )

    # -- TAB 1: Tren bulanan
    with tab1:
        fig = chart_tren_bulanan_status(df_pinjam)
        st.plotly_chart(fig, use_container_width=True)

        df_pinjam["bulan"] = df_pinjam["tgl_pinjam"].dt.to_period("M").astype(str)
        per_bulan = df_pinjam.groupby("bulan").size().reset_index(name="jumlah")

        if not per_bulan.empty:
            puncak = per_bulan.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"📌 **Bulan dengan peminjaman tertinggi:** {puncak['bulan']} ({puncak['jumlah']} transaksi)"
            )

    # -- TAB 2: Per fakultas
    with tab2:
        fig, per_fak = chart_peminjaman_per_fakultas(df_pinjam)
        st.plotly_chart(fig, use_container_width=True)

        if len(per_fak) > 0:
            f_top = per_fak.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"🏆 Fakultas dengan peminjaman terbanyak adalah **{f_top['nama_fakultas']}** "
                f"dengan {f_top['jumlah']} transaksi."
            )

    # -- TAB 3: Heatmap Fakultas × Kategori
    with tab3:
        fig, per_fak_kat = chart_heatmap_fakultas_kategori(df_pinjam)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            top = per_fak_kat.sort_values("jumlah", ascending=False).iloc[0]
            st.caption(
                f"🔥 Kombinasi paling dominan adalah **{top['nama_fakultas']} × {top['kategori_buku']}** "
                f"dengan {top['jumlah']} peminjaman."
            )
        else:
            show_empty_message()

    # -- TAB 4: Durasi per fakultas
    with tab4:
        fig, durasi = chart_durasi_rata_per_fakultas(df_pinjam)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            top = durasi.sort_values("rata_durasi", ascending=False).iloc[0]
            st.caption(
                f"⏳ Fakultas dengan rata-rata durasi peminjaman terlama: **{top['nama_fakultas']}** "
                f"({top['rata_durasi']:.1f} hari)."
            )
        else:
            show_empty_message()

# ==========================================
# HALAMAN 2 — DATA PEMINJAMAN
# ==========================================
elif page == "Data peminjaman":

    st.subheader("Data Peminjaman Buku")

    df = load_peminjaman_detail()

    # ===== FILTER =====
    st.sidebar.subheader("Filter Peminjaman")
    min_date = df["tgl_pinjam"].min().date()
    max_date = df["tgl_pinjam"].max().date()

    date_range = st.sidebar.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, (tuple, list)):
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    fakultas_list = ["(Semua)"] + sorted(df["nama_fakultas"].unique())
    status_list = ["(Semua)"] + sorted(df["status_peminjaman"].unique())

    fak_filter = st.sidebar.selectbox("Fakultas", fakultas_list)
    stat_filter = st.sidebar.selectbox("Status", status_list)

    # APPLY FILTER
    df_filtered = df[
        (df["tgl_pinjam"].dt.date >= start_date) &
        (df["tgl_pinjam"].dt.date <= end_date)
    ]

    if fak_filter != "(Semua)":
        df_filtered = df_filtered[df_filtered["nama_fakultas"] == fak_filter]

    if stat_filter != "(Semua)":
        df_filtered = df_filtered[df_filtered["status_peminjaman"] == stat_filter]

    st.caption(
        f"Menampilkan data {start_date} — {end_date}, "
        f"{'Fakultas ' + fak_filter if fak_filter != '(Semua)' else 'semua fakultas'}, "
        f"{'Status ' + stat_filter if stat_filter != '(Semua)' else 'semua status'}."
    )

    # TABLE
    with st.expander("Tabel Data Peminjaman"):
        st.dataframe(df_filtered, use_container_width=True, height=350)

    st.download_button(
        label="Unduh Data (CSV)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="peminjaman.csv",
        mime="text/csv"
    )

    # KPI untuk halaman ini
    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.metric("Jumlah peminjaman", len(df_filtered))
    col_k2.metric("Total denda", f"Rp {df_filtered['denda_buku'].sum():,}")
    col_k3.metric(
        "Rata-rata durasi",
        f"{df_filtered['durasi_peminjaman'].mean():.1f} hari" if df_filtered["durasi_peminjaman"].notna().any() else "-"
    )

    # Grafik
    col1, col2 = st.columns(2)
    with col1:
        fig, _ = chart_peminjaman_per_status(df_filtered)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig, top = chart_top5_judul(df_filtered)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    fig = chart_boxplot_durasi_per_status(df_filtered)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# HALAMAN 3 — DATA ANGGOTA
# ==========================================
elif page == "Data anggota":

    st.subheader("Data Anggota Perpustakaan")
    df_a = load_anggota()

    search = st.text_input("Cari nama anggota", placeholder="ketik nama...")

    df_view = df_a.copy()
    if search:
        df_view = df_view[df_view["nama_anggota"].str.contains(search, case=False)]

    with st.expander("Tabel Anggota"):
        st.dataframe(df_view, use_container_width=True, height=350)

    st.download_button(
        "Unduh Data (CSV)",
        df_view.to_csv(index=False).encode("utf-8"),
        "anggota.csv",
        "text/csv"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(chart_anggota_per_status(df_view), use_container_width=True)
    with col2:
        st.plotly_chart(chart_anggota_per_fakultas_treemap(df_view), use_container_width=True)

# ==========================================
# HALAMAN 4 — DATA BUKU
# ==========================================
elif page == "Data buku":

    st.subheader("Data Koleksi Buku")
    df_b = load_buku()

    search = st.text_input("Cari judul buku", placeholder="ketik judul...")

    df_view = df_b.copy()
    if search:
        df_view = df_view[df_view["judul"].str.contains(search, case=False)]

    with st.expander("Tabel Buku"):
        st.dataframe(df_view, use_container_width=True, height=350)

    st.download_button(
        "Unduh Data (CSV)",
        df_view.to_csv(index=False).encode("utf-8"),
        "buku.csv",
        "text/csv"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(chart_buku_per_kategori(df_view), use_container_width=True)
    with col2:
        st.plotly_chart(chart_buku_per_tahun(df_view), use_container_width=True)
