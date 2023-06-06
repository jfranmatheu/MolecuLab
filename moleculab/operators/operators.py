import sys
import platform

bit_depth = platform.architecture()[0]
if sys.version_info.major == 3 and sys.version_info.minor == 10 and bit_depth == '64bit':
    from moleculab import cy_moleculab_310_64 as cy_moleculab
else:
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    raise BaseException('+++++++++++++++++++++++++ Unsupported python version ++++++++++++++++++++++++')


# +++++++++++++++++++++++++++++++++++++++++

from bpy.types import Context, Operator

from collections import defaultdict


def pack_ps_data(context: Context, initiate: bool = False):
    # scene = context.scene
    view_layer = context.view_layer
    space_data = context.space_data
    depsgraph = context.evaluated_depsgraph_get()

    packed_data = defaultdict(dict)

    for ob_name, ob in view_layer.objects.items():
        if 'moleculab' not in ob:
            continue

        if not ob.visible_get(view_layer=view_layer, viewport=space_data):
            continue

        if len(ob.particle_systems) == 0:
            continue

        if not any(['moleculab' in ps for ps in eval_ob.particle_systems]):
            continue

        eval_ob = ob.evaluated_get(depsgraph)
        mol_particle_systems = [ps for ps in eval_ob.particle_systems if 'moleculab' in ps]

        for ps in mol_particle_systems:
            packed_data[ps.name][ob_name] = ps.molecular_pack_data()

    return packed_data


class MOLECULAB_OT_test_cy_moleculab(Operator):
    bl_idname = 'moleculab.test_cy_moleculab'
    bl_label = "Test cy_moleculab"

    def execute(self, context: Context) -> set[str]:
        cy_moleculab.testfunc()
        return {'FINISHED'}
