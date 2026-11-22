# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Zaianlpfp/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Zaianlpfp/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entri ini berisi sebuah gambar koran (entry.png) yang merangkum 36 cerita berita hari itu, beserta program kecil (main.ts) yang menyalin gambar tersebut ke direktori output.

Program main.ts tidak mengubah gambar sama sekali: ia membaca entry.png, memeriksa bahwa berkas itu memang gambar yang sah (magic bytes PNG atau JPEG, ukuran minimal 1024 byte, dan dimensi yang bisa dibaca), lalu menyalinnya ke direktori output. Setelah disalin, hasil salinan dibaca kembali dan dibandingkan byte per byte serta sha256-nya dengan sumber, supaya salinan yang rusak atau terpotong langsung ketahuan.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=vdteqqjz&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
