import bpy
from bpy.types import PropertyGroup, ParticleSystem, ParticleSettings, Particle
from bpy.props import PointerProperty, BoolProperty

import numpy as np


alive_state_to_code = {
    "UNBORN": 2,
    "ALIVE": 0,
    "DEAD": 3
}


class MoleculabPSData:
    _cache: dict[int, 'MoleculabPSData'] = {}

    @classmethod
    def has_data(cls, psys: ParticleSystem) -> bool:
        return psys.as_pointer() in cls._cache

    @classmethod
    def create_data(cls, psys: ParticleSystem) -> 'MoleculabPSData':
        data = cls(psys)
        cls._cache[psys.as_pointer()] = data
        return data

    @classmethod
    def get_data(cls, psys: ParticleSystem) -> 'MoleculabPSData':
        return cls._cache.get(psys.as_pointer(), None)

    @classmethod
    def update_data(cls, psys: ParticleSystem) -> 'MoleculabPSData':
        data = cls.get_data(psys)
        data.update(psys)
        return data

    def __init__(self, ps: ParticleSystem):
        mass = ps.settings.mass
        particles: list[Particle] = ps.particles

        self.particle_count = len(particles)
        par_loc = np.empty(self.particle_count * 3, dtype=np.float32) # [0, 0, 0] * self.particle_count
        par_vel = np.empty(self.particle_count * 3, dtype=np.float32) # [0, 0, 0] * self.particle_count
        par_size = np.array(tuple(p.size for p in particles), dtype=np.float32) # [0] * self.particle_count
        self.par_alive = np.array(tuple(alive_state_to_code[p.alive_state] for p in particles), dtype=np.int32)

        ps.particles.foreach_get('location', par_loc)
        ps.particles.foreach_get('velocity', par_vel)
        ps.particles.foreach_get('size', par_size)

        self.par_loc = np.array(par_loc)
        self.par_vel = np.array(par_vel)
        self.par_size = np.array(par_size)
        self.par_mass = self.par_size * mass

    def update(self, ps: ParticleSystem):
        self.par_alive = np.array(tuple(alive_state_to_code[p.alive_state] for p in ps.particles))

        if self.par_loc.ndim != 1:
            self.par_loc = self.par_loc.reshape(-1)
        if self.par_vel.ndim != 1:
            self.par_vel = self.par_vel.reshape(-1)

        ps.particles.foreach_get('location', self.par_loc)
        ps.particles.foreach_get('velocity', self.par_vel)

        print("\n__Update Moleculab PS Data _____________________")
        print("Particle 1:")
        print("\t- Location:", self.par_loc[0:3])
        print("\t- Velocity:", self.par_vel[0:3])
        print("_________________________________________________")

    def export(self):
        # print("Loc:", self.par_loc.shape, self.par_loc.ndim)
        # print("Vel:", self.par_vel.shape, self.par_vel.ndim)
        # print("Size:", self.par_size.shape, self.par_size.ndim)
        # print("Mass:", self.par_mass.shape, self.par_mass.ndim)

        if self.par_loc.ndim == 1:
            self.par_loc = self.par_loc.reshape((self.particle_count, 3))
        if self.par_vel.ndim == 1:
            self.par_vel = self.par_vel.reshape((self.particle_count, 3))

        return self.particle_count, self.par_loc, self.par_vel, self.par_mass, self.par_size, self.par_alive


class MOLECULAB_PG_particle_settings(PropertyGroup):
    enabled: BoolProperty()

    def update(self, ps: ParticleSystem) -> None:
        packed_data = MoleculabPSData.get_data(ps)
        if packed_data is None:
            return

        if packed_data.par_loc.ndim != 1:
            packed_data.par_loc = packed_data.par_loc.reshape(-1)
        if packed_data.par_vel.ndim != 1:
            packed_data.par_vel = packed_data.par_vel.reshape(-1)

        ps.particles.foreach_set('location', packed_data.par_loc)
        ps.particles.foreach_set('velocity', packed_data.par_vel)

    def pack_data(self, ps: ParticleSystem, initialize: bool = False) -> None:

        # Just in case we are working with non-evaluated data...
        if not ps.id_data.is_evaluated:
            # We need to process the evaluated one.
            eval_ob = ps.id_data.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for psys in eval_ob.particle_systems:
                if psys.name == ps.name:
                    return psys.moleculab_pack_data(initialize)

        if not MoleculabPSData.has_data(ps) or initialize:
            packed_data = MoleculabPSData.create_data(ps)
        else:
            packed_data = MoleculabPSData.update_data(ps)

        print(ps, initialize, packed_data)
        return packed_data


def register():
    ParticleSystem.moleculab_pack_data = lambda ps, initialize=False: ps.settings.moleculab.pack_data(ps, initialize=initialize)
    ParticleSystem.moleculab_update = lambda ps: ps.settings.moleculab.update(ps)
    ParticleSettings.moleculab = PointerProperty(type=MOLECULAB_PG_particle_settings)

def unregister():
    del ParticleSystem.moleculab_pack_data
    del ParticleSettings.moleculab
