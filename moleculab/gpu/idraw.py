''' Immediate Drawing functions. '''

import bpy
import gpu
from gpu_extras.batch import batch_for_shader


shader_unif_color = gpu.shader.from_builtin('UNIFORM_COLOR')


rect_indices = ((0, 1, 2), (2, 1, 3))
def rect_coords(x, y, w, h): return [(x, y),(x+w, y),(x, y+h),(x+w, y+h)]


def rect(pos, size, color):
    shader = shader_unif_color
    batch = batch_for_shader(shader, 'TRIS', {"pos": rect_coords(*pos, *size)}, indices=rect_indices)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
