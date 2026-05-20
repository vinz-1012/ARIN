from collections import deque

# Trạng thái ban đầu và goal
start = [
    [1, 2, 3],
    [4, 0, 6],
    [7, 5, 8]
]

goal = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# Thứ tự sinh node: L, R, U, D
moves = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0)
}


# Tìm vị trí số 0
def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


# Đổi ma trận sang tuple để lưu visited
def to_tuple(state):
    return tuple(tuple(row) for row in state)


# In ma trận
def print_state(state):
    for row in state:
        print(row)
    print()


# Sinh các node con
def expand(state):
    children = []

    x, y = find_zero(state)

    for action in ["L", "R", "U", "D"]:
        dx, dy = moves[action]

        nx, ny = x + dx, y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state]

            # Hoán đổi
            new_state[x][y], new_state[nx][ny] = (
                new_state[nx][ny],
                new_state[x][y]
            )

            children.append((new_state, action))

    return children


# DFS giới hạn độ sâu
def depth_limited_search(start, goal, limit):

    stack = [(start, [], 0)]  # (state, path, depth)
    visited = set()

    while stack:

        state, path, depth = stack.pop()

        print("Đang xét node ở tầng", depth)
        print_state(state)

        if state == goal:
            return path

        if depth < limit:

            visited.add(to_tuple(state))

            children = expand(state)

            # DFS dùng stack nên đảo ngược để đúng thứ tự L,R,U,D
            for child_state, action in reversed(children):

                if to_tuple(child_state) not in visited:
                    stack.append(
                        (child_state,
                         path + [action],
                         depth + 1)
                    )

    return None


# IDS - DFS theo từng tầng
def iterative_deepening_search(start, goal, max_depth):

    for depth in range(max_depth + 1):

        print("==========")
        print("DFS với giới hạn tầng =", depth)
        print("==========")

        result = depth_limited_search(start, goal, depth)

        if result is not None:
            print("Tìm thấy goal!")
            print("Đường đi:", result)
            return result

    print("Không tìm thấy")


import tkinter as tk
from tkinter import messagebox, ttk


class PuzzleUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DFS 8-Puzzle Solver")
        self.root.geometry("600x700")

        # Input frame
        input_frame = ttk.LabelFrame(root, text="Input Puzzle State", padding=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Start state input
        ttk.Label(input_frame, text="Start State (3x3, use 0 for empty):").grid(row=0, column=0, columnspan=3, pady=5)

        self.start_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                entry = ttk.Entry(input_frame, width=5)
                entry.grid(row=i+1, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.start_entries.append(row_entries)

        # Set default start state
        default_start = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].insert(0, str(default_start[i][j]))

        # Max depth input
        ttk.Label(input_frame, text="Max Depth:").grid(row=4, column=0, pady=10)
        self.depth_entry = ttk.Entry(input_frame, width=10)
        self.depth_entry.grid(row=4, column=1, pady=10)
        self.depth_entry.insert(0, "10")

        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Solve", command=self.solve).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side="left", padx=5)

        # Result frame
        result_frame = ttk.LabelFrame(root, text="Solution", padding=10)
        result_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.result_text = tk.Text(result_frame, height=15, width=60, state="disabled")
        self.result_text.pack(pady=5)

        # Step buttons
        step_frame = ttk.Frame(result_frame)
        step_frame.pack(pady=5)

        ttk.Button(step_frame, text="Previous Step", command=self.prev_step).pack(side="left", padx=5)
        ttk.Button(step_frame, text="Next Step", command=self.next_step).pack(side="left", padx=5)

        self.step_label = ttk.Label(step_frame, text="Step: 0 / 0")
        self.step_label.pack(side="left", padx=10)

        # Puzzle display
        self.puzzle_frame = ttk.LabelFrame(root, text="Current State", padding=10)
        self.puzzle_frame.pack(pady=10, padx=10, fill="x")

        self.puzzle_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                label = ttk.Label(self.puzzle_frame, text="", width=5, relief="solid", font=("Arial", 16))
                label.grid(row=i, column=j, padx=5, pady=5)
                row_labels.append(label)
            self.puzzle_labels.append(row_labels)

        self.solution_path = []
        self.current_step = 0
        self.states = []

    def get_start_state(self):
        try:
            state = []
            for i in range(3):
                row = []
                for j in range(3):
                    val = int(self.start_entries[i][j].get())
                    row.append(val)
                state.append(row)
            return state
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers (0-8)")
            return None

    def solve(self):
        start_state = self.get_start_state()
        if start_state is None:
            return

        try:
            max_depth = int(self.depth_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid depth")
            return

        # Clear previous results
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")

        # Run IDS
        result = iterative_deepening_search(start_state, goal, max_depth)

        if result:
            self.solution_path = result
            self.current_step = 0

            # Generate all states
            self.states = [start_state]
            current = start_state
            for action in result:
                x, y = find_zero(current)
                dx, dy = moves[action]
                nx, ny = x + dx, y + dy
                new_state = [row[:] for row in current]
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                self.states.append(new_state)
                current = new_state

            # Display result
            self.result_text.config(state="normal")
            self.result_text.insert(tk.END, f"Solution found!\n")
            self.result_text.insert(tk.END, f"Steps: {len(result)}\n")
            self.result_text.insert(tk.END, f"Path: {' -> '.join(result)}\n\n")
            self.result_text.config(state="disabled")

            self.step_label.config(text=f"Step: 0 / {len(self.states)-1}")
            self.update_puzzle_display(self.states[0])
        else:
            self.result_text.config(state="normal")
            self.result_text.insert(tk.END, "No solution found within the given depth limit.\n")
            self.result_text.config(state="disabled")

    def reset(self):
        default_start = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
        for i in range(3):
            for j in range(3):
                self.start_entries[i][j].delete(0, tk.END)
                self.start_entries[i][j].insert(0, str(default_start[i][j]))

        self.depth_entry.delete(0, tk.END)
        self.depth_entry.insert(0, "10")

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")

        self.solution_path = []
        self.current_step = 0
        self.states = []

        for i in range(3):
            for j in range(3):
                self.puzzle_labels[i][j].config(text="")

        self.step_label.config(text="Step: 0 / 0")

    def update_puzzle_display(self, state):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val == 0:
                    self.puzzle_labels[i][j].config(text="", background="lightgray")
                else:
                    self.puzzle_labels[i][j].config(text=str(val), background="white")

    def next_step(self):
        if self.states and self.current_step < len(self.states) - 1:
            self.current_step += 1
            self.update_puzzle_display(self.states[self.current_step])
            self.step_label.config(text=f"Step: {self.current_step} / {len(self.states)-1}")

            if self.current_step > 0:
                action = self.solution_path[self.current_step - 1]
                self.result_text.config(state="normal")
                self.result_text.insert(tk.END, f"Step {self.current_step}: Move {action}\n")
                self.result_text.config(state="disabled")

    def prev_step(self):
        if self.states and self.current_step > 0:
            self.current_step -= 1
            self.update_puzzle_display(self.states[self.current_step])
            self.step_label.config(text=f"Step: {self.current_step} / {len(self.states)-1}")


# Chạy chương trình với UI
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleUI(root)
    root.mainloop()