# Start
start = (
    (2, 8, 3),
    (1, 6, 4),
    (7, 0, 5)
)

# Goal
goal = (
    (1, 2, 3),
    (8, 0, 4),
    (7, 6, 5)
)

moves = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1)
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


def dfs(state, goal, visited, path, depth_limit):

    # gặp goal
    if state == goal:
        return path + [state]

    # vượt giới hạn
    if depth_limit == 0:
        return None

    visited.add(state)

    zx, zy = find_zero(state)

    for dx, dy in moves:

        nx = zx + dx
        ny = zy + dy

        if 0 <= nx < 3 and 0 <= ny < 3:

            new_state = swap(state, zx, zy, nx, ny)

            if new_state not in visited:

                result = dfs(
                    new_state,
                    goal,
                    visited,
                    path + [state],
                    depth_limit - 1
                )

                if result:
                    return result

    return None



solution = dfs(
    start,
    goal,
    set(),
    [],
    20
)

if solution:

    print("Answer:\n")

    for step, state in enumerate(solution):

        print("Buoc", step)

        for row in state:
            print(row)

        print()

else:
    print("No answer")