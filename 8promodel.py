import copy

start = [
    [3, 1, 2],
    [6, 4, 5],
    [7, 8, 0]
]

goal = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# Tìm ô trống
def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

# Heuristic: số ô sai vị trí
def heuristic(state):
    count = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != goal[i][j]:
                count += 1
    return count

# Sinh trạng thái theo rule
def get_neighbors(state):
    x, y = find_zero(state)
    moves = []

    directions = [
        (-1, 0),  # up
        (1, 0),   # down
        (0, -1),  # left
        (0, 1)    # right
    ]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = copy.deepcopy(state)
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append(new_state)

    return moves

def to_tuple(state):
    return tuple(tuple(row) for row in state)

# Model-based agent
def solve(state):
    steps = 0
    visited = set()

    while state != goal:
        visited.add(to_tuple(state))

        neighbors = get_neighbors(state)

        neighbors = [n for n in neighbors if to_tuple(n) not in visited]

        if not neighbors:
            break

        best = min(neighbors, key=heuristic)

        state = best
        steps += 1

    return state, steps

result, steps = solve(start)

print("Ma trận sau khi sắp xếp:")
for row in result:
    print(row)

print("Số lần đổi chỗ:", steps)