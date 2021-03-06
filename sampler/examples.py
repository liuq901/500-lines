import matplotlib.pyplot as plt
import numpy as np

from rpg import DamageDistribution
from rpg import MagicItemDistribution

def main():
    bonus_probs = np.array([0.0, 0.55, 0.25, 0.12, 0.06, 0.02])
    stats_probs = np.ones(6) / 6.0
    rso = np.random.RandomState(234892)

    item_dist = MagicItemDistribution(bonus_probs, stats_probs, rso=rso)
    print(item_dist.sample())
    print(item_dist.sample())
    print(item_dist.sample())

    item = item_dist.sample()
    print(item)
    print(item_dist.log_pmf(item))
    print(item_dist.pmf(item))

    damage_dist = DamageDistribution(2, item_dist, num_hits=3, rso=rso)
    samples = np.array([damage_dist.sample() for i in range(100000)])

    minval = samples.min()
    print(minval)

    maxval = samples.max()
    print(maxval)

    median = np.percentile(samples, 50)
    print(median)

    plt.hist(samples, bins=maxval + 1, range=(0, maxval), histtype='step', color='k')
    plt.vlines([minval, maxval, median], 0, 4000, color='r', linestyle='--', linewidth=2)

    plt.xlabel('Damage')
    plt.ylabel('Number of samples')
    plt.title('Distribution over attack damage for 2 weapons')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
