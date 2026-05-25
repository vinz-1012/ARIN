import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import queue
import sys
import os

# Standard 8-puzzle configurations
goal = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

moves = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0)
}

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

# Modern Theme Colors (Nord Dark Theme)
BG_MAIN = "#1E1E2E"
BG_CARD = "#252538"
BG_INNER = "#181825"
COLOR_ACCENT = "#89B4FA"      # Pastel Lavender Blue
COLOR_ACCENT_HOVER = "#A6ADC8"# Soft Gray Blue
COLOR_SUCCESS = "#A6E3A1"     # Sage Green
COLOR_WARNING = "#F9E2AF"     # Soft Yellow
COLOR_ERROR = "#F38BA8"       # Soft Red
COLOR_TEXT = "#CDD6F4"        # Off-white
COLOR_MUTED = "#7F849C"       # Muted cool gray
COLOR_TILE_BG = "#313244"     # Dark Slate for standard tiles
COLOR_BORDER = "#45475A"      # Slate gray border
COLOR_TEXT_DARK = "#11111B"   # Deepest dark

class PuzzleUI:
    def __init__(self, root, solve_function, goal_state=None, moves_map=None):
        self.root = root
        self.solve_function = solve_function
        
        # Override goals and moves if supplied dynamically
        self.goal = goal_state if goal_state is not None else goal
        self.moves = moves_map if moves_map is not None else moves

        self.root.title("8-Puzzle Generic Visual Solver")
        self.root.geometry("1000x680")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)

        # Apply global option styles
        self.root.option_add("*Font", ("Segoe UI", 10))

        # Internal State variables
        self.solution_path = []
        self.current_step = 0
        self.states = []
        self.is_playing = False
        self.solving_active = False
        self.log_queue = queue.Queue()

        self.setup_ui_layout()
        self.load_preset("medium") # Default preset
        self.check_log_queue()

    def setup_ui_layout(self):
        # 1. Main Container
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 2. Left Column: Control Panel (width = 300)
        left_panel = tk.Frame(main_container, bg=BG_CARD, width=300, bd=0)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        # Header Title
        title_label = tk.Label(left_panel, text="8-PUZZLE SOLVER", font=("Segoe UI", 16, "bold"), fg=COLOR_ACCENT, bg=BG_CARD)
        title_label.pack(pady=(20, 5))
        subtitle_label = tk.Label(left_panel, text="Generic Visualizer Dashboard", font=("Segoe UI", 9, "italic"), fg=COLOR_MUTED, bg=BG_CARD)
        subtitle_label.pack(pady=(0, 20))

        # Section: Puzzle Presets
        preset_frame = tk.LabelFrame(left_panel, text=" Cấu hình sẵn (Presets) ", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=BG_CARD, bd=1, relief="solid")
        preset_frame.pack(fill="x", padx=15, pady=10)
        
        btn_preset_easy = self.create_flat_btn(preset_frame, "Dễ", lambda: self.load_preset("easy"), COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        btn_preset_easy.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        btn_preset_med = self.create_flat_btn(preset_frame, "Vừa", lambda: self.load_preset("medium"), COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        btn_preset_med.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        btn_preset_hard = self.create_flat_btn(preset_frame, "Khó", lambda: self.load_preset("hard"), COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        btn_preset_hard.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        btn_preset_unsolvable = self.create_flat_btn(preset_frame, "Lỗi", lambda: self.load_preset("unsolvable"), COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        btn_preset_unsolvable.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        
        preset_frame.columnconfigure((0, 1, 2, 3), weight=1)

        # Section: Manual Input
        input_section = tk.LabelFrame(left_panel, text=" Trạng thái bắt đầu (Start State) ", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=BG_CARD, bd=1, relief="solid")
        input_section.pack(fill="x", padx=15, pady=10)

        # Label inside Manual Input
        info_label = tk.Label(input_section, text="Nhập số từ 0-8 (0 là ô trống)\nHoặc nhấp chuột trên bảng để di chuyển", font=("Segoe UI", 8), fg=COLOR_MUTED, bg=BG_CARD, justify="center")
        info_label.pack(pady=(5, 10))

        # Lưới 3x3 Entry
        grid_container = tk.Frame(input_section, bg=BG_CARD)
        grid_container.pack(pady=(0, 10))

        self.start_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = tk.Entry(
                    grid_container,
                    width=3,
                    font=("Segoe UI", 12, "bold"),
                    bg=BG_INNER,
                    fg=COLOR_TEXT,
                    bd=0,
                    insertbackground=COLOR_ACCENT,
                    justify="center",
                    highlightthickness=1,
                    highlightbackground=COLOR_BORDER,
                    highlightcolor=COLOR_ACCENT
                )
                entry.grid(row=i, column=j, padx=4, pady=4)
                # Event to update board instantly on entry change
                entry.bind("<KeyRelease>", lambda e: self.sync_board_from_entries())
                row_entries.append(entry)
            self.start_entries.append(row_entries)



        # Action: Solve Button (Large primary button)
        self.solve_btn = self.create_flat_btn(left_panel, "GIẢI CÂU ĐỐ (SOLVE)", self.start_solve_thread, COLOR_ACCENT, COLOR_TEXT_DARK, COLOR_ACCENT_HOVER, font=("Segoe UI", 10, "bold"))
        self.solve_btn.pack(fill="x", padx=15, pady=(20, 10))

        # Bottom Muted Tips
        tips_lbl = tk.Label(left_panel, text="* Mẹo: Click trực tiếp vào các ô liền kề\nô trống trên bảng để hoán đổi thủ công.", font=("Segoe UI", 8, "italic"), fg=COLOR_MUTED, bg=BG_CARD, justify="left")
        tips_lbl.pack(side="bottom", pady=15, padx=15)


        # 3. Center Column: Interactive Visual Board (width = 380)
        center_panel = tk.Frame(main_container, bg=BG_MAIN, width=380)
        center_panel.pack(side="left", fill="both", expand=True, padx=10)
        center_panel.pack_propagate(False)

        # Visual board state label
        self.status_title = tk.Label(center_panel, text="Trạng thái: Sẵn sàng", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT, bg=BG_MAIN)
        self.status_title.pack(pady=(10, 5))

        # Canvas Board Container (has dark background padding)
        canvas_bg = tk.Frame(center_panel, bg=BG_INNER, padx=10, pady=10, bd=0)
        canvas_bg.pack(pady=10)

        # Interactive Board Canvas
        self.canvas = tk.Canvas(canvas_bg, width=360, height=360, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Playback Controls Frame
        playback_frame = tk.Frame(center_panel, bg=BG_MAIN)
        playback_frame.pack(fill="x", pady=10)

        self.prev_btn = self.create_flat_btn(playback_frame, "◀ Trở lại", self.prev_step, COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        self.prev_btn.pack(side="left", expand=True, fill="x", padx=3)

        self.play_btn = self.create_flat_btn(playback_frame, "Tự động (Auto)", self.toggle_auto_play, COLOR_ACCENT, COLOR_TEXT_DARK, COLOR_ACCENT_HOVER)
        self.play_btn.pack(side="left", expand=True, fill="x", padx=3)

        self.next_btn = self.create_flat_btn(playback_frame, "Tiếp tục ▶", lambda: self.next_step(), COLOR_BORDER, COLOR_TEXT, COLOR_TILE_BG)
        self.next_btn.pack(side="left", expand=True, fill="x", padx=3)

        # Step index count indicator
        self.step_label = tk.Label(center_panel, text="Bước: 0 / 0", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=BG_MAIN)
        self.step_label.pack(pady=5)

        # Speed slider control
        speed_frame = tk.Frame(center_panel, bg=BG_MAIN)
        speed_frame.pack(fill="x", pady=5)
        
        speed_lbl = tk.Label(speed_frame, text="Tốc độ tự động (ms):", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=BG_MAIN)
        speed_lbl.pack(side="left", padx=(10, 10))
        
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=200,
            to=2000,
            orient="horizontal",
            bg=BG_MAIN,
            fg=COLOR_TEXT,
            troughcolor=BG_INNER,
            activebackground=COLOR_ACCENT,
            highlightthickness=0,
            bd=0,
            resolution=100
        )
        self.speed_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.speed_scale.set(600) # Default autoplay interval: 600ms


        # 4. Right Column: Solved Stats & Log Console (width = 280)
        right_panel = tk.Frame(main_container, bg=BG_CARD, width=280)
        right_panel.pack(side="left", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        # Section Title
        stats_title_lbl = tk.Label(right_panel, text="THÔNG SỐ & TIẾN TRÌNH", font=("Segoe UI", 11, "bold"), fg=COLOR_ACCENT, bg=BG_CARD)
        stats_title_lbl.pack(pady=(20, 15))

        # Stats Cards container
        stats_grid = tk.Frame(right_panel, bg=BG_CARD)
        stats_grid.pack(fill="x", padx=15, pady=5)

        # Time metric
        tk.Label(stats_grid, text="Thời gian giải:", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=BG_CARD).grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_stat_time = tk.Label(stats_grid, text="-", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=BG_CARD)
        self.lbl_stat_time.grid(row=0, column=1, sticky="e", pady=4)

        # Total moves
        tk.Label(stats_grid, text="Tổng số bước đi:", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=BG_CARD).grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_stat_steps = tk.Label(stats_grid, text="-", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=BG_CARD)
        self.lbl_stat_steps.grid(row=1, column=1, sticky="e", pady=4)

        # Total expanded nodes (based on states generated)
        tk.Label(stats_grid, text="Tổng số nút xét:", font=("Segoe UI", 9), fg=COLOR_MUTED, bg=BG_CARD).grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_stat_nodes = tk.Label(stats_grid, text="-", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT, bg=BG_CARD)
        self.lbl_stat_nodes.grid(row=2, column=1, sticky="e", pady=4)
        
        stats_grid.columnconfigure(1, weight=1)

        # Separation line
        sep = tk.Frame(right_panel, height=1, bg=COLOR_BORDER)
        sep.pack(fill="x", padx=15, pady=15)

        # Log box label
        log_lbl = tk.Label(right_panel, text="Nhật ký tìm kiếm :", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT, bg=BG_CARD)
        log_lbl.pack(anchor="w", padx=15, pady=(0, 5))

        # Log Text Box
        self.log_text = tk.Text(
            right_panel,
            bg=BG_INNER,
            fg=COLOR_TEXT,
            font=("Consolas", 8),
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_ACCENT,
            state="disabled",
            padx=5,
            pady=5
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Attach custom scrollbar to log box
        scrollbar = ttk.Scrollbar(self.log_text, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.stats_labels = {
            "time": self.lbl_stat_time,
            "steps": self.lbl_stat_steps,
            "nodes": self.lbl_stat_nodes
        }

    # Helper method to create Flat hoverable button
    def create_flat_btn(self, parent, text, command, bg_color, fg_color, hover_bg, font=("Segoe UI", 9, "bold")):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_bg,
            activeforeground=fg_color,
            font=font,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6
        )
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg_color))
        return btn

    # Load predefined puzzle states
    def load_preset(self, difficulty):
        self.reset_playback_data()
        
        presets = {
            "easy": [[1, 2, 3], [4, 5, 6], [7, 0, 8]],
            "medium": [[1, 2, 3], [4, 0, 6], [7, 5, 8]],
            "hard": [[0, 1, 3], [4, 2, 5], [7, 8, 6]],
            "unsolvable": [[1, 2, 3], [4, 5, 6], [8, 7, 0]]
        }
        
        state = presets.get(difficulty, presets["medium"])
        self.update_entries_from_state(state)
        self.draw_board_state(state)
        self.update_status(f"Preset '{difficulty.upper()}' loaded", COLOR_MUTED)

    # Sync grid visualizer when modifying entry boxes
    def sync_board_from_entries(self):
        state = self.get_start_state(show_error=False)
        if state is not None:
            self.draw_board_state(state)
            self.reset_playback_data()

    def update_entries_from_state(self, state):
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].delete(0, tk.END)
                self.start_entries[i][j].insert(0, str(state[i][j]))

    def get_start_state(self, show_error=True):
        try:
            state = []
            vals = set()
            for i in range(3):
                row = []
                for j in range(3):
                    val_str = self.start_entries[i][j].get().strip()
                    if not val_str:
                        return None # Incomplete entry
                    val = int(val_str)
                    if val < 0 or val > 8:
                        raise ValueError
                    vals.add(val)
                    row.append(val)
                state.append(row)
            if len(vals) != 9:
                if show_error:
                    messagebox.showerror("Lỗi dữ liệu", "Lưới bắt buộc phải chứa các số duy nhất từ 0 đến 8.")
                return None
            return state
        except ValueError:
            if show_error:
                messagebox.showerror("Lỗi nhập liệu", "Vui lòng chỉ nhập các chữ số hợp lệ từ 0 đến 8!")
            return None

    def reset_playback_data(self):
        self.solution_path = []
        self.states = []
        self.current_step = 0
        self.is_playing = False
        self.play_btn.configure(text="Tự động (Auto)", bg=COLOR_ACCENT, fg=COLOR_TEXT_DARK)
        self.step_label.config(text="Bước: 0 / 0")
        self.stats_labels["time"].config(text="-")
        self.stats_labels["steps"].config(text="-")
        self.stats_labels["nodes"].config(text="-")

    def update_status(self, text, color=COLOR_TEXT):
        self.status_title.config(text=f"Trạng thái: {text}", fg=color)

    def set_buttons_state(self, state):
        # Disable/enable UI interactions during background solver runs
        self.solve_btn.configure(state=state)
        if state == "disabled":
            self.solving_active = True
            self.solve_btn.configure(bg=COLOR_BORDER)
        else:
            self.solving_active = False
            self.solve_btn.configure(bg=COLOR_ACCENT)

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")

    # Render a static state representation
    def draw_board_state(self, state):
        self.canvas.delete("all")
        for r in range(3):
            for c in range(3):
                val = state[r][c]
                if val != 0:
                    self.draw_single_tile(c * 120, r * 120, val)
                else:
                    # Void empty space render
                    self.canvas.create_rectangle(c * 120 + 8, r * 120 + 8, (c + 1) * 120 - 8, (r + 1) * 120 - 8, fill=BG_INNER, outline=COLOR_BORDER, width=1)

    # Render single gorgeous flat tile with subtle border and drop shadow
    def draw_single_tile(self, x, y, val):
        # 3D Drop Shadow offset
        self.canvas.create_rectangle(x + 10, y + 10, x + 114, y + 114, fill="#11111B", outline="")

        # Highlight cell if it rests in correct goal coordinate
        correct_r = (val - 1) // 3
        correct_c = (val - 1) % 3
        
        # Calculate cell coordinates
        cell_c = int(round(x / 120))
        cell_r = int(round(y / 120))
        
        if cell_r == correct_r and cell_c == correct_c:
            tile_bg = COLOR_SUCCESS
            text_fg = COLOR_TEXT_DARK
            border_col = ""
        else:
            tile_bg = COLOR_TILE_BG
            text_fg = COLOR_TEXT
            border_col = COLOR_BORDER

        # Draw main tile rectangle
        self.canvas.create_rectangle(
            x + 6, y + 6, x + 110, y + 110,
            fill=tile_bg,
            outline=border_col,
            width=1 if border_col else 0
        )
        
        # Draw number text
        self.canvas.create_text(
            x + 58, y + 58,
            text=str(val),
            fill=text_fg,
            font=("Segoe UI", 32, "bold")
        )

    # Core Slide Interpolation Animation Method
    def animate_transition(self, state_from, state_to, callback=None):
        x_from, y_from = -1, -1
        x_to, y_to = -1, -1
        moved_val = -1
        
        for r in range(3):
            for c in range(3):
                # The tile that moved is non-zero in from_state and zero in to_state
                if state_from[r][c] != 0 and state_to[r][c] == 0:
                    x_from, y_from = c, r
                    moved_val = state_from[r][c]
                # It slides to the zero slot
                if state_from[r][c] == 0 and state_to[r][c] != 0:
                    x_to, y_to = c, r
                    
        if moved_val == -1:
            # Fallback if no clean single move is discovered
            self.draw_board_state(state_to)
            if callback: callback()
            return

        # Frame interpolation
        frames = 8
        delay_ms = 12
        
        start_x = x_from * 120
        start_y = y_from * 120
        end_x = x_to * 120
        end_y = y_to * 120
        
        def render_frame(idx):
            if idx > frames:
                # Finished animation
                self.draw_board_state(state_to)
                if callback: callback()
                return
                
            t = idx / frames
            # Ease-out interpolation formula
            ease_t = 1 - (1 - t) * (1 - t) 
            
            curr_x = start_x + (end_x - start_x) * ease_t
            curr_y = start_y + (end_y - start_y) * ease_t
            
            self.canvas.delete("all")
            
            # Render all cells statically EXCEPT the transition slot
            for r in range(3):
                for c in range(3):
                    if (r == y_from and c == x_from) or (r == y_to and c == x_to):
                        # Empty slot representation
                        self.canvas.create_rectangle(c * 120 + 8, r * 120 + 8, (c + 1) * 120 - 8, (r + 1) * 120 - 8, fill=BG_INNER, outline=COLOR_BORDER, width=1)
                    else:
                        val = state_from[r][c]
                        if val != 0:
                            self.draw_single_tile(c * 120, r * 120, val)
                            
            # Render the moving tile on top of everything!
            self.draw_single_tile(curr_x, curr_y, moved_val)
            self.root.after(delay_ms, lambda: render_frame(idx + 1))
            
        render_frame(0)

    # Click Board Tile to Scramble manually
    def on_canvas_click(self, event):
        if self.is_playing or self.solving_active:
            return
            
        col = event.x // 120
        row = event.y // 120
        
        if 0 <= col < 3 and 0 <= row < 3:
            start_state = self.get_start_state(show_error=False)
            if start_state is None:
                return
                
            zero_r, zero_c = find_zero(start_state)
            
            # Verify clicking tile is adjacent to empty tile
            if abs(col - zero_c) + abs(row - zero_r) == 1:
                new_state = [r[:] for r in start_state]
                new_state[zero_r][zero_c], new_state[row][col] = new_state[row][col], new_state[zero_r][zero_c]
                
                # Perform responsive swap animation
                self.animate_transition(start_state, new_state)
                self.update_entries_from_state(new_state)
                self.reset_playback_data()
                self.update_status("Bảng được chỉnh sửa thủ công", COLOR_MUTED)

    # Background solving thread launch
    def start_solve_thread(self):
        if self.solving_active:
            return
            
        start_state = self.get_start_state()
        if start_state is None:
            return


        self.set_buttons_state("disabled")
        self.clear_logs()
        self.update_status("Đang giải câu đố...", COLOR_WARNING)
        
        # Reset stats labels
        self.stats_labels["time"].config(text="-")
        self.stats_labels["steps"].config(text="-")
        self.stats_labels["nodes"].config(text="-")
        
        # Start thread
        self.solve_start_time = time.time()
        self.log_queue = queue.Queue()
        
        t = threading.Thread(target=self.run_solver, args=(start_state,))
        t.daemon = True
        t.start()

    # Redirect logs and run algorithm
    def run_solver(self, start_state):
        class StdoutRedirector:
            def __init__(self, log_q):
                self.log_q = log_q
            def write(self, s):
                self.log_q.put(s)
            def flush(self):
                pass
                
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.log_queue)
        
        try:
            result = self.solve_function(start_state, self.goal)
        except Exception as e:
            self.log_queue.put(f"\n[LỖI THUẬT TOÁN]: {str(e)}\n")
            result = None
        finally:
            sys.stdout = old_stdout
            
        elapsed = (time.time() - self.solve_start_time) * 1000  # ms
        self.root.after(0, lambda: self.on_solver_complete(result, elapsed, start_state))

    def on_solver_complete(self, result, elapsed_time, start_state):
        self.set_buttons_state("normal")
        self.stats_labels["time"].config(text=f"{elapsed_time:.1f} ms")
        
        if result is not None:
            self.update_status("Tìm thấy lời giải!", COLOR_SUCCESS)
            self.solution_path = result
            self.current_step = 0
            
            # Pre-compute all states along solution path
            self.states = [start_state]
            curr = start_state
            for action in result:
                x, y = find_zero(curr)
                dx, dy = self.moves[action]
                nx, ny = x + dx, y + dy
                new_state = [row[:] for row in curr]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                self.states.append(new_state)
                curr = new_state
                
            self.stats_labels["steps"].config(text=str(len(result)))
            self.stats_labels["nodes"].config(text=str(len(self.states)))
            self.step_label.config(text=f"Bước: 0 / {len(self.states)-1}")
            
            self.draw_board_state(start_state)
        else:
            self.update_status("Không tìm thấy lời giải!", COLOR_ERROR)
            self.solution_path = []
            self.states = []
            self.current_step = 0
            self.stats_labels["steps"].config(text="N/A")
            self.stats_labels["nodes"].config(text="-")
            self.step_label.config(text="Bước: 0 / 0")
            messagebox.showinfo("Thông báo", "Không tìm thấy lời giải!")

    # Periodically poll background logs and dump to logs UI box
    def check_log_queue(self):
        try:
            while True:
                text = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert(tk.END, text)
                self.log_text.see(tk.END)
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(30, self.check_log_queue)

    def next_step(self, callback=None):
        if self.states and self.current_step < len(self.states) - 1:
            old_state = self.states[self.current_step]
            self.current_step += 1
            new_state = self.states[self.current_step]
            
            self.step_label.config(text=f"Bước: {self.current_step} / {len(self.states)-1}")
            
            # Log transition
            act = self.solution_path[self.current_step - 1]
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, f"▶ Bước {self.current_step}: Di chuyển ô trống sang [{act}]\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
            
            self.animate_transition(old_state, new_state, callback)
        else:
            if callback: callback()

    def prev_step(self):
        if self.states and self.current_step > 0:
            old_state = self.states[self.current_step]
            self.current_step -= 1
            new_state = self.states[self.current_step]
            
            self.step_label.config(text=f"Bước: {self.current_step} / {len(self.states)-1}")
            
            # Log transition
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, f"◀ Quay lại Bước {self.current_step}\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
            
            self.animate_transition(old_state, new_state)

    # Toggle Auto Play loop state
    def toggle_auto_play(self):
        if not self.states:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhấp nút Giải câu đố trước!")
            return
            
        if self.is_playing:
            self.is_playing = False
            self.play_btn.configure(text="Tự động (Auto)", bg=COLOR_ACCENT, fg=COLOR_TEXT_DARK)
            self.update_status("Đang tạm dừng tự động", COLOR_WARNING)
        else:
            self.is_playing = True
            self.play_btn.configure(text="Tạm dừng (Pause)", bg=COLOR_WARNING, fg=COLOR_TEXT_DARK)
            self.update_status("Đang phát tự động...", COLOR_SUCCESS)
            self.auto_play_loop()

    # Recursive autoplay state loop
    def auto_play_loop(self):
        if not self.is_playing:
            return
            
        if self.current_step < len(self.states) - 1:
            interval = int(self.speed_scale.get())
            self.next_step(callback=lambda: self.root.after(interval, self.auto_play_loop))
        else:
            self.is_playing = False
            self.play_btn.configure(text="Tự động (Auto)", bg=COLOR_ACCENT, fg=COLOR_TEXT_DARK)
            self.update_status("Hoàn thành trình diễn!", COLOR_SUCCESS)
