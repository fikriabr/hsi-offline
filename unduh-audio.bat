@echo off
setlocal EnableExtensions
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

where ffmpeg >nul 2>nul
if errorlevel 1 echo  Catatan: ffmpeg tidak ditemukan. Audio tetap diunduh, gelombang dibuat oleh peramban saat pertama kali diputar.

:menu
echo.
echo  ===== UNDUH AUDIO HALAQAH HSI =====
echo  Hanya untuk belajar pribadi. Hak cipta materi milik tim HSI dan Ustadz Abdullah Roy.
echo.
echo   1. Al-Ushul Ats-Tsalatsah saja, kitab yang sedang dipelajari
echo   2. Pilih kitab sendiri
echo   3. Semua audio, sekitar 2 GB dan 1 sampai 1,5 jam
echo   4. Keluar
echo.
set "PILIH="
set /p PILIH= Pilih 1 sampai 4: 
if "%PILIH%"=="1" goto satu
if "%PILIH%"=="2" goto dua
if "%PILIH%"=="3" goto tiga
if "%PILIH%"=="4" exit /b 0
goto menu

:satu
%PY% download_audio.py --series tsalatsah
goto selesai

:dua
echo.
%PY% download_audio.py --list
echo.
echo  Ketik kode seri dari kolom paling kiri. Boleh lebih dari satu, pisahkan dengan spasi.
echo  Contoh: fadhlul qawaid
set "KODE="
set /p KODE= Kode seri: 
if "%KODE%"=="" goto menu
%PY% download_audio.py --series %KODE%
goto selesai

:tiga
set "YAKIN="
set /p YAKIN= Unduh semuanya? Ketik Y lalu tekan Enter: 
if /i not "%YAKIN%"=="Y" goto menu
%PY% download_audio.py --all
goto selesai

:selesai
echo.
echo  Selesai. Jika ada yang terputus atau gagal, jalankan berkas ini lagi: yang sudah selesai dilewati.
echo  Untuk berhenti di tengah jalan, tekan Ctrl+C lalu ketik Y. Lanjutkan kapan saja nanti.
echo  Setelah unduhan, jalankan jalankan.bat untuk membuka aplikasi.
echo.
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
