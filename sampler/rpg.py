import numpy as np

from multinomial import MultinomialDistribution

class MagicItemDistribution(object):
    stats_names = (
        'dexterity', 'constitution', 'strength',
        'intelligence', 'wisdom', 'charisma'
    )

    def __init__(self, bonus_probs, stats_probs, rso=np.random):
        self.bonus_dist = MultinomialDistribution(bonus_probs, rso=rso)
        self.stats_dist = MultinomialDistribution(stats_probs, rso=rso)

    def sample(self):
        stats = self._sample_stats()
        item_stats = dict(zip(self.stats_names, stats))
        return item_stats

    def log_pmf(self, item):
        stats = np.array([item[stat] for stat in self.stats_names])
        log_pmf = self._stats_log_pmf(stats)
        return log_pmf

    def pmf(self, item):
        return np.exp(self.log_pmf(item))

    def _sample_bonus(self):
        sample = self.bonus_dist.sample(1)

        bonus = np.argmax(sample)
        return bonus

    def _sample_stats(self):
        bonus = self._sample_bonus()

        stats = self.stats_dist.sample(bonus)
        return stats

    def _bonus_log_pmf(self, bonus):
        if bonus < 0 or bonus >= len(self.bonus_dist.p):
            return -np.inf

        x = np.zeros(len(self.bonus_dist.p))
        x[bonus] = 1

        return self.bonus_dist.log_pmf(x)

    def _stats_log_pmf(self, stats):
        total_bonus = np.sum(stats)

        logp_bonus = self._bonus_log_pmf(total_bonus)

        logp_stats = self.stats_dist.log_pmf(stats)

        log_pmf = logp_bonus + logp_stats
        return log_pmf

class DamageDistribution(object):
    def __init__(self, num_items, item_dist, num_dice_sides=12, num_hits=1, rso=np.random):
        self.dice_sides = np.arange(1, num_dice_sides + 1)
        self.dice_dist = MultinomialDistribution(np.ones(num_dice_sides) / float(num_dice_sides), rso=rso)

        self.num_hits = num_hits
        self.num_items = num_items
        self.item_dist = item_dist

    def sample(self):
        items = [self.item_dist.sample() for i in range(self.num_items)]

        num_dice = 1 + np.sum([item['strength'] for item in items])

        dice_rolls = self.dice_dist.sample(self.num_hits * num_dice)
        damage = np.sum(self.dice_sides * dice_rolls)
        return damage
