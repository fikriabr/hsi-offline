#!/usr/bin/env python3
"""
Pengunduh audio halaqah HSI untuk belajar pribadi. Hanya memakai pustaka standar Python 3.
Gelombang suara untuk pemutar dibuat otomatis bila ffmpeg terpasang (disarankan, tetapi tidak wajib).

Cara pakai (jalankan di folder ini):
  python3 download_audio.py --list                       # daftar kode seri
  python3 download_audio.py --series tsalatsah           # satu seri
  python3 download_audio.py --series tsalatsah fadhlul   # beberapa seri
  python3 download_audio.py --all --delay 5              # semua, jeda 5 detik
  python3 download_audio.py --peaks-only                 # buat ulang gelombang untuk audio yang sudah ada

Hasil:
  audio/<seri>/<id>.<ekstensi>   berkas audio
  audio/manifest.json            daftar audio yang tersedia (dibaca aplikasi)
  peaks/<id>.json                data gelombang untuk pemutar

Catatan:
- Skrip membuka halaman halaqah di ilmiyyah.com, membaca alamat audio dari pemutar di halaman itu
  (sama seperti peramban Anda), lalu mengunduhnya. Tidak ada kunci yang tersimpan di skrip ini.
- Berurutan satu per satu dengan jeda (bawaan 3 detik, minimal 1 detik) supaya tidak membebani server HSI.
- Bisa dilanjutkan: berkas yang sudah selesai dilewati, unduhan yang terputus dilanjutkan.
- Simpan hanya untuk belajar sendiri. Hak cipta materi milik tim HSI dan Ustadz Abdullah Roy.
"""
import argparse, html, json, os, re, shutil, subprocess, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://ilmiyyah.com/archives/"
UA = "Mozilla/5.0 (personal study downloader)"
EXT = {"audio/mpeg": ".mp3", "audio/mp3": ".mp3", "audio/mp4": ".m4a", "audio/x-m4a": ".m4a", "audio/aac": ".aac",
       "audio/ogg": ".ogg", "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/webm": ".webm"}
PEAK_BINS = 600

def get(url, headers=None, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})}), timeout=timeout)

def audio_url(archive_id):
    page = get(BASE + str(archive_id)).read().decode("utf-8", "ignore")
    m = re.search(r'<audio[^>]*\ssrc="([^"]+)"', page)
    return html.unescape(m.group(1)) if m else None

def sniff_ext(path, ctype):
    if ctype in EXT: return EXT[ctype]
    with open(path, "rb") as f: head = f.read(12)
    if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"): return ".mp3"
    if head[4:8] == b"ftyp": return ".m4a"
    if head[:4] == b"OggS": return ".ogg"
    if head[:4] == b"RIFF": return ".wav"
    return ".audio"

def download(url, folder, stem):
    os.makedirs(folder, exist_ok=True)
    part = os.path.join(folder, stem + ".part")
    start = os.path.getsize(part) if os.path.exists(part) else 0
    try:
        r = get(url, {"Range": f"bytes={start}-"} if start else {}, timeout=120)
    except urllib.error.HTTPError as e:
        if e.code != 416: raise
        r = None
    ctype = r.headers.get("Content-Type", "").split(";")[0].strip().lower() if r else ""
    if r:
        if r.status == 200 and start: start = 0
        with open(part, "ab" if start else "wb") as out:
            while True:
                chunk = r.read(1 << 16)
                if not chunk: break
                out.write(chunk)
    final = os.path.join(folder, stem + sniff_ext(part, ctype))
    os.replace(part, final)
    return final

def with_retry(fn, tries=3):
    """Coba ulang untuk gangguan jaringan sementara (bukan untuk 404/403 yang pasti gagal)."""
    for n in range(1, tries + 1):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            if e.code in (404, 403, 401, 410) or n == tries: raise
        except Exception:
            if n == tries: raise
        time.sleep(5 * n)

def make_peaks(path, archive_id):
    """Gelombang dari ffmpeg: audio mono 8 kHz, lalu energi rata-rata (RMS) per bagian, skala 0 sampai 255."""
    if not shutil.which("ffmpeg"): return False
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True)
    data = r.stdout
    n = len(data) // 2
    if r.returncode != 0 or n < PEAK_BINS: return False
    import array, math
    samples = array.array("h"); samples.frombytes(data[: n * 2])
    step = n / PEAK_BINS; rms = []
    for i in range(PEAK_BINS):
        seg = samples[int(i * step): max(int(i * step) + 1, int((i + 1) * step))]
        rms.append(math.sqrt(sum(x * x for x in seg) / len(seg)))
    ref = sorted(rms)[int(0.95 * (PEAK_BINS - 1))] or 1.0   # ceramah biasanya rata volumenya, jadi pakai energi (RMS) dan skala persentil 95
    out = [min(255, round(v / ref * 255)) for v in rms]
    os.makedirs(os.path.join(HERE, "peaks"), exist_ok=True)
    with open(os.path.join(HERE, "peaks", f"{archive_id}.json"), "w") as f: json.dump({"p": out}, f, separators=(",", ":"))
    return True

def load_manifest(mpath):
    try:
        with open(mpath, encoding="utf-8") as f: return json.load(f)
    except Exception: return {}

def save_manifest(mpath, m):
    tmp = mpath + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(m, f, ensure_ascii=False, indent=0)
    os.replace(tmp, mpath)

def main():
    ap = argparse.ArgumentParser(description="Pengunduh audio halaqah HSI untuk belajar pribadi")
    ap.add_argument("--series", nargs="*", default=[]); ap.add_argument("--all", action="store_true"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--peaks-only", action="store_true", help="buat ulang gelombang untuk audio yang sudah ada")
    ap.add_argument("--out", default=os.path.join(HERE, "audio")); ap.add_argument("--delay", type=float, default=3.0)
    ap.add_argument("--limit", type=int, default=0, help="batasi jumlah halaqah per seri (uji coba)")
    a = ap.parse_args()
    idx = json.load(open(os.path.join(HERE, "halaqah-index.json"), encoding="utf-8"))
    if a.list:
        for k, v in idx.items(): print(f"{k:12} {len(v['halaqah']):4}  {v['name']}")
        return
    mpath = os.path.join(a.out, "manifest.json"); os.makedirs(a.out, exist_ok=True)
    manifest = load_manifest(mpath)
    chosen = list(idx) if (a.all or a.peaks_only and not a.series) else a.series
    if not chosen: ap.error("pilih --series KODE atau --all (lihat --list)")
    for k in chosen:
        if k not in idx: sys.exit(f"Kode seri tidak dikenal: {k}")
    if not shutil.which("ffmpeg"):
        print("Catatan: ffmpeg tidak ditemukan. Audio tetap diunduh, gelombang dibuat oleh peramban saat pertama kali diputar.")
    delay = max(a.delay, 1.0); fails = []
    for k in chosen:
        s = idx[k]; items = s["halaqah"][: a.limit] if a.limit else s["halaqah"]
        print(f"== {s['name']} ({len(items)} halaqah)")
        for h in items:
            aid = str(h["archive_id"]); rel = manifest.get(aid); full = os.path.join(a.out, rel) if rel else None
            if a.peaks_only:
                if full and os.path.exists(full) and not os.path.exists(os.path.join(HERE, "peaks", aid + ".json")):
                    print(f"  {h['no']:3}  gelombang: {'OK' if make_peaks(full, aid) else 'dilewati'}")
                continue
            if full and os.path.exists(full):
                if not os.path.exists(os.path.join(HERE, "peaks", aid + ".json")): make_peaks(full, aid)
                continue
            try:
                u = with_retry(lambda: audio_url(aid))
                if not u:
                    print(f"  {h['no']:3}  tidak ada audio di halaman, dilewati"); fails.append((k, h["no"], "tanpa audio")); time.sleep(delay); continue
                f = with_retry(lambda: download(u, os.path.join(a.out, k), aid))
                manifest[aid] = os.path.relpath(f, a.out).replace(os.sep, "/"); save_manifest(mpath, manifest)
                pk = make_peaks(f, aid)
                print(f"  {h['no']:3}  OK  {os.path.getsize(f)/1e6:.1f} MB  {os.path.basename(f)}  gelombang: {'ya' if pk else 'tidak'}")
            except Exception as e:
                print(f"  {h['no']:3}  GAGAL: {e}"); fails.append((k, h["no"], str(e)))
            time.sleep(delay)
    noaudio = [f for f in fails if f[2] == "tanpa audio"]; errors = [f for f in fails if f[2] != "tanpa audio"]
    have = sum(1 for v in manifest.values() if os.path.exists(os.path.join(a.out, v)))
    print(f"\nSelesai. Audio yang tersedia sekarang: {have}.")
    if noaudio: print(f"{len(noaudio)} halaqah memang belum punya audio di situs (tag audio kosong), tidak bisa diunduh.")
    if errors:
        print(f"{len(errors)} gagal diunduh. Jalankan perintah yang sama lagi untuk mencoba ulang hanya yang gagal:")
        for f in errors[:50]: print("  ", f)

if __name__ == "__main__":
    main()
