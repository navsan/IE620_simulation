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
      'started_processing': [],
      'finished_processing': [],
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
      else:
        self.generate()
      yield self.env.process(self.process_item())
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

  def process_item(self):
    self.pprint('started processing an item')
    self.stats['started_processing'].append(self.env.now)
    yield self.env.timeout(self.processing_time())
    self.stats['finished_processing'].append(self.env.now)
    self.pprint('finished processing an item')

