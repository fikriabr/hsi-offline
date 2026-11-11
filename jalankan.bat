@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
set "PY="
where py >nul 2>nul
if not errorlevel 1 py -3 --version >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto pyfound
where python >nul 2>nul
if errorlevel 1 goto nopython
python --version >nul 2>nul
if errorlevel 1 goto nopython
set "PY=python"
:pyfound
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" >nul 2>nul
if errorlevel 1 goto oldpython

set "PORT=8000"
if not "%~1"=="" set "PORT=%~1"
echo.
echo  Aplikasi HSI berjalan di http://localhost:%PORT%
echo  Peramban akan terbuka sebentar lagi. Biarkan jendela ini tetap terbuka selama Anda belajar.
echo  Untuk berhenti, tutup jendela ini atau tekan Ctrl+C.
echo.
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:%PORT%"
%PY% serve.py %PORT%
echo.
echo  Server berhenti. Jika muncul pesan port sudah dipakai, jalankan lagi dengan port lain, misalnya: jalankan.bat 9000
pause
exit /b 0

:nopython
echo.
echo  Python 3 belum terpasang di komputer ini.
echo  1. Buka https://www.python.org/downloads/ dan unduh Python 3.
echo  2. Saat memasang, centang "Add python.exe to PATH".
echo  3. Setelah selesai, klik dua kali berkas ini lagi.
echo.
pause
exit /b 1

:oldpython
echo.
echo  Versi Python di komputer ini terlalu lama. Butuh Python 3.7 atau yang lebih baru.
echo  Unduh versi terbaru di https://www.python.org/downloads/ lalu coba lagi.
echo.
pause
exit /b 1
