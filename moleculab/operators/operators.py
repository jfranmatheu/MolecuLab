import bpy
from bpy.types import Context, Event, Operator, ParticleSystem, ParticleSettings

from collections import defaultdict

from moleculab.utils.math import map_value
from moleculab.gpu import idraw
from moleculab.cy_wrapper import simulate_ps


def get_moleculab_ps(context: Context) -> dict[ParticleSystem, set[str]]:
    view_layer = context.view_layer
    space_data = context.space_data
    depsgraph = context.evaluated_depsgraph_get()

    particle_systems = defaultdict(set)
    
    frame_count = context.scene.frame_end - context.scene.frame_start

    for ob_name, ob in view_layer.objects.items():
        if 'moleculab' not in ob:
            continue

        if not ob.visible_get(view_layer=view_layer, viewport=space_data):
            continue

        if len(ob.particle_systems) == 0:
            continue

        if not any(['moleculab' in ps.settings for ps in ob.particle_systems]):
            continue

        eval_ob = ob.evaluated_get(depsgraph)
        mol_particle_systems = [ps for ps in eval_ob.particle_systems if 'moleculab' in ps.settings]

        for ps in mol_particle_systems:
            ps.settings.frame_start = 1
            ps.settings.frame_end = 1
            ps.settings.lifetime = frame_count
            ps.settings.physics_type = 'NEWTON'
            # ps.show_instancer_for_viewport = False

            particle_systems[ps].add(ob_name)

    return particle_systems


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

        if not any(['moleculab' in ps for ps in ob.particle_systems]):
            continue

        eval_ob = ob.evaluated_get(depsgraph)
        mol_particle_systems = [ps for ps in eval_ob.particle_systems if 'moleculab' in ps]
        
        frame_count = context.scene.frame_end - context.scene.frame_start

        for ps in mol_particle_systems:
            ps.settings.frame_start = 1
            ps.settings.frame_end = 1
            ps.settings.lifetime = frame_count
            ps.physics_type = 'NEWTONIAN'
            ps.show_instancer_for_viewport = False

            packed_data[ps.name][ob_name] = ps.moleculab_pack_data()

    return packed_data


class MOLECULAB_OT_test_cy_moleculab(Operator):
    bl_idname = 'moleculab.test_cy_moleculab'
    bl_label = "Test cy_moleculab"

    def execute(self, context: Context) -> set[str]:
        if not context.window_manager.modal_handler_add(self):
            return {'CANCELLED'}

        self.modal_start(context)
        return {'RUNNING_MODAL'}

    def modal_start(self, context: Context) -> None:
        print("modal_start()")
        self.first_time = True

        # Start timer.
        self._modal_timer = context.window_manager.event_timer_add(0.000000001, window=context.window)

        # Start draw handler.
        def _draw(_context: Context, target_area: int, scale: float):
            if _context.area.as_pointer() != target_area:
                return
            self.draw_progress_bar(context, scale)

        self.progress = 0
        context.region.tag_redraw()
        self._draw_handler = context.space_data.draw_handler_add(_draw,
                                                                 (context, context.area.as_pointer(), context.preferences.system.ui_scale),
                                                                 'WINDOW', 'POST_PIXEL')

        # Proceed by loading next frame (actually start frame).
        self.frame_step = context.scene.frame_step
        self.frame = context.scene.frame_start - self.frame_step
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        self.time_delta = 1 / context.scene.render.fps * self.frame_step

        self.next_frame(context)

        # Get valid particle systems.
        self.moleculab_ps = get_moleculab_ps(context)

    def modal(self, context: Context, event: Event) -> set[str]:
        print("modal() -> ", event.type, event.value)

        # Check cancel events.
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        # Ignore any event that is not from the modal's timer.
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        # Check if frame range is over.
        if self.frame > self.frame_end:
            self.modal_end(context)
            bpy.ops.screen.animation_play('INVOKE_DEFAULT')
            return {'FINISHED'}

        # Simulate each PS in current frame.
        for ps in self.moleculab_ps.keys():
            # Get PS packed data to send to cython.
            simulate_ps(self.time_delta, ps, self.first_time)

        self.next_frame(context)
        return {'RUNNING_MODAL'}

    def modal_end(self, context: Context) -> None:
        print("modal_end()")

        if hasattr(self, '_modal_timer'):
            context.window_manager.event_timer_remove(self._modal_timer)
            del self._modal_timer

        if hasattr(self, '_draw_handler'):
            context.region.tag_redraw()
            context.space_data.draw_handler_remove(self._draw_handler, 'WINDOW')
            del self._draw_handler

        # ----------------------------------
        # IF BAKE OPTION IS ENABLED.
        # fake_context = context.copy()
        # for psys in self.moleculab_ps:
        #     fake_context["point_cache"] = psys.point_cache
        #     with context.temp_override(**fake_context):
        #         bpy.ops.ptcache.bake_from_cache()
        # ----------------------------------

        # context.scene.render.frame_map_new = 1
        context.view_layer.update()

        # Return to the start.
        # context.scene.frame_current = self.frame_start
        context.scene.frame_set(self.frame_start)

    def cancel(self, context: Context) -> None:
        print("cancel()")

        self.modal_end(context)

    def next_frame(self, context: Context) -> None:
        print("next_frame() ->", self.frame)
        # context.scene.frame_current = self.frame
        self.frame += self.frame_step
        context.scene.frame_set(self.frame)
        self.progress = map_value(self.frame, (self.frame_start, self.frame_end), (0, 1))

        context.region.tag_redraw()

        if self.first_time:
            self.first_time = False

    def draw_progress_bar(self, context: Context, scale: float) -> None:
        idraw.rect(
            (context.region.x, context.region.y),
            (context.region.width * self.progress, 40 * scale),
            (0.2, 1, 1, 1)
        )
