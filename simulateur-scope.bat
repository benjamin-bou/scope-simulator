@echo off
title Simulateur de Scope Medical - Installation et Lancement
echo Simulateur de Scope Medical v2.0
echo ===================================
echo.

:check_python
echo Verification de Python...

REM Test Python
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Python detecte - Demarrage serveur...
    python server.py
    goto :end
)

python3 --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Python3 detecte - Demarrage serveur...
    python3 server.py
    goto :end
)

py --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Python Launcher detecte - Demarrage serveur...
    py server.py
    goto :end
)

REM Python non trouve - Installation automatique
echo.
echo Python non detecte - Installation automatique...
echo.
echo INSTALLATION DE PYTHON EN COURS...
echo Cela peut prendre quelques minutes, veuillez patienter...
echo.

REM Creation du dossier pour Python portable
if not exist "python-portable" mkdir python-portable

echo Telechargement de Python portable...
powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-portable\python.zip' -UseBasicParsing; Write-Host 'Telechargement reussi' } catch { Write-Host 'Erreur de telechargement' }"

if exist "python-portable\python.zip" (
    echo Extraction de Python...
    powershell -Command "try { Expand-Archive -Path 'python-portable\python.zip' -DestinationPath 'python-portable' -Force; Write-Host 'Extraction reussie' } catch { Write-Host 'Erreur extraction' }"
    
    REM Nettoyage
    del "python-portable\python.zip" >nul 2>&1
    
    REM Test de l'installation
    if exist "python-portable\python.exe" (
        echo.
        echo Installation reussie!
        echo Demarrage du serveur avec Python portable...
        echo.
        "python-portable\python.exe" server.py
    ) else (
        echo.
        echo Erreur lors de l'installation de Python
        echo Ouverture du Microsoft Store...
        start ms-windows-store://pdp/?productid=9NRWMJP3717K
        echo.
        echo INSTRUCTIONS:
        echo 1. Installez Python depuis le Microsoft Store
        echo 2. Appuyez sur une touche pour continuer
        pause
        goto check_python
    )
) else (
    echo.
    echo Echec du telechargement de Python
    echo Verification de votre connexion Internet...
    echo.
    echo Ouverture du Microsoft Store pour installer Python...
    start ms-windows-store://pdp/?productid=9NRWMJP3717K
    echo.
    echo INSTRUCTIONS:
    echo 1. Cliquez sur "Installer" dans le Microsoft Store
    echo 2. Attendez la fin de l'installation
    echo 3. Appuyez sur une touche ici pour continuer
    echo.
    pause
    echo.
    echo Nouvelle tentative de lancement...
    goto check_python
)

:end
echo.
pause