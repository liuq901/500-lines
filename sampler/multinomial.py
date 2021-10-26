import numpy as np
from scipy.special import gammaln

class MultinomialDistribution(object):
    def __init__(self, p, rso=np.random):
        if not np.isclose(np.sum(p), 1.0):
            raise ValueError('outcome probabilities do not sum to 1')
        np.seterr(all='ignore')

        self.p = p
        self.rso = rso

        self.logp = np.log(self.p)

    def sample(self, n):
        x = self.rso.multinomial(n, self.p)
        return x

    def log_pmf(self, x):
        n = np.sum(x)

        log_n_factorial = gammaln(n + 1)
        sum_log_xi_factorial = np.sum(gammaln(x + 1))

        log_pi_xi = self.logp * x
        log_pi_xi[x == 0] = 0
        sum_log_pi_xi = np.sum(log_pi_xi)

        log_pmf = log_n_factorial - sum_log_xi_factorial + sum_log_pi_xi
        return log_pmf

    def pmf(self, x):
        pmf = np.exp(self.log_pmf(x))
        return pmf
