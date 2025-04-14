bl_info = {
    "name": "Farsi/Arabic Text for Blender",
    "author": "Hossein Jenabi",
    "version": (1, 0),
    "blender": (3, 0, 1),
    "location": "3Dviewport, Text edit mode",
    "description": "Farsi/Arabic Text for Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Text",
}

import bpy
from bpy.types import Operator, Context, Event
from . import FarsiText as Fa


# Keyboard Handler
class __OT_FarsiTextMode(Operator):

    bl_idname = "view3d.arabic_text_mode"
    bl_label = "Write Farsi Text"
    my_map: dict[int, Fa.Text] = {}
    
    def modal(self, context: Context, event: Event):
        
        # Use this handler only when a 3DText object is selected and being edited
        
        if context.object is None or context.object.type != 'FONT' or context.object.mode != 'EDIT':
        
            return {'PASS_THROUGH'}
        
        if id(context.object) not in self.my_map:
            self.my_map[id(context.object)] = Fa.Text(context.object.data.body)
        fa = self.my_map[id(context.object)]
        
        if event.type == 'BACK_SPACE':
            if event.value == 'PRESS':
                fa.delete_previous()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'DEL':
            if event.value == 'PRESS':
                fa.delete_next()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'HOME':
            if event.value == 'PRESS':
                fa.move_line_start()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'END':
            if event.value == 'PRESS':
                fa.move_line_end()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'RIGHT_ARROW':
            if event.value == 'PRESS':
                fa.move_previous()
            return {'RUNNING_MODAL'}
            
        elif event.type == 'LEFT_ARROW':
            if event.value == 'PRESS':
                fa.move_next()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'UP_ARROW':
            if event.value == 'PRESS':
                fa.move_up()
            return {'RUNNING_MODAL'}

        elif event.type == 'DOWN_ARROW':
            if event.value == 'PRESS':
                fa.move_down()
            return {'RUNNING_MODAL'}

        elif event.type == 'RET':
            if event.value == 'PRESS':
                fa.insert_char('\n')
            return {'RUNNING_MODAL'}
                   
        elif event.type == 'TAB':
            return {'PASS_THROUGH'}
            
        elif event.unicode:
            if event.value == 'PRESS':
                fa.insert_char(event.unicode)
            return {'RUNNING_MODAL'}
        
        elif event.type == 'V' and event.ctrl:
            if event.value == 'PRESS':
                pasted_text = bpy.context.window_manager.clipboard
                fa.insert_text(pasted_text)
            return {'RUNNING_MODAL'}
        
        return {'PASS_THROUGH'}
     
    #
        
    def invoke(self, context: Context, event: Event):
        
        if context.area.type == 'VIEW_3D':
            self.key = ""
            context.window_manager.modal_handler_add(self)
            if context.object is not None and context.object.type == 'FONT' and context.object.mode == 'EDIT':
                # update text data (i don't know a better way to do this)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}

from bpy.app.handlers import persistent

@persistent
def load_handler(dummy):
    # only apply to startup
    if not bpy.data.filepath:
        return
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            with bpy.context.temp_override(area = area):
                bpy.ops.view3d.arabic_text_mode('INVOKE_DEFAULT')
                break

def register():
    bpy.utils.register_class(__OT_FarsiTextMode)

    bpy.app.handlers.load_post.append(load_handler)
    
def unregister():
    bpy.utils.unregister_class(__OT_FarsiTextMode)

if __name__ == "__main__":
    register()
