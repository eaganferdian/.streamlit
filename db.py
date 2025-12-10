import streamlit as st
import pandas as pd
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="seperlima"
    )

@st.cache_data
def load_peminjaman_detail():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vw_peminjaman_detail", conn)
    conn.close()

    df["tgl_pinjam"] = pd.to_datetime(df["tgl_pinjam"])
    df["tgl_kembali"] = pd.to_datetime(df["tgl_kembali"])
    return df

@st.cache_data
def load_anggota():
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
