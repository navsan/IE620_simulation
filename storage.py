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
      'inventory_level': [],
      'num_shortfalls': 0,
      'num_orders': 0,
      'shortfall_qty': 0,
      'total_demand_qty': 0,
    }
    self.env.process(self.demand())

  def set_in_channel(self, chan):
    pass

  def pprint(self, *args):
    print '%.3f' % self.env.now, ': ', self.name, ' '.join(args)

  def pprint_level(self):
    self.pprint('has inventory level ', str(self.inventory.level))
    self.stats['inventory_level'].append((self.env.now, self.inventory.level))

  def update_inventory(self, order_qty):
    self.pprint('has inventory level ', str(self.inventory.level))
    if self.inventory.level >= order_qty:
      yield self.inventory.get(order_qty)
      self.pprint('satisfied order. Inventory level ',
                  str(self.inventory.level))
    else:
      self.stats['num_shortfalls'] += 1
      self.stats['shortfall_qty'] += order_qty - self.inventory.level
      if self.inventory.level > 0:
        yield self.inventory.get(self.inventory.level)
      self.pprint('could not satisfy order. Overall shortfall',
                  str(self.stats['shortfall_qty']))
    self.stats['inventory_level'].append((self.env.now, self.inventory.level))
    self.stats['total_demand_qty'] += order_qty
    self.stats['num_orders'] += 1

  def demand(self):
    while True:
      yield self.env.timeout(self.demand_time())
      order_qty = int(self.demand_qty())
      self.pprint('order arrived. Quantity: ', str(order_qty))
      yield self.env.process(self.update_inventory(order_qty))

  def get_TS_inventory_level(self):
    ts = self.stats['inventory_level']
    times = [x[0] for x in ts]
    vals = [x[1] for x in ts]
    return (times, vals)

