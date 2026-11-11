#!/usr/bin/env python3
"""
Server lokal untuk aplikasi HSI. Mendukung HTTP Range supaya audio bisa digeser (seek) dengan benar,
yang tidak didukung oleh `python3 -m http.server`.

Pakai:  python3 serve.py            lalu buka http://localhost:8000
        python3 serve.py 9000       port lain
        python3 serve.py --lan      bisa dibuka dari HP di jaringan yang sama (hati-hati, jangan di jaringan umum)
Bawaan hanya menerima koneksi dari komputer ini (127.0.0.1).
"""
import http.server, mimetypes, os, re, socketserver, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
mimetypes.add_type("audio/mpeg", ".mp3"); mimetypes.add_type("audio/mp4", ".m4a"); mimetypes.add_type("audio/aac", ".aac")
mimetypes.add_type("audio/ogg", ".ogg"); mimetypes.add_type("audio/wav", ".wav"); mimetypes.add_type("audio/webm", ".webm")
mimetypes.add_type("application/json", ".json")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def guess_type(self, path):
        t = mimetypes.guess_type(path)[0] or "application/octet-stream"
        return t + "; charset=utf-8" if t.startswith("text/") or t == "application/json" else t
    def log_message(self, fmt, *a): pass
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes"); self.send_header("Cache-Control", "no-cache")
        super().end_headers()
    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
        size = os.path.getsize(path)
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return super().send_head()
        if m.group(1) == "":                      # "bytes=-N" artinya N byte terakhir
            start, end = max(0, size - int(m.group(2))), size - 1
        else:
            start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start >= size or start > end:
            self.send_response(416); self.send_header("Content-Range", f"bytes */{size}"); self.end_headers(); return None
        f = open(path, "rb"); f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f
    def copyfile(self, source, outputfile):
        n = getattr(self, "_remaining", None)
        if n is None: return super().copyfile(source, outputfile)
        while n > 0:
            chunk = source.read(min(65536, n))
            if not chunk: break
            try: outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError): break
            n -= len(chunk)
        self._remaining = None

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    port = int(args[0]) if args else 8000
    host = "" if "--lan" in sys.argv else "127.0.0.1"
    # Di Windows, reuse_address membolehkan dua server memakai port yang sama tanpa pesan galat, jadi hanya dipakai di Linux dan macOS.
    socketserver.ThreadingTCPServer.allow_reuse_address = (os.name != "nt")
    with socketserver.ThreadingTCPServer((host, port), H) as srv:
        print(f"Aplikasi HSI berjalan di http://localhost:{port}  (Ctrl+C untuk berhenti)")
        try: srv.serve_forever()
        except KeyboardInterrupt: print("\nBerhenti.")
