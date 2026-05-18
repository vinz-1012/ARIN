from collections import deque
import tkinter as tk
from tkinter import messagebox

start = (
    (2, 8, 3),
    (1, 6, 4),
    (7, 0, 5)   # 0 là ô trống
)

goal = (
    (1, 2, 3),
    (8, 0, 4),
    (7, 6, 5)
)

moves = [
    (-1, 0),  # lên
    (1, 0),   # xuống
    (0, -1),  # trái
    (0, 1)    # phải
]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]
    state[x1][y1], state[x2][y2] = state[x2][y2], state[x1][y1]
    return tuple(tuple(row) for row in state)

def bfs(start, goal):
    queue = deque()
    queue.append((start, []))

    visited = set()
    visited.add(start)

    while queue:
        current_state, path = queue.popleft()

        if current_state == goal:
            return path + [current_state]

        zx, zy = find_zero(current_state)

        for dx, dy in moves:
            nx, ny = zx + dx, zy + dy

            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current_state, zx, zy, nx, ny)

                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [current_state]))

    return None


class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle BFS Solver")
        self.root.geometry("500x600")
        
        self.solution = []
        self.current_step = 0
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="8-Puzzle BFS Solver", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Start state frame
        start_frame = tk.LabelFrame(self.root, text="Start State", font=("Arial", 10, "bold"))
        start_frame.pack(pady=5)
        self.start_canvas = tk.Canvas(start_frame, width=150, height=150, bg="white")
        self.start_canvas.pack(pady=5)
        self.draw_state(self.start_canvas, start)
        
        # Goal state frame
        goal_frame = tk.LabelFrame(self.root, text="Goal State", font=("Arial", 10, "bold"))
        goal_frame.pack(pady=5)
        self.goal_canvas = tk.Canvas(goal_frame, width=150, height=150, bg="white")
        self.goal_canvas.pack(pady=5)
        self.draw_state(self.goal_canvas, goal)
        
        # Current state frame
        self.current_frame = tk.LabelFrame(self.root, text="Current State", font=("Arial", 10, "bold"))
        self.current_frame.pack(pady=5)
        self.current_canvas = tk.Canvas(self.current_frame, width=150, height=150, bg="white")
        self.current_canvas.pack(pady=5)
        
        # Step info
        self.step_label = tk.Label(self.root, text="Step: 0 / 0", font=("Arial", 12))
        self.step_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        solve_button = tk.Button(button_frame, text="Solve", command=self.solve_puzzle, 
                                bg="#4CAF50", fg="white", font=("Arial", 12), width=10)
        solve_button.grid(row=0, column=0, padx=5)
        
        prev_button = tk.Button(button_frame, text="Previous", command=self.previous_step,
                               bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        prev_button.grid(row=0, column=1, padx=5)
        
        next_button = tk.Button(button_frame, text="Next", command=self.next_step,
                               bg="#2196F3", fg="white", font=("Arial", 12), width=10)
        next_button.grid(row=0, column=2, padx=5)
        
        reset_button = tk.Button(button_frame, text="Reset", command=self.reset,
                                bg="#f44336", fg="white", font=("Arial", 12), width=10)
        reset_button.grid(row=1, column=1, padx=5, pady=5)
        
    def draw_state(self, canvas, state):
        canvas.delete("all")
        cell_size = 50
        
        for i in range(3):
            for j in range(3):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                value = state[i][j]
                
                if value == 0:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray", outline="black", width=2)
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=2)
                    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, 
                                     text=str(value), font=("Arial", 20, "bold"))
    
    def solve_puzzle(self):
        self.solution = bfs(start, goal)
        
        if self.solution:
            self.current_step = 0
            self.update_display()
            messagebox.showinfo("Success", f"Solution found in {len(self.solution) - 1} steps!")
        else:
            messagebox.showerror("Error", "No solution found!")
    
    def update_display(self):
        if self.solution:
            self.draw_state(self.current_canvas, self.solution[self.current_step])
            self.step_label.config(text=f"Step: {self.current_step} / {len(self.solution) - 1}")
    
    def previous_step(self):
        if self.solution and self.current_step > 0:
            self.current_step -= 1
            self.update_display()
    
    def next_step(self):
        if self.solution and self.current_step < len(self.solution) - 1:
            self.current_step += 1
            self.update_display()
    
    def reset(self):
        self.solution = []
        self.current_step = 0
        self.current_canvas.delete("all")
        self.step_label.config(text="Step: 0 / 0")


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()