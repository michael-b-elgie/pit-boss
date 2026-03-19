import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
import threading
import time
import base64
from io import BytesIO

class PokerTimer:
    def __init__(self, root):
        self.root = root
        
        # Configuration file
        self.config_file = "poker_config.json"
        
        # Load configuration first
        self.load_config()
        
        # Set title and window properties
        title = self.config.get("tournament_title", "Pit Boss - Poker Timer")
        self.root.title(title)
        self.root.geometry("1200x800")
        
        # Initialize state variables
        self.is_game_running = False
        self.is_break_running = False
        self.game_time_remaining = 0
        self.break_time_remaining = 0
        self.current_level = 1
        self.last_blind_increase = datetime.now()
        self.blind_time_remaining = 0  # Countdown to next blind increase
        
        # Apply theme
        self.setup_theme()
        
        # Set icon if available
        self.setup_icon()
        
        # Load icon for display (separate from window icon)
        self.display_icon = None
        self.load_display_icon()
        
        # Setup GUI
        self.setup_gui()
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Auto-save every 30 seconds
        self.auto_save()
    
    def load_config(self):
        """Load configuration from JSON file or create default"""
        default_config = {
            "tournament_title": "Pit Boss - Poker Timer",
            "theme": "dark",  # classic, dark, midnight, poker-green, vegas, royal
            "game_duration": 20,  # minutes
            "break_duration": 10,  # minutes
            "blind_increase_interval": 15,  # minutes
            "blinds": [
                {"small": 25, "big": 50, "ante": 0},
                {"small": 50, "big": 100, "ante": 0},
                {"small": 75, "big": 150, "ante": 25},
                {"small": 100, "big": 200, "ante": 25},
                {"small": 150, "big": 300, "ante": 50},
                {"small": 200, "big": 400, "ante": 50},
                {"small": 300, "big": 600, "ante": 75},
                {"small": 400, "big": 800, "ante": 100},
                {"small": 500, "big": 1000, "ante": 100},
                {"small": 750, "big": 1500, "ante": 150},
            ],
            "players": [],
            "eliminated_players": [],
            "prize_structure": [
                {"position": 1, "percentage": 50, "amount": 0},
                {"position": 2, "percentage": 30, "amount": 0},
                {"position": 3, "percentage": 20, "amount": 0}
            ],
            "total_prize_pool": 1000,
            "current_state": {
                "level": 1,
                "game_time_remaining": 1200,  # 20 minutes in seconds
                "break_time_remaining": 600,   # 10 minutes in seconds
                "blind_time_remaining": 900,   # 15 minutes in seconds
                "is_game_running": False,
                "is_break_running": False,
                "last_blind_increase": datetime.now().isoformat()
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Ensure all required keys exist
                for key in default_config:
                    if key not in self.config:
                        self.config[key] = default_config[key]
            except:
                self.config = default_config
        else:
            self.config = default_config
        
        # Load current state
        state = self.config["current_state"]
        self.current_level = state["level"]
        self.game_time_remaining = state["game_time_remaining"]
        self.break_time_remaining = state["break_time_remaining"]
        self.blind_time_remaining = state.get("blind_time_remaining", self.config["blind_increase_interval"] * 60)
        self.is_game_running = state["is_game_running"]
        self.is_break_running = state["is_break_running"]
        self.last_blind_increase = datetime.fromisoformat(state["last_blind_increase"])
        
        # Initialize blind countdown timer - ensure backward compatibility
        if "blind_time_remaining" not in state:
            self.blind_time_remaining = self.config["blind_increase_interval"] * 60
    
    def save_config(self):
        """Save current configuration to JSON file"""
        # Update current state
        self.config["current_state"] = {
            "level": self.current_level,
            "game_time_remaining": self.game_time_remaining,
            "break_time_remaining": self.break_time_remaining,
            "blind_time_remaining": self.blind_time_remaining,
            "is_game_running": self.is_game_running,
            "is_break_running": self.is_break_running,
            "last_blind_increase": self.last_blind_increase.isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def setup_theme(self):
        """Setup application theme"""
        style = ttk.Style()
        
        theme = self.config.get("theme", "classic")
        
        if theme == "dark":
            # Enhanced dark theme with modern colors
            self.root.configure(bg="#1e1e1e")
            style.theme_use("clam")
            style.configure(".", background="#1e1e1e", foreground="#ffffff", 
                          fieldbackground="#3c3c3c", borderwidth=1)
            style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("TFrame", background="#1e1e1e")
            style.configure("TLabelFrame", background="#1e1e1e", foreground="#ffffff",
                          labeloutside=True, relief="solid", borderwidth=1)
            style.configure("TButton", background="#0078d4", foreground="#ffffff",
                          borderwidth=1, focuscolor="none")
            style.map("TButton", 
                     background=[("active", "#106ebe"), ("pressed", "#005a9e")])
            
            # Progress bar styling
            style.configure("TProgressbar", background="#06b025", 
                          troughcolor="#3c3c3c", borderwidth=0, lightcolor="#06b025",
                          darkcolor="#06b025")
            
            # Treeview styling
            style.configure("Treeview", background="#2d2d2d", foreground="#ffffff",
                          fieldbackground="#2d2d2d", borderwidth=0)
            style.configure("Treeview.Heading", background="#3c3c3c", foreground="#ffffff")
            
        elif theme == "midnight":
            # Midnight blue theme
            self.root.configure(bg="#0f1419")
            style.theme_use("clam")
            style.configure(".", background="#0f1419", foreground="#e6f1ff", 
                          fieldbackground="#1a2332", borderwidth=1)
            style.configure("TLabel", background="#0f1419", foreground="#e6f1ff")
            style.configure("TFrame", background="#0f1419")
            style.configure("TLabelFrame", background="#0f1419", foreground="#e6f1ff",
                          labeloutside=True, relief="solid", borderwidth=1)
            style.configure("TButton", background="#1565c0", foreground="#ffffff",
                          borderwidth=1, focuscolor="none")
            style.map("TButton", 
                     background=[("active", "#1976d2"), ("pressed", "#0d47a1")])
            
            # Progress bar styling
            style.configure("TProgressbar", background="#2196f3", 
                          troughcolor="#1a2332", borderwidth=0, lightcolor="#2196f3",
                          darkcolor="#2196f3")
                          
            # Treeview styling
            style.configure("Treeview", background="#1a2332", foreground="#e6f1ff",
                          fieldbackground="#1a2332", borderwidth=0)
            style.configure("Treeview.Heading", background="#0f1419", foreground="#e6f1ff")
            
        elif theme == "poker-green":
            # Professional poker green theme
            self.root.configure(bg="#0a2e0a")
            style.theme_use("clam")
            style.configure(".", background="#0a2e0a", foreground="#ffffff", 
                          fieldbackground="#1b5e20", borderwidth=1)
            style.configure("TLabel", background="#0a2e0a", foreground="#ffffff")
            style.configure("TFrame", background="#0a2e0a")
            style.configure("TLabelFrame", background="#0a2e0a", foreground="#ffffff",
                          labeloutside=True, relief="solid", borderwidth=1)
            style.configure("TButton", background="#388e3c", foreground="#ffffff",
                          borderwidth=1, focuscolor="none")
            style.map("TButton", 
                     background=[("active", "#4caf50"), ("pressed", "#2e7d32")])
            
            # Progress bar styling
            style.configure("TProgressbar", background="#4caf50", 
                          troughcolor="#1b5e20", borderwidth=0, lightcolor="#4caf50",
                          darkcolor="#4caf50")
                          
            # Treeview styling
            style.configure("Treeview", background="#1b5e20", foreground="#ffffff",
                          fieldbackground="#1b5e20", borderwidth=0)
            style.configure("Treeview.Heading", background="#388e3c", foreground="#ffffff")
            
        elif theme == "vegas":
            # Vegas casino theme
            self.root.configure(bg="#0d3d0d")
            style.theme_use("clam")
            style.configure(".", background="#0d3d0d", foreground="#ffd700", 
                          fieldbackground="#1a5d1a", borderwidth=2)
            style.configure("TLabel", background="#0d3d0d", foreground="#ffd700")
            style.configure("TFrame", background="#0d3d0d")
            style.configure("TLabelFrame", background="#0d3d0d", foreground="#ffd700")
            style.configure("TButton", background="#1a5d1a", foreground="#ffd700")
            style.map("TButton", background=[("active", "#267326")])
            
        elif theme == "royal":
            # Royal blue/gold theme
            self.root.configure(bg="#1a237e")
            style.theme_use("clam")
            style.configure(".", background="#1a237e", foreground="#ffd700", 
                          fieldbackground="#303f9f", borderwidth=2)
            style.configure("TLabel", background="#1a237e", foreground="#ffd700")
            style.configure("TFrame", background="#1a237e")
            style.configure("TLabelFrame", background="#1a237e", foreground="#ffd700")
            style.configure("TButton", background="#303f9f", foreground="#ffd700")
            style.map("TButton", background=[("active", "#3f51b5")])
            
        else:  # classic theme
            style.theme_use("default")
            self.root.configure(bg="#f0f0f0")
    
    def setup_icon(self):
        """Setup application icon"""
        # List of possible icon files
        icon_files = ['poker_icon.ico', 'poker_icon.png', 'poker_icon.jpg', 'poker_icon.jpeg']
        
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                try:
                    if icon_file.endswith('.ico'):
                        # Use ICO file directly
                        self.root.iconbitmap(icon_file)
                    else:
                        # For PNG/JPG, we need to use PhotoImage (requires tkinter)
                        try:
                            icon_image = tk.PhotoImage(file=icon_file)
                            self.root.iconphoto(False, icon_image)
                        except:
                            # If PhotoImage fails, skip icon
                            pass
                    print(f"Loaded icon: {icon_file}")
                    break
                except Exception as e:
                    print(f"Could not load icon {icon_file}: {e}")
                    continue
    
    def load_display_icon(self):
        """Load icon for display within the application interface"""
        icon_files = ['poker_icon.png', 'poker_icon.gif', 'poker_icon.jpg', 'poker_icon.jpeg']
        
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                try:
                    # Load image for display in the interface
                    original_icon = tk.PhotoImage(file=icon_file)
                    
                    # Check size and resize if needed
                    width = original_icon.width()
                    height = original_icon.height()
                    
                    if width > 120 or height > 120:
                        # Calculate scale factor to fit within 120x120
                        scale_x = 120 / width
                        scale_y = 120 / height
                        scale = min(scale_x, scale_y)
                        
                        if scale < 1:
                            # Use subsample to make it smaller
                            subsample_factor = int(1 / scale)
                            if subsample_factor > 1:
                                self.display_icon = original_icon.subsample(subsample_factor, subsample_factor)
                            else:
                                self.display_icon = original_icon
                        else:
                            self.display_icon = original_icon
                    else:
                        self.display_icon = original_icon
                    
                    print(f"Loaded display icon: {icon_file} ({self.display_icon.width()}x{self.display_icon.height()})")
                    break
                except tk.TclError as e:
                    print(f"Could not load display icon {icon_file}: Invalid image format or corrupted file")
                    continue
                except Exception as e:
                    print(f"Could not load display icon {icon_file}: {e}")
                    continue
        
        if not hasattr(self, 'display_icon') or self.display_icon is None:
            print("No valid icon found. You can add poker_icon.png, poker_icon.gif, or poker_icon.jpg to display your tournament logo.")
    
    def setup_gui(self):
        """Setup the main GUI"""
        # Main container with three columns
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        
        # Left panel - Timer and Blinds
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row_counter = 0
        
        # Icon display section (if icon is available)
        if hasattr(self, 'display_icon') and self.display_icon:
            icon_frame = ttk.LabelFrame(left_frame, text="Tournament", padding="10")
            icon_frame.grid(row=row_counter, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Icon display
            icon_label = ttk.Label(icon_frame, image=self.display_icon)
            icon_label.grid(row=0, column=0, pady=5)
            
            # Tournament title below icon (if different from default)
            if self.config.get("tournament_title") != "Pit Boss - Poker Timer":
                title_label = ttk.Label(icon_frame, text=self.config.get("tournament_title", ""), 
                                      font=("Arial", 12, "bold"))
                title_label.grid(row=1, column=0, pady=(5, 0))
            
            row_counter += 1
        
        # Title section (only if no icon and custom title)
        elif self.config.get("tournament_title") != "Pit Boss - Poker Timer":
            title_frame = ttk.LabelFrame(left_frame, text="Tournament", padding="10")
            title_frame.grid(row=row_counter, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            title_label = ttk.Label(title_frame, text=self.config.get("tournament_title", ""), 
                                  font=("Arial", 14, "bold"))
            title_label.grid(row=0, column=0, pady=5)
            
            row_counter += 1
        
        # Timer section
        timer_frame = ttk.LabelFrame(left_frame, text="Timer", padding="15")
        timer_frame.grid(row=row_counter, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row_counter += 1
        
        self.timer_label = ttk.Label(timer_frame, text="20:00", font=("Arial", 32, "bold"))
        self.timer_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))
        
        # Timer progress bar
        self.timer_progress = ttk.Progressbar(timer_frame, length=250, mode='determinate')
        self.timer_progress.grid(row=1, column=0, columnspan=3, pady=(5, 10), sticky=(tk.W, tk.E))
        
        # Timer status label
        self.status_label = ttk.Label(timer_frame, text="Game Timer", font=("Arial", 12))
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        self.start_stop_btn = ttk.Button(timer_frame, text="Start Game", command=self.toggle_game_timer)
        self.start_stop_btn.grid(row=3, column=0, padx=5, pady=5)
        
        self.break_btn = ttk.Button(timer_frame, text="Start Break", command=self.start_break)
        self.break_btn.grid(row=3, column=1, padx=5, pady=5)
        
        self.reset_btn = ttk.Button(timer_frame, text="Reset", command=self.reset_timers)
        self.reset_btn.grid(row=3, column=2, padx=5, pady=5)
        
        # Blinds section
        blinds_frame = ttk.LabelFrame(left_frame, text="Current Blinds", padding="15")
        blinds_frame.grid(row=row_counter, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row_counter += 1
        
        self.level_label = ttk.Label(blinds_frame, text="Level 1", font=("Arial", 18, "bold"))
        self.level_label.grid(row=0, column=0, columnspan=2, pady=8)
        
        self.blinds_label = ttk.Label(blinds_frame, text="25/50", font=("Arial", 24, "bold"))
        self.blinds_label.grid(row=1, column=0, columnspan=2, pady=8)
        
        self.ante_label = ttk.Label(blinds_frame, text="Ante: 0", font=("Arial", 14))
        self.ante_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Blind countdown timer with progress bar
        self.blind_timer_label = ttk.Label(blinds_frame, text="Next increase in: 15:00", font=("Arial", 12, "bold"))
        self.blind_timer_label.grid(row=3, column=0, columnspan=2, pady=(10, 5))
        
        self.blind_progress = ttk.Progressbar(blinds_frame, length=200, mode='determinate')
        self.blind_progress.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Next blind level display
        self.next_blind_label = ttk.Label(blinds_frame, text="Next: 50/100", font=("Arial", 10))
        self.next_blind_label.grid(row=5, column=0, columnspan=2, pady=2)
        
        ttk.Button(blinds_frame, text="Next Level", command=self.next_blind_level).grid(row=6, column=0, padx=5, pady=8)
        ttk.Button(blinds_frame, text="Prev Level", command=self.prev_blind_level).grid(row=6, column=1, padx=5, pady=8)
        
        # Configuration section
        config_frame = ttk.LabelFrame(left_frame, text="Configuration", padding="10")
        config_frame.grid(row=row_counter, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(config_frame, text="Edit Title", command=self.edit_title).grid(row=0, column=0, padx=5, pady=2)
        ttk.Button(config_frame, text="Theme", command=self.change_theme).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(config_frame, text="Edit Blinds", command=self.edit_blinds).grid(row=1, column=0, padx=5, pady=2)
        ttk.Button(config_frame, text="Edit Prizes", command=self.edit_prizes).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(config_frame, text="Timer Settings", command=self.edit_timer_settings).grid(row=2, column=0, padx=5, pady=2)
        ttk.Button(config_frame, text="Save Config", command=self.save_config).grid(row=2, column=1, padx=5, pady=2)
        
        # Middle panel - Players
        middle_frame = ttk.Frame(main_frame, padding="5")
        middle_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.rowconfigure(0, weight=1)
        middle_frame.rowconfigure(1, weight=1)
        
        # Active Players section
        players_frame = ttk.LabelFrame(middle_frame, text="Active Players", padding="10")
        players_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        players_frame.columnconfigure(0, weight=1)
        players_frame.rowconfigure(2, weight=1)
        
        player_controls = ttk.Frame(players_frame)
        player_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(player_controls, text="Add Player", command=self.add_player).grid(row=0, column=0, padx=5)
        ttk.Button(player_controls, text="Remove Selected", command=self.remove_player).grid(row=0, column=1, padx=5)
        
        # Instructions
        ttk.Label(players_frame, text="Double-click player to eliminate", 
                 font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Players list
        self.players_tree = ttk.Treeview(players_frame, columns=("Name",), show="headings", height=6)
        self.players_tree.heading("Name", text="Player Name")
        self.players_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        players_scroll = ttk.Scrollbar(players_frame, orient="vertical", command=self.players_tree.yview)
        players_scroll.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.players_tree.configure(yscrollcommand=players_scroll.set)
        
        # Bind double-click to eliminate player
        self.players_tree.bind("<Double-1>", self.eliminate_player)
        
        # Eliminated Players section
        eliminated_frame = ttk.LabelFrame(middle_frame, text="Eliminated Players", padding="10")
        eliminated_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        eliminated_frame.columnconfigure(0, weight=1)
        eliminated_frame.rowconfigure(1, weight=1)
        
        # Controls for eliminated players
        eliminated_controls = ttk.Frame(eliminated_frame)
        eliminated_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(eliminated_controls, text="Double-click or right-click to reactivate", 
                 font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(eliminated_controls, text="Reactivate Selected", 
                  command=self.reactivate_selected_player).grid(row=0, column=1, padx=5, sticky=tk.E)
        
        self.eliminated_tree = ttk.Treeview(eliminated_frame, columns=("Position", "Name", "Prize"), show="headings", height=6)
        self.eliminated_tree.heading("Position", text="Position")
        self.eliminated_tree.heading("Name", text="Player")
        self.eliminated_tree.heading("Prize", text="Prize")
        self.eliminated_tree.column("Position", width=70)
        self.eliminated_tree.column("Name", width=120)
        self.eliminated_tree.column("Prize", width=100)
        self.eliminated_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        eliminated_scroll = ttk.Scrollbar(eliminated_frame, orient="vertical", command=self.eliminated_tree.yview)
        eliminated_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.eliminated_tree.configure(yscrollcommand=eliminated_scroll.set)
        
        # Bind double-click to reactivate player
        self.eliminated_tree.bind("<Double-1>", self.reactivate_player)
        
        # Add right-click context menu for eliminated players
        self.eliminated_context_menu = tk.Menu(self.root, tearoff=0)
        self.eliminated_context_menu.add_command(label="Reactivate Player", command=self.reactivate_selected_player)
        self.eliminated_tree.bind("<Button-3>", self.show_eliminated_context_menu)  # Right-click
        
        # Right panel - Prize Structure
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Prize pool display
        pool_frame = ttk.LabelFrame(right_frame, text="Prize Pool", padding="10")
        pool_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.pool_label = ttk.Label(pool_frame, text=f"${self.config['total_prize_pool']:,}", 
                                   font=("Arial", 20, "bold"))
        self.pool_label.grid(row=0, column=0, pady=10)
        
        # Prize structure display
        prizes_frame = ttk.LabelFrame(right_frame, text="Payout Structure", padding="10")
        prizes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        prizes_frame.columnconfigure(0, weight=1)
        prizes_frame.rowconfigure(0, weight=1)
        
        self.prizes_tree = ttk.Treeview(prizes_frame, columns=("Position", "Prize"), show="headings", height=12)
        self.prizes_tree.heading("Position", text="Position")
        self.prizes_tree.heading("Prize", text="Prize Amount")
        self.prizes_tree.column("Position", width=80)
        self.prizes_tree.column("Prize", width=120)
        self.prizes_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        prizes_scroll = ttk.Scrollbar(prizes_frame, orient="vertical", command=self.prizes_tree.yview)
        prizes_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.prizes_tree.configure(yscrollcommand=prizes_scroll.set)
        
        # Load initial data
        self.update_display()
        self.populate_players()
        self.populate_eliminated()
        self.populate_prizes()
    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def update_display(self):
        """Update timer and blinds display"""
        if self.is_break_running:
            self.timer_label.config(text=f"{self.format_time(self.break_time_remaining)}")
            self.status_label.config(text="BREAK TIME")
            # Update break timer progress bar
            max_break_time = self.config["break_duration"] * 60
            if max_break_time > 0:
                progress = (self.break_time_remaining / max_break_time) * 100
                self.timer_progress['value'] = progress
        else:
            self.timer_label.config(text=self.format_time(self.game_time_remaining))
            if self.is_game_running:
                self.status_label.config(text="Game Timer - RUNNING")
            else:
                self.status_label.config(text="Game Timer - PAUSED")
            
            # Update game timer progress bar
            max_game_time = self.config["game_duration"] * 60
            if max_game_time > 0:
                progress = (self.game_time_remaining / max_game_time) * 100
                self.timer_progress['value'] = progress
        
        # Update blinds display
        if self.current_level <= len(self.config["blinds"]):
            blind = self.config["blinds"][self.current_level - 1]
            self.level_label.config(text=f"Level {self.current_level}")
            self.blinds_label.config(text=f"{blind['small']}/{blind['big']}")
            self.ante_label.config(text=f"Ante: {blind['ante']}")
            
            # Update blind countdown timer
            self.blind_timer_label.config(text=f"Next increase in: {self.format_time(self.blind_time_remaining)}")
            
            # Update blind progress bar
            max_blind_time = self.config["blind_increase_interval"] * 60
            if max_blind_time > 0:
                progress = (self.blind_time_remaining / max_blind_time) * 100
                self.blind_progress['value'] = progress
            
            # Update next blind level display
            if self.current_level < len(self.config["blinds"]):
                next_blind = self.config["blinds"][self.current_level]
                self.next_blind_label.config(text=f"Next: {next_blind['small']}/{next_blind['big']}")
            else:
                self.next_blind_label.config(text="Next: Final Level")
        
        # Update button states
        if self.is_game_running:
            self.start_stop_btn.config(text="Pause Game")
        else:
            self.start_stop_btn.config(text="Start Game")
        
        if self.is_break_running:
            self.break_btn.config(text="End Break")
        else:
            self.break_btn.config(text="Start Break")
        
        # Update prize pool display
        if hasattr(self, 'pool_label'):
            self.pool_label.config(text=f"${self.config['total_prize_pool']:,}")
    
    def toggle_game_timer(self):
        """Toggle game timer on/off"""
        if self.is_break_running:
            self.is_break_running = False
        
        if not self.is_game_running:
            # Starting the game - reset timer if it's at 0
            if self.game_time_remaining <= 0:
                self.game_time_remaining = self.config["game_duration"] * 60
        
        self.is_game_running = not self.is_game_running
        self.update_display()
    
    def start_break(self):
        """Start or end break timer"""
        if self.is_break_running:
            self.is_break_running = False
        else:
            self.is_game_running = False
            self.is_break_running = True
            self.break_time_remaining = self.config["break_duration"] * 60
        
        self.update_display()
    
    def reset_timers(self):
        """Reset all timers"""
        self.is_game_running = False
        self.is_break_running = False
        self.game_time_remaining = self.config["game_duration"] * 60
        self.break_time_remaining = self.config["break_duration"] * 60
        self.last_blind_increase = datetime.now()
        self.blind_time_remaining = self.config["blind_increase_interval"] * 60
        # Reset progress bars
        self.timer_progress['value'] = 100
        self.blind_progress['value'] = 100
        self.update_display()
    
    def next_blind_level(self):
        """Advance to next blind level"""
        if self.current_level < len(self.config["blinds"]):
            self.current_level += 1
            self.last_blind_increase = datetime.now()
            self.blind_time_remaining = self.config["blind_increase_interval"] * 60
            self.update_display()
    
    def prev_blind_level(self):
        """Go back to previous blind level"""
        if self.current_level > 1:
            self.current_level -= 1
            self.update_display()
    
    def timer_loop(self):
        """Main timer loop running in separate thread"""
        while True:
            if self.is_game_running and self.game_time_remaining > 0:
                self.game_time_remaining -= 1
                
                # Update blind countdown timer - only when game is running
                if self.blind_time_remaining > 0:
                    self.blind_time_remaining -= 1
                
                # Check if blind level should increase
                if self.blind_time_remaining <= 0:
                    if self.current_level < len(self.config["blinds"]):
                        self.current_level += 1
                        self.last_blind_increase = datetime.now()
                        self.blind_time_remaining = self.config["blind_increase_interval"] * 60
                
                if self.game_time_remaining == 0:
                    self.is_game_running = False
                    # Auto start break
                    self.is_break_running = True
                    self.break_time_remaining = self.config["break_duration"] * 60
                
            elif self.is_break_running and self.break_time_remaining > 0:
                self.break_time_remaining -= 1
                
                if self.break_time_remaining == 0:
                    self.is_break_running = False
                    self.game_time_remaining = self.config["game_duration"] * 60
            # When paused, blind timer stays frozen (no updates needed)
            
            # Update display in main thread
            self.root.after_idle(self.update_display)
            time.sleep(1)
    
    def add_player(self):
        """Add a new player"""
        name = simpledialog.askstring("Add Player", "Enter player name:")
        if name and name.strip():
            self.config["players"].append(name.strip())
            self.populate_players()
    
    def remove_player(self):
        """Remove selected player"""
        selection = self.players_tree.selection()
        if selection:
            item = self.players_tree.item(selection[0])
            player_name = item["values"][0]
            self.config["players"].remove(player_name)
            self.populate_players()
    
    def eliminate_player(self, event):
        """Eliminate player and add to prize list"""
        selection = self.players_tree.selection()
        if selection:
            item = self.players_tree.item(selection[0])
            player_name = item["values"][0]
            
            # Calculate position (number of active players)
            position = len(self.config["players"])
            
            # Calculate prize
            prize = self.calculate_prize(position)
            
            # Add to eliminated list
            self.config["eliminated_players"].append({
                "name": player_name,
                "position": position,
                "prize": prize
            })
            
            # Remove from active players
            self.config["players"].remove(player_name)
            
            self.populate_players()
            self.populate_eliminated()
    
    def reactivate_player(self, event):
        """Reactivate an eliminated player (move back to active)"""
        selection = self.eliminated_tree.selection()
        if selection:
            item = self.eliminated_tree.item(selection[0])
            player_name = item["values"][1]  # Name is in column 1
            
            # Confirm the action
            result = messagebox.askyesno("Reactivate Player", 
                                       f"Move {player_name} back to active players?\n\n"
                                       f"This will also reorder the eliminated players' positions.")
            
            if result:
                # Find and remove the player from eliminated list
                eliminated_player = None
                for i, player in enumerate(self.config["eliminated_players"]):
                    if player["name"] == player_name:
                        eliminated_player = self.config["eliminated_players"].pop(i)
                        break
                
                if eliminated_player:
                    # Add back to active players
                    self.config["players"].append(eliminated_player["name"])
                    
                    # Reorder remaining eliminated players' positions
                    # The positions should be consecutive based on elimination order
                    for i, player in enumerate(self.config["eliminated_players"]):
                        # Update position (starting from the number of active players + 1)
                        new_position = len(self.config["players"]) + i + 1
                        player["position"] = new_position
                        # Recalculate prize for new position
                        player["prize"] = self.calculate_prize(new_position)
                    
                    self.populate_players()
                    self.populate_eliminated()
                    
                    messagebox.showinfo("Player Reactivated", 
                                      f"{player_name} has been moved back to active players.\n"
                                      f"Eliminated players have been reordered.")
    
    def show_eliminated_context_menu(self, event):
        """Show context menu for eliminated players"""
        # Select the item under the cursor
        item = self.eliminated_tree.identify_row(event.y)
        if item:
            self.eliminated_tree.selection_set(item)
            self.eliminated_context_menu.post(event.x_root, event.y_root)
    
    def reactivate_selected_player(self):
        """Reactivate the currently selected eliminated player"""
        selection = self.eliminated_tree.selection()
        if selection:
            # Create a mock event to reuse the existing method
            class MockEvent:
                pass
            self.reactivate_player(MockEvent())
    
    def calculate_prize(self, position):
        """Calculate prize for given position"""
        for prize_info in self.config["prize_structure"]:
            if prize_info["position"] == position:
                if prize_info["amount"] > 0:
                    return prize_info["amount"]
                else:
                    return int(self.config["total_prize_pool"] * prize_info["percentage"] / 100)
        return 0
    
    def populate_players(self):
        """Populate active players list"""
        for item in self.players_tree.get_children():
            self.players_tree.delete(item)
        
        for player in self.config["players"]:
            self.players_tree.insert("", "end", values=(player,))
    
    def populate_eliminated(self):
        """Populate eliminated players list"""
        for item in self.eliminated_tree.get_children():
            self.eliminated_tree.delete(item)
        
        for player in sorted(self.config["eliminated_players"], key=lambda x: x["position"]):
            prize_str = f"${player['prize']}" if player['prize'] > 0 else "No Prize"
            self.eliminated_tree.insert("", "end", values=(player["position"], player["name"], prize_str))
    
    def populate_prizes(self):
        """Populate prize structure display"""
        if not hasattr(self, 'prizes_tree'):
            return
            
        for item in self.prizes_tree.get_children():
            self.prizes_tree.delete(item)
        
        for prize_info in sorted(self.config["prize_structure"], key=lambda x: x["position"]):
            prize_amount = self.calculate_prize(prize_info["position"])
            prize_str = f"${prize_amount:,}" if prize_amount > 0 else "No Prize"
            position_str = self.get_ordinal(prize_info["position"])
            self.prizes_tree.insert("", "end", values=(position_str, prize_str))
    
    def get_ordinal(self, n):
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"
    
    def edit_title(self):
        """Edit tournament title"""
        current_title = self.config.get("tournament_title", "Pit Boss - Poker Timer")
        new_title = simpledialog.askstring("Edit Title", "Enter tournament title:", initialvalue=current_title)
        if new_title and new_title.strip():
            self.config["tournament_title"] = new_title.strip()
            self.root.title(new_title.strip())
            self.save_config()
    
    def change_theme(self):
        """Change application theme"""
        themes = ["classic", "dark", "midnight", "poker-green", "vegas", "royal"]
        current_theme = self.config.get("theme", "classic")
        
        # Create theme selection window
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Select Theme")
        theme_window.geometry("350x280")
        theme_window.grab_set()
        
        ttk.Label(theme_window, text="Select Theme:", font=("Arial", 12, "bold")).pack(pady=10)
        
        theme_var = tk.StringVar(value=current_theme)
        
        theme_descriptions = {
            "classic": "Classic - Default light theme",
            "dark": "Dark - Modern dark theme",
            "midnight": "Midnight - Deep blue theme",
            "poker-green": "Poker Green - Casino green theme",
            "vegas": "Vegas - Gold casino style",
            "royal": "Royal - Blue and gold theme"
        }
        
        for theme in themes:
            text = theme_descriptions.get(theme, theme.title())
            ttk.Radiobutton(theme_window, text=text, variable=theme_var, 
                          value=theme).pack(pady=3, anchor='w', padx=20)
        
        def apply_theme():
            self.config["theme"] = theme_var.get()
            self.save_config()
            # Apply theme immediately without restart
            self.setup_theme()
            messagebox.showinfo("Theme Applied", "Theme has been applied successfully!")
            theme_window.destroy()
        
        ttk.Button(theme_window, text="Apply", command=apply_theme).pack(pady=10)
    
    def edit_blinds(self):
        """Open blinds editor window"""
        BlindsEditor(self.root, self.config["blinds"], self.save_config)
    
    def edit_prizes(self):
        """Open prize structure editor window"""
        PrizeEditor(self.root, self.config, self.save_config, self.populate_prizes)
    
    def edit_timer_settings(self):
        """Open timer settings window"""
        TimerSettingsEditor(self.root, self.config, self.save_config)
    
    def auto_save(self):
        """Auto-save configuration every 30 seconds"""
        self.save_config()
        self.root.after(30000, self.auto_save)  # 30 seconds


class BlindsEditor:
    def __init__(self, parent, blinds, save_callback):
        self.blinds = blinds
        self.save_callback = save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Blind Levels")
        self.window.geometry("400x500")
        self.window.grab_set()
        
        self.setup_gui()
    
    def setup_gui(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Controls
        controls = ttk.Frame(frame)
        controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls, text="Add Level", command=self.add_level).grid(row=0, column=0, padx=5)
        ttk.Button(controls, text="Remove Level", command=self.remove_level).grid(row=0, column=1, padx=5)
        ttk.Button(controls, text="Save", command=self.save_changes).grid(row=0, column=2, padx=5)
        
        # Blinds tree
        self.tree = ttk.Treeview(frame, columns=("Level", "Small", "Big", "Ante"), show="headings")
        self.tree.heading("Level", text="Level")
        self.tree.heading("Small", text="Small Blind")
        self.tree.heading("Big", text="Big Blind")
        self.tree.heading("Ante", text="Ante")
        
        self.tree.column("Level", width=60)
        self.tree.column("Small", width=100)
        self.tree.column("Big", width=100)
        self.tree.column("Ante", width=80)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.populate_tree()
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.edit_level)
    
    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, blind in enumerate(self.blinds):
            self.tree.insert("", "end", values=(i+1, blind["small"], blind["big"], blind["ante"]))
    
    def add_level(self):
        # Add a new level with default values
        self.blinds.append({"small": 100, "big": 200, "ante": 0})
        self.populate_tree()
    
    def remove_level(self):
        selection = self.tree.selection()
        if selection and len(self.blinds) > 1:
            index = self.tree.index(selection[0])
            del self.blinds[index]
            self.populate_tree()
    
    def edit_level(self, event):
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            blind = self.blinds[index]
            
            # Simple edit dialog
            new_small = simpledialog.askinteger("Edit Level", f"Small blind (current: {blind['small']}):", initialvalue=blind["small"])
            if new_small is not None:
                new_big = simpledialog.askinteger("Edit Level", f"Big blind (current: {blind['big']}):", initialvalue=blind["big"])
                if new_big is not None:
                    new_ante = simpledialog.askinteger("Edit Level", f"Ante (current: {blind['ante']}):", initialvalue=blind["ante"])
                    if new_ante is not None:
                        self.blinds[index] = {"small": new_small, "big": new_big, "ante": new_ante}
                        self.populate_tree()
    
    def save_changes(self):
        self.save_callback()
        self.window.destroy()


class PrizeEditor:
    def __init__(self, parent, config, save_callback, refresh_callback=None):
        self.config = config
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Prize Structure")
        self.window.geometry("500x400")
        self.window.grab_set()
        
        self.setup_gui()
    
    def setup_gui(self):
        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Prize pool
        pool_frame = ttk.Frame(frame)
        pool_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(pool_frame, text="Total Prize Pool: $").pack(side=tk.LEFT)
        self.pool_var = tk.StringVar(value=str(self.config["total_prize_pool"]))
        pool_entry = ttk.Entry(pool_frame, textvariable=self.pool_var, width=10)
        pool_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(pool_frame, text="Update", command=self.update_pool).pack(side=tk.LEFT, padx=5)
        
        # Prize structure
        ttk.Label(frame, text="Prize Structure:").pack(anchor=tk.W, pady=(10, 5))
        
        self.tree = ttk.Treeview(frame, columns=("Position", "Percentage", "Amount"), show="headings", height=10)
        self.tree.heading("Position", text="Position")
        self.tree.heading("Percentage", text="Percentage %")
        self.tree.heading("Amount", text="Fixed Amount $")
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Controls
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X)
        
        ttk.Button(controls, text="Add Position", command=self.add_position).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Remove", command=self.remove_position).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Edit", command=self.edit_position).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Save", command=self.save_changes).pack(side=tk.RIGHT, padx=5)
        
        self.populate_tree()
        self.tree.bind("<Double-1>", lambda e: self.edit_position())
    
    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for prize in sorted(self.config["prize_structure"], key=lambda x: x["position"]):
            self.tree.insert("", "end", values=(prize["position"], prize["percentage"], prize["amount"]))
    
    def update_pool(self):
        try:
            self.config["total_prize_pool"] = int(self.pool_var.get())
            if self.refresh_callback:
                self.refresh_callback()
        except ValueError:
            messagebox.showerror("Error", "Invalid prize pool amount")
    
    def add_position(self):
        position = simpledialog.askinteger("Add Position", "Position number:")
        if position:
            percentage = simpledialog.askinteger("Add Position", "Percentage (0-100):", initialvalue=0)
            if percentage is not None:
                amount = simpledialog.askinteger("Add Position", "Fixed amount (0 to use percentage):", initialvalue=0)
                if amount is not None:
                    self.config["prize_structure"].append({
                        "position": position,
                        "percentage": percentage,
                        "amount": amount
                    })
                    self.populate_tree()
    
    def remove_position(self):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            position = item["values"][0]
            self.config["prize_structure"] = [p for p in self.config["prize_structure"] if p["position"] != position]
            self.populate_tree()
    
    def edit_position(self):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            position = item["values"][0]
            
            # Find the prize structure
            prize = next(p for p in self.config["prize_structure"] if p["position"] == position)
            
            new_percentage = simpledialog.askinteger("Edit Position", f"Percentage for position {position}:", initialvalue=prize["percentage"])
            if new_percentage is not None:
                new_amount = simpledialog.askinteger("Edit Position", f"Fixed amount for position {position}:", initialvalue=prize["amount"])
                if new_amount is not None:
                    prize["percentage"] = new_percentage
                    prize["amount"] = new_amount
                    self.populate_tree()
    
    def save_changes(self):
        self.save_callback()
        if self.refresh_callback:
            self.refresh_callback()
        self.window.destroy()


class TimerSettingsEditor:
    def __init__(self, parent, config, save_callback):
        self.config = config
        self.save_callback = save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Timer Settings")
        self.window.geometry("350x200")
        self.window.grab_set()
        
        self.setup_gui()
    
    def setup_gui(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Game duration
        ttk.Label(frame, text="Game Duration (minutes):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.game_duration = tk.StringVar(value=str(self.config["game_duration"]))
        ttk.Entry(frame, textvariable=self.game_duration, width=10).grid(row=0, column=1, padx=10, pady=5)
        
        # Break duration
        ttk.Label(frame, text="Break Duration (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.break_duration = tk.StringVar(value=str(self.config["break_duration"]))
        ttk.Entry(frame, textvariable=self.break_duration, width=10).grid(row=1, column=1, padx=10, pady=5)
        
        # Blind increase interval
        ttk.Label(frame, text="Blind Increase Interval (minutes):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.blind_interval = tk.StringVar(value=str(self.config["blind_increase_interval"]))
        ttk.Entry(frame, textvariable=self.blind_interval, width=10).grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_settings(self):
        try:
            self.config["game_duration"] = int(self.game_duration.get())
            self.config["break_duration"] = int(self.break_duration.get())
            self.config["blind_increase_interval"] = int(self.blind_interval.get())
            self.save_callback()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")


def main():
    root = tk.Tk()
    app = PokerTimer(root)
    
    # Handle window closing
    def on_closing():
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()