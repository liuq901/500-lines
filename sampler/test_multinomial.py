import unittest

import numpy as np

from multinomial import MultinomialDistribution

class TestMultinomial(unittest.TestCase):
    def test_init_without_rso(self):
        p = np.array([0.1, 0.5, 0.3, 0.1])
        dist = MultinomialDistribution(p)
        self.assertTrue((dist.p == p).all())
        self.assertTrue((dist.logp == np.log(p)).all())
        self.assertIs(dist.rso, np.random)

    def test_init_with_rso(self):
        p = np.array([0.1, 0.5, 0.3, 0.1])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        self.assertTrue((dist.p == p).all())
        self.assertTrue((dist.logp == np.log(p)).all())
        self.assertEqual(dist.rso, rso)

    def test_init_bad_probabilities(self):
        p = np.array([0.1, 0.5, 0.3, 0.0])
        rso = np.random.RandomState(29348)
        with self.assertRaises(ValueError):
            MultinomialDistribution(p, rso=rso)

    def test_pmf_1(self):
        p = np.array([1.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        self.assertEqual(dist.pmf(np.array([1])), 1.0)
        self.assertEqual(dist.pmf(np.array([2])), 1.0)
        self.assertEqual(dist.pmf(np.array([10])), 1.0)

    def test_pmf_2(self):
        p = np.array([1.0, 0.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        self.assertEqual(dist.pmf(np.array([1, 0])), 1.0)
        self.assertEqual(dist.pmf(np.array([0, 1])), 0.0)
        self.assertEqual(dist.pmf(np.array([1, 0])), 1.0)
        self.assertEqual(dist.pmf(np.array([2, 2])), 0.0)
        self.assertEqual(dist.pmf(np.array([10, 0])), 1.0)
        self.assertEqual(dist.pmf(np.array([10, 3])), 0.0)

        p = np.array([0.0, 1.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        self.assertEqual(dist.pmf(np.array([0, 1])), 1.0)
        self.assertEqual(dist.pmf(np.array([1, 0])), 0.0)
        self.assertEqual(dist.pmf(np.array([0, 2])), 1.0)
        self.assertEqual(dist.pmf(np.array([2, 2])), 0.0)
        self.assertEqual(dist.pmf(np.array([0, 10])), 1.0)
        self.assertEqual(dist.pmf(np.array([3, 10])), 0.0)

    def test_pmf_3(self):
        p = np.array([0.5, 0.5])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        self.assertEqual(dist.pmf(np.array([1, 0])), 0.5)
        self.assertEqual(dist.pmf(np.array([0, 1])), 0.5)
        self.assertEqual(dist.pmf(np.array([2, 0])), 0.25)
        self.assertEqual(dist.pmf(np.array([0, 2])), 0.25)
        self.assertEqual(dist.pmf(np.array([1, 1])), 0.5)

    def test_sample_1(self):
        p = np.array([1.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        samples = np.array([dist.sample(1) for i in range(100)])
        self.assertEqual(samples.shape, (100, 1))
        self.assertTrue((samples == 1).all())
        samples = np.array([dist.sample(3) for i in range(100)])
        self.assertEqual(samples.shape, (100, 1))
        self.assertTrue((samples == 3).all())

    def test_sample_2(self):
        p = np.array([1.0, 0.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        samples = np.array([dist.sample(1) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((samples == np.array([1, 0])).all())
        samples = np.array([dist.sample(3) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((samples == np.array([3, 0])).all())

        p = np.array([0.0, 1.0])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        samples = np.array([dist.sample(1) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((samples == np.array([0, 1])).all())
        samples = np.array([dist.sample(3) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((samples == np.array([0, 3])).all())

    def test_sample_3(self):
        p = np.array([0.5, 0.5])
        rso = np.random.RandomState(29348)
        dist = MultinomialDistribution(p, rso=rso)
        samples = np.array([dist.sample(1) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((
            (samples == np.array([1, 0])) |
            (samples == np.array([0, 1]))).all()
        )
        samples = np.array([dist.sample(3) for i in range(100)])
        self.assertEqual(samples.shape, (100, 2))
        self.assertTrue((
            (samples == np.array([3, 0])) |
            (samples == np.array([2, 1])) |
            (samples == np.array([1, 2])) |
            (samples == np.array([0, 3]))).all()
        )
