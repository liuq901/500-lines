from collections import namedtuple
from functools import partial
from itertools import product
import random
import sys
import time

import heuristic
import neighbourhood

TIME_LIMIT = 300.0
TIME_INCREMENT = 13.0
DEBUG_SWITCH = False
MAX_LNS_NEIGHBOURHOODS = 1000

STRATEGIES = []

Strategy = namedtuple('Strategy', ['name', 'neighbourhood', 'heuristic'])

def initialize_strategies():
    global STRATEGIES

    neighbourhoods = [
        ('Random Permutation', partial(neighbourhood.neighbours_random, num=100)),
        ('Swapped Pairs', neighbourhood.neighbours_swap),
        ('Large Neighbourhood Search (2)', partial(neighbourhood.neighbours_LNS, size=2)),
        ('Large Neighbourhood Search (3)', partial(neighbourhood.neighbours_LNS, size=3)),
        ('Idle Neighbourhood (3)', partial(neighbourhood.neighbours_idle, size=3)),
        ('Idle Neighbourhood (4)', partial(neighbourhood.neighbours_idle, size=4)),
        ('Idle Neighbourhood (5)', partial(neighbourhood.neighbours_idle, size=5)),
    ]

    heuristics = [
        ('Hill Climbing', heuristic.heuristic_hillclimbing),
        ('Random Selection', heuristic.heuristic_random),
        ('Biased Random Selction', heuristic.heuristic_random_hillclimbing),
    ]

    for (n, h) in product(neighbourhoods, heuristics):
        STRATEGIES.append(Strategy(f'{n[0]} / {h[0]}', n[1], h[1]))

def solve(data):
    info, data = data

    assert info['num_jobs'] == len(data) and info['num_machines'] == len(data[0])
    random.seed(info['seed'])

    initialize_strategies()
    global STRATEGIES

    strategy_improvements = {strategy: 0 for strategy in STRATEGIES}
    strategy_time_spent = {strategy: 0 for strategy in STRATEGIES}
    strategy_weights = {strategy: 1 for strategy in STRATEGIES}
    strategy_usage = {strategy: 0 for strategy in STRATEGIES}

    perm = list(range(len(data)))
    random.shuffle(perm)

    best_make = makespan(data, perm)
    best_perm = perm
    res = best_make

    iteration = 0
    time_limit = time.time() + TIME_LIMIT
    time_last_switch = time.time()

    time_delta = TIME_LIMIT / 10
    checkpoint = time.time() + time_delta
    percent_complete = 10

    print('\nSolving...')

    while time.time() < time_limit:
        if time.time() > checkpoint:
            print(f'{percent_complete} %')
            percent_complete += 10
            checkpoint += time_delta

        iteration += 1

        strategy = pick_strategy(STRATEGIES, strategy_weights)

        old_val = res
        old_time = time.time()

        candidates = strategy.neighbourhood(data, perm)
        perm = strategy.heuristic(data, candidates)
        res = makespan(data, perm)

        strategy_improvements[strategy] += res - old_val
        strategy_time_spent[strategy] += time.time() - old_time
        strategy_usage[strategy] += 1

        if res < best_make:
            best_make = res
            best_perm = perm[:]

        if time.time() > time_last_switch + TIME_INCREMENT:
            results = sorted([(float(strategy_improvements[s]) / max(0.001, strategy_time_spent[s]), s) for s in STRATEGIES])
        
            if DEBUG_SWITCH:
                print('\nComputing another switch...')
                print(f'Best performer: {results[0][1].name} ({results[0][0]})')
                print(f'Worst performer: {results[-1][1].name} ({results[-1][0]})')

            for i in range(len(STRATEGIES)):
                strategy_weights[results[i][1]] += len(STRATEGIES) - i

                if results[i][0] == 0:
                    strategy_weights[results[i][1]] += len(STRATEGIES)

            time_last_switch = time.time()

            if DEBUG_SWITCH:
                print([(result[0], result[1].name) for result in results])
                print(sorted([strategy_weights[STRATEGIES[i]] for i in range(len(STRATEGIES))]))

            strategy_improvements = {strategy: 0 for strategy in STRATEGIES}
            strategy_time_spent = {strategy: 0 for strategy in STRATEGIES}

    print(f'{percent_complete} %')
    print(f'\nWent through {iteration} iterations.')

    print(f'\n(usage) Strategy:')
    results = sorted([(strategy_weights[STRATEGIES[i]], i) for i in range(len(STRATEGIES))], reverse=True)
    for (w, i) in results:
        print(f'({strategy_usage[STRATEGIES[i]]}) \t{STRATEGIES[i].name}')

    return (best_perm, best_make)

def parse_info(info_line):
    info_line = list(map(int, info_line.split()))
    assert len(info_line) == 5
    info = {
        'num_jobs': info_line[0],
        'num_machines': info_line[1],
        'seed': info_line[2],
        'upper_bound': info_line[3],
        'lower_bound': info_line[4],
    }
    return info

def parse_problem(filename, k=1):
    print('\nParsing...')

    with open(filename, 'r') as f:
        problem_line = '/number of jobs, number of machines, initial seed, upper bound and lower bound :/'

        lines = list(map(str.strip, f.readlines()))

        lines[0] = '/' + lines[0]

        try:
            if k == 0:
                raise IndexError
            lines = '/'.join(lines).split(problem_line)[k].split('/')
            info = parse_info(lines[0])
            lines = lines[2:]
        except IndexError:
            max_instances = len('/'.join(lines).split(problem_line)) - 1
            print(f'\nError: Instance must be within 1 and {max_instances}\n')
            sys.exit(0)

        data = [map(int, line.split()) for line in lines]

    return info, list(zip(*data))

def pick_strategy(strategies, weights):
    total = sum([weights[strategy] for strategy in strategies])
    pick = random.uniform(0, total)
    count = weights[strategies[0]]

    i = 0
    while pick > count:
        count += weights[strategies[i + 1]]
        i += 1
    
    return strategies[i]

def makespan(data, perm):
    return complie_solution(data, perm)[-1][-1] + data[perm[-1]][-1]

def complie_solution(data, perm):
    num_machines = len(data[0])

    machine_times = [[] for _ in range(num_machines)]

    machine_times[0].append(0)
    for machine in range(1, num_machines):
        machine_times[machine].append(machine_times[machine - 1][0] + data[perm[0]][machine - 1])

    for i in range(1, len(perm)):
        job = perm[i]
        machine_times[0].append(machine_times[0][-1] + data[perm[i - 1]][0])

        for machine in range(1, num_machines):
            machine_times[machine].append(max(machine_times[machine - 1][i] + data[perm[i]][machine - 1],
                machine_times[machine][i - 1] + data[perm[i - 1]][machine]))

    return machine_times

def print_solution(data, perm):
    info, data = data

    sol = complie_solution(data, perm)

    print(f'\nPermutation: {str([i + 1 for i in perm])}')

    print(f'Makespan: {makespan(data, perm)}')
    print(f'Lower bound: {info["lower_bound"]}')
    print(f'Upper bound: {info["upper_bound"]}')

    row_format = "{:>15}" * 4
    print(row_format.format('Machine', 'Start Time', 'Finish Time', 'Idle Time'))
    for machine in range(len(data[0])):
        finish_time = sol[machine][-1] + data[perm[-1]][machine]
        idle_time = (finish_time - sol[machine][0]) - sum([job[machine] for job in data])
        print(row_format.format(machine + 1, sol[machine][0], finish_time, idle_time))

    results = []
    for i in range(len(data)):
        finish_time = sol[-1][i] + data[perm[i]][-1]
        idle_time = (finish_time - sol[0][i]) - sum([time for time in data[perm[i]]])
        results.append((perm[i] + 1, sol[0][i], finish_time, idle_time))

    print('\n' + row_format.format('Job', 'Start Time', 'Finish Time', 'Idle Time'))
    for r in sorted(results):
        print(row_format.format(*r))

    print('\nNote: Idle time does not include initial or final wait time.')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        data = parse_problem(sys.argv[1])
    elif len(sys.argv) == 3:
        data = parse_problem(sys.argv[1], int(sys.argv[2]))
    else:
        print('\nUsage: python flow.py <Taillard problem file> [<instance number>]\n')
        sys.exit(0)

    (perm, ms) = solve(data)
    print_solution(data, perm)
