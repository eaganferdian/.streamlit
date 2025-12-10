"""
charts.py
Modul berisi fungsi-fungsi pembuat grafik menggunakan Plotly.
Setiap fungsi menerima DataFrame dan mengembalikan objek figure.
"""

import plotly.express as px
import pandas as pd

# Peta warna khusus fakultas ITK
FAKULTAS_COLOR_MAP = {
    "Fakultas Sains dan Teknologi Informasi": "#3B82F6",      # biru
    "Fakultas Pembangunan Berkelanjutan": "#22C55E",          # hijau
    "Fakultas Rekayasa dan Teknologi Industri": "#EF4444",    # merah
}

# ==============================
# Grafik untuk halaman Ringkasan
# ==============================

def chart_tren_bulanan_status(df_pinjam: pd.DataFrame):
    """
    Grafik batang bertumpuk jumlah peminjaman per bulan,
    dikelompokkan berdasarkan status peminjaman.
    """
    df = df_pinjam.copy()
    df["bulan"] = df["tgl_pinjam"].dt.to_period("M").astype(str)

    per_bulan_status = (
        df.groupby(["bulan", "status_peminjaman"])
          .size()
          .reset_index(name="jumlah")
    )

    fig = px.bar(
        per_bulan_status,
        x="bulan",
        y="jumlah",
        color="status_peminjaman",
        title="Perkembangan peminjaman per bulan berdasarkan status",
    )
    fig.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah peminjaman"
    )
    return fig


def chart_peminjaman_per_fakultas(df_pinjam: pd.DataFrame):
    """
    Grafik batang jumlah peminjaman per fakultas.
    Menggunakan warna khusus per fakultas.
    """
    per_fak = df_pinjam.groupby("nama_fakultas").size().reset_index(name="jumlah")

    # Urutan kategori sesuai mapping warna (kalau ada)
    kategori_fakultas = [
        f for f in FAKULTAS_COLOR_MAP.keys()
        if f in per_fak["nama_fakultas"].unique()
    ]

    fig = px.bar(
        per_fak,
        x="nama_fakultas",
        y="jumlah",
        color="nama_fakultas",
        title="Peminjaman per fakultas",
        color_discrete_map=FAKULTAS_COLOR_MAP,
        category_orders={"nama_fakultas": kategori_fakultas},
    )
    fig.update_layout(
        xaxis_title="Fakultas",
        yaxis_title="Jumlah peminjaman",
        showlegend=False
    )
    return fig, per_fak


def chart_heatmap_fakultas_kategori(df_pinjam: pd.DataFrame):
    """
    Peta panas (heatmap) peminjaman berdasarkan kombinasi
    fakultas dan kategori buku.
    """
    per_fak_kat = (
        df_pinjam
        .groupby(["nama_fakultas", "kategori_buku"])
        .size()
        .reset_index(name="jumlah")
    )

    if per_fak_kat.empty:
        return None, per_fak_kat

    fig = px.density_heatmap(
        per_fak_kat,
        x="kategori_buku",
        y="nama_fakultas",
        z="jumlah",
        color_continuous_scale="Blues",
        title="Pola peminjaman berdasarkan fakultas dan kategori buku",
    )
    fig.update_layout(
        xaxis_title="Kategori buku",
        yaxis_title="Fakultas"
    )
    return fig, per_fak_kat


def chart_durasi_rata_per_fakultas(df_pinjam: pd.DataFrame):
    """
    Grafik batang rata-rata durasi peminjaman per fakultas.
    """
    durasi_fak = (
        df_pinjam.groupby("nama_fakultas")["durasi_peminjaman"]
        .mean()
        .reset_index(name="rata_durasi")
    )

    if durasi_fak.empty:
        return None, durasi_fak

    kategori_fakultas = [
        f for f in FAKULTAS_COLOR_MAP.keys()
        if f in durasi_fak["nama_fakultas"].unique()
    ]

    fig = px.bar(
        durasi_fak,
        x="nama_fakultas",
        y="rata_durasi",
        color="nama_fakultas",
        title="Rata-rata durasi peminjaman per fakultas",
        color_discrete_map=FAKULTAS_COLOR_MAP,
        category_orders={"nama_fakultas": kategori_fakultas},
    )
    fig.update_layout(
        xaxis_title="Fakultas",
        yaxis_title="Rata-rata durasi (hari)",
        showlegend=False
    )
    return fig, durasi_fak


# ==============================
# Grafik untuk halaman Peminjaman
# ==============================

def chart_peminjaman_per_status(df_filtered: pd.DataFrame):
    """
    Grafik batang distribusi jumlah peminjaman per status peminjaman.
    """
    per_status = df_filtered.groupby("status_peminjaman").size().reset_index(name="jumlah")

    if per_status.empty:
        return None, per_status

    fig = px.bar(
        per_status,
        x="status_peminjaman",
        y="jumlah",
        color="status_peminjaman",
        title="Peminjaman per status peminjaman",
    )
    fig.update_layout(
        xaxis_title="Status peminjaman",
        yaxis_title="Jumlah peminjaman",
        showlegend=False
    )
    return fig, per_status


def chart_top5_judul(df_filtered: pd.DataFrame):
    """
    Grafik batang horizontal untuk lima judul buku
    dengan frekuensi peminjaman tertinggi.
    """
    top_judul = (
        df_filtered.groupby("judul")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
        .head(5)
    )

    if top_judul.empty:
        return None, top_judul

    fig = px.bar(
        top_judul,
        x="jumlah",
        y="judul",
        orientation="h",
        title="Lima judul buku dengan peminjaman tertinggi",
        color="jumlah",
        text="jumlah",
    )
    fig.update_layout(
        xaxis_title="Jumlah peminjaman",
        yaxis_title="Judul buku"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig, top_judul


def chart_boxplot_durasi_per_status(df_filtered: pd.DataFrame):
    """
    (VERSI BARU – BUKAN BOXplot)
    Grafik batang berkelompok untuk menunjukkan
    jumlah peminjaman menurut:
      - status peminjaman
      - kelompok durasi (≤7, 8–14, 15–21, >21 hari)
    Lebih mudah dijelaskan dibanding boxplot.
    """
    df_durasi = df_filtered[df_filtered["durasi_peminjaman"].notna()].copy()

    if df_durasi.empty:
        return None

    max_durasi = int(df_durasi["durasi_peminjaman"].max())
    # Batas kelompok durasi (boleh diubah kalau mau)
    bins = [0, 7, 14, 21, max_durasi + 1]
    labels = ["≤ 7 hari", "8–14 hari", "15–21 hari", "> 21 hari"]

    df_durasi["kelompok_durasi"] = pd.cut(
        df_durasi["durasi_peminjaman"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    per_status_durasi = (
        df_durasi
        .groupby(["status_peminjaman", "kelompok_durasi"])
        .size()
        .reset_index(name="jumlah")
    )

    if per_status_durasi.empty:
        return None

    fig = px.bar(
        per_status_durasi,
        x="status_peminjaman",
        y="jumlah",
        color="kelompok_durasi",
        barmode="group",
        title="Sebaran durasi peminjaman per status (kelompok hari)",
        text="jumlah",
    )
    fig.update_layout(
        xaxis_title="Status peminjaman",
        yaxis_title="Jumlah peminjaman",
        legend_title_text="Kelompok durasi",
    )
    return fig


# ==============================
# Grafik untuk halaman Anggota
# ==============================

def chart_anggota_per_status(df_anggota_view: pd.DataFrame):
    """
    Grafik batang jumlah anggota per status keanggotaan.
    """
    per_status = df_anggota_view.groupby("status_anggota").size().reset_index(name="jumlah")

    fig = px.bar(
        per_status,
        x="status_anggota",
        y="jumlah",
        color="status_anggota",
        title="Jumlah anggota per status",
    )
    fig.update_layout(
        xaxis_title="Status anggota",
        yaxis_title="Jumlah anggota",
        showlegend=False
    )
    return fig


def chart_anggota_per_fakultas_treemap(df_anggota_view: pd.DataFrame):
    """
    Treemap jumlah anggota per fakultas, dengan warna khusus per fakultas.
    """
    per_fak = df_anggota_view.groupby("nama_fakultas").size().reset_index(name="jumlah")

    fig = px.treemap(
        per_fak,
        path=["nama_fakultas"],
        values="jumlah",
        title="Jumlah anggota per fakultas",
        color="nama_fakultas",
        color_discrete_map=FAKULTAS_COLOR_MAP,
    )
    return fig


# ==============================
# Grafik untuk halaman Buku
# ==============================

def chart_buku_per_kategori(df_buku_view: pd.DataFrame):
    """
    Grafik batang horizontal jumlah buku per kategori.
    """
    per_kat = df_buku_view.groupby("kategori_buku").size().reset_index(name="jumlah")

    fig = px.bar(
        per_kat,
        x="jumlah",
        y="kategori_buku",
        orientation="h",
        color="kategori_buku",
        title="Jumlah buku per kategori",
        text="jumlah",
    )
    fig.update_layout(
        xaxis_title="Jumlah buku",
        yaxis_title="Kategori buku"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


def chart_buku_per_tahun(df_buku_view: pd.DataFrame):
    """
    Grafik garis jumlah buku per tahun terbit.
    """
    per_tahun = df_buku_view.groupby("tahun_terbit").size().reset_index(name="jumlah")

    fig = px.line(
        per_tahun,
        x="tahun_terbit",
        y="jumlah",
        markers=True,
        title="Jumlah buku per tahun terbit",
    )
    fig.update_layout(
        xaxis_title="Tahun terbit",
        yaxis_title="Jumlah buku"
    )
    return fig
