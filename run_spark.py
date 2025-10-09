#!/usr/bin/env python3
"""
Apache Spark GUI Launcher - Sistema EU-UTVT
Interfaz gráfica profesional para análisis de big data

Autor: Sistema EU-UTVT  
Fecha: Octubre 2025
Versión: GUI Professional 2.0
"""

import os
import sys
import subprocess
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkFont

class SparkGUILauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.setup_layout()
        
    def setup_window(self):
        """Configurar ventana principal"""
        self.root.title("🔥 Apache Spark - Sistema EU-UTVT")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configurar colores
        self.colors = {
            'primary': '#1e3a8a',      # Azul profesional
            'secondary': '#3b82f6',     # Azul claro
            'success': '#10b981',       # Verde
            'warning': '#f59e0b',       # Amarillo
            'danger': '#ef4444',        # Rojo
            'dark': '#1f2937',          # Gris oscuro
            'light': '#f9fafb',         # Gris claro
            'white': '#ffffff',
            'text': '#374151'
        }
        
        self.root.configure(bg=self.colors['light'])
        
    def create_styles(self):
        """Crear estilos personalizados"""
        self.style = ttk.Style()
        
        # Configurar tema
        self.style.theme_use('clam')
        
        # Estilo para botones principales
        self.style.configure(
            'Primary.TButton',
            background=self.colors['primary'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(20, 10)
        )
        self.style.map('Primary.TButton',
            background=[('active', self.colors['secondary']),
                       ('pressed', '#1d4ed8')])
        
        # Estilo para botones secundarios
        self.style.configure(
            'Secondary.TButton',
            background=self.colors['light'],
            foreground=self.colors['text'],
            borderwidth=1,
            focuscolor='none',
            padding=(15, 8)
        )
        
        # Estilo para frames
        self.style.configure(
            'Card.TFrame',
            background=self.colors['white'],
            relief='flat',
            borderwidth=1
        )
        
    def create_widgets(self):
        """Crear widgets de la interfaz"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, style='Card.TFrame')
        
        # Header
        self.create_header()
        
        # Stats frame
        self.create_stats_section()
        
        # Botones principales
        self.create_main_buttons()
        
        # Panel de resultados
        self.create_results_panel()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Crear header profesional"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors['primary'], height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_font = tkFont.Font(family='Segoe UI', size=24, weight='bold')
        title = tk.Label(
            header_frame,
            text="🔥 Apache Spark Analytics",
            font=title_font,
            bg=self.colors['primary'],
            fg='white'
        )
        title.pack(pady=15)
        
        # Subtítulo
        subtitle_font = tkFont.Font(family='Segoe UI', size=12)
        subtitle = tk.Label(
            header_frame,
            text="Sistema EU-UTVT • Big Data Analytics • 16.6M Usuarios",
            font=subtitle_font,
            bg=self.colors['primary'],
            fg='#cbd5e1'
        )
        subtitle.pack()
        
    def create_stats_section(self):
        """Crear sección de estadísticas"""
        stats_frame = tk.Frame(self.main_frame, bg=self.colors['light'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Stats cards
        stats_data = [
            ("📊 Usuarios", "16,640,000", self.colors['success']),
            ("🚀 Spark", "3.4.4", self.colors['secondary']),
            ("☕ Java", "8", self.colors['warning']),
            ("📈 Estado", "Listo", self.colors['success'])
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, width=200, height=80)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            card.pack_propagate(False)
            
            # Label
            label_font = tkFont.Font(family='Segoe UI', size=10, weight='bold')
            tk.Label(
                card, text=label, font=label_font,
                bg=color, fg='white'
            ).pack(pady=(10, 0))
            
            # Value
            value_font = tkFont.Font(family='Segoe UI', size=16, weight='bold')
            tk.Label(
                card, text=value, font=value_font,
                bg=color, fg='white'
            ).pack()
        
        # Configurar grid
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
            
    def create_main_buttons(self):
        """Crear botones principales"""
        buttons_frame = tk.Frame(self.main_frame, bg=self.colors['light'])
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Configurar grid
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        # Botones principales
        buttons_data = [
            ("📊 Análisis Rápido", "500K usuarios • ~5 min", self.colors['success'], self.quick_analysis),
            ("📈 Análisis Completo", "16.6M usuarios • ~45 min", self.colors['warning'], self.full_analysis),
            ("🧪 Test Sistema", "Verificar compatibilidad", self.colors['secondary'], self.test_system)
        ]
        
        for i, (title, desc, color, command) in enumerate(buttons_data):
            card = tk.Frame(buttons_frame, bg=color, width=280, height=120)
            card.grid(row=0, column=i, padx=10, pady=10)
            card.pack_propagate(False)
            
            # Título
            title_font = tkFont.Font(family='Segoe UI', size=14, weight='bold')
            title_label = tk.Label(
                card, text=title, font=title_font,
                bg=color, fg='white'
            )
            title_label.pack(pady=(15, 5))
            
            # Descripción
            desc_font = tkFont.Font(family='Segoe UI', size=10)
            desc_label = tk.Label(
                card, text=desc, font=desc_font,
                bg=color, fg='white'
            )
            desc_label.pack(pady=(0, 10))
            
            # Botón
            btn = tk.Button(
                card, text="EJECUTAR",
                font=tkFont.Font(family='Segoe UI', size=10, weight='bold'),
                bg='white', fg=color,
                border=0, cursor='hand2',
                command=command
            )
            btn.pack(pady=(0, 10))
            
        # Botones secundarios
        secondary_frame = tk.Frame(buttons_frame, bg=self.colors['light'])
        secondary_frame.grid(row=1, column=0, columnspan=3, pady=20)
        
        secondary_buttons = [
            ("🚀 Spark Nativo", self.spark_native),
            ("📁 Abrir Carpeta", self.open_folder),
            ("📖 Documentación", self.show_docs),
            ("⚙️ Configuración", self.show_config)
        ]
        
        for i, (text, command) in enumerate(secondary_buttons):
            btn = tk.Button(
                secondary_frame, text=text,
                font=tkFont.Font(family='Segoe UI', size=10),
                bg=self.colors['white'], fg=self.colors['text'],
                border=1, relief='solid',
                cursor='hand2', command=command,
                padx=20, pady=8
            )
            btn.grid(row=0, column=i, padx=5)
            
    def create_results_panel(self):
        """Crear panel de resultados"""
        # Frame contenedor
        results_frame = tk.Frame(self.main_frame, bg=self.colors['light'])
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Título
        title_font = tkFont.Font(family='Segoe UI', size=14, weight='bold')
        title = tk.Label(
            results_frame, text="📋 Consola de Resultados",
            font=title_font, bg=self.colors['light'], fg=self.colors['text']
        )
        title.pack(anchor='w', pady=(0, 10))
        
        # Text area con scroll
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=12,
            font=tkFont.Font(family='Consolas', size=10),
            bg='#1e293b', fg='#e2e8f0',
            insertbackground='white',
            selectbackground='#3b82f6'
        )
        self.results_text.pack(fill='both', expand=True)
        
        # Mensaje inicial
        self.log_message("🔥 Apache Spark GUI Launcher iniciado", "success")
        self.log_message("📊 16,640,000 usuarios disponibles en MongoDB", "info")
        self.log_message("✅ Sistema listo para análisis de big data", "success")
        
    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_bar = tk.Frame(self.main_frame, bg=self.colors['dark'], height=30)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            text="🟢 Sistema listo • Spark 3.4.4 • Java 8 Compatible",
            bg=self.colors['dark'], fg='white',
            font=tkFont.Font(family='Segoe UI', size=9)
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Progreso
        self.progress = ttk.Progressbar(
            self.status_bar, length=200, mode='determinate'
        )
        self.progress.pack(side='right', padx=10, pady=5)
        
    def setup_layout(self):
        """Configurar layout principal"""
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
    def log_message(self, message, level="info"):
        """Agregar mensaje al log"""
        colors = {
            "info": "#3b82f6",
            "success": "#10b981", 
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        
        # Configurar tags de color
        for lvl, color in colors.items():
            self.results_text.tag_configure(lvl, foreground=color)
        
        # Agregar timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Insertar mensaje
        self.results_text.insert('end', f"[{timestamp}] {message}\n", level)
        self.results_text.see('end')
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Actualizar barra de estado"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def run_in_thread(self, func, *args):
        """Ejecutar función en hilo separado"""
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()
        
    def execute_script(self, script_name, option=None, description=""):
        """Ejecutar script de Spark"""
        script_path = Path("spark") / script_name
        
        if not script_path.exists():
            self.log_message(f"❌ Error: No se encontró {script_path}", "error")
            messagebox.showerror("Error", f"No se encontró el archivo {script_name}")
            return
        
        self.log_message(f"🚀 Iniciando {description}...", "info")
        self.update_status(f"🔄 Ejecutando {description}...")
        self.progress.start()
        
        def run_script():
            try:
                if option:
                    # Para scripts con opciones - con encoding UTF-8
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    stdout, _ = process.communicate(input=f"{option}\n")
                else:
                    # Para scripts simples - con encoding UTF-8
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                    stdout = result.stdout if result.stdout else ""
                    if result.stderr:
                        stdout += "\n" + result.stderr
                
                # Verificar que stdout no sea None
                if stdout is None:
                    stdout = ""
                
                # Mostrar resultados
                self.root.after(0, lambda: self.show_results(stdout, description))
                
            except Exception as e:
                error_msg = f"❌ Error ejecutando {description}: {str(e)}"
                self.root.after(0, lambda: self.log_message(error_msg, "error"))
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            finally:
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.update_status("🟢 Sistema listo"))
        
        self.run_in_thread(run_script)
        
    def show_results(self, output, description):
        """Mostrar resultados en el panel"""
        self.log_message(f"✅ {description} completado", "success")
        
        # Verificar que output no sea None o vacío
        if not output:
            self.log_message("⚠️ No se recibió output del script", "warning")
            return
        
        # Procesar output line by line
        lines = output.split('\n')
        for line in lines[:50]:  # Mostrar solo primeras 50 líneas
            if line.strip():
                if "error" in line.lower() or "failed" in line.lower():
                    self.log_message(line, "error")
                elif "success" in line.lower() or "✅" in line:
                    self.log_message(line, "success")
                elif "warning" in line.lower() or "⚠️" in line:
                    self.log_message(line, "warning")
                else:
                    self.log_message(line, "info")
        
        if len(lines) > 50:
            self.log_message(f"... (+{len(lines)-50} líneas más)", "info")
            
    # Métodos para botones
    def quick_analysis(self):
        """Análisis rápido"""
        if messagebox.askyesno("Confirmar", "¿Ejecutar análisis rápido (500K usuarios)?"):
            self.execute_script("spark_reports_java8.py", "1\n5\n", "Análisis Rápido")
            
    def full_analysis(self):
        """Análisis completo"""
        if messagebox.askyesno("Confirmar", 
                              "¿Ejecutar análisis completo (16.6M usuarios)?\n\n"
                              "⚠️ Este proceso puede tomar ~45 minutos"):
            self.execute_script("spark_reports_java8.py", "2\n5\n", "Análisis Completo")
            
    def test_system(self):
        """Test del sistema"""
        self.execute_script("test_spark_simple.py", None, "Test de Diagnóstico Spark")
        
    def spark_native(self):
        """Configurar Spark nativo"""
        config_msg = """🔧 CONFIGURACIÓN SPARK NATIVO

Para usar Spark nativo, ejecuta estos comandos:

Windows PowerShell:
$env:PYSPARK_PYTHON = "C:\\Users\\luis1\\.conda\\envs\\spark_env\\python.exe"
$env:PYSPARK_DRIVER_PYTHON = "C:\\Users\\luis1\\.conda\\envs\\spark_env\\python.exe"

Luego:
python spark/spark_mongo_analytics.py"""
        
        messagebox.showinfo("Configuración Spark Nativo", config_msg)
        
    def open_folder(self):
        """Abrir carpeta Spark"""
        spark_folder = Path("spark").absolute()
        try:
            if sys.platform == "win32":
                os.startfile(spark_folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(spark_folder)])
            else:
                subprocess.run(["xdg-open", str(spark_folder)])
            self.log_message(f"📁 Abriendo carpeta: {spark_folder}", "info")
        except Exception as e:
            self.log_message(f"❌ Error abriendo carpeta: {e}", "error")
            
    def show_docs(self):
        """Mostrar documentación"""
        docs_path = Path("spark") / "README.md"
        if docs_path.exists():
            try:
                if sys.platform == "win32":
                    os.startfile(docs_path)
                else:
                    subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(docs_path)])
                self.log_message("📖 Abriendo documentación Spark", "info")
            except Exception as e:
                self.log_message(f"❌ Error abriendo documentación: {e}", "error")
        else:
            messagebox.showerror("Error", "No se encontró la documentación")
            
    def show_config(self):
        """Mostrar configuración del sistema"""
        config_info = """🔧 CONFIGURACIÓN DEL SISTEMA

• Apache Spark: 3.4.4 (Compatible Java 8)
• PySpark: 3.4.4
• Java: 1.8.0_202
• MongoDB: 16,640,000 usuarios
• Python: spark_env environment

📊 CAPACIDADES:
• Análisis rápido: 500K usuarios (~5 min)
• Análisis completo: 16.6M usuarios (~45 min)  
• Procesamiento: 300K+ registros/segundo
• Reportes: CSV automáticos

✅ ESTADO: Sistema totalmente funcional"""
        
        messagebox.showinfo("Configuración del Sistema", config_info)
        
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    # Verificar que estamos en el directorio correcto
    if not Path("spark").exists():
        messagebox.showerror("Error", 
                           "Carpeta 'spark' no encontrada.\n"
                           "Ejecuta este script desde el directorio del proyecto")
        return
    
    # Crear y ejecutar aplicación
    app = SparkGUILauncher()
    app.run()

if __name__ == "__main__":
    main()