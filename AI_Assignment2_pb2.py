import math

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

class State:
    def __init__(self, x, y, g=0, h=0, parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
    def pos(self):
        return (self.x, self.y)

def heuristic(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def moveGen(state, n, grid):
    x, y = state.x, state.y
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 0:
            yield (nx, ny)

def reconstruct_path(state):
    path = []
    cur = state
    while cur:
        path.append(cur.pos())
        cur = cur.parent
    path.reverse()
    return path

def a_star_search(grid):
    n = len(grid)
    start, goal = (0, 0), (n-1, n-1)
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return -1, []
    start_state = State(start[0], start[1], g=0, h=heuristic(start, goal))
    open_list = [start_state]
    visited = {start: 0}
    while open_list:
        current = min(open_list, key=lambda s: s.f)
        open_list.remove(current)
        if current.pos() == goal:
            path = reconstruct_path(current)
            return len(path), path
        for nx, ny in moveGen(current, n, grid):
            new_g = current.g + 1
            new_state = State(nx, ny, g=new_g,
                              h=heuristic((nx, ny), goal),
                              parent=current)
            if (nx, ny) not in visited or new_g < visited[(nx, ny)]:
                visited[(nx, ny)] = new_g
                open_list.append(new_state)
    return -1, []

if __name__ == "__main__":
    print("Example 1:")
    grid1 = [[0,1],[1,0]]
    print("A* Search  →", a_star_search(grid1))

    print("\nExample 2:")
    grid2 = [[0,0,0],[1,1,0],[1,1,0]]
    print("A* Search  →", a_star_search(grid2))

    print("\nExample 3:")
    grid3 = [[1,0,0],[1,1,0],[1,1,0]]
    print("A* Search  →", a_star_search(grid3))
