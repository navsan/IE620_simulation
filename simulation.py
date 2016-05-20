"""
Manufacturing Facility Simulation

Raw Material Storage -> M1 -> M2 -> M3 -> M4 -> Final Product Storage

* The raw material is always abundant
* M1 produces with a processing time of Uni(20,120) seconds, each piece of
  raw material can be converted into 10 semi-products at M1.
* The processing time of M2, M3, and M4 are Uni(2,5) min, Normal (300,30)
  seconds, and Normal (6,1) minutes, respectively.
* There is a Uni(10,60) seconds transfer time between every two machines
* All finished goods generated after M4 is stored in the final product storage,
  assuming infinite storage space.
* Raw materials are routed to M1 using an AGV with a fixed travel time of
  1 min. Also, finished goods are routed from M4 to Final product storage with
  a batch of 10 using an AGV with a fixed travel time of 1 min. There is only
  one AGV available in the shop.
* Whenever M1 finishes consuming a raw material (produce 10 semi-products), 
  it will pull another raw material from RM storage and start processing.
* Finished goods will be pulled from the warehouse whenever an order arrives.
  Orders arrive with interarrival time of Uniform (10,500) min; each order
  contains Normal (80,5) quantity order. If inventory is smaller than demand,
  all remaining inventory will be pulled and the shortage amount will be
  recorded. No back-order will be made in such case


"""
from machine import Machine
from channel import Channel, AGVChannelFromStorage, AGVChannelToStorage
from storage import RawMaterialStorage, FinalProductStorage
from random_variates import *


import random
import matplotlib.pyplot as plt
import simpy

NUM_RUNS = 30
RUN_DURATION = 30 * 24 * 60 * 60

def run_simulation(seed=0):
  print '-' * 60
  print 'Starting simulation run ', seed
  random.seed(seed)
  env.run(until=RUN_DURATION)

  for m in (M1, M2, M3, M4):
    m.finalize()
    print m.name, 'has utilization rate', m.busy_fraction()

  for c in (RMS_M1_C, M4_FPS_C):
    c.finalize()
    print c.name, 'has AGV wait fraction', c.wait_fraction()

def initialize_stats():
  global stats
  stats = {}
  for m in (M1, M2, M3, M4):
    stats[m.name] = {
      'num_items': 0,
      'utilization_rate': 0,
    }
  for c in (RMS_M1_C, M4_FPS_C):
    stats[c.name] = {
      'wait_fraction': 0
    }
  stats[FPS.name] = {
    'num_shortfalls': 0,
    'num_orders': 0,
    'shortfall_qty': 0,
    'total_demand_qty': 0,
  }

def update_stats():
  global stats
  for m in (M1, M2, M3, M4):
    stats[m.name]['num_items'] += m.out_size * len(m.stats['proc_finish'])
    stats[m.name]['utilization_rate'] += m.busy_fraction()

  for c in (RMS_M1_C, M4_FPS_C):
    stats[c.name]['wait_fraction'] += c.wait_fraction()

  for k in ['num_shortfalls', 'num_orders',
            'shortfall_qty', 'total_demand_qty']:
    stats[FPS.name][k] += FPS.stats[k]

def finalize_stats():
  global stats
  for m in (M1, M2, M3, M4):
    stats[m.name]['num_items'] /= NUM_RUNS
    stats[m.name]['utilization_rate'] /= NUM_RUNS 

  for c in (RMS_M1_C, M4_FPS_C):
    stats[c.name]['wait_fraction'] /= NUM_RUNS 

  for k in ['num_shortfalls', 'num_orders',
            'shortfall_qty', 'total_demand_qty']:
    stats[FPS.name][k] /= NUM_RUNS

def print_stats():
  global stats
  print '-' * 60
  for k,d in stats.iteritems():
    print '-' * 20,  k, '-' * 20
    for k1, d1 in d.iteritems():
      print k1, ':', d1


def show_machine_items_processed():
  for m in (M1, M2, M3, M4):
    times, vals = m.get_TS_items_processed()
    plt.step(times, vals, label=m.name)
    print m.name, 'processed', vals[-1], 'items'
  plt.grid(True)
  plt.xlabel('Time (s)')
  plt.ylabel('Num items processed')
  plt.legend(loc='upper left')
  plt.show()

def show_FPS_inventory_level():
  times, vals = FPS.get_TS_inventory_level()
  print 'final inventory level ', vals[-1]
  plt.step(times, vals, label='Final Inventory Level')
  plt.grid(True)
  plt.xlabel('Time (s)')
  plt.ylabel('Num products')
  plt.legend(loc = 'upper left')
  plt.show()

def show_plots():
  show_machine_items_processed()
  show_FPS_inventory_level()
  for k in ['num_shortfalls', 'num_orders', 'shortfall_qty', 'total_demand_qty']:
    print 'FPS ', k, FPS.stats[k]


#==============================================================================
#                 INITIALIZE
#==============================================================================

def initialize():
  global env, RMS, M1, M2, M3, M4, FPS
  global RMS_M1_C, M1_M2_C, M2_M3_C, M3_M4_C, M4_FPS_C
  env = simpy.Environment()

  RMS = RawMaterialStorage(env)
  M1 = Machine(env, 'M1', Uni(20,120), out_size=10)
  M2 = Machine(env, 'M2', Uni(120,300))
  M3 = Machine(env, 'M3', Normal(300,30))
  M4 = Machine(env, 'M4', Normal(360,60))
  FPS = FinalProductStorage(env, demand_time=Uni(600, 30000),
                            demand_qty=Normal(80,5))

  RMS_M1_C = AGVChannelFromStorage(env, RMS, M1, Constant(60))
  M1_M2_C = Channel(env, M1, M2, Uni(10,60))
  M2_M3_C = Channel(env, M2, M3, Uni(10,60))
  M3_M4_C = Channel(env, M3, M4, Uni(10,60))
  M4_FPS_C = AGVChannelToStorage(env, M4, FPS, Constant(60), agv=RMS_M1_C.agv)


#==============================================================================
#                 RUN SIMULATION
#==============================================================================

for seed in xrange(NUM_RUNS):
  initialize()
  run_simulation(seed)
  if not seed:
    initialize_stats()
  update_stats()

finalize_stats()
print_stats()


#==============================================================================
#                 GENERATE PLOTS
#==============================================================================

# show_plots()
