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
        self.root.geometry("1400x900")  # Larger window for new layout
        self.root.configure(bg='#1e1e1e')  # Dark background
        
        # Initialize state variables
        self.is_game_running = False
        self.is_break_running = False
        self.game_time_remaining = 0
        self.break_time_remaining = 0
        self.current_level = 1
        self.last_blind_increase = datetime.now()
        self.blind_time_remaining = 0  # Countdown to next blind increase
        self.total_game_time = 0  # Total elapsed time since game start
        self.game_start_time = None
        
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
            "accent_color": "#2196f3",  # Configurable blue accent color
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
                        except tk.TclError as e:
                            if ".jpg" in icon_file or ".jpeg" in icon_file:
                                print(f"⚠️  Window icon: JPEG format not supported - {icon_file}")
                            else:
                                print(f"⚠️  Window icon: Could not load {icon_file} - try different format")
                            continue
                        except:
                            # If PhotoImage fails, skip icon
                            continue
                    print(f"✅ Loaded window icon: {icon_file}")
                    break
                except Exception as e:
                    print(f"⚠️  Could not load window icon {icon_file}: {e}")
                    continue
    
    def load_display_icon(self):
        """Load icon for display within the application interface"""
        icon_files = ['poker_icon.png', 'poker_icon.gif', 'poker_icon.jpg', 'poker_icon.jpeg']
        
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                try:
                    # Load image for display in the interface
                    original_icon = tk.PhotoImage(file=icon_file)
                    
                    # Check size and resize if needed - make it bigger since we removed PIT BOSS text
                    width = original_icon.width()
                    height = original_icon.height()
                    
                    if width > 300 or height > 300:
                        # Calculate scale factor to fit within 300x300 (much bigger now)
                        scale_x = 300 / width
                        scale_y = 300 / height
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
                    
                    print(f"✅ Loaded display icon: {icon_file} ({self.display_icon.width()}x{self.display_icon.height()})")
                    break
                except tk.TclError as e:
                    if "couldn't recognize data in image file" in str(e) or "unknown color type" in str(e):
                        print(f"❌ Could not load {icon_file}: Unsupported image format")
                        if icon_file.endswith(('.jpg', '.jpeg')):
                            print(f"   💡 TIP: JPEG format not supported. Convert {icon_file} to PNG format")
                            print(f"   🔧 Try: Open {icon_file} in Paint, Save As → PNG picture → poker_icon.png")
                        else:
                            print(f"   💡 TIP: Try resaving {icon_file} in a compatible format")
                    else:
                        print(f"❌ Could not load {icon_file}: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Could not load {icon_file}: {e}")
                    continue
        
        if not hasattr(self, 'display_icon') or self.display_icon is None:
            print()
            print("🃏 No valid icon found for display.")
            print("📁 Add one of these files to show your tournament logo:")
            print("   • poker_icon.png (recommended)")  
            print("   • poker_icon.gif (animated supported!)")
            print("❌ Note: JPEG files (.jpg/.jpeg) are not supported by tkinter")
            print("🔧 Convert JPEG to PNG: Run 'python fix_icon.py' for instructions")
    
    def setup_gui(self):
        """Setup the modern poker timer GUI with full three-panel layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Timer and circular displays
        self.setup_timer_section(main_frame)
        
        # Middle section - Three-panel layout for players and prizes
        self.setup_main_panels(main_frame)
        
        # Bottom section - Controls
        self.setup_bottom_section(main_frame)
        
        # Load initial data
        self.update_display()
        self.populate_players()
        self.populate_eliminated()
        self.populate_prizes()
    
    def setup_timer_section(self, parent):
        """Setup the timer section with circular displays"""
        timer_frame = tk.Frame(parent, bg='#1e1e1e')
        timer_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left circular display - Blinds
        left_frame = tk.Frame(timer_frame, bg='#1e1e1e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_circular_display(left_frame, "BLINDS", "25/50", self.config.get("accent_color", "#2196f3"))
        
        # Center section - Main timer and controls  
        center_frame = tk.Frame(timer_frame, bg='#1e1e1e')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)
        
        # TIME TO NEXT BREAK label (store reference for break mode)
        self.time_label = tk.Label(center_frame, text="TIME TO NEXT BREAK", 
                             font=("Arial", 12), fg="#888888", bg="#1e1e1e")
        self.time_label.pack(pady=(10, 5))
        
        # Main timer display
        self.timer_label = tk.Label(center_frame, text="20:00", 
                                   font=("Arial", 48, "bold"), fg=self.config.get("accent_color", "#2196f3"), bg="#1e1e1e")
        self.timer_label.pack(pady=5)
        
        # Total playing time label
        total_time_text = tk.Label(center_frame, text="TOTAL PLAYING TIME", 
                                 font=("Arial", 10), fg="#888888", bg="#1e1e1e")
        total_time_text.pack(pady=(5, 2))
        
        # Total playing time display
        self.total_time_display = tk.Label(center_frame, text="00:00", 
                                          font=("Arial", 16), fg="#ffffff", bg="#1e1e1e")
        self.total_time_display.pack(pady=2)
        
        # Tournament logo/icon area - bigger without PIT BOSS text
        if self.config.get("tournament_title") != "Pit Boss - Poker Timer":
            title_label = tk.Label(center_frame, text=self.config.get("tournament_title", "POKER"), 
                                 font=("Arial", 14, "bold"), fg=self.config.get("accent_color", "#2196f3"), bg="#1e1e1e")
            title_label.pack(pady=5)
        
        # Add large icon without PIT BOSS text
        if hasattr(self, 'display_icon') and self.display_icon:
            icon_label = tk.Label(center_frame, image=self.display_icon, bg="#1e1e1e")
            icon_label.pack(pady=(5, 5))
        
        # Right circular display - Ante
        right_frame = tk.Frame(timer_frame, bg='#1e1e1e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_circular_display(right_frame, "ANTE", "0", self.config.get("accent_color", "#2196f3"))
        
        # Next level displays under circles
        self.create_next_level_displays(left_frame, right_frame)
    
    def setup_main_panels(self, parent):
        """Setup the main three-panel layout for players and prizes"""
        panels_frame = tk.Frame(parent, bg='#1e1e1e')
        panels_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left Panel - Active Players
        self.setup_players_panel(panels_frame)
        
        # Center Panel - Eliminated Players
        self.setup_eliminated_panel(panels_frame)
        
        # Right Panel - Prize Structure
        self.setup_prizes_panel(panels_frame)
    
    def setup_players_panel(self, parent):
        """Setup active players panel"""
        players_frame = tk.LabelFrame(parent, text="ACTIVE PLAYERS", 
                                     fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                     font=("Arial", 12, "bold"))
        players_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Player count display at top of panel
        count_frame = tk.Frame(players_frame, bg='#1e1e1e')
        count_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(count_frame, text="PLAYERS LEFT:", font=("Arial", 9, "bold"), 
                fg="#888888", bg="#1e1e1e").pack(side=tk.LEFT)
        self.players_count_label = tk.Label(count_frame, text=str(len(self.config.get("players", []))), 
                                           font=("Arial", 14, "bold"), fg="#ffffff", bg="#1e1e1e")
        self.players_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Players treeview
        self.players_tree = ttk.Treeview(players_frame, columns=("Name",), show="headings", height=6)
        self.players_tree.heading("Name", text="Player Name")
        self.players_tree.column("Name", width=150)
        self.players_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind double-click to eliminate
        self.players_tree.bind("<Double-1>", self.eliminate_player)
        
        # Players control buttons
        players_btn_frame = tk.Frame(players_frame, bg='#1e1e1e')
        players_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(players_btn_frame, text="Add Player", command=self.add_player,
                 bg=self.config.get("accent_color", "#2196f3"), fg='white',
                 font=("Arial", 9), padx=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(players_btn_frame, text="Remove", command=self.remove_player,
                 bg='#f44336', fg='white',
                 font=("Arial", 9), padx=10).pack(side=tk.LEFT, padx=2)
        
        # Instructions
        tk.Label(players_frame, text="Double-click to eliminate", 
                font=("Arial", 8), fg="#888888", bg="#1e1e1e").pack(pady=(0, 5))
    
    def setup_eliminated_panel(self, parent):
        """Setup eliminated players panel"""  
        eliminated_frame = tk.LabelFrame(parent, text="ELIMINATED PLAYERS",
                                        fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                        font=("Arial", 12, "bold"))
        eliminated_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Eliminated players treeview
        self.eliminated_tree = ttk.Treeview(eliminated_frame, columns=("Position", "Name", "Prize"), show="headings", height=6)
        self.eliminated_tree.heading("Position", text="Pos")
        self.eliminated_tree.heading("Name", text="Player")
        self.eliminated_tree.heading("Prize", text="Prize")
        
        self.eliminated_tree.column("Position", width=40)
        self.eliminated_tree.column("Name", width=100)
        self.eliminated_tree.column("Prize", width=80)
        
        self.eliminated_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind double-click to reactivate
        self.eliminated_tree.bind("<Double-1>", self.reactivate_player)
        
        # Context menu for eliminated players
        self.eliminated_context_menu = tk.Menu(self.root, tearoff=0)
        self.eliminated_context_menu.add_command(label="Reactivate Player", command=self.reactivate_selected_player)
        self.eliminated_tree.bind("<Button-3>", self.show_eliminated_context_menu)
        
        # Eliminated control button
        eliminated_btn_frame = tk.Frame(eliminated_frame, bg='#1e1e1e')
        eliminated_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(eliminated_btn_frame, text="Reactivate Selected", command=self.reactivate_selected_player,
                 bg='#4caf50', fg='white',
                 font=("Arial", 9), padx=10).pack(side=tk.LEFT)
        
        # Instructions
        tk.Label(eliminated_frame, text="Double-click or right-click to reactivate", 
                font=("Arial", 8), fg="#888888", bg="#1e1e1e").pack(pady=(0, 5))
    
    def setup_prizes_panel(self, parent):
        """Setup prize structure panel"""
        prizes_frame = tk.LabelFrame(parent, text="PRIZE STRUCTURE",
                                    fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                    font=("Arial", 12, "bold"))
        prizes_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Prize pool display
        pool_frame = tk.Frame(prizes_frame, bg='#1e1e1e')
        pool_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(pool_frame, text="TOTAL PRIZE POOL", 
                font=("Arial", 10), fg="#888888", bg="#1e1e1e").pack()
        
        self.prize_pool_label = tk.Label(pool_frame, text=f"${self.config.get('total_prize_pool', 1000):,}", 
                                        font=("Arial", 20, "bold"), fg=self.config.get("accent_color", "#2196f3"), bg="#1e1e1e")
        self.prize_pool_label.pack()
        
        # Prize structure treeview
        self.prizes_tree = ttk.Treeview(prizes_frame, columns=("Position", "Prize"), show="headings", height=6)
        self.prizes_tree.heading("Position", text="Position")  
        self.prizes_tree.heading("Prize", text="Prize")
        
        self.prizes_tree.column("Position", width=70)
        self.prizes_tree.column("Prize", width=100)
        
        self.prizes_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Prize control button
        prizes_btn_frame = tk.Frame(prizes_frame, bg='#1e1e1e')
        prizes_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(prizes_btn_frame, text="Edit Prizes", command=self.edit_prizes,
                 bg=self.config.get("accent_color", "#2196f3"), fg='white',
                 font=("Arial", 9), padx=10).pack()
    
    def setup_bottom_section(self, parent):
        """Setup bottom control section"""
        bottom_frame = tk.Frame(parent, bg='#1e1e1e')
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Control buttons only
        self.create_control_buttons(bottom_frame)
    
    def create_circular_display(self, parent, label, value, color):
        """Create a circular display for blinds/ante with values inside circles"""
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(expand=True, pady=30)
        
        # Label text above circle
        label_widget = tk.Label(container, text=label, font=("Arial", 10), 
                               fg="#888888", bg="#1e1e1e")
        label_widget.pack(pady=(0, 10))
        
        # Create circular canvas
        canvas = tk.Canvas(container, width=200, height=200, bg='#1e1e1e', highlightthickness=0)
        canvas.pack()
        
        # Draw circle
        canvas.create_oval(15, 15, 185, 185, outline=color, width=3, fill='#2a2a2a')
        
        # Add text inside the circle
        if label == "BLINDS":
            self.blinds_text_id = canvas.create_text(100, 100, text=value, font=("Arial", 24, "bold"), 
                                                    fill="#ffffff", anchor="center")
            self.blinds_canvas = canvas
        else:  # ANTE
            self.ante_text_id = canvas.create_text(100, 100, text=value, font=("Arial", 28, "bold"), 
                                                  fill="#ffffff", anchor="center")
            self.ante_canvas = canvas
    
    def create_next_level_displays(self, left_frame, right_frame):
        """Create next level displays under the circular displays"""
        # Left - Next blinds with countdown
        left_next = tk.Frame(left_frame, bg='#1e1e1e')
        left_next.pack(pady=(0, 10))
        
        tk.Label(left_next, text="NEXT LEVEL", font=("Arial", 10), 
                fg="#888888", bg="#1e1e1e").pack()
        self.next_blind_label = tk.Label(left_next, text="50/100", font=("Arial", 20, "bold"), 
                                        fg="#ffffff", bg="#1e1e1e")
        self.next_blind_label.pack()
        
        # Blind countdown timer
        self.blind_countdown_label = tk.Label(left_next, text="(15:00)", font=("Arial", 12), 
                                             fg="#888888", bg="#1e1e1e")
        self.blind_countdown_label.pack(pady=(2, 0))
        
        # Right - Next ante with countdown
        right_next = tk.Frame(right_frame, bg='#1e1e1e')
        right_next.pack(pady=(0, 10))
        
        tk.Label(right_next, text="NEXT LEVEL", font=("Arial", 10), 
                fg="#888888", bg="#1e1e1e").pack()
        self.next_ante_label = tk.Label(right_next, text="0", font=("Arial", 20, "bold"), 
                                       fg="#ffffff", bg="#1e1e1e")
        self.next_ante_label.pack()
        
        # Ante countdown timer (same as blinds)
        self.ante_countdown_label = tk.Label(right_next, text="(15:00)", font=("Arial", 12), 
                                            fg="#888888", bg="#1e1e1e")
        self.ante_countdown_label.pack(pady=(2, 0))
    

    
    def create_control_buttons(self, parent):
        """Create control buttons at bottom"""
        control_frame = tk.Frame(parent, bg='#1e1e1e')
        control_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Media player style buttons
        button_frame = tk.Frame(control_frame, bg='#1e1e1e')
        button_frame.pack()
        
        # Create custom styled buttons
        btn_style = {
            'font': ('Arial', 12),
            'bg': '#404040',
            'fg': '#ffffff',
            'activebackground': '#606060',
            'activeforeground': '#ffffff',
            'border': 0,
            'padx': 15,
            'pady': 8
        }
        
        # Previous level button
        tk.Button(button_frame, text="◀◀", command=self.prev_blind_level, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Start/Pause button (larger, center)
        self.start_stop_btn = tk.Button(button_frame, text="▶ START", command=self.toggle_game_timer,
                                       font=('Arial', 14, 'bold'), bg=self.config.get("accent_color", "#2196f3"), fg='#ffffff',
                                       activebackground=self.darken_color(self.config.get("accent_color", "#2196f3")), activeforeground='#ffffff',
                                       border=0, padx=20, pady=10)
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Next level button  
        tk.Button(button_frame, text="▶▶", command=self.next_blind_level, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Reset button
        tk.Button(button_frame, text="↻", command=self.reset_timers, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Settings button
        self.settings_btn = tk.Button(button_frame, text="⚙ SETTINGS", command=self.show_settings,
                                     bg='#2196f3', fg='#ffffff', font=('Arial', 10),
                                     activebackground='#1976d2', activeforeground='#ffffff',
                                     border=0, padx=15, pady=8)
        self.settings_btn.pack(side=tk.RIGHT, padx=(50, 0))
    
    def show_settings(self):
        """Show comprehensive settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg='#1e1e1e')
        settings_window.grab_set()
        
        # Main settings frame
        main_frame = tk.Frame(settings_window, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings sections
        sections_frame = tk.Frame(main_frame, bg='#1e1e1e')
        sections_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tournament section
        tournament_section = tk.LabelFrame(sections_frame, text="Tournament Settings", 
                                         fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                         font=("Arial", 12, "bold"))
        tournament_section.pack(fill=tk.X, pady=(0, 15))
        
        tournament_frame = tk.Frame(tournament_section, bg='#1e1e1e')
        tournament_frame.pack(fill=tk.X, padx=15, pady=10)
        
        btn_row1 = tk.Frame(tournament_frame, bg='#1e1e1e')
        btn_row1.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_row1, text="Edit Tournament Title", command=self.edit_title,
                 bg=self.config.get("accent_color", "#2196f3"), fg='white', 
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_row1, text="Edit Timer Settings", command=self.edit_timer_settings,
                 bg=self.config.get("accent_color", "#2196f3"), fg='white',
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_row1, text="Edit Blind Structure", command=self.edit_blinds,
                 bg=self.config.get("accent_color", "#2196f3"), fg='white',
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        
        # Appearance section  
        appearance_section = tk.LabelFrame(sections_frame, text="Appearance Settings",
                                         fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                         font=("Arial", 12, "bold"))
        appearance_section.pack(fill=tk.X, pady=(0, 15))
        
        appearance_frame = tk.Frame(appearance_section, bg='#1e1e1e')
        appearance_frame.pack(fill=tk.X, padx=15, pady=10)
        
        btn_row2 = tk.Frame(appearance_frame, bg='#1e1e1e')
        btn_row2.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_row2, text="Change Theme", command=self.change_theme,
                 bg='#4caf50', fg='white',
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(btn_row2, text="Choose Accent Color", command=self.choose_accent_color,
                 bg='#4caf50', fg='white',
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        
        # Player Management section
        players_section = tk.LabelFrame(sections_frame, text="Player Management",
                                      fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                      font=("Arial", 12, "bold"))
        players_section.pack(fill=tk.X, pady=(0, 15))
        
        players_frame = tk.Frame(players_section, bg='#1e1e1e')
        players_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Current player count
        count_label = tk.Label(players_frame, 
                             text=f"Active Players: {len(self.config.get('players', []))}", 
                             fg='white', bg='#1e1e1e', font=("Arial", 10))
        count_label.pack(anchor=tk.W, pady=(0, 10))
        
        btn_row3 = tk.Frame(players_frame, bg='#1e1e1e')
        btn_row3.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_row3, text="Add Player", command=lambda: [self.add_player(), settings_window.destroy()],
                 bg='#4caf50', fg='white',
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(btn_row3, text="Manage Players", command=lambda: [self.manage_players(), settings_window.destroy()],
                 bg='#4caf50', fg='white', 
                 font=("Arial", 10), padx=15).pack(side=tk.LEFT, padx=5)
        
        # Prize Management section
        prizes_section = tk.LabelFrame(sections_frame, text="Prize Management",
                                     fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e',
                                     font=("Arial", 12, "bold"))
        prizes_section.pack(fill=tk.X, pady=(0, 15))
        
        prizes_frame = tk.Frame(prizes_section, bg='#1e1e1e')
        prizes_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Current prize pool
        pool_label = tk.Label(prizes_frame, 
                            text=f"Prize Pool: ${self.config.get('total_prize_pool', 1000):,}", 
                            fg='white', bg='#1e1e1e', font=("Arial", 10))
        pool_label.pack(anchor=tk.W, pady=(0, 10))
        
        tk.Button(prizes_frame, text="Edit Prize Structure", command=lambda: [self.edit_prizes(), settings_window.destroy()],
                 bg='#ff9800', fg='white',
                 font=("Arial", 10), padx=15).pack(anchor=tk.W)
        
        # Close button
        close_frame = tk.Frame(main_frame, bg='#1e1e1e')
        close_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(close_frame, text="Close", command=settings_window.destroy,
                 bg='#666666', fg='white', font=("Arial", 12),
                 padx=20, pady=5).pack()
    
    def darken_color(self, color, factor=0.8):
        """Darken a hex color for hover effects"""
        if color.startswith('#'):
            color = color[1:]
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16) 
            b = int(color[4:6], 16)
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#1976d2"  # fallback color
    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def update_display(self):
        """Update timer and blinds display"""
        # Update main timer - show break timer when on break, otherwise time to next break
        if self.is_break_running:
            self.timer_label.config(text=f"{self.format_time(self.break_time_remaining)}")
            # Change header during break
            if hasattr(self, 'time_label'):
                self.time_label.config(text="TIME LEFT IN BREAK")
        else:
            self.timer_label.config(text=self.format_time(self.game_time_remaining))
            # Reset header for game time
            if hasattr(self, 'time_label'):
                self.time_label.config(text="TIME TO NEXT BREAK")
        
        # Update blinds and ante displays
        if self.current_level <= len(self.config["blinds"]):
            blind = self.config["blinds"][self.current_level - 1]
            
            # Update circular displays (text inside circles)
            if hasattr(self, 'blinds_canvas') and hasattr(self, 'blinds_text_id'):
                self.blinds_canvas.itemconfig(self.blinds_text_id, text=f"{blind['small']}/{blind['big']}")
            if hasattr(self, 'ante_canvas') and hasattr(self, 'ante_text_id'):
                self.ante_canvas.itemconfig(self.ante_text_id, text=str(blind['ante']))
            
            # Update total playing time display
            if hasattr(self, 'total_time_display'):
                self.total_time_display.config(text=self.format_time(self.total_game_time))
            
            # Update next level displays with countdown timer
            if self.current_level < len(self.config["blinds"]):
                next_blind = self.config["blinds"][self.current_level]
                self.next_blind_label.config(text=f"{next_blind['small']}/{next_blind['big']}")
                self.next_ante_label.config(text=str(next_blind['ante']))
                
                # Update countdown displays
                countdown_text = f"({self.format_time(self.blind_time_remaining)})"
                if hasattr(self, 'blind_countdown_label'):
                    self.blind_countdown_label.config(text=countdown_text)
                if hasattr(self, 'ante_countdown_label'):
                    self.ante_countdown_label.config(text=countdown_text)
            else:
                self.next_blind_label.config(text="FINAL")
                self.next_ante_label.config(text="LEVEL")
                if hasattr(self, 'blind_countdown_label'):
                    self.blind_countdown_label.config(text="")
                if hasattr(self, 'ante_countdown_label'):
                    self.ante_countdown_label.config(text="")
        
        # Update player count in active players panel
        if hasattr(self, 'players_count_label'):
            self.players_count_label.config(text=str(len(self.config.get("players", []))))
        
        # Update prize pool display
        if hasattr(self, 'prize_pool_label'):
            self.prize_pool_label.config(text=f"${self.config.get('total_prize_pool', 1000):,}")
        
        # Update button states
        if self.is_game_running:
            self.start_stop_btn.config(text="⏸ PAUSE")
        else:
            self.start_stop_btn.config(text="▶ START")
    
    def toggle_game_timer(self):
        """Toggle game timer on/off"""
        if self.is_break_running:
            self.is_break_running = False
        
        if not self.is_game_running:
            # Starting the game - reset timer if it's at 0 and set start time
            if self.game_time_remaining <= 0:
                self.game_time_remaining = self.config["game_duration"] * 60
            
            # Set game start time if not already set
            if not self.game_start_time:
                self.game_start_time = datetime.now()
        
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
        self.total_game_time = 0
        self.game_start_time = None
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
            # Always track total game time if game has started (even when paused)
            if self.game_start_time:
                self.total_game_time = int((datetime.now() - self.game_start_time).total_seconds())
            
            if self.is_game_running and self.game_time_remaining > 0:
                self.game_time_remaining -= 1
                
                # Update blind countdown timer - only when game is running (NOT during breaks)
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
                # Note: blind_time_remaining is NOT decremented during breaks
                
                if self.break_time_remaining == 0:
                    self.is_break_running = False
                    self.game_time_remaining = self.config["game_duration"] * 60
            # When paused, both game timer and blind timer stay frozen
            
            # Update display in main thread
            self.root.after_idle(self.update_display)
            time.sleep(1)
    
    def show_settings_dialog(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog - use individual buttons for now: Manage Players, Change Theme, Edit Tournament Settings, etc.")
    
    def manage_players(self):
        """Open simple player management dialog"""
        player_window = tk.Toplevel(self.root)
        player_window.title("Manage Players")
        player_window.geometry("400x300")
        player_window.configure(bg='#1e1e1e')
        
        frame = tk.Frame(player_window, bg='#1e1e1e')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Player Management", font=('Arial', 14, 'bold'), 
                fg=self.config.get("accent_color", "#2196f3"), bg='#1e1e1e').pack(pady=(0, 20))
        
        # Show current player count
        tk.Label(frame, text=f"Current players: {len(self.config.get('players', []))}", 
                fg='white', bg='#1e1e1e', font=('Arial', 12)).pack(pady=10)
        
        # Add/Remove buttons
        btn_frame = tk.Frame(frame, bg='#1e1e1e')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Add Player", command=lambda: [self.add_player(), player_window.destroy()],
                 bg=self.config.get("accent_color", "#2196f3"), fg='white', padx=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Remove Player", command=lambda: [self.remove_player(), player_window.destroy()],
                 bg='#f44336', fg='white', padx=15).pack(side=tk.LEFT, padx=10)
        
        tk.Button(frame, text="Close", command=player_window.destroy,
                 bg='#666666', fg='white', padx=20).pack(pady=20)
    
    def choose_accent_color(self):
        """Choose custom accent color"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(initialcolor=self.config.get("accent_color", "#2196f3"))[1]
            if color:
                self.config["accent_color"] = color
                self.save_config()
                messagebox.showinfo("Color Changed", "Accent color updated! Some changes may require restart.")
        except ImportError:
            messagebox.showerror("Error", "Color chooser not available.")
    
    def add_player(self):
        """Add a new player"""
        name = simpledialog.askstring("Add Player", "Enter player name:")
        if name and name.strip():
            self.config["players"].append(name.strip())
            self.populate_players()
            self.update_display()
    
    def remove_player(self):
        """Remove selected player"""
        selection = self.players_tree.selection()
        if selection:
            item = self.players_tree.item(selection[0])
            player_name = item["values"][0]
            self.config["players"].remove(player_name)
            self.populate_players()
            self.update_display()
    
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
            self.update_display()
    
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
                    self.update_display()
                    
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
        self.window.geometry("650x500")
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