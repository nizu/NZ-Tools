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

class NZTGASobject(bpy.types.PropertyGroup):
    is_lopo_chunk = bpy.props.BoolProperty()
    is_additional = bpy.props.BoolProperty()
    my_string = bpy.props.StringProperty()

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

#                put_on_layers = lambda x: tuple((i in x) for i in range(20))
#                ob.layers[:] = put_on_layers({2,6,5,11})
#            
#            
#            ob.layers[counter] = True
#            #wipe other layers
#            for i in range(20):
#                ob.layers[i] = (i == counter)
#            
            
                                        
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
            exppath='C:\\unityprojects\\Metris Soccer - Base\\Metris Soccer - Base\\Assets\\Floating-Field\\'+astype+'\\'+root.name[3:]+'.fbx'
            bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,use_anim=False)

            bpy.ops.object.delete()
#        
#        # export to blend file location
#        scene = bpy.context.scene
#        obj_active = scene.objects.active

#        def step_export(step):    

#            exppath = bpy.path.abspath(bpy.context.scene.render.filepath)+scene.name+'-'+step+'.fbx'
#                
#            bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF')
#                
#            
#            print("written:", scene.name,step)

#        selection = []

#        for step in ['bake-lopo','bake-hipo','output-assets']:
#            bpy.ops.object.select_all(action='DESELECT')
#        
#            if step == 'bake-lopo' :       
#                bpy.ops.object.select_pattern(pattern='*-lo',extend=False)
#                bpy.ops.object.select_pattern(pattern='*-addlo',extend=True)            
#                step_export(step)

#            elif step == 'bake-hipo':
#                bpy.ops.object.select_pattern(pattern='*-hi',extend=False)
#                bpy.ops.object.select_pattern(pattern='*-addhi',extend=True)            
#                step_export(step)
#                
#            elif step == 'output-assets':
##               for group in ...                                       
#                pass

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
                else:
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


def register():
    bpy.utils.register_class(NZTGASobject)
    bpy.types.Object.GASobj = bpy.props.PointerProperty(type=NZTGASobject)

    bpy.utils.register_class(NZTPanel)
    bpy.utils.register_class(OpNZTGameAssetExport)
    bpy.utils.register_class(OpNZTBakeExport)

    bpy.utils.register_class(OpNZTGameAssetPrep1)
    bpy.utils.register_class(OpNZTGameAssetPrep2)


def unregister():
    bpy.utils.unregister_class(NZTGASobject)
#   Del gasobj ?

    bpy.utils.unregister_class(NZTPanel)
    bpy.utils.unregister_class(OpNZTGameAssetExport)
    bpy.utils.unregister_class(OpNZTBakeExport)

    bpy.utils.unregister_class(OpNZTGameAssetPrep1)
    bpy.utils.unregister_class(OpNZTGameAssetPrep2)


if __name__ == "__main__":
    register()
