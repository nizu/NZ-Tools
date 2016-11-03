#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------
 
#    Addon info
bl_info = {
    'name': 'NiZu-ToolS',
    'author': 'Ni Zu',
    'location': 'scene panel',
    'category': 'Scene'
    }

import bpy , os , sys , random


class OpNZTGameAssetPrep1(bpy.types.Operator):
    "prepare meshes for hipoly and texturing"
    bl_idname = "scene.nzt_prep1"
    bl_label = "Prep Lowpoly"
    
     
    def execute(self, context):
        lopos=[]
            
        for ob in bpy.context.selected_objects:
            if ob.type=='MESH':
                lopos.append(ob)    
        print(lopos)        
        for ob in lopos:
            print('---'+ob.name)
            ob.name = ob.name+'-lopo'
            
                
        return {'FINISHED'}


class OpNZTGameAssetPrep2(bpy.types.Operator):
    "prepare meshes for hipoly and texturing"
    bl_idname = "scene.nzt_prep2"
    bl_label = "Prep Hipoly"
    
     
    def execute(self, context):
        bpy.ops.object.duplicate_move() 
        
        for ob in bpy.context.selected_objects:
            if ob.type=='MESH':
                ob.name = ob.name.replace('-lopo','-hipo')           
                ob.name = ob.name.split('.')[0] 
            if ob.type=='EMPTY':
                ob.name = ob.name.replace('root','root-hipo')           
                ob.name = ob.name.split('.')[0] 

        
                                        
        return {'FINISHED'}


class OpNZTGameAssetExport(bpy.types.Operator):
    "export meshes for game asset"
    bl_idname = "scene.nzt_export"
    bl_label = "Export Asset"
     
    def execute(self, context):

        print('exporting current Game Asset Scene meshes ')
        roots=[]
        for obj in bpy.context.visible_objects:
            if obj.type=='EMPTY':
                if obj.name.startswith('AS-'):
                    roots.append(obj)    
        for root in roots:
            bpy.ops.object.select_pattern(pattern=root.name,extend=False)
            
            bpy.context.scene.objects.active=root

            bpy.ops.object.select_hierarchy(direction='CHILD')
             
            bpy.ops.object.duplicate()
             
            bpy.ops.object.duplicates_make_real()

            bpy.context.scene.objects.active=bpy.context.selected_objects[0]
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
            bpy.ops.object.convert(target='MESH')

            # un-flip
            scn = bpy.context.scene
            sel = bpy.context.selected_objects
            meshes = [o for o in sel if o.type == 'MESH']


            for obj in meshes:
                scn.objects.active = obj


                scale=obj.scale

                if scale[0]<0 or scale[1]<0 or scale[2] <0 :

                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT')

                    bpy.ops.mesh.flip_normals() # just flip normals

                    bpy.ops.object.mode_set()
            
            #UVs cleanup    
                print(obj.name)

                try:
                    obj.data.uv_layers[0].name='uv0'
        
                    
                    if len(obj.data.uv_layers) ==1 :
                        
                        bpy.ops.mesh.uv_texture_add()
                        obj.data.uv_layers[1].name ='uv1'                    
                        print('1uv found adding copy for lm')
                        
                    elif len(obj.data.uv_layers) ==2 :
                        
                        if obj.data.uv_layers[1].name =='uv1':
                            pass
                            print('custom lm found')
                        else:    
                            obj.data.uv_textures.active=obj.data.uv_textures[1]
                            bpy.ops.mesh.uv_texture_remove()
                            bpy.ops.mesh.uv_texture_add()
                            obj.data.uv_layers[1].name ='uv1'
                            print('2uvs found resetting 2 for lm')

                    else:
                        print('unexpected')
                except:
                    pass                                

            bpy.ops.object.join()
            scn.objects.active = bpy.context.selected_objects[0]
            scn.objects.active.name         =root.name[3:]
                       
            if bpy.context.selected_objects[0].type=='MESH':
                jobj = bpy.context.selected_objects[0]
#                try:
#                    jobj.data.uv_textures.active=jobj.data.uv_textures[1]
#                    bpy.ops.mesh.uv_texture_remove()
#                    
#                except:
#                    pass
#                
#                bpy.ops.mesh.uv_texture_add()
                
                jobj.data.uv_textures.active=obj.data.uv_textures[1]

                jobj.data.use_auto_smooth=True
                
                bpy.ops.object.editmode_toggle()
                
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='SELECT')
                                
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.average_islands_scale()
                bpy.ops.uv.pack_islands()
                bpy.ops.object.mode_set()
                 
             
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
            if bpy.context.scene.name=='props':
                astype='props'
            else:
                astype='set-pieces'
            exppath='bpy.context.scene.render.filepath' +'\\'+root.name[3:]+'.fbx'
            bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,use_anim=False)

            bpy.ops.object.delete()

        return {'FINISHED'}

class OpNZTBakeExport(bpy.types.Operator):
    "export bake meshes for game asset"
    bl_idname = "scene.nzt_bakeexport"
    bl_label = "Export for bake"
     
    def execute(self, context):

        print('exporting bake meshes ')
        roots=[]
        for obj in bpy.context.visible_objects:
            if obj.type=='EMPTY':
                roots.append(obj)    
 
        steps=['lo','hi']
        
        for step in steps:
            
            print('exporting '+step+' meshes')
            steproots=[]
                            
            for root in roots:
                if root.name.endswith('-hipo'):
                    if step =='hi':
                       steproots.append(root)                      
                    else:
                       pass 
                elif root.name.endswith('-lopo'):
                    if step =='lo':
                       steproots.append(root)                     
                    else:
                        pass
 

            bpy.ops.object.select_all(action='DESELECT')
            for root in steproots:
                bpy.ops.object.select_pattern(pattern=root.name,extend=True)
                bpy.ops.object.select_hierarchy(direction='CHILD',extend=True)
                exppath=bpy.path.abspath('//bake-meshes')+'\\'+bpy.context.scene.name +'-'+step+'.fbx'
                print(exppath)
                bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True)

        return {'FINISHED'}
class OpNZTcustomNormalFacesAverage(bpy.types.Operator):
    "average normals of selected faces"
    bl_idname = "object.nzt_custnormfaceavg"
    bl_label = "faces average"
     
    def execute(self, context):

        #start in edit mode having selected all 'flat' faces, those which that aren't bevels or transition areas.

        #To object mode , set smooth
        bpy.ops.object.editmode_toggle()
        obj=bpy.context.active_object
        obj.data.use_auto_smooth=True

        bpy.ops.object.shade_smooth()

        #To edit mode , create vertgroup with selected flat faces
        bpy.ops.object.editmode_toggle()

        try :
            obj.vertex_groups.remove(obj.vertex_groups['NZT-flatfaces'])
        except: pass

        bpy.ops.object.vertex_group_add()
        obj.vertex_groups.active.name='NZT-flatfaces'
        bpy.ops.object.vertex_group_assign()

        #To object mode , create obj2 to copy normals from
        bpy.ops.object.editmode_toggle()

        bpy.ops.object.duplicate()
        obj2=bpy.context.active_object
        obj2.name=obj2.name.split('.')[0]+'-vertnorm-source'

        #To edit mode  remove unselected faces (bevels) from object
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='FACE')

        #To object mode , hide obj2 add data transf modif to obj1

        obj2.hide=True
        obj.select=True
        bpy.context.scene.objects.active=obj
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        obj.modifiers['DataTransfer'].object=obj2
        obj.modifiers['DataTransfer'].use_loop_data=True
        obj.modifiers['DataTransfer'].data_types_loops={'CUSTOM_NORMAL'}

        return {'FINISHED'}




##########################
####   USER INTERFACE
##########################


class NZTPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "NiZu-Tools Shelf"
    bl_idname = "OBJECT_PT_NZT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'NZT'   

    def draw(self, context):
        layout = self.layout

        sce = context.scene

        row = layout.row()
        row.label(text="Game Asset Scene", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Name: " + sce.name)
        row = layout.row()
#        row.prop(sce.objects.active.GASobj, "is_lopo_chunk")
#        row.prop(sce.objects.active.GASobj, "is_additional")
        
        row.operator("scene.nzt_bakeexport")
        row = layout.row()
        row.operator("scene.nzt_export")

        row = layout.row()
        row.operator("scene.nzt_prep1")
        row = layout.row()
        row.operator("scene.nzt_prep2")
        row = layout.row()
        row.operator("object.nzt_custnormfaceavg")

def register():

    bpy.utils.register_class(NZTPanel)
    bpy.utils.register_class(OpNZTGameAssetExport)
    bpy.utils.register_class(OpNZTBakeExport)

    bpy.utils.register_class(OpNZTGameAssetPrep1)
    bpy.utils.register_class(OpNZTGameAssetPrep2)
    bpy.utils.register_class(OpNZTcustomNormalFacesAverage)

def unregister():

    bpy.utils.unregister_class(NZTPanel)
    bpy.utils.unregister_class(OpNZTGameAssetExport)
    bpy.utils.unregister_class(OpNZTBakeExport)

    bpy.utils.unregister_class(OpNZTGameAssetPrep1)
    bpy.utils.unregister_class(OpNZTGameAssetPrep2)
    bpy.utils.unregister_class(OpNZTcustomNormalFacesAverage)


if __name__ == "__main__":
    register()
