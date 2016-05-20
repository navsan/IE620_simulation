"""
Manufacturing Facility Simulation

Raw Material Storage -> M1 -> M2 -> M3 -> M4 -> Final Product Storage

* The raw material is always abundant
* M1 produces with a processing time of Uni(20,120) seconds, each piece of raw material can be converted into 10 semi-products at M1.
* The processing time of M2, M3, and M4 are Uni(2,5) min, Normal (300,30) seconds, and Normal (6,1) minutes, respectively.
* There is a Uni(10,60) seconds transfer time between every two machines
* All finished goods generated after M4 is stored in the final product storage, assuming infinite storage space.
* Raw materials are routed to M1 using an AGV with a fixed travel time of 1 min. Also, finished goods are routed from M4 to Final product storage with a batch of 10 using an AGV with a fixed travel time of 1 min. There is only one AGV available in the shop.
* Whenever M1 finishes consuming a raw material (produce 10 semi-products), it will pull another raw material from RM storage and start processing.
* Finished goods will be pulled from the warehouse whenever an order arrives. Orders arrive with interarrival time of Uniform (10,500) min; each order contains Normal (80,5) quantity order. If inventory is smaller than demand, all remaining inventory will be pulled and the shortage amount will be recorded. No back-order will be made in such case


"""


import random
import simpy

SLEEP_DURATION = 10

def Uni(a,b):
  return lambda: random.uniform(a,b)

def get_normal(mu, sigma, low_threshold=1):
  r = low_threshold
  while (r <= low_threshold):
    r = random.normalvariate(mu, sigma)
  return r

def Normal(mu,sigma):
  return lambda: get_normal(mu, sigma)


class Machine:
  def __init__(self, env, name, processing_time):
    self.env = env
    self.name = name
    self.processing_time = processing_time
    self.in_channel = None
    self.out_channel = None
    self.process = env.process(self.run())
    self.stats = {}

  def set_in_channel(self, chan):
    assert not self.in_channel      # Ensure no channel previously assigned
    self.in_channel = chan

  def set_out_channel(self, chan):
    assert not self.out_channel     # Ensure no channel previously assigned
    self.out_channel = chan

  def pprint(self, *args):
    print self.env.now, ': ', self.name, ' '.join(args)

  def run(self):
    while True:
      if self.in_channel:
        print self.env.now, ': ', 'Current queue size', self.in_channel.queue.level
        yield self.env.process(self.in_channel.get())
        self.pprint('got an item from queue')
      else:
        self.generate()
      self.pprint('started processing an item')
      yield self.env.timeout(self.processing_time())
      self.pprint('finished processing an item')
      if self.out_channel:
        self.pprint ('sent an item')
        self.env.process(self.out_channel.send(1))
        # yield self.env.process(self.out_channel.send(1))
      else:
        self.dispose()

  def dispose(self):
    self.pprint('disposed an item')

  def generate(self):
    self.pprint('generated an item')



class Channel:
  def __init__(self, env, src, dest, delay):
    self.env = env
    self.src = src
    self.dest = dest
    self.delay = delay
    self.queue = simpy.resources.container.Container(env)
    self.name = self.src.name + '->' + self.dest.name
    self.src.set_out_channel(self)
    self.dest.set_in_channel(self)

  def pprint(self, *args):
    print self.env.now, ': ', self.name, ' '.join(args)

  def send(self, qty):
    self.pprint('started sending an item')
    yield self.env.timeout(self.delay())     # Simulate channel delay first
    yield self.queue.put(qty)         # Place the item in the queue
    self.pprint('delivered an item')

  def get(self, qty=1):
    yield self.queue.get(qty)


def main():
  env = simpy.Environment()
  M1 = Machine(env, 'M1', Uni(10,20))
  M2 = Machine(env, 'M2', Normal(10,3))
  c = Channel(env, M1, M2, Uni(2,5))
  print 'Starting simulation now'
  env.run(until=100)

main()
