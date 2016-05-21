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
    self.wait_start = None
    self.stats = {
      'wait_time': 0,
      'busy_time': 0,
      'sleep_time': 0,
    }

  def wait_fraction(self):
    s = self.stats['sleep_time']
    w = self.stats['wait_time']
    b = self.stats['busy_time']
    return w / (s+b+w)

  def sleep_fraction(self):
    s = self.stats['sleep_time']
    w = self.stats['wait_time']
    b = self.stats['busy_time']
    return s / (s+b+w)

  def finalize(self):
    if self.wait_start:
      self.stats['wait_time'] += self.env.now - self.wait_start
    if self.busy_start:
      self.stats['busy_time'] += self.env.now - self.busy_start

class AGVChannelToStorage(AGVChannel):
  max_batch_size = 10
  def __init__(self, env, src, dest, delay, agv=None):
    AGVChannel.__init__(self, env, src, dest, delay, agv)
    self.current_batch_size = 0

  def send(self, qty=1):
    self.current_batch_size += qty
    if (self.current_batch_size >= self.max_batch_size):
      self.pprint('started waiting to acquire AGV.')
      self.wait_start = self.env.now
      self.busy_start = self.env.now
      with self.agv.request() as req:
        yield req
        self.pprint('acquired AGV.')
        self.stats['wait_time'] += self.env.now - self.wait_start
        self.wait_start = None
        yield self.env.timeout(self.delay())
        yield self.dest.inventory.put(self.max_batch_size)
        self.pprint('delivered an item.')
        self.current_batch_size = 0
        self.stats['busy_time'] += self.env.now - self.busy_start
        self.busy_start = None
        self.dest.pprint_level()

  def get(self, qty=1):
    raise "AGVChannelToStorage does not support get()"

class AGVChannelFromStorage(AGVChannel):
  def __init__(self, env, src, dest, delay, fps, s, S, agv=None):
    AGVChannel.__init__(self, env, src, dest, delay, agv)
    self.fps = fps
    self.s = s
    self.S = S

  def send(self, qty=1):
    raise "AGVChannelFromStorage does not support send()"

  def sleep_if_inventory_level_OK(self):
    while self.fps.inventory.level < self.S and self.fps.inventory.level > self.s:
      self.pprint('inventory level is ', str(self.fps.inventory.level),
                  '. Sleeping.')
      self.stats['sleep_time'] += 10
      yield self.env.timeout(10)

  def get(self, qty=1):
    yield self.env.process(self.sleep_if_inventory_level_OK())
    self.pprint('started waiting to acquire AGV.')
    self.wait_start = self.env.now
    self.busy_start = self.env.now
    with self.agv.request() as req:
      yield req
      yield self.src.inventory.get(qty)
      self.pprint('acquired AGV.')
      self.stats['wait_time'] += self.env.now - self.wait_start
      yield self.env.timeout(self.delay())
      self.stats['busy_time'] += self.env.now - self.busy_start
      self.busy_start = None
      self.pprint('delivered an item')

