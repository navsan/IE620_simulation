import simpy

SLEEP_DURATION = 10

class Machine:
  def __init__(self, env, name, processing_time):
    self.env = env
    self.name = name
    self.processing_time = processing_time
    self.in_channel = None
    self.out_channel = None
    self.process = env.process(self.run())
    self.stats = {
      'proc_start': [],
      'proc_finish': [],
      'busy_time': 0,
    }

  def set_in_channel(self, chan):
    assert not self.in_channel      # Ensure no channel previously assigned
    self.in_channel = chan

  def set_out_channel(self, chan):
    assert not self.out_channel     # Ensure no channel previously assigned
    self.out_channel = chan

  def pprint(self, *args):
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def run(self):
    while True:
      if self.in_channel:
        yield self.env.process(self.in_channel.get())
        self.pprint('got an item from queue')
      yield self.env.process(self.process_item())
      if self.out_channel:
        self.pprint ('sent an item')
        self.env.process(self.out_channel.send(1))

  # def dispose(self):
  #   self.pprint('disposed an item')

  # def generate(self):
  #   self.pprint('generated an item')

  def process_item(self):
    self.pprint('started processing an item')
    self.stats['proc_start'].append(self.env.now)
    yield self.env.timeout(self.processing_time())
    self.stats['proc_finish'].append(self.env.now)
    self.stats['busy_time'] += self.env.now - self.stats['proc_start'][-1]
    self.pprint('finished processing an item')

  def finalize(self):
    # If there's an unfinished item, count that in the busy_time 
    if self.stats['proc_start'][-1] >= self.stats['proc_finish'][-1]:
      self.stats['busy_time'] += self.env.now - self.stats['proc_start'][-1]

  def busy_fraction(self):
    return self.stats['busy_time'] / self.env.now
