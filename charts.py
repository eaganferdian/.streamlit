"""
charts.py
Semua fungsi visualisasi untuk dashboard perpustakaan.

Catatan:
- Semua fungsi SELALU mengembalikan plotly.graph_objs.Figure (tidak pernah None),
  sehingga aman untuk langsung dipakai di st.plotly_chart().
- Beberapa fungsi juga mengembalikan DataFrame agregat sebagai nilai kedua
  untuk dipakai sebagai insight/caption di app.py.
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ==========================
# Palet warna “perpustakaan”
# ==========================
# Diangkat dari gambar:
#  - #8C663E  Cambridge Leather
#  - #57391B  Earthtone
#  - #0D3B4A  Sea of Stars (aksen biru)
#  - #381F08  Medium Roast
#  - #200E03  Super Black

PALETTE = ["#8C663E", "#57391B", "#0D3B4A", "#381F08", "#200E03"]

# Background chart dibuat transparan supaya menyatu dengan tema Streamlit
PLOT_BG = "rgba(0,0,0,0)"   # transparan
PAPER_BG = "rgba(0,0,0,0)"

GRID_COLOR = "#3A2A18"      # garis grid cokelat lembut
AXIS_LINE = "#8C663E"       # garis sumbu warna leather
FONT_COLOR = "#F9FAFB"


def _apply_common_layout(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Layout seragam untuk semua grafik (tanpa background solid)."""
    fig.update_layout(
        title=title or "",
        title_font=dict(color=FONT_COLOR, size=18),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=FONT_COLOR),
        legend=dict(
            bgcolor="rgba(32,14,3,0.85)",   # panel legenda cokelat transparan
            bordercolor="#57391B",
            borderwidth=1,
        ),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor=AXIS_LINE,
        showline=True,
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        linecolor=AXIS_LINE,
        showline=True,
    )
    return fig



def _empty_fig(title: str, message: str) -> go.Figure:
    """Figure placeholder ketika tidak ada data / kolom yang dibutuhkan."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color=FONT_COLOR),
        align="center",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _apply_common_layout(fig, title)


# ============================================================
# 1. RINGKASAN / PEMINJAMAN
# ============================================================

def chart_tren_bulanan_status(df_pinjam: pd.DataFrame) -> go.Figure:
    """
    Line chart (dengan area) tren peminjaman per bulan berdasarkan status.
    Menggunakan kolom:
      - tgl_pinjam (datetime)
      - status_peminjaman
    """
    if df_pinjam.empty:
        return _empty_fig(
            "Perkembangan peminjaman per bulan",
            "Belum ada data peminjaman yang bisa ditampilkan."
        )

    df = df_pinjam.copy()
    df["bulan"] = df["tgl_pinjam"].dt.to_period("M").astype(str)

    per_bulan_status = (
        df.groupby(["bulan", "status_peminjaman"])
          .size()
          .reset_index(name="jumlah")
    )

    fig = px.area(
        per_bulan_status,
        x="bulan",
        y="jumlah",
        color="status_peminjaman",
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(mode="lines+markers")
    fig.update_xaxes(title_text="Bulan")
    fig.update_yaxes(title_text="Jumlah peminjaman")
    return _apply_common_layout(fig, "Perkembangan peminjaman per bulan berdasarkan status")


def chart_peminjaman_per_fakultas(df_pinjam: pd.DataFrame):
    """
    Bar chart jumlah peminjaman per fakultas.
    """
    if df_pinjam.empty or "nama_fakultas" not in df_pinjam.columns:
        fig = _empty_fig(
            "Peminjaman per fakultas",
            "Kolom nama_fakultas tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    per_fak = (
        df_pinjam.groupby("nama_fakultas")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )

    fig = px.bar(
        per_fak,
        x="nama_fakultas",
        y="jumlah",
        color="nama_fakultas",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Fakultas")
    fig.update_yaxes(title_text="Jumlah peminjaman")
    fig = _apply_common_layout(fig, "Peminjaman per fakultas")
    return fig, per_fak


def chart_peminjaman_per_kategori(df_pinjam: pd.DataFrame):
    """
    Donut chart komposisi peminjaman per kategori_buku.
    """
    if df_pinjam.empty or "kategori_buku" not in df_pinjam.columns:
        fig = _empty_fig(
            "Peminjaman per kategori buku",
            "Kolom kategori_buku tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    per_kat = (
        df_pinjam.groupby("kategori_buku")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )

    fig = px.pie(
        per_kat,
        names="kategori_buku",
        values="jumlah",
        hole=0.5,
        color="kategori_buku",
        color_discrete_sequence=PALETTE,
    )
    fig = _apply_common_layout(fig, "Peminjaman per kategori buku")
    return fig, per_kat


def chart_durasi_rata_per_fakultas(df_pinjam: pd.DataFrame):
    """
    Bar chart rata-rata durasi peminjaman per fakultas.
    Menggunakan kolom:
      - nama_fakultas
      - durasi_peminjaman
    """
    if df_pinjam.empty or "durasi_peminjaman" not in df_pinjam.columns:
        fig = _empty_fig(
            "Rata-rata durasi peminjaman per fakultas",
            "Kolom durasi_peminjaman tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    durasi_fak = (
        df_pinjam.groupby("nama_fakultas")["durasi_peminjaman"]
        .mean()
        .reset_index(name="rata_durasi")
        .sort_values("rata_durasi", ascending=False)
    )

    fig = px.bar(
        durasi_fak,
        x="nama_fakultas",
        y="rata_durasi",
        color="nama_fakultas",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Fakultas")
    fig.update_yaxes(title_text="Rata-rata durasi (hari)")
    fig = _apply_common_layout(fig, "Rata-rata durasi peminjaman per fakultas")
    return fig, durasi_fak


def chart_hist_durasi(df_pinjam: pd.DataFrame):
    """
    Histogram distribusi durasi_peminjaman.
    """
    if df_pinjam.empty or "durasi_peminjaman" not in df_pinjam.columns:
        fig = _empty_fig(
            "Distribusi durasi peminjaman",
            "Kolom durasi_peminjaman tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    df = df_pinjam[df_pinjam["durasi_peminjaman"].notna()].copy()
    if df.empty:
        fig = _empty_fig(
            "Distribusi durasi peminjaman",
            "Semua durasi_peminjaman bernilai NULL."
        )
        return fig, pd.DataFrame()

    fig = px.histogram(
        df,
        x="durasi_peminjaman",
        nbins=10,
        color_discrete_sequence=[PALETTE[1]],
    )
    fig.update_xaxes(title_text="Durasi peminjaman (hari)")
    fig.update_yaxes(title_text="Jumlah peminjaman")
    fig = _apply_common_layout(fig, "Distribusi durasi peminjaman")
    # Data agregat sederhana (jumlah per bin tidak kita kembalikan di sini)
    return fig, df[["durasi_peminjaman"]]


def chart_scatter_durasi_denda(df_pinjam: pd.DataFrame) -> go.Figure:
    """
    Scatter plot durasi_peminjaman vs denda_buku.
    Membantu menjelaskan logika denda: semakin lama, potensi denda makin besar.
    """
    if df_pinjam.empty or "durasi_peminjaman" not in df_pinjam.columns or "denda_buku" not in df_pinjam.columns:
        return _empty_fig(
            "Hubungan durasi peminjaman dan denda",
            "Kolom durasi_peminjaman atau denda_buku tidak ditemukan."
        )

    df = df_pinjam.copy()
    df = df[df["durasi_peminjaman"].notna()]

    if df.empty:
        return _empty_fig(
            "Hubungan durasi peminjaman dan denda",
            "Belum ada data durasi & denda yang bisa ditampilkan."
        )

    fig = px.scatter(
        df,
        x="durasi_peminjaman",
        y="denda_buku",
        color="status_peminjaman",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Durasi peminjaman (hari)")
    fig.update_yaxes(title_text="Denda buku (Rp)")
    return _apply_common_layout(fig, "Hubungan durasi peminjaman dan denda")


# ============================================================
# 2. HALAMAN DATA PEMINJAMAN
# ============================================================

def chart_peminjaman_per_status(df_filtered: pd.DataFrame):
    """
    Bar chart distribusi jumlah peminjaman per status_peminjaman.
    """
    if df_filtered.empty or "status_peminjaman" not in df_filtered.columns:
        fig = _empty_fig(
            "Peminjaman per status peminjaman",
            "Kolom status_peminjaman tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    per_status = (
        df_filtered.groupby("status_peminjaman")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )

    fig = px.bar(
        per_status,
        x="status_peminjaman",
        y="jumlah",
        color="status_peminjaman",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Status peminjaman")
    fig.update_yaxes(title_text="Jumlah peminjaman")
    fig = _apply_common_layout(fig, "Peminjaman per status peminjaman")
    return fig, per_status


def chart_top5_judul(df_filtered: pd.DataFrame):
    """
    Horizontal bar: 5 judul buku dengan jumlah peminjaman terbanyak.
    """
    if df_filtered.empty or "judul" not in df_filtered.columns:
        fig = _empty_fig(
            "Lima judul buku dengan peminjaman tertinggi",
            "Kolom judul tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    top_judul = (
        df_filtered.groupby("judul")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
        .head(5)
    )

    if top_judul.empty:
        fig = _empty_fig(
            "Lima judul buku dengan peminjaman tertinggi",
            "Belum ada data peminjaman per judul."
        )
        return fig, top_judul

    fig = px.bar(
        top_judul,
        x="jumlah",
        y="judul",
        orientation="h",
        color="jumlah",
        color_continuous_scale=[PALETTE[0], PALETTE[1]],
    )
    fig.update_xaxes(title_text="Jumlah peminjaman")
    fig.update_yaxes(title_text="Judul buku", autorange="reversed")
    fig = _apply_common_layout(fig, "Lima judul buku dengan peminjaman tertinggi")
    return fig, top_judul


# ============================================================
# 3. HALAMAN DATA ANGGOTA
# ============================================================

def chart_anggota_per_status(df_anggota_view: pd.DataFrame) -> go.Figure:
    """
    Bar chart jumlah anggota per status_anggota (mahasiswa, dosen, tendik).
    """
    if df_anggota_view.empty or "status_anggota" not in df_anggota_view.columns:
        return _empty_fig(
            "Jumlah anggota per status",
            "Kolom status_anggota tidak ditemukan atau data kosong."
        )

    per_status = (
        df_anggota_view.groupby("status_anggota")
        .size()
        .reset_index(name="jumlah")
    )

    fig = px.bar(
        per_status,
        x="status_anggota",
        y="jumlah",
        color="status_anggota",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Status anggota")
    fig.update_yaxes(title_text="Jumlah anggota")
    return _apply_common_layout(fig, "Jumlah anggota per status")


def chart_anggota_per_fakultas(df_anggota_view: pd.DataFrame) -> go.Figure:
    """
    Treemap jumlah anggota per fakultas.
    """
    if df_anggota_view.empty or "nama_fakultas" not in df_anggota_view.columns:
        return _empty_fig(
            "Jumlah anggota per fakultas",
            "Kolom nama_fakultas tidak ditemukan atau data kosong."
        )

    per_fak = (
        df_anggota_view.groupby("nama_fakultas")
        .size()
        .reset_index(name="jumlah")
    )

    fig = px.treemap(
        per_fak,
        path=["nama_fakultas"],
        values="jumlah",
        color="jumlah",
        color_continuous_scale=[PALETTE[2], PALETTE[1]],
    )
    return _apply_common_layout(fig, "Jumlah anggota per fakultas")


# ============================================================
# 4. HALAMAN DATA BUKU
# ============================================================

def chart_buku_per_kategori(df_buku_view: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar jumlah buku per kategori_buku.
    """
    if df_buku_view.empty or "kategori_buku" not in df_buku_view.columns:
        return _empty_fig(
            "Jumlah buku per kategori",
            "Kolom kategori_buku tidak ditemukan atau data kosong."
        )

    per_kat = (
        df_buku_view.groupby("kategori_buku")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )

    fig = px.bar(
        per_kat,
        x="jumlah",
        y="kategori_buku",
        orientation="h",
        color="kategori_buku",
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Jumlah buku")
    fig.update_yaxes(title_text="Kategori buku", autorange="reversed")
    return _apply_common_layout(fig, "Jumlah buku per kategori")


def chart_buku_per_tahun(df_buku_view: pd.DataFrame) -> go.Figure:
    """
    Line chart jumlah buku per tahun_terbit.
    """
    if df_buku_view.empty or "tahun_terbit" not in df_buku_view.columns:
        return _empty_fig(
            "Jumlah buku per tahun terbit",
            "Kolom tahun_terbit tidak ditemukan atau data kosong."
        )

    per_tahun = (
        df_buku_view.groupby("tahun_terbit")
        .size()
        .reset_index(name="jumlah")
        .sort_values("tahun_terbit")
    )

    fig = px.line(
        per_tahun,
        x="tahun_terbit",
        y="jumlah",
        markers=True,
        color_discrete_sequence=[PALETTE[0]],
    )
    fig.update_xaxes(title_text="Tahun terbit")
    fig.update_yaxes(title_text="Jumlah buku")
    return _apply_common_layout(fig, "Jumlah buku per tahun terbit")


def chart_buku_per_status(df_buku_view: pd.DataFrame):
    """
    Bar chart jumlah buku per status (Tersedia, Dipinjam, Rusak, Hilang).
    SELALU mengembalikan Figure.
    """
    # Deteksi nama kolom status
    status_col = None
    if "status_buku" in df_buku_view.columns:
        status_col = "status_buku"
    elif "status" in df_buku_view.columns:
        status_col = "status"

    if df_buku_view.empty or not status_col:
        fig = _empty_fig(
            "Kondisi / status koleksi buku",
            "Kolom status/status_buku tidak ditemukan atau data kosong."
        )
        return fig, pd.DataFrame()

    per_status = (
        df_buku_view.groupby(status_col)
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )

    if per_status.empty:
        fig = _empty_fig(
            "Kondisi / status koleksi buku",
            "Belum ada data status buku yang bisa ditampilkan."
        )
        return fig, per_status

    fig = px.bar(
        per_status,
        x=status_col,
        y="jumlah",
        color=status_col,
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(title_text="Status buku")
    fig.update_yaxes(title_text="Jumlah buku")
    fig = _apply_common_layout(fig, "Kondisi / status koleksi buku")
    return fig, per_status
