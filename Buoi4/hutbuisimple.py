import random

SIZE = 4

matrix = [
    [1, 0, 1, 1],
    [0, 1, 0, 0],
    [1, 1, 0, 1],
    [0, 0, 1, 0]
]

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

while not all_zero():

    # random vị trí
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)

    moves = P_moves(x, y)


    for nx, ny in moves:

        if matrix[nx][ny] == 0:
            matrix[nx][ny] = 1
        else:
            matrix[nx][ny] = 0

    count += 1


print("Ma trận sau khi xử lý:")
print_matrix()

print("Số lần random:", count)