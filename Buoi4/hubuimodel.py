SIZE = 4

matrix = [
    [1, 0, 1, 1],
    [0, 1, 0, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 0]
]

# MODEL (bộ nhớ của agent)
visited = [[False] * SIZE for _ in range(SIZE)]


def print_matrix():

    for row in matrix:
        for val in row:
            print(val, end=" ")
        print()

    print()


def P_moves(x, y):

    moves = [(x, y)]

    if x < SIZE - 1:
        moves.append((x + 1, y))

    if x > 0:
        moves.append((x - 1, y))

    if y < SIZE - 1:
        moves.append((x, y + 1))

    if y > 0:
        moves.append((x, y - 1))

    return moves


def all_zero():

    for row in matrix:
        for val in row:

            if val != 0:
                return False

    return True


print("Ma trận ban đầu:")
print_matrix()

count = 0

# MODEL-BASED REFLEX AGENT
while not all_zero():

    action_done = False

    for i in range(SIZE):
        for j in range(SIZE):

            if matrix[i][j] == 1 and not visited[i][j]:

                moves = P_moves(i, j)

                for nx, ny in moves:

                    # toggle
                    if matrix[nx][ny] == 0:
                        matrix[nx][ny] = 1
                    else:
                        matrix[nx][ny] = 0

                # cập nhật MODEL
                visited[i][j] = True

                count += 1
                action_done = True

                break

        if action_done:
            break

    if not action_done:
        break


print("Ma trận cuối:")
print_matrix()

print("Số lần xử lý:", count)