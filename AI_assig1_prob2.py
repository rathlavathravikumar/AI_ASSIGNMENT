import copy

class State:
    def __init__(self, people, torch_side, cost):
        self.people = people
        self.torch_side = torch_side
        self.cost = cost

    def is_goal(self):
        return all(p[1] == 'r' for p in self.people) and self.cost <= 65

    def gen_moves(self):
        children = []
        if self.torch_side == 'l':
            left_indices = [i for i, p in enumerate(self.people) if p[1] == 'l']
            for i in range(len(left_indices)):
                for j in range(i + 1, len(left_indices)):
                    a = left_indices[i]
                    b = left_indices[j]
                    new_people = copy.deepcopy(self.people)
                    new_people[a][1] = 'r'
                    new_people[b][1] = 'r'
                    crossing_time = max(self.people[a][2], self.people[b][2])
                    children.append(State(new_people, 'r', self.cost + crossing_time))
        else:
            right_indices = [i for i, p in enumerate(self.people) if p[1] == 'r']
            for i in right_indices:
                new_people = copy.deepcopy(self.people)
                new_people[i][1] = 'l'
                crossing_time = self.people[i][2]
                children.append(State(new_people, 'l', self.cost + crossing_time))
        return children

    def remove_seen(self, open_list, closed_list, children):
        open_nodes = [n for n, _ in open_list]
        closed_nodes = [n for n, _ in closed_list]
        return [c for c in children if c not in open_nodes and c not in closed_nodes]

    def reconstruct_path(self, closed, goal_node_pair):
        path = []
        parent_map = {}
        for node, parent in closed:
            parent_map[node] = parent
        node = goal_node_pair[0]
        while node:
            path.append(node)
            node = parent_map.get(node)
        path.reverse()
        return path

    def bfs(self):
        open_list = [(self, None)]
        closed = []
        while open_list:
            current_node, parent = open_list.pop(0)
            if current_node.is_goal():
                path = self.reconstruct_path(closed, (current_node, parent))
                return path, current_node.cost
            closed.append((current_node, parent))
            children = current_node.gen_moves()
            unseen = self.remove_seen(open_list, closed, children)
            open_list.extend((child, current_node) for child in unseen)
        return [], -1

    def __eq__(self, other):
        return self.torch_side == other.torch_side and all(p1 == p2 for p1, p2 in zip(self.people, other.people))

    def __hash__(self):
        return hash((tuple(tuple(p) for p in self.people), self.torch_side))

    def __str__(self):
        left = [p[0] for p in self.people if p[1] == 'l']
        right = [p[0] for p in self.people if p[1] == 'r']
        return f"Left: {left}, Right: {right}, Torch at: {self.torch_side.upper()}, Time so far: {self.cost} min"

initial_people = [
    ["ayansh", 'l', 5],
    ["ananya", 'l', 10],
    ["grandma", 'l', 20],
    ["grandpa", 'l', 25]
]
initial_state = State(initial_people, 'l', 0)
solution_path, total_time = initial_state.bfs()

if solution_path:
    print("Solution Path:")
    for step, state in enumerate(solution_path):
        print(f"Step {step}: {state}\n")
    print(f"Total time to cross the bridge: {total_time} minutes")
else:
    print("No solution found within the time limit.")
