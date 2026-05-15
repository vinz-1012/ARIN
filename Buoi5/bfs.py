from collections import deque

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

            # kiểm tra biên
            if 0 <= nx < 3 and 0 <= ny < 3:

                new_state = swap(current_state, zx, zy, nx, ny)

                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [current_state]))

    return None

solution = bfs(start, goal)

if solution:
    print("Answer:\n")

    for step, state in enumerate(solution):

        print(f"Bước {step}:")

        for row in state:
            print(row)

        print()

else:
    print("No answer")