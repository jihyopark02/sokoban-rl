import itertools
import math
from src.constants import *

def has_Q_converged_l2(Q, Q_opt, threshold):
    l2_sum = 0
    for state, actions in Q_opt.items():
        if state not in Q:
            continue
        for action, q_opt_value in actions.items():
            if action not in Q[state]:
                continue
            l2_sum += (Q[state][action] - q_opt_value) ** 2
    l2_norm = math.sqrt(l2_sum)
    return l2_norm <= threshold

def has_Q_converged(Q, Q_opt, threshold):
    for state, actions in Q_opt.items():
        if state not in Q:
            return False
        for action, q_opt_value in actions.items():
            if action not in Q[state]:
                return False
            if abs(Q[state][action] - q_opt_value) > threshold:
                return False
    return True

def has_policy_converged(env, policy, opt_policy):
    current_state, info = env.reset()
    current_state = tuple(current_state)
    for opt_action in opt_policy:        
        if current_state not in policy:
            return False
        if policy[current_state] != opt_action:
            return False
        next_state, reward, done, truncated, info = env.step(opt_action)
        if done:
            break
    return True

def compute_v_and_q_from_policy(env, policy_actions, gamma):
    # policy_actions should be numeric
    # e.g. [0, 1, 2, 3] not ['up', 'left', 'down', 'right']
    # Note that this function only returns the V and Q values for the states visited in the inputted policy.
    V = {}
    Q = {}

    state, info = env.reset()
    trajectory = []

    for action in policy_actions:
        serialized_state = tuple(state)
        next_state, reward, done, truncated, _ = env.step(action)
        trajectory.append((serialized_state, action, reward))
        state = next_state
        if done or truncated:
            break

    G = 0
    for serialized_state, action, reward in reversed(trajectory):
        G = reward + gamma * G
        V[serialized_state] = G
        if serialized_state not in Q:
            Q[serialized_state] = {}
        Q[serialized_state][action] = G

    return V, Q

def find_player_in_state(state):
    for y, row in enumerate(state):
        for x, cell in enumerate(row):
            if cell in ('@', '+'):
                return (x, y)
    return None

def is_wall(state, x, y):
    return state[y][x] == "#"

def is_box(state, x, y):
    return state[y][x] in ["$", "*"]

def is_box_placed(state, x, y):
    return state[y][x] == "*"

def is_obstacle(state, x, y):
    return state[y][x] in ["#", "$", "*"]

def is_box_stuck(state, x, y):
    if is_box_placed(state, x, y):
        return False
    
    dirs = list(ACTION_MAP.values())

    for i in range(4):
        dx1, dy1 = dirs[i]
        dx2, dy2 = dirs[(i + 1) % 4]
        if is_wall(state, x + dx1, y + dy1) and is_wall(state, x + dx2, y + dy2):
            return True

    return False

def move_agent(state, x, y, nx, ny):
    if state[y][x] == "@":
        state[y][x] = " "
    elif state[y][x] == "+":
        state[y][x] = "."
    if state[ny][nx] == ".":
        state[ny][nx] = "+"
    else:
        state[ny][nx] = "@"

def is_position_free(state, x, y):
    return state[y][x] in [' ', '.']

def move_box(state, x, y, dx, dy):
    nx, ny = x + dx, y + dy
    if not is_position_free(state, nx, ny):
        return False
    if state[y][x] == "$":
        state[y][x] = " "
    elif state[y][x] == "*":
        state[y][x] = "."
    if state[ny][nx] == ".":
        state[ny][nx] = "*"
    else:
        state[ny][nx] = "$"
    return True

def check_win(state):
    for row in state:
        if '$' in row:
            return False
    return True

def generate_state_space(initial_level):
    print("Generating state space...")
    state_space = set()
    wall_positions = set()
    goal_positions = set()
    box_positions = set()

    for y, row in enumerate(initial_level):
        for x, cell in enumerate(row):
            if cell == "#":
                wall_positions.add((y, x))
            elif cell == ".":
                goal_positions.add((y, x))
            elif cell == "$":
                box_positions.add((y, x))
            elif cell == "@":
                player_position = (y, x)

    non_wall_positions = [
        (y, x)
        for y, row in enumerate(initial_level)
        for x, cell in enumerate(row)
        if cell != "#"
    ]
    box_combinations = itertools.combinations(
        non_wall_positions, len(box_positions)
    )

    for box_comb in box_combinations:
        for player_pos in non_wall_positions:
            if player_pos not in box_comb:
                level_state = []
                for y, row in enumerate(initial_level):
                    new_row = []
                    for x, cell in enumerate(row):
                        pos = (y, x)
                        if pos in wall_positions:
                            new_row.append("#")
                        elif pos in goal_positions and pos in box_comb:
                            new_row.append("*")
                        elif pos in goal_positions and pos == player_pos:
                            new_row.append("+")
                        elif pos in goal_positions:
                            new_row.append(".")
                        elif pos == player_pos:
                            new_row.append("@")
                        elif pos in box_comb:
                            new_row.append("$")
                        else:
                            new_row.append(" ")
                    level_state.append(tuple(new_row))

                state_space.add(tuple(level_state))
    print("Finished generating state space.")
    return state_space