"""
db.py
Modul untuk menangani koneksi ke database MySQL dan pemuatan data
ke dalam DataFrame pandas. Dipanggil dari app.py.
"""

import streamlit as st
import pandas as pd
import mysql.connector


def get_connection():
    """
    Membuat koneksi ke database MySQL.
    Sesuaikan parameter host, user, password, dan database
    dengan konfigurasi lokal.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",        # sesuaikan jika berbeda
        password="",        # isi jika MySQL memakai password
        database="seperlima"
    )


@st.cache_data
def load_peminjaman_detail():
    """
    Mengambil data dari view vw_peminjaman_detail.
    View ini menggabungkan informasi peminjaman, anggota, buku, prodi, dan fakultas.
    Hasil dikembalikan sebagai DataFrame.
    """
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vw_peminjaman_detail", conn)
    conn.close()

    # Konversi kolom tanggal ke tipe datetime untuk memudahkan filter dan visualisasi
    df["tgl_pinjam"] = pd.to_datetime(df["tgl_pinjam"])
    df["tgl_kembali"] = pd.to_datetime(df["tgl_kembali"])
    return df


@st.cache_data
def load_anggota():
    """
    Mengambil data anggota beserta program studi dan fakultas.
    Data digunakan untuk halaman 'Anggota'.
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
    Mengambil data koleksi buku beserta judul dan kategori/klasifikasi.
    Data digunakan untuk halaman 'Buku'.
    """
    conn = get_connection()
    query = """
        SELECT 
            b.id_buku,
            j.judul,
            k.kategori_buku,
            b.tahun_terbit,
            b.isbn
        FROM buku b
        JOIN judul j ON b.kode_judul = j.kode_judul
        JOIN klasifikasi k ON b.kode_klasifikasi = k.kode_klasifikasi
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
