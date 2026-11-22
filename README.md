# News Image — 21 November 2026

Entri ini berisi sebuah gambar koran (entry.png) yang merangkum 36 cerita
berita hari itu, beserta program kecil (main.ts) yang menyalin gambar
tersebut ke direktori output.

Program main.ts tidak mengubah gambar sama sekali: ia membaca entry.png,
memeriksa bahwa berkas itu memang gambar yang sah (magic bytes PNG atau
JPEG, ukuran minimal 1024 byte, dan dimensi yang bisa dibaca), lalu
menyalinnya ke direktori output. Setelah disalin, hasil salinan dibaca
kembali dan dibandingkan byte per byte serta sha256-nya dengan sumber,
supaya salinan yang rusak atau terpotong langsung ketahuan.

## Cara menjalankan

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Hasilnya: `out/entry.png`, salinan yang identik byte per byte dengan
`entry.png` di repo ini. Kalau variabel `MAKEFUN_OUTPUT_DIR` tidak diisi,
output ditulis ke direktori `out`.

## File

- `main.ts` — program penyalin + pemeriksa gambar (Node.js, tanpa dependensi)
- `entry.png` — gambar koran hasil entri ini
- `build.py` — skrip pembangun gambar
- `LICENSE` — lisensi MIT
