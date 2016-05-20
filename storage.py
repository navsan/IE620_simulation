import simpy

class RawMaterialStorage:
  def __init__(self, env):
    self.env = env
    self.name = 'RawMaterialStorage'
    self.inventory = simpy.Container(env, init=simpy.core.Infinity)

  def set_out_channel(self, chan):
    pass

class FinalProductStorage:
  def __init__(self, env):
    self.env = env
    self.name = 'FinalProductStorage'
    self.inventory = simpy.Container(env)

  def set_in_channel(self, chan):
    pass

  def pprint(self, *args):
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def pprint_level(self):
    self.pprint('has inventory level ', str(self.inventory.level))

