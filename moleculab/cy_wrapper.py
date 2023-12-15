import sys
import platform

bit_depth = platform.architecture()[0]
if sys.version_info.major == 3 and sys.version_info.minor == 10 and bit_depth == '64bit':
    from moleculab import cy_moleculab_310_64 as cy_moleculab
else:
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    raise BaseException('+++++++++++++++++++++++++ Unsupported python version ++++++++++++++++++++++++')


# +++++++++++++++++++++++++++++++++++++++++

import multiprocessing

from bpy.types import ParticleSystem

from moleculab.pg.particle_settings import MoleculabPSData


class MoleculabParticleSystem(ParticleSystem):
    def moleculab_pack_data(self, initialize: bool = False) -> MoleculabPSData: pass


def simulate_ps(time_delta: float, ps: MoleculabParticleSystem, initialize: bool = False):
    ps_data = ps.moleculab_pack_data(initialize)
    cy_moleculab.simulate_ps(multiprocessing.cpu_count(), time_delta, *ps_data.export())
    ps.moleculab_update()
