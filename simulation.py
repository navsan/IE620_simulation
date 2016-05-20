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
import simpy


def main():
  env = simpy.Environment()

  RMS = RawMaterialStorage(env)
  M1 = Machine(env, 'M1', Uni(10,20))
  M2 = Machine(env, 'M2', Normal(10,3))
  FPS = FinalProductStorage(env)

  RMS_M1_C = AGVChannelFromStorage(env, RMS, M1, Constant(1))
  M1_M2_C = Channel(env, M1, M2, Uni(2,5))
  M2_FPS_C = AGVChannelToStorage(env, M2, FPS, Constant(1), agv=RMS_M1_C.agv)

  print 'Starting simulation now'
  env.run(until=100)

  print M1.stats
  print M2.stats
  M1.finalize()
  M2.finalize()
  print M1.busy_fraction()
  print M2.busy_fraction()


main()
