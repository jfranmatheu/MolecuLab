import bpy
from bpy.types import PropertyGroup, ParticleSystem, ParticleSettings, Particle
from bpy.props import PointerProperty, BoolProperty


alive_state_to_code = {
    "UNBORN": 2,
    "ALIVE": 0,
    "DEAD": 3
}


class MoleculabPSData:
    def __init__(self, ps: ParticleSystem):
        mass = ps.settings.mass
        particles: list[Particle] = ps.particles

        self.particle_count = len(particles)
        self.par_loc = [0, 0, 0] * self.particle_count
        self.par_vel = [0, 0, 0] * self.particle_count
        self.par_size = [0] * self.particle_count
        self.par_mass = tuple(mass * p.size for p in particles)
        self.par_alive = tuple(alive_state_to_code[p.alive_state] for p in particles)

        ps.particles.foreach_get('location', self.par_loc)
        ps.particles.foreach_get('velocity', self.par_vel)
        ps.particles.foreach_get('size', self.par_size)

    def update(self, ps: ParticleSystem):
        self.par_alive = tuple(alive_state_to_code[p.alive_state] for p in ps.particles)
        ps.particles.foreach_get('location', self.par_loc)
        ps.particles.foreach_get('velocity', self.par_vel)


class MOLECULAB_PG_particle_settings(PropertyGroup):
    packed_data: MoleculabPSData = None

    enabled: BoolProperty()

    def pack_data(self, ps: ParticleSystem) -> None:
        # Just in case we are working with non-evaluated data...
        if not ps.id_data.is_evaluated:
            # We need to process the evaluated one.
            eval_ob = ps.id_data.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for psys in eval_ob.particle_systems:
                if psys.name == ps.name:
                    return psys.moleculab_pack_data()

        if self.packed_data is None:
            self.packed_data = MoleculabPSData(ps)
        else:
            self.packed_data.update(ps)
        return self.packed_data


def register():
    ParticleSystem.moleculab_pack_data = lambda ps: ps.settings.moleculab.pack_data(ps)
    ParticleSettings.moleculab = PointerProperty(type=MOLECULAB_PG_particle_settings)

def unregister():
    del ParticleSystem.moleculab_pack_data
    del ParticleSettings.moleculab
