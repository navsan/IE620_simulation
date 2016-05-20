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


# import random
import matplotlib.pyplot as plt
import simpy


def run_simulation():
  print 'Starting simulation now'
  env.run(until=24*60*60)

  for m in (M1, M2, M3, M4):
    m.finalize()
    print m.busy_fraction()

  for c in (RMS_M1_C, M2_FPS_C):
    c.finalize()
    print c.wait_fraction()

def show_machine_items_processed():
  for m in (M1, M2, M3, M4):
    times, vals = m.get_TS_items_processed()
    plt.step(times, vals, label=m.name)
  plt.grid(True)
  plt.xlabel('Time (s)')
  plt.ylabel('Num items processed')
  plt.legend(loc='upper left')
  plt.show()

def show_FPS_inventory_level():
  times, vals = FPS.get_TS_inventory_level()
  plt.step(times, vals, label='Final Inventory Level')
  plt.grid(True)
  plt.xlabel('Time (s)')
  plt.ylabel('Num products')
  plt.legend(loc = 'upper left')
  plt.show()

def show_plots():
  # show_machine_items_processed()
  show_FPS_inventory_level()

#==============================================================================
#                 INITIALIZE
#==============================================================================
env = simpy.Environment()

RMS = RawMaterialStorage(env)
M1 = Machine(env, 'M1', Uni(20,120), out_size=10)
M2 = Machine(env, 'M2', Uni(120,300))
M3 = Machine(env, 'M3', Normal(300,30))
M4 = Machine(env, 'M4', Normal(360,60))
FPS = FinalProductStorage(env, Uni(10*60, 500*60), Normal(80,5))

RMS_M1_C = AGVChannelFromStorage(env, RMS, M1, Constant(60))
M1_M2_C = Channel(env, M1, M2, Uni(10,60))
M2_M3_C = Channel(env, M2, M3, Uni(10,60))
M3_M4_C = Channel(env, M3, M4, Uni(10,60))
M2_FPS_C = AGVChannelToStorage(env, M4, FPS, Constant(60), agv=RMS_M1_C.agv)

#==============================================================================
#                 RUN SIMULATION
#==============================================================================

run_simulation()

#==============================================================================
#                 GENERATE PLOTS
#==============================================================================

show_plots()
