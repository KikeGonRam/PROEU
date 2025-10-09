@echo off
rem Apache Spark GUI Launcher - Windows Batch
rem Sistema EU-UTVT - Acceso directo GUI

title Apache Spark - Sistema EU-UTVT

echo.
echo  🔥 APACHE SPARK - SISTEMA EU-UTVT
echo  ===================================
echo.
echo  Iniciando interfaz gráfica profesional...
echo.

rem Activar entorno conda
call conda activate spark_env

rem Ejecutar GUI
python run_spark.py

rem Pausa si hay error
if errorlevel 1 (
    echo.
    echo  ❌ Error ejecutando la interfaz gráfica
    echo  Presiona cualquier tecla para salir...
    pause >nul
)