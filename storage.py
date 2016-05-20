import simpy

class RawMaterialStorage:
  def __init__(self, env):
    self.env = env
    self.name = 'RawMaterialStorage'
    self.inventory = simpy.Container(env, init=simpy.core.Infinity)

  def set_out_channel(self, chan):
    pass

class FinalProductStorage:
  def __init__(self, env, demand_time, demand_qty):
    self.env = env
    self.name = 'FinalProductStorage'
    self.inventory = simpy.Container(env)
    self.demand_time = demand_time
    self.demand_qty = demand_qty
    self.stats = {
      'shortfall_qty': 0,
    }
    self.env.process(self.demand())

  def set_in_channel(self, chan):
    pass

  def pprint(self, *args):
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def pprint_level(self):
    self.pprint('has inventory level ', str(self.inventory.level))

  def update_inventory(self, order_qty):
    self.pprint('has inventory level ', str(self.inventory.level))
    if self.inventory.level >= order_qty:
      yield self.inventory.get(order_qty)
      self.pprint('satisfied order. Inventory level ',
                  str(self.inventory.level))
    else:
      yield self.inventory.get(self.inventory.level)
      self.stats['shortfall_qty'] += order_qty - self.inventory.level
      self.pprint('could not satisfy order. Overall shortfall',
                  str(self.stats['shortfall_qty']))

  def demand(self):
    while True:
      yield self.env.timeout(self.demand_time())
      order_qty = self.demand_qty()
      self.pprint('order arrived. Quantity: ', str(order_qty))
      yield self.env.process(self.update_inventory(order_qty))
