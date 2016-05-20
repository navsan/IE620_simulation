import simpy

class Channel:
  def __init__(self, env, src, dest, delay):
    self.env = env
    self.src = src
    self.dest = dest
    self.delay = delay
    self.queue = simpy.Container(env)
    self.name = self.src.name + '->' + self.dest.name
    self.src.set_out_channel(self)
    self.dest.set_in_channel(self)

  def pprint(self, *args):
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def send(self, qty=1):
    self.pprint('started sending an item')
    yield self.env.timeout(self.delay())     # Simulate channel delay first
    yield self.queue.put(qty)         # Place the item in the queue
    self.pprint('delivered an item')

  def get(self, qty=1):
    yield self.queue.get(qty)

class AGVChannel(Channel):
  def __init__(self, env, src, dest, delay, agv=None):
    Channel.__init__(self, env, src, dest, delay)
    if agv == None:
      self.agv = simpy.Resource(env, capacity=1)
    else:
      self.agv = agv

class AGVChannelToStorage(AGVChannel):
  def __init__(self, env, src, dest, delay, agv=None):
    AGVChannel.__init__(self, env, src, dest, delay, agv)
    self.current_batch_size = 0

  def send(self, qty=1):
    self.current_batch_size += qty
    if (self.current_batch_size >= 10):
      self.pprint('started waiting to acquire AGV.')
      with self.agv.request() as req:
        yield req
        self.pprint('acquired AGV.')
        yield self.env.timeout(self.delay())
        yield self.dest.inventory.put(qty)
        self.pprint('delivered an item.')
        self.dest.pprint_level()

  def get(self, qty=1):
    raise "AGVChannelToStorage does not support get()"

class AGVChannelFromStorage(AGVChannel):
  def send(self, qty=1):
    raise "AGVChannelFromStorage does not support send()"
 
  def get(self, qty=1):
    self.pprint('started waiting to acquire AGV.')
    with self.agv.request() as req:
      yield req
      yield self.src.inventory.get(qty)
      self.pprint('acquired AGV.')
      yield self.env.timeout(self.delay())
      self.pprint('delivered an item')

