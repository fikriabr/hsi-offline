# Aplikasi HSI dengan pemutar audio

Aplikasi belajar HSI AbdullahRoy: roadmap per kitab, pembaca teks lengkap, dan pemutar audio bergelombang.
Hanya untuk belajar pribadi. Hak cipta materi milik tim HSI dan Ustadz Abdullah Roy, jadi jangan dibagikan
atau dipublikasikan (jangan taruh folder ini di hosting publik).

## Isi folder
- `index.html`  aplikasinya (satu berkas)
- `text/`       teks 1.437 halaqah
- `audio/`      tempat audio (diisi oleh `download_audio.py`), dengan `manifest.json`
- `peaks/`      data gelombang untuk pemutar (dibuat otomatis oleh pengunduh)
- `serve.py`    server lokal (mendukung geser posisi audio)
- `download_audio.py`  pengunduh audio, `halaqah-index.json` daftar halaqah

## Langkah
Butuh Python 3. ffmpeg disarankan supaya gelombang dibuat saat mengunduh (tanpa ffmpeg, peramban membuatnya
saat audio pertama kali diputar).

1. Unduh audio. Mulai dari kitab yang sedang Anda pelajari:
   ```
   python3 download_audio.py --list
   python3 download_audio.py --series tsalatsah
   ```
   Pengunduh berjalan satu per satu dengan jeda 3 detik, bisa dihentikan (Ctrl+C) lalu dilanjutkan.
   `--all` mengunduh semuanya. Ukurannya besar, jadi cek ruang disk dulu.
2. Jalankan aplikasi:
   ```
   python3 serve.py
   ```
   Lalu buka http://localhost:8000. Jangan memakai `python3 -m http.server`, karena tidak mendukung geser audio.
3. Buka halaqah, lalu tekan putar. Klik atau seret gelombang untuk berpindah posisi.
   Pemutar mengingat posisi terakhir tiap halaqah dan kecepatan putar Anda.

## Windows (tanpa mengetik perintah)
1. Pasang Python 3 dari https://www.python.org/downloads/ dan centang "Add python.exe to PATH" saat memasang.
   ffmpeg tidak wajib. Jika ada, gelombang dibuat saat mengunduh.
2. Ekstrak zip ini, buka foldernya.
3. Klik dua kali `unduh-audio.bat`, lalu pilih 1 (kitab yang sedang dipelajari), 2 (pilih sendiri), atau 3 (semua).
   Bisa dihentikan dengan Ctrl+C lalu Y, dan dilanjutkan dengan membuka berkas ini lagi.
4. Klik dua kali `jalankan.bat`. Peramban terbuka sendiri di http://localhost:8000.
   Biarkan jendela hitamnya terbuka selama belajar. `jalankan.bat 9000` memakai port lain.
Jika Windows menampilkan peringatan "SmartScreen", pilih "Info lebih lanjut" lalu "Tetap jalankan": berkas ini hanya
skrip teks biasa yang bisa Anda baca dengan Notepad.

## Pemutar
- Klik atau seret gelombang untuk berpindah posisi. Dari keyboard: panah kiri/kanan (5 detik), Shift+panah (15 detik),
  PageUp/PageDown (60 detik), Home/End, Spasi untuk putar dan jeda.
- Kecepatan 0,75× sampai 2×. Tombol mundur dan maju 15 detik.
- Tombol media di HP dan keyboard (layar kunci) ikut berfungsi.
- Halaqah yang audionya belum diunduh tetap bisa dibaca, dan audionya diputar di ilmiyyah.com.

## Catatan
- Progres belajar tersimpan di peramban yang Anda pakai (tidak ikut ke perangkat lain).
- Agar bisa dibuka dari HP di jaringan rumah yang sama: `python3 serve.py --lan`. Jangan di jaringan umum.

## Perkiraan unduhan semuanya (`--all`)
- Sekitar 1.150 halaqah punya audio. Sekitar 280 lainnya belum punya audio di situs (tag audio kosong), jadi dilewati
  dan dilaporkan di akhir. Ini perkiraan dari sampel 78 halaqah, bukan hitungan pasti.
- Audio disimpan di beberapa tempat (Google Drive, archive.org, Dropbox). Pengunduh mengikutinya otomatis.
- Dari sampel Google Drive, rata-rata sekitar 1,7 MB per halaqah, jadi totalnya kira-kira 2 GB.
- Dengan jeda 3 detik, waktunya sekitar 1 sampai 1,5 jam. Boleh dihentikan dan dilanjutkan kapan saja.
- Halaqah yang gagal karena gangguan jaringan dicoba ulang otomatis. Sisanya dicoba lagi dengan menjalankan perintah yang sama.
