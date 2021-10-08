import random

import flow

def heuristic_hillclimbing(data, candidates):
    scores = [(flow.makespan(data, perm), perm) for perm in candidates]
    return sorted(scores)[0][1]

def heuristic_random(data, candidates):
    return random.choice(candidates)

def heuristic_random_hillclimbing(data, candidates):
    scores = [(flow.makespan(data, perm), perm) for perm in candidates]
    i = 0
    while (random.random() < 0.5) and (i < len(scores) - 1):
        i += 1
    return sorted(scores)[i][1]
