import sys
import os
import heapq

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from puzzle_ui import PuzzleUI

# =========================
# GOAL STATE
# =========================
goal = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# =========================
# MOVES
# =========================
moves = {
    "L": (0, -1),
    "R": (0, 1),
    "U": (-1, 0),
    "D": (1, 0)
}


# =========================
# FIND ZERO
# =========================
def find_zero(state):

    for i in range(3):
        for j in range(3):

            if state[i][j] == 0:
                return i, j


# =========================
# CONVERT TO TUPLE
# =========================
def to_tuple(state):

    return tuple(tuple(row) for row in state)


# =========================
# PRINT STATE
# =========================
def print_state(state):

    for row in state:
        print(row)

    print()


# =========================
# MANHATTAN HEURISTIC
# =========================
def manhattan(state, goal):

    cost = 0

    for i in range(3):
        for j in range(3):

            value = state[i][j]

            if value != 0:

                for x in range(3):
                    for y in range(3):

                        if goal[x][y] == value:

                            cost += abs(i - x) + abs(j - y)

    return cost


# =========================
# EXPAND CHILDREN
# =========================
def expand(state):

    children = []

    x, y = find_zero(state)

    for action in ["L", "R", "U", "D"]:

        dx, dy = moves[action]

        nx = x + dx
        ny = y + dy

        if 0 <= nx < 3 and 0 <= ny < 3:

            new_state = [row[:] for row in state]

            new_state[x][y], new_state[nx][ny] = (
                new_state[nx][ny],
                new_state[x][y]
            )

            children.append((new_state, action))

    return children


# =========================
# GREEDY BEST FIRST SEARCH
# =========================
def greedy_search(start, goal):

    pq = []

    visited = set()

    start_h = manhattan(start, goal)

    heapq.heappush(
        pq,
        (
            start_h,
            start,
            []
        )
    )

    while pq:

        h, state, path = heapq.heappop(pq)

        print("Đang xét node với h(n) =", h)
        print_state(state)

        if state == goal:

            print("Tìm thấy goal!")
            print("Đường đi:", path)

            return path

        state_tuple = to_tuple(state)

        if state_tuple in visited:
            continue

        visited.add(state_tuple)

        for child_state, action in expand(state):

            child_tuple = to_tuple(child_state)

            if child_tuple not in visited:

                child_h = manhattan(
                    child_state,
                    goal
                )

                heapq.heappush(
                    pq,
                    (
                        child_h,
                        child_state,
                        path + [action]
                    )
                )

    return None


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    import tkinter as tk

    root = tk.Tk()

    app = PuzzleUI(
        root,
        solve_function=greedy_search
    )

    root.mainloop()