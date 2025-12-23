import customtkinter as ctk
import sys
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
import os
import time
import queue

# --- Configuration & Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ProjectBuilderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("AI Project Builder - VS Code Style")
        self.geometry("1400x900")
        self.minsize(1200, 700)

        # State variables
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False
        self.generated_files = {}
        self.selected_file = None
        self.chat_history = []
        self.current_folder = None  # Track current app folder
        self.available_folders = []  # List of app folders

        # Layout Configuration
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=0)  # File Explorer
        self.grid_columnconfigure(2, weight=3)  # Code Editor
        self.grid_columnconfigure(3, weight=2)  # Chat/Terminal
        self.grid_rowconfigure(0, weight=1)     # Main Content
        self.grid_rowconfigure(1, weight=0)     # Status Bar

        self.setup_ui()
        
        # Scan for existing folders
        self.scan_app_folders()
        
        # Start output monitor
        self.check_output_queue()

    def setup_ui(self):
        # --- 1. Left Sidebar (Activity Bar) ---
        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0, fg_color="#1e1e1e")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.create_sidebar_btn("▶", self.show_run_dialog, "Run Project")
        self.create_sidebar_btn("📂", self.refresh_files, "Refresh Files")
        self.create_sidebar_btn("🔄", self.clear_all, "Clear All")
        
        self.sidebar_spacer = ctk.CTkLabel(self.sidebar, text="")
        self.sidebar_spacer.pack(side="top", fill="y", expand=True)
        
        self.create_sidebar_btn("⚙", None, "Settings")

        # --- 2. File Explorer ---
        self.explorer_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#252526")
        self.explorer_frame.grid(row=0, column=1, sticky="nsew")
        self.explorer_frame.grid_propagate(False)
        self.explorer_frame.grid_rowconfigure(2, weight=1)
        self.explorer_frame.grid_columnconfigure(0, weight=1)

        self.explorer_title = ctk.CTkLabel(
            self.explorer_frame, 
            text=" 📁 EXPLORER", 
            font=("Consolas", 12, "bold"), 
            anchor="w",
            fg_color="#2d2d2d"
        )
        self.explorer_title.grid(row=0, column=0, sticky="ew", pady=(0,2))

        # Folder Selector
        self.folder_selector_frame = ctk.CTkFrame(self.explorer_frame, fg_color="#1e1e1e")
        self.folder_selector_frame.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.folder_selector_frame.grid_columnconfigure(0, weight=1)

        # Create a custom frame for folder selection with scan button
        self.folder_control_frame = ctk.CTkFrame(self.folder_selector_frame, fg_color="transparent")
        self.folder_control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.folder_control_frame.grid_columnconfigure(0, weight=1)
        
        self.folder_dropdown = ctk.CTkOptionMenu(
            self.folder_control_frame,
            values=["No folders"],
            command=self.switch_folder,
            font=("Consolas", 11),
            fg_color="#333333",
            button_color="#007acc",
            button_hover_color="#005a9e",
            dropdown_fg_color="#2d2d2d"
        )
        self.folder_dropdown.grid(row=0, column=0, sticky="ew")
        self.folder_dropdown.set("Select Folder")
        
        # Bind button press to scan before opening dropdown
        self.folder_dropdown.bind("<Button-1>", lambda e: self.scan_before_dropdown())

        # File List
        self.file_list = ctk.CTkScrollableFrame(
            self.explorer_frame, 
            fg_color="#1e1e1e",
            corner_radius=0
        )
        self.file_list.grid(row=2, column=0, sticky="nsew", padx=2, pady=2)
        self.file_list.grid_columnconfigure(0, weight=1)

        # --- 3. Code Editor Area ---
        self.editor_frame = ctk.CTkFrame(self, fg_color="#252526", corner_radius=0)
        self.editor_frame.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.editor_header = ctk.CTkLabel(
            self.editor_frame, 
            text=" 📝 CODE EDITOR", 
            font=("Consolas", 12, "bold"), 
            anchor="w",
            fg_color="#2d2d2d"
        )
        self.editor_header.grid(row=0, column=0, sticky="ew", padx=1, pady=(1,0))

        self.code_editor = ctk.CTkTextbox(
            self.editor_frame, 
            font=("Consolas", 13), 
            text_color="#d4d4d4",
            fg_color="#1e1e1e",
            corner_radius=0,
            wrap="none"
        )
        self.code_editor.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)
        
        placeholder = """
        
        ╔═══════════════════════════════════════════════════╗
        ║                                                   ║
        ║          AI PROJECT BUILDER                       ║
        ║          VS Code Style Interface                  ║
        ║                                                   ║
        ║  Select a folder from the dropdown above         ║
        ║  Select a file from the explorer to view code    ║
        ║  or start generating a project using chat →       ║
        ║                                                   ║
        ╚═══════════════════════════════════════════════════╝
        """
        self.code_editor.insert("0.0", placeholder)

        # --- 4. Chat & Terminal Panel (Right) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="#252526", corner_radius=0)
        self.right_panel.grid(row=0, column=3, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=2)  # Chat
        self.right_panel.grid_rowconfigure(3, weight=3)  # Terminal
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Chat Section
        self.chat_header = ctk.CTkLabel(
            self.right_panel, 
            text=" 💬 PROJECT CHAT", 
            font=("Consolas", 12, "bold"), 
            anchor="w",
            fg_color="#2d2d2d"
        )
        self.chat_header.grid(row=0, column=0, sticky="ew", padx=1, pady=(1,0))

        self.chat_display = ctk.CTkScrollableFrame(
            self.right_panel, 
            fg_color="#1e1e1e",
            corner_radius=0
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.chat_display.grid_columnconfigure(0, weight=1)

        # Chat Input
        self.chat_input_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.chat_input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.chat_input_frame.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(
            self.chat_input_frame, 
            placeholder_text="Describe your project...",
            font=("Consolas", 12),
            height=35
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.chat_entry.bind("<Return>", lambda e: self.start_generation())

        self.generate_btn = ctk.CTkButton(
            self.chat_input_frame, 
            text="🚀 Generate",
            width=100,
            height=35,
            command=self.start_generation,
            font=("Consolas", 12, "bold")
        )
        self.generate_btn.grid(row=0, column=1)

        # Terminal Section
        self.terminal_header = ctk.CTkLabel(
            self.right_panel, 
            text=" 🖥️ TERMINAL OUTPUT", 
            font=("Consolas", 12, "bold"), 
            anchor="w",
            fg_color="#2d2d2d"
        )
        self.terminal_header.grid(row=3, column=0, sticky="ew", padx=1, pady=(5,0))

        self.terminal = ctk.CTkTextbox(
            self.right_panel, 
            font=("Consolas", 11), 
            text_color="#a9b7c6",
            fg_color="#000000",
            corner_radius=0,
            wrap="word"
        )
        self.terminal.grid(row=4, column=0, sticky="nsew", padx=2, pady=2)
        self.log_terminal("Terminal ready. Waiting for commands...\n", "info")

        # --- 5. Status Bar ---
        self.status_bar = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#007acc")
        self.status_bar.grid(row=1, column=0, columnspan=4, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text=" ● Ready  |  Folder: None  |  Files: 0  |  Lines: 0", 
            text_color="white", 
            font=("Consolas", 11), 
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=10)

    def create_sidebar_btn(self, icon, command, tooltip):
        btn = ctk.CTkButton(
            self.sidebar, 
            text=icon, 
            command=command, 
            width=50, 
            height=50, 
            corner_radius=0,
            fg_color="transparent",
            hover_color="#333333",
            font=("Segoe UI", 20)
        )
        btn.pack(side="top", pady=2)
        return btn
    def scan_app_folders(self):
        """Scan for app1, app2, app3, etc. folders"""
        self.available_folders = []
        current_dir = Path('.')
        
        # Look for folders matching pattern app1, app2, etc.
        for item in current_dir.iterdir():
            if item.is_dir() and item.name.startswith('app'):
                self.available_folders.append(item.name)
        
        # Sort folders
        self.available_folders.sort(key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
        
        # Update dropdown
        if self.available_folders:
            self.folder_dropdown.configure(values=self.available_folders)
            self.folder_dropdown.set(self.available_folders[0])
            self.current_folder = self.available_folders[0]
            self.log_terminal(f"📂 Found {len(self.available_folders)} project folders", "success")
            self.load_generated_files()
        else:
            self.folder_dropdown.configure(values=["No folders"])
            self.folder_dropdown.set("No folders")
            self.log_terminal("⚠️ No app folders found. Generate a project first.", "warning")

    def switch_folder(self, folder_name):
        """Switch to a different app folder"""
        if folder_name == "No folders" or folder_name == "Select Folder":
            return
        
        self.current_folder = folder_name
        self.log_terminal(f"🔄 Switched to {folder_name}", "info")
        self.load_generated_files()

    def add_chat_message(self, message, role="user"):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color = "#0e639c" if role == "user" else "#1a1a1a" if role == "assistant" else "#2d2d30"
        icon = "👤" if role == "user" else "🤖" if role == "assistant" else "⚙️"
        
        msg_frame = ctk.CTkFrame(self.chat_display, fg_color=color, corner_radius=8)
        msg_frame.grid(row=len(self.chat_history), column=0, sticky="ew", padx=5, pady=3)
        msg_frame.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkLabel(
            msg_frame,
            text=f"{icon} {role.upper()} [{timestamp}]",
            font=("Consolas", 10, "bold"),
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", padx=10, pady=(5,0))
        
        content = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=("Consolas", 11),
            anchor="w",
            justify="left",
            wraplength=350
        )
        content.grid(row=1, column=0, sticky="w", padx=10, pady=(0,5))
        
        self.chat_history.append({"role": role, "message": message})
        self.chat_display._parent_canvas.yview_moveto(1.0)

    def log_terminal(self, text, level="info"):
        """Add text to terminal with color coding"""
        colors = {
            "info": "#4fc1ff",
            "success": "#73c991",
            "error": "#f48771",
            "warning": "#dcdcaa"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.terminal.configure(state="normal")
        
        # Insert timestamp
        self.terminal.insert("end", f"[{timestamp}] ", "timestamp")
        
        # Insert message with color
        self.terminal.insert("end", f"{text}\n")
        
        self.terminal.see("end")
        self.terminal.configure(state="disabled")
        
        # Update UI
        self.update_idletasks()

    def start_generation(self):
        """Start project generation in subprocess"""
        prompt = self.chat_entry.get().strip()
        if not prompt or self.is_running:
            return
        
        self.chat_entry.delete(0, "end")
        self.add_chat_message(prompt, "user")
        
        # Update UI
        self.is_running = True
        self.generate_btn.configure(state="disabled", text="⏳ Running...")
        self.update_status("● Running...", "#4ec9b0")
        
        # Clear terminal
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        
        self.log_terminal("🚀 Starting project generation...", "info")
        self.add_chat_message("🚀 Starting project generation...", "system")
        
        # Start subprocess
        threading.Thread(target=self.run_generation, args=(prompt,), daemon=True).start()

    def run_generation(self, prompt):
        """Run the project generator in subprocess"""
        try:
            # Escape prompt
            escaped_prompt = prompt.replace('"', '\\"').replace('\\', '\\\\')
            
            # Create runner script with unbuffered output
            runner_script = f"""
import sys
import os

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

sys.path.append('.')
from main5 import UniversalProjectGenerator

print("=== Initializing Generator ===", flush=True)
generator = UniversalProjectGenerator()
print("=== Starting Pipeline ===", flush=True)
generator.run_pipeline("{escaped_prompt}")
print("=== Pipeline Complete ===", flush=True)
"""
            
            with open('temp_runner.py', 'w', encoding='utf-8') as f:
                f.write(runner_script)
            
            # Start process with unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            
            self.process = subprocess.Popen(
                [sys.executable, '-u', 'temp_runner.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                env=env
            )
            
            # Read output character by character for immediate updates
            line_buffer = ""
            while True:
                char = self.process.stdout.read(1)
                
                if not char:
                    # Process ended
                    if line_buffer:
                        self.output_queue.put(("terminal", line_buffer.strip(), "info"))
                    break
                
                line_buffer += char
                
                # When we hit a newline, process the line
                if char == '\n':
                    line = line_buffer.strip()
                    if line:
                        # Determine level
                        level = "info"
                        if any(x in line.lower() for x in ["error", "exception", "❌", "failed", "traceback"]):
                            level = "error"
                        elif any(x in line.lower() for x in ["success", "complete", "✅", "successfully"]):
                            level = "success"
                        elif any(x in line.lower() for x in ["warning", "⚠"]):
                            level = "warning"
                        
                        # Queue the output immediately
                        self.output_queue.put(("terminal", line, level))
                    
                    line_buffer = ""
            
            # Wait for completion
            self.process.wait()
            
            if self.process.returncode == 0:
                self.output_queue.put(("complete", "success", None))
            else:
                self.output_queue.put(("complete", "error", self.process.returncode))
            
        except Exception as e:
            self.output_queue.put(("error", str(e), None))
        finally:
            self.process = None

    def check_output_queue(self):
        """Check queue for output from subprocess"""
        try:
            while True:
                msg_type, content, extra = self.output_queue.get_nowait()
                
                if msg_type == "terminal":
                    self.log_terminal(content, extra)
                    self.add_chat_message(content, "system")
                    
                elif msg_type == "complete":
                    if content == "success":
                        self.log_terminal("✅ Project generated successfully!", "success")
                        self.add_chat_message("✅ Project generated successfully!", "assistant")
                        # Rescan folders and load the new one
                        self.scan_app_folders()
                    else:
                        self.log_terminal(f"❌ Process failed with code {extra}", "error")
                        self.add_chat_message(f"❌ Process failed with code {extra}", "system")
                    
                    self.generation_complete()
                    
                elif msg_type == "error":
                    self.log_terminal(f"❌ Error: {content}", "error")
                    self.add_chat_message(f"❌ Error: {content}", "system")
                    self.generation_complete()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self.check_output_queue)

    def generation_complete(self):
        """Called when generation is complete"""
        self.is_running = False
        self.generate_btn.configure(state="normal", text="🚀 Generate")
        self.update_status("● Ready", "#007acc")
        
        # Cleanup
        if os.path.exists('temp_runner.py'):
            try:
                os.remove('temp_runner.py')
            except:
                pass

    def load_generated_files(self):
        """Load generated files from current folder"""
        if not self.current_folder:
            self.log_terminal("⚠️ No folder selected", "warning")
            return
        
        app_dir = Path(f'./{self.current_folder}')
        if not app_dir.exists():
            self.log_terminal(f"⚠️ Folder {self.current_folder} not found", "warning")
            return
        
        self.generated_files.clear()
        total_lines = 0
        file_count = 0
        
        for file_path in app_dir.rglob('*'):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    rel_path = str(file_path.relative_to(app_dir))
                    self.generated_files[rel_path] = content
                    total_lines += len(content.split('\n'))
                    file_count += 1
                except:
                    pass
        
        self.log_terminal(f"📂 Loaded {file_count} files from {self.current_folder} ({total_lines} lines)", "success")
        self.update_file_list()
        self.update_status(f"● Ready  |  Folder: {self.current_folder}  |  Files: {file_count}  |  Lines: {total_lines}", "#007acc")

    def update_file_list(self):
        """Update file explorer with generated files"""
        # Clear existing
        for widget in self.file_list.winfo_children():
            widget.destroy()
        
        if not self.generated_files:
            no_files = ctk.CTkLabel(
                self.file_list,
                text="No files in this folder.\nSelect a different folder\nor generate a project.",
                font=("Consolas", 11),
                text_color="#666666"
            )
            no_files.pack(pady=20)
            return
        
        # Add files
        for file_path in sorted(self.generated_files.keys()):
            file_btn = ctk.CTkButton(
                self.file_list,
                text=f"📄 {file_path}",
                command=lambda fp=file_path: self.open_file(fp),
                anchor="w",
                fg_color="transparent",
                hover_color="#2a2d2e",
                font=("Consolas", 11),
                height=28
            )
            file_btn.pack(fill="x", padx=2, pady=1)

    def open_file(self, file_path):
        """Open file in code editor"""
        if file_path not in self.generated_files:
            return
        
        self.selected_file = file_path
        content = self.generated_files[file_path]
        
        # Update header
        self.editor_header.configure(text=f" 📝 {self.current_folder}/{file_path}")
        
        # Update editor
        self.code_editor.delete("1.0", "end")
        self.code_editor.insert("1.0", content)
        
        self.log_terminal(f"📂 Opened: {self.current_folder}/{file_path}", "info")

    def update_status(self, text, color="#007acc"):
        """Update status bar"""
        self.status_bar.configure(fg_color=color)
        self.status_label.configure(text=f" {text}")

    def show_run_dialog(self):
        """Show dialog to run generated project"""
        if not self.generated_files or not self.current_folder:
            self.log_terminal("⚠️ No project to run. Generate one first.", "warning")
            return
        
        # Simple execution - look for main.py
        main_files = [f for f in self.generated_files.keys() if 'main.py' in f.lower()]
        
        if main_files:
            self.log_terminal(f"▶ Running {self.current_folder}/{main_files[0]}...", "info")
            try:
                # Change to the app folder before running
                app_path = Path(f'./{self.current_folder}')
                subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
                    cwd=str(app_path)
                )
                
                self.log_terminal("✔ Server started on http://127.0.0.1:8000", "success")
                
            except Exception as e:
                self.log_terminal(f"❌ Failed to start uvicorn: {str(e)}", "error")
        else:
            self.log_terminal("⚠️ No main.py found in project", "warning")

    def refresh_files(self):
        """Refresh file list and rescan folders"""
        self.log_terminal("🔄 Refreshing folders and files...", "info")
        self.scan_app_folders()

    def clear_all(self):
        """Clear all data"""
        self.generated_files.clear()
        self.selected_file = None
        self.chat_history.clear()
        
        # Clear UI
        self.code_editor.delete("1.0", "end")
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", "end")
        self.terminal.configure(state="disabled")
        
        for widget in self.file_list.winfo_children():
            widget.destroy()
        for widget in self.chat_display.winfo_children():
            widget.destroy()
        
        self.log_terminal("🗑️ Cleared all data", "info")
        self.update_status("● Ready  |  Folder: None  |  Files: 0  |  Lines: 0", "#007acc")

if __name__ == "__main__":
    app = ProjectBuilderApp()
    app.mainloop()