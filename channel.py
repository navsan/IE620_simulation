import simpy

class Channel:
  def __init__(self, env, src, dest, delay, initial_qty=0):
    self.env = env
    self.src = src
    self.dest = dest
    self.delay = delay
    self.queue = simpy.Container(env, init=initial_qty)
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
  def __init__(self, env, src, dest, delay, initial_qty=0, agv=None):
    Channel.__init__(self, env, src, dest, delay, initial_qty)
    if agv == None:
      self.agv = simpy.Resource(env, capacity=1)
    else:
      self.agv = agv

  def send(self, qty=1):
    req = self.agv.request()
    yield req
    Channel.send(self, qty)
    self.agv.release(req)
    
  def get(self, qty=1):
    req = self.agv.request()
    yield req
    Channel.get(self, qty)
    self.agv.release(req)
