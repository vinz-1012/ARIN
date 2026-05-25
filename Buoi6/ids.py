import sys
import os

# Tự động thêm thư mục chứa file hiện tại vào sys.path để đảm bảo import puzzle_ui hoạt động ổn định
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from puzzle_ui import PuzzleUI

# --- PHẦN THUẬT TOÁN (ALGORITHMS) ---

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


def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def to_tuple(state):
    return tuple(tuple(row) for row in state)


def print_state(state):
    for row in state:
        print(row)
    print()


def expand(state):
    children = []

    x, y = find_zero(state)

    for action in ["L", "R", "U", "D"]:
        dx, dy = moves[action]

        nx, ny = x + dx, y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state]

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

            # đảo ngược để đúng thứ tự L,R,U,D
            for child_state, action in reversed(children):

                if to_tuple(child_state) not in visited:
                    stack.append(
                        (child_state,
                         path + [action],
                         depth + 1)
                    )

    return None


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


# --- KHỞI CHẠY GIAO DIỆN (BOOTSTRAP UI) ---

if __name__ == "__main__":
    import tkinter as tk
    
    root = tk.Tk()
    
    # Khởi tạo Giao diện dùng chung và truyền thuật toán DFS/IDS vào làm dependency
    app = PuzzleUI(root, solve_function=iterative_deepening_search)
    
    root.mainloop()
