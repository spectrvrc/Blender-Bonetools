bl_info = {
    "name": "blender_bonetools",
    "author": "Spectr",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Bone Tools",
    "description": "Tools for working with bones",
    "warning": "",
    "category": "Object",
}

import bpy

class OBJECT_OT_reorder_child_bones(bpy.types.Operator):
    bl_idname = "object.reorder_child_bones"
    bl_label = "Apply Reordering"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        
        parent_bone_name = armature.selected_bone_name
        parent_bone = armature.data.edit_bones.get(parent_bone_name)
        
        print(f"\nReordering children of '{parent_bone_name}':")

        # Disconnect each child bone
        for child in parent_bone.children:
            print(f"Detaching {child.name} from {parent_bone_name}")
            child.parent = None
        
        # Reconnect the child bones in the specified order to the parent bone
        for item in armature.ChildBonesCollection:
            bone = armature.data.edit_bones.get(item.name)
            print(f"Attaching {bone.name} to {parent_bone_name}")
            bone.parent = parent_bone
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class OBJECT_OT_move_child_bone(bpy.types.Operator):
    bl_idname = "object.move_child_bone"
    bl_label = "Move Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    direction: bpy.props.EnumProperty(items=[('UP', 'Up', ""), ('DOWN', 'Down', "")])
    idx: bpy.props.IntProperty()

    def execute(self, context):
        armature = context.active_object
        index = self.idx
        
        if self.direction == 'UP' and index > 0:
            armature.ChildBonesCollection.move(index, index-1)
            armature.active_child_bone_index = index - 1
        elif self.direction == 'DOWN' and index < len(armature.ChildBonesCollection) - 1:
            armature.ChildBonesCollection.move(index, index+1)
            armature.active_child_bone_index = index + 1
            
        return {'FINISHED'}

class OBJECT_PT_reorder_child_bones(bpy.types.Panel):
    bl_label = "Reorder Child Bones"
    bl_idname = "OBJECT_PT_reorder_child_bones"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Spectr'

    def draw(self, context):
        layout = self.layout
        armature = context.active_object

        if armature and armature.type == 'ARMATURE':
            layout.prop_search(armature, "selected_bone_name", armature.data, "bones", text="Parent Bone")
            if armature.selected_bone_name:
                parent_bone = armature.data.bones.get(armature.selected_bone_name)
                if parent_bone:
                    for idx, item in enumerate(armature.ChildBonesCollection):
                        row = layout.row(align=True)
                        row.label(text=item.name)
                        op_up = row.operator("object.move_child_bone", text="", icon="TRIA_UP")
                        op_up.direction = 'UP'
                        op_up.idx = idx
                        op_down = row.operator("object.move_child_bone", text="", icon="TRIA_DOWN")
                        op_down.direction = 'DOWN'
                        op_down.idx = idx

                    layout.operator("object.reorder_child_bones")

        else:
            layout.label(text="Please select an armature")

def update_selected_bone(self, context):
    armature = context.active_object
    armature.ChildBonesCollection.clear()
    parent_bone = armature.data.bones.get(self.selected_bone_name)
    if parent_bone:
        print(f"\nChildren of '{self.selected_bone_name}':")
        for child_bone in parent_bone.children:
            item = armature.ChildBonesCollection.add()
            item.name = child_bone.name
            print(child_bone.name)

def register_properties():
    bpy.types.Object.selected_bone_name = bpy.props.StringProperty(name="Selected Bone Name", update=update_selected_bone)
    bpy.types.Object.active_child_bone_index = bpy.props.IntProperty(default=-1)

    bpy.types.Object.ChildBonesCollection = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

def unregister_properties():
    del bpy.types.Object.selected_bone_name
    del bpy.types.Object.active_child_bone_index
    del bpy.types.Object.ChildBonesCollection

def register():
    bpy.utils.register_class(OBJECT_OT_reorder_child_bones)
    bpy.utils.register_class(OBJECT_OT_move_child_bone)
    bpy.utils.register_class(OBJECT_PT_reorder_child_bones)
    register_properties()

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_reorder_child_bones)
    bpy.utils.unregister_class(OBJECT_OT_move_child_bone)
    bpy.utils.unregister_class(OBJECT_PT_reorder_child_bones)
    unregister_properties()

if __name__ == "__main__":
    register()