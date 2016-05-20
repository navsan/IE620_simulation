import simpy

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
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def send(self, qty):
    self.pprint('started sending an item')
    yield self.env.timeout(self.delay())     # Simulate channel delay first
    yield self.queue.put(qty)         # Place the item in the queue
    self.pprint('delivered an item')

  def get(self, qty=1):
    yield self.queue.get(qty)

