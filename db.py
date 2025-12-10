"""
db.py
Modul koneksi dan pemuatan data dari MySQL untuk dashboard Seperlima.
Semua query menggunakan tabel dasar (tanpa VIEW).
"""

import streamlit as st
import pandas as pd
import mysql.connector


def get_connection():
    """
    Membuat koneksi ke database MySQL lokal.
    Sesuaikan user/password jika konfigurasi berbeda.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # isi jika MySQL memakai password
        database="seperlima"  # nama database
    )


@st.cache_data
def load_peminjaman_detail():
    """
    Mengambil data peminjaman dan menggabungkan dengan anggota, prodi,
    fakultas, buku, judul, klasifikasi, dan petugas.

    Kolom penting yang dihasilkan antara lain:
    - tgl_pinjam, tgl_kembali, durasi_peminjaman, denda_buku, status_peminjaman
    - nama_anggota, status_anggota, nama_prodi, jenjang, nama_fakultas
    - judul, kategori_buku, tahun_terbit, status_buku, eksemplar
    - nama_petugas
    """
    conn = get_connection()
    query = """
        SELECT
            p.id_peminjaman,
            p.tgl_pinjam,
            p.tgl_kembali,
            p.durasi_peminjaman,
            p.denda_buku,
            CASE
                WHEN p.tgl_kembali IS NULL THEN 'Sedang dipinjam'
                ELSE 'Selesai'
            END AS status_peminjaman,

            a.id_anggota,
            a.no_identitas,
            a.status AS status_anggota,
            a.nama_anggota,
            a.email,

            ps.nama_prodi,
            ps.jenjang,
            f.nama_fakultas,

            b.id_buku,
            j.judul,
            k.kategori_buku,
            b.tahun_terbit,
            b.isbn,
            b.status AS status_buku,
            b.eksemplar,

            pt.id_petugas,
            pt.nama_petugas
        FROM peminjaman p
        JOIN anggota a ON p.id_anggota = a.id_anggota
        LEFT JOIN program_studi ps ON a.id_prodi = ps.id_prodi
        LEFT JOIN fakultas f ON ps.id_fakultas = f.id_fakultas
        JOIN buku b ON p.id_buku = b.id_buku
        JOIN judul j ON b.id_judul = j.id_judul
        JOIN klasifikasi k ON b.id_klasifikasi = k.id_klasifikasi
        JOIN petugas pt ON p.id_petugas = pt.id_petugas
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df["tgl_pinjam"] = pd.to_datetime(df["tgl_pinjam"])
    df["tgl_kembali"] = pd.to_datetime(df["tgl_kembali"])
    return df


@st.cache_data
def load_anggota():
    """
    Mengambil data anggota, sudah digabung dengan program studi dan fakultas.
    Dipakai di halaman 'Anggota'.
    """
    conn = get_connection()
    query = """
        SELECT
            a.id_anggota,
            a.no_identitas,
            a.status AS status_anggota,
            a.nama_anggota,
            a.email,
            ps.nama_prodi,
            ps.jenjang,
            f.nama_fakultas
        FROM anggota a
        LEFT JOIN program_studi ps ON a.id_prodi = ps.id_prodi
        LEFT JOIN fakultas f ON ps.id_fakultas = f.id_fakultas
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def load_buku():
    """
    Mengambil data koleksi buku beserta:
    - kode_judul & judul
    - kode_klasifikasi & kategori_buku
    - kode_pengarang (bisa lebih dari satu, digabung dengan koma)
    - tahun terbit, ISBN, status, dan eksemplar

    Sumber: tabel buku, judul, klasifikasi, buku_pengarang, pengarang.
    """
    conn = get_connection()
    query = """
        SELECT
            b.id_buku,
            j.kode_judul,
            j.judul,
            k.kode_klasifikasi,
            k.kategori_buku,
            -- bisa lebih dari satu pengarang per buku
            GROUP_CONCAT(pg.kode_pengarang
                         ORDER BY bp.urutan_pengarang
                         SEPARATOR ', ') AS kode_pengarang,
            b.tahun_terbit,
            b.isbn,
            b.status AS status_buku,
            b.eksemplar
        FROM buku b
        JOIN judul j
            ON b.id_judul = j.id_judul
        JOIN klasifikasi k
            ON b.id_klasifikasi = k.id_klasifikasi
        LEFT JOIN buku_pengarang bp
            ON b.id_buku = bp.id_buku
        LEFT JOIN pengarang pg
            ON bp.id_pengarang = pg.id_pengarang
        GROUP BY
            b.id_buku,
            j.kode_judul,
            j.judul,
            k.kode_klasifikasi,
            k.kategori_buku,
            b.tahun_terbit,
            b.isbn,
            b.status,
            b.eksemplar
        ORDER BY b.id_buku;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df



@st.cache_data
def load_fakultas():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM fakultas", conn)
    conn.close()
    return df


@st.cache_data
def load_program_studi():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM program_studi", conn)
    conn.close()
    return df


@st.cache_data
def load_pengarang():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM pengarang", conn)
    conn.close()
    return df


@st.cache_data
def load_buku_pengarang():
    """
    Mengambil data relasi buku-pengarang beserta nama judul & nama pengarang.
    """
    conn = get_connection()
    query = """
        SELECT
            bp.id_buku_pengarang,
            bp.id_buku,
            bp.id_pengarang,
            bp.urutan_pengarang,
            j.judul,
            pg.nama_pengarang
        FROM buku_pengarang bp
        JOIN buku b ON bp.id_buku = b.id_buku
        JOIN judul j ON b.id_judul = j.id_judul
        JOIN pengarang pg ON bp.id_pengarang = pg.id_pengarang
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def load_petugas():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM petugas", conn)
    conn.close()
    return df

# nambah tabel klasifikasi sama judul

@st.cache_data
def load_judul():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM judul", conn)
    conn.close()
    return df

@st.cache_data
def load_klasifikasi():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM klasifikasi", conn)
    conn.close()
    return df
