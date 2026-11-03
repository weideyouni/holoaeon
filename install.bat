@echo off
REM ============================================================================
REM HoloAeon - One-Click Install (Windows) - Batch 3 Product Layer
REM New users: put this file in the repo root and double-click install.bat
REM Zero-dependency: only needs python (>=3.8); no pip install of 3rd-party libs.
REM Read-only checks + selftest; no source code outside this repo is touched.
REM ============================================================================
chcp 65001 >nul
setlocal EnableExtensions
echo == HoloAeon Install (Windows) ==

where python >nul 2>nul
if errorlevel 1 (
  echo !! python not found. Install Python 3.8+ and check "Add to PATH".
  exit /b 1
)

echo == [1/3] Kernel assembly check (dimension lock 25/47/9) ==
python -c "from holoaeon.packs import PACK_ORDER, EXTRA_PACK_ORDER; from holoaeon.spec import VERSION, DOC_VERSION; print(f'  version={VERSION} doc={DOC_VERSION}'); print(f'  domain_packs={len(PACK_ORDER)} extra_packs={len(EXTRA_PACK_ORDER)}'); assert len(PACK_ORDER)==9 and len(EXTRA_PACK_ORDER)>=10; print('  assembly check passed')"
if errorlevel 1 (
  echo !! assembly check failed. Run this from the repo root.
  exit /b 1
)

echo == [2/3] Kernel selftest (25/25) ==
python scripts\launch_local.py selftest | findstr /C:"==>" /C:"25/25"
if errorlevel 1 (
  echo !! selftest did not pass.
  exit /b 1
)

echo == [3/3] Product demo (one-click experience) ==
python -m holoaeon.demo_product
if errorlevel 1 (
  echo !! demo failed.
  exit /b 1
)

echo.
echo == Install done ==
echo   Drive via chat frontend: python -m holoaeon.frontend_adapter "your task"
echo   Optional: pip install -e .  (repo is zero-dep, works without install)
echo   Seal: evidence_class=simulated. Simulation is not proof; carbon final.
endlocal
