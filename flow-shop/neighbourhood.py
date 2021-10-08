from itertools import combinations, permutations
import random

import flow

def neighbours_random(data, perm, num=1):
    candidates = [perm]
    for i in range(num):
        candidate = perm[:]
        random.shuffle(candidate)
        candidates.append(candidate)
    return candidates

def neighbours_swap(data, perm):
    candidates = [perm]
    for (i, j) in combinations(range(len(perm)), 2):
        candidate = perm[:]
        candidate[i], candidate[j] = candidate[j], candidate[i]
        candidates.append(candidate)
    return candidates

def neighbours_LNS(data, perm, size=2):
    candidates = [perm]

    neighbourhoods = list(combinations(range(len(perm)), size))
    random.shuffle(neighbourhoods)

    for subset in neighbourhoods[:flow.MAX_LNS_NEIGHBOURHOODS]:
        best_make = flow.makespan(data, perm)
        best_perm = perm

        for ordering in permutations(subset):
            candidate = perm[:]
            for i in range(len(ordering)):
                candidate[subset[i]] = perm[ordering[i]]
            res = flow.makespan(data, candidate)
            if res < best_make:
                best_make = res
                best_perm = candidate

        candidates.append(best_perm)

    return candidates

def neighbours_idle(data, perm, size=4):
    candidates = [perm]

    sol = flow.complie_solution(data, perm)
    results = []

    for i in range(len(data)):
        finish_time = sol[-1][i] + data[perm[i]][-1]
        idle_time = (finish_time - sol[0][i]) - sum([t for t in data[perm[i]]])
        results.append((idle_time, i))

    subset = [job_idx for (idle, job_idx) in reversed(sorted(results))][:size]

    for ordering in permutations(subset):
        candidate = perm[:]
        for i in range(len(ordering)):
            candidate[subset[i]] = perm[ordering[i]]
        candidates.append(candidate)

    return candidates
