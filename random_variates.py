import random


def Uni(a,b):
  return lambda: random.uniform(a,b)

def _get_normal(mu, sigma, low_threshold=1):
  r = low_threshold
  while (r <= low_threshold):
    r = random.normalvariate(mu, sigma)
  return r

def Normal(mu,sigma):
  return lambda: _get_normal(mu, sigma)
