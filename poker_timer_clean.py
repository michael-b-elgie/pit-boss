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
        
        # Apply theme
        self.setup_theme()
        
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
        else:  # classic theme
            style.theme_use("default")
    
    def setup_gui(self):
        """Setup the modern poker timer GUI"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section with circular displays and central timer
        top_frame = tk.Frame(main_frame, bg='#1e1e1e')
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left circular display - Blinds
        left_frame = tk.Frame(top_frame, bg='#1e1e1e')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_circular_display(left_frame, "BLINDS", "25/50", "#2196f3")
        
        # Center section - Main timer and controls  
        center_frame = tk.Frame(top_frame, bg='#1e1e1e')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)
        
        # TIME REMAINING label
        time_label = tk.Label(center_frame, text="TIME REMAINING", 
                             font=("Arial", 12), fg="#888888", bg="#1e1e1e")
        time_label.pack(pady=(50, 10))
        
        # Main timer display
        self.timer_label = tk.Label(center_frame, text="20:00", 
                                   font=("Arial", 64, "bold"), fg="#2196f3", bg="#1e1e1e")
        self.timer_label.pack(pady=10)
        
        # Break countdown timer
        self.blind_timer_label = tk.Label(center_frame, text="15:00", 
                                         font=("Arial", 20), fg="#ffffff", bg="#1e1e1e")
        self.blind_timer_label.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(center_frame, text="UNTIL NEXT BREAK", 
                                   font=("Arial", 10), fg="#888888", bg="#1e1e1e")
        self.status_label.pack(pady=(0, 30))
        
        # Tournament logo/title area
        if self.config.get("tournament_title") != "Pit Boss - Poker Timer":
            title_label = tk.Label(center_frame, text=self.config.get("tournament_title", "POKER"), 
                                 font=("Arial", 16, "bold"), fg="#2196f3", bg="#1e1e1e")
            title_label.pack(pady=10)
        else:
            logo_label = tk.Label(center_frame, text="PIT BOSS", 
                                 font=("Arial", 16, "bold"), fg="#2196f3", bg="#1e1e1e")
            logo_label.pack(pady=10)
        
        # Right circular display - Ante
        right_frame = tk.Frame(top_frame, bg='#1e1e1e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_circular_display(right_frame, "ANTE", "0", "#2196f3")
        
        # Next level displays under circles
        self.create_next_level_displays(left_frame, right_frame)
        
        # Bottom statistics bar
        self.create_stats_bar(main_frame)
        
        # Control buttons at bottom
        self.create_control_buttons(main_frame)
        
        # Load initial data
        self.update_display()
    
    def create_circular_display(self, parent, label, value, color):
        """Create a circular display for blinds/ante"""
        container = tk.Frame(parent, bg='#1e1e1e')
        container.pack(expand=True, pady=50)
        
        # Create circular canvas
        canvas = tk.Canvas(container, width=150, height=150, bg='#1e1e1e', highlightthickness=0)
        canvas.pack()
        
        # Draw circle
        canvas.create_oval(10, 10, 140, 140, outline=color, width=3, fill='#2a2a2a')
        
        # Label text
        label_widget = tk.Label(container, text=label, font=("Arial", 10), 
                               fg="#888888", bg="#1e1e1e")
        label_widget.pack(pady=(10, 0))
        
        # Value text (store reference for updates)
        if label == "BLINDS":
            self.blinds_display = tk.Label(container, text=value, font=("Arial", 32, "bold"), 
                                          fg="#ffffff", bg="#1e1e1e")
            self.blinds_display.pack()
            self.blinds_canvas = canvas
        else:  # ANTE
            self.ante_display = tk.Label(container, text=value, font=("Arial", 32, "bold"), 
                                        fg="#ffffff", bg="#1e1e1e")
            self.ante_display.pack()
            self.ante_canvas = canvas
    
    def create_next_level_displays(self, left_frame, right_frame):
        """Create next level displays under the circular displays"""
        # Left - Next blinds
        left_next = tk.Frame(left_frame, bg='#1e1e1e')
        left_next.pack(pady=(0, 20))
        
        tk.Label(left_next, text="NEXT LEVEL", font=("Arial", 10), 
                fg="#888888", bg="#1e1e1e").pack()
        self.next_blind_label = tk.Label(left_next, text="50/100", font=("Arial", 24, "bold"), 
                                        fg="#ffffff", bg="#1e1e1e")
        self.next_blind_label.pack()
        
        # Right - Next ante
        right_next = tk.Frame(right_frame, bg='#1e1e1e')
        right_next.pack(pady=(0, 20))
        
        tk.Label(right_next, text="NEXT LEVEL", font=("Arial", 10), 
                fg="#888888", bg="#1e1e1e").pack()
        self.next_ante_label = tk.Label(right_next, text="0", font=("Arial", 24, "bold"), 
                                       fg="#ffffff", bg="#1e1e1e")
        self.next_ante_label.pack()
    
    def create_stats_bar(self, parent):
        """Create bottom statistics bar"""
        stats_frame = tk.Frame(parent, bg='#1e1e1e')
        stats_frame.pack(fill=tk.X, pady=(20, 10))
        
        # Create stat items
        stats = [
            ("PLAYERS LEFT", "players_count", lambda: str(len(self.config.get("players", [])))),
            ("BUY-INS", "buy_ins", lambda: str(len(self.config.get("players", [])))),
            ("ADD-ONS", "add_ons", lambda: "0"),
            ("AVG STACK", "avg_stack", lambda: "15000"),
            ("TOTAL CHIPS", "total_chips", lambda: str(self.config.get("total_prize_pool", 200000)))
        ]
        
        for i, (label, attr, value_func) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg='#1e1e1e')
            stat_frame.pack(side=tk.LEFT, expand=True, padx=10)
            
            tk.Label(stat_frame, text=label, font=("Arial", 8), 
                    fg="#888888", bg="#1e1e1e").pack()
            
            value_label = tk.Label(stat_frame, text=value_func(), font=("Arial", 16, "bold"), 
                                  fg="#ffffff", bg="#1e1e1e")
            value_label.pack()
            
            # Store reference for updates
            setattr(self, f"{attr}_label", value_label)
    
    def create_control_buttons(self, parent):
        """Create control buttons at bottom"""
        control_frame = tk.Frame(parent, bg='#1e1e1e')
        control_frame.pack(fill=tk.X, pady=10)
        
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
            'relief': 'flat',
            'padx': 15,
            'pady': 8
        }
        
        # Previous level button
        tk.Button(button_frame, text="◀◀", command=self.prev_blind_level, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Start/Pause button (larger, center)
        self.start_stop_btn = tk.Button(button_frame, text="▶ START", command=self.toggle_game_timer,
                                       font=('Arial', 14, 'bold'), bg='#2196f3', fg='#ffffff',
                                       activebackground='#1976d2', activeforeground='#ffffff',
                                       relief='flat', padx=20, pady=10)
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Next level button  
        tk.Button(button_frame, text="▶▶", command=self.next_blind_level, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Reset button
        tk.Button(button_frame, text="↻", command=self.reset_timers, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Settings button
        self.settings_btn = tk.Button(button_frame, text="⚙ SETTINGS", command=self.show_settings,
                                     bg='#2196f3', fg='#ffffff', font=('Arial', 10),
                                     activebackground='#1976d2', activeforeground='#ffffff',
                                     relief='flat', padx=15, pady=8)
        self.settings_btn.pack(side=tk.RIGHT, padx=(50, 0))
    
    def show_settings(self):
        """Show simplified settings menu"""
        messagebox.showinfo("Settings", "Settings functionality coming soon!")
    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        minutes, secs = divmod(int(seconds), 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def update_display(self):
        """Update timer and blinds display"""
        # Update main timer
        if self.is_break_running:
            self.timer_label.config(text=f"{self.format_time(self.break_time_remaining)}")
            self.status_label.config(text="UNTIL BREAK ENDS")
        else:
            self.timer_label.config(text=self.format_time(self.game_time_remaining))
            if self.is_game_running:
                self.status_label.config(text="UNTIL NEXT BREAK")
            else:
                self.status_label.config(text="GAME PAUSED")
        
        # Update blinds and ante displays
        if self.current_level <= len(self.config["blinds"]):
            blind = self.config["blinds"][self.current_level - 1]
            
            # Update circular displays
            self.blinds_display.config(text=f"{blind['small']}/{blind['big']}")
            self.ante_display.config(text=str(blind['ante']))
            
            # Update blind countdown timer
            self.blind_timer_label.config(text=f"{self.format_time(self.blind_time_remaining)}")
            
            # Update next level displays
            if self.current_level < len(self.config["blinds"]):
                next_blind = self.config["blinds"][self.current_level]
                self.next_blind_label.config(text=f"{next_blind['small']}/{next_blind['big']}")
                self.next_ante_label.config(text=str(next_blind['ante']))
            else:
                self.next_blind_label.config(text="FINAL")
                self.next_ante_label.config(text="LEVEL")
        
        # Update statistics bar
        if hasattr(self, 'players_count_label'):
            self.players_count_label.config(text=str(len(self.config.get("players", []))))
        if hasattr(self, 'buy_ins_label'):
            self.buy_ins_label.config(text=str(len(self.config.get("players", []))))
        if hasattr(self, 'total_chips_label'):
            self.total_chips_label.config(text=str(self.config.get("total_prize_pool", 200000)))
        
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
            # Starting the game - reset timer if it's at 0
            if self.game_time_remaining <= 0:
                self.game_time_remaining = self.config["game_duration"] * 60
        
        self.is_game_running = not self.is_game_running
        self.update_display()
    
    def reset_timers(self):
        """Reset all timers"""
        self.is_game_running = False
        self.is_break_running = False
        self.game_time_remaining = self.config["game_duration"] * 60
        self.break_time_remaining = self.config["break_duration"] * 60
        self.last_blind_increase = datetime.now()
        self.blind_time_remaining = self.config["blind_increase_interval"] * 60
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
    
    def auto_save(self):
        """Periodically save configuration"""
        self.save_config()
        self.root.after(30000, self.auto_save)  # Save every 30 seconds


def main():
    root = tk.Tk()
    app = PokerTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()