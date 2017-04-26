#todo  make single for SP bake


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

import bpy , os , sys , random , subprocess

class nztprops(bpy.types.PropertyGroup):
    bakemeshespath=bpy.props.StringProperty(subtype="DIR_PATH", default='//bake-meshes')
    engineroot= bpy.props.StringProperty(subtype="DIR_PATH")
    packerpath= bpy.props.StringProperty(subtype="FILE_PATH",default='C:\steam\steamapps\common\IPackThat\IPackThat.exe')

    unity5=bpy.props.BoolProperty()
    
    
class nztroot(bpy.types.PropertyGroup):
    is_lopo_root=bpy.props.BoolProperty(description='is this object root-parent of a set of lowpoly chunks')
    hipo_target=bpy.props.StringProperty(description='name of hipoly root-parent corresponding to this lowpoly') 
    


class OpNZTGameAssetPrepLoPo(bpy.types.Operator):
    "prepare meshes for hipoly and texturing"
    bl_idname = "scene.nzt_prep_lo"
    bl_label = "Prep Lowpoly"
    
     
    def execute(self, context):
        lopos=[]
            
        for ob in bpy.context.selected_objects:
            if ob.type=='MESH':
                lopos.append(ob)    
        for ob in lopos:
            if ob.name.endswith('-lopo'):
                pass
            else:
                for group in ob.users_group:
                    if group.name == 'extra':
                        pass
                else:
                    ob.name = ob.name+'-lopo'

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.context.scene.cursor_location[2]=0
        bpy.ops.object.add()
        activeob=bpy.context.scene.objects.active
        activeob.empty_draw_type='CIRCLE'
        activeob.nztroot.is_lopo_root=True
        
        N=0
        for ob in bpy.data.objects:
            if ob.name.startswith('asset'):
                N=N+1
        assetname='asset'+str(N)
                
        activeob.name=assetname

        for ob in lopos:
            ob.select=True
        bpy.context.scene.objects.active=bpy.data.objects[assetname]        
        bpy.ops.object.parent_set(keep_transform=True)    
        return {'FINISHED'}
    
    




class OpNZTGameAssetPrepHiPo(bpy.types.Operator):
    "prepare meshes for hipoly and texturing"
    bl_idname = "scene.nzt_prep_hi"
    bl_label = "Prep Hipoly"
    
     
    def execute(self, context):
        for ob in bpy.context.selected_objects:
            if ob.type=='EMPTY':
                ob.nztroot.hipo_target = ob.name.split('.')[0]+'root-hipo' 
        
        
        bpy.ops.object.duplicate_move() 
        
        for ob in bpy.context.selected_objects:
            if ob.type=='MESH':
                ob.name = ob.name.replace('-lopo','-hipo')           
                ob.name = ob.name.split('.')[0] 
            if ob.type=='EMPTY':
                ob.name = ob.name.split('.')[0]+'root-hipo' 
                ob.nztroot.is_lopo_root=False
                ob.nztroot.hipo_target=''
        
                                        
        return {'FINISHED'}

class OpNZTextrasDataNamefromObject(bpy.types.Operator):
    "rename object data as object's name"
    bl_idname = "scene.nzt_renamedata"
    bl_label = "rename data"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            ob.data.name=ob.name
        
        return {'FINISHED'}

class OpNZTextrasSwitchMatType(bpy.types.Operator):
    "switch materials between data and object link type"
    bl_idname = "scene.nzt_switchmattype"
    bl_label = "switch material link type"

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            for slot in ob.material_slots:
                if slot.link=='OBJECT':
                    slot.link='DATA'
                else:     
                    slot.link='OBJECT'
        
        return {'FINISHED'}
    
    




class OpNZTGameAssetExport(bpy.types.Operator):
    "export meshes for game asset"
    bl_idname = "scene.nzt_export"
    bl_label = "Export Asset"
     
    def execute(self, context):

        print('exporting current scene game assets ')
        roots=[]
        for obj in bpy.context.visible_objects:


# create list of export assets from parenting and names:

            if obj.type=='EMPTY':
                if obj.nztroot.is_lopo_root==True:
                    roots.append(obj)    

        for root in roots:
            
            
            
#set cursor to asset pivot
            bpy.context.scene.objects.active=root
            
            bpy.ops.view3d.snap_cursor_to_active()

#Select parts of asset    
            bpy.ops.object.select_pattern(pattern=root.name,extend=False)
            bpy.ops.object.select_hierarchy(direction='CHILD')

#create copy of parts for export , apply modifiers

            bpy.ops.object.duplicate()

# set all obs to use object material, used to have a different set of mat names in unity            
            for ob in bpy.context.selected_objects:
                bpy.context.scene.objects.active=ob
                for slot in ob.material_slots:
                    slotmat=slot.material
                    slot.link='OBJECT'
                    if slot.material==None:       
                        slot.material=slotmat
            
            bpy.context.scene.objects.active=bpy.context.selected_objects[0]

            bpy.ops.object.duplicates_make_real()
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True)
            bpy.ops.object.convert(target='MESH')
            
            
# prepare each part for join:

    # fix negative scaling causing flipped normals on join   

            scn = bpy.context.scene
            sel = bpy.context.selected_objects
            meshes = [o for o in sel if o.type == 'MESH']


            for obj in meshes:
                scn.objects.active = obj
                
                
    #clear deltas used for exploded bake
                obj.delta_location=[0,0,0]            
                
                
                scale=obj.scale

                if scale[0]<0 or scale[1]<0 or scale[2] <0 :

                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT')

                    bpy.ops.mesh.flip_normals() # just flip normals

                    bpy.ops.object.mode_set()
            
    # normals cleanup , fix join with custom normal parts
                
        #if mesh is using auto-smooth apply it as sharp edges , then  add custom normals        
                if obj.data.use_auto_smooth==True and obj.data.has_custom_normals==False:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.mesh.edges_select_sharp(sharpness=obj.data.auto_smooth_angle)                    
                    bpy.ops.mesh.mark_sharp()
                    bpy.ops.object.mode_set()    
                obj.data.use_auto_smooth=True

                bpy.ops.mesh.customdata_custom_splitnormals_add()   

            
    #UVs cleanup    
                print('uv-cleanup of ',obj.name)

                UVs=obj.data.uv_layers
                
                if UVs:

        # 1st channel always renamed uv0 , 2nd = uv1
                
                    UVs[0].name='uv0'
        
                    
                    if len(UVs) ==1 :
                        
                        bpy.ops.mesh.uv_texture_add()
                        UVs[1].name ='uv1'                    
                        print('1uv found adding copy for lm')
                        
                    elif len(UVs) >=2 :
                        
                        if UVs[1].name =='uv1':
                            pass
                            print('custom lm found')
                        else:    
                            obj.data.uv_textures.active=obj.data.uv_textures[1]
                            bpy.ops.mesh.uv_texture_remove()
                            bpy.ops.mesh.uv_texture_add()
                            UVs[1].name ='uv1'
                            print('2nd uv not named, copying 1 to 2 for lm')

                else:
                    bpy.ops.uv.smart_project()
                    UVs[0].name='uv0'
                    bpy.ops.mesh.uv_texture_add()
                    UVs[1].name ='uv1'
                    print('no UVs found, adding dummy')


# join mesh parts of asset, unparent and weld verts.

            bpy.ops.object.join()
            
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.001)

            bpy.ops.object.mode_set()
            scn.objects.active = bpy.context.selected_objects[0]
            scn.objects.active.name =root.name+'-joined'

            obj=bpy.data.objects[root.name+'-joined']           

# forced repack of channel 1..

            obj.data.uv_textures.active=obj.data.uv_textures[1]
                
            bpy.ops.object.editmode_toggle()
 
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')
                            
            Di=obj.dimensions
            obscale=max(Di)   
            
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.average_islands_scale()
            bpy.ops.uv.pack_islands(rotate=False, margin=(0.002/obscale))
            origarea = bpy.context.area.type
            bpy.context.area.type = 'IMAGE_EDITOR'
            bpy.ops.transform.resize(value=(obscale,obscale,obscale))
            bpy.context.area.type = origarea

#  weld verts.
            bpy.ops.object.mode_set()
            
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.001)

            bpy.ops.object.mode_set()
                 
             

# apply transform and set orignin to asset root empty location

            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')            

# save asset as fbx

#            exppath=bpy.path.abspath(bpy.context.scene.render.filepath)+root.name[:-10]+'.fbx'
        
        bpy.ops.object.select_all(action='DESELECT')
        for root in roots:
            joinedroot=bpy.data.objects[(root.name+'-joined')]
            joinedroot.select=True
# check if root has a parent and sibling roots to export toghether
            
            if root.parent !=None :
                for sibling in root.parent.children:
                    extrajoinedroot=bpy.data.objects[(sibling.name+'-joined')]    
                    extrajoinedroot.select=True
                    roots.remove(sibling)
                    extrajoinedroot.name='-'+extrajoinedroot.name[:-7]
                    
                scn.objects.active=joinedroot            
                
                filename=root.parent.name
                

# single object export            
            else:
                filename=root.name
                scn.objects.active=joinedroot
                scn.objects.active.location=[0,0,0,]            
            

            expdir=bpy.path.abspath(bpy.context.scene.nztprops.engineroot)
            exppath=expdir+filename+'.fbx'
            if not os.path.exists(expdir):
                os.makedirs(expdir)


            bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,use_anim=False,apply_unit_scale=not(bpy.context.scene.nztprops.unity5))

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
            if obj.type=='EMPTY' and obj.nztroot.is_lopo_root==True:
                roots.append(obj)    
                roots.append(bpy.data.objects[obj.nztroot.hipo_target])
                
        steps=['lo','hi']
        
        for step in steps:
            
            print('exporting '+step+' meshes')
            steproots=[]
                            
            for root in roots:
                if root.nztroot.is_lopo_root==False:
                    if step =='hi':
                       steproots.append(root)                      
                    else:
                       pass 
                elif root.nztroot.is_lopo_root==True:
                    if step =='lo':
                       steproots.append(root)                     
                    else:
                        pass
 

            bpy.ops.object.select_all(action='DESELECT')
            for root in steproots:
                bpy.ops.object.select_pattern(pattern=root.name,extend=True)
                bpy.context.scene.objects.active=root
                bpy.ops.object.select_hierarchy(direction='CHILD',extend=True)

                exppath=bpy.path.abspath(bpy.context.scene.nztprops.bakemeshespath)+'\\'+bpy.context.scene.name +'-'+step+'.fbx'
                print('started export', exppath)
                bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,apply_unit_scale=False)

        return {'FINISHED'}

class OpNZTPackExport(bpy.types.Operator):
    "export mesh for IPack That "
    bl_idname = "scene.nzt_packexport"
    bl_label = "Export for UVPack"
     
    def execute(self, context):

        print('exporting for uv pack')
        exppath=bpy.path.abspath((bpy.context.scene.nztprops.bakemeshespath)+'\packme.fbx')
        packapp= (bpy.context.scene.nztprops.packerpath) 

        obj=bpy.context.selected_objects[0]

        obname=obj.name
        
        obj.name='packme-temp'

        bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,apply_unit_scale=False)

        subprocess.run(str(packapp+' '+exppath))
        
        bpy.ops.import_scene.fbx(filepath=(exppath),global_scale=1)
        
        bpy.ops.object.select_pattern(pattern='packme-temp',extend=False)
        bpy.context.scene.objects.active=bpy.data.objects['packme-temp.001']
        bpy.ops.object.join_uvs()
    
        bpy.ops.object.select_pattern(pattern='packme-temp.001',extend=False)    
        bpy.ops.object.delete()    

        bpy.data.objects['packme-temp'].name=obname

      
        return {'FINISHED'}

class OpNZTorigintoselected(bpy.types.Operator):
    "set pivot to current selected vert, edge or face"
    bl_idname = "object.nzt_origintoselected"
    bl_label = "origin to selected"
    
    def execute(self, context):

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}
    
# outdated, weight normals by Simon Lusenc is better than this.






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
        row.label(text="mesh export paths:  ", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(bpy.context.scene.nztprops,"engineroot",text='game')
        row = layout.row()
        row.prop(bpy.context.scene.nztprops,"bakemeshespath",text='bake')
        row = layout.row()
        row.prop(bpy.context.scene.nztprops,"unity5",text='unity5 scale')
        row = layout.row()
        row.prop(bpy.context.scene.nztprops,"packerpath",text='uvpack app')
    

        row = layout.row()
        row.label(text="Export ops :", icon='EXPORT')
        row = layout.row()
        row.operator("scene.nzt_bakeexport")
        row = layout.row()
        row.operator("scene.nzt_packexport")
        row = layout.row()
        row.operator("scene.nzt_export")

        row = layout.row()
        row.label(text="mesh prep. ops:", icon='MESH_ICOSPHERE')
  
        row = layout.row()
        row.operator("scene.nzt_prep_lo")
        row = layout.row()
        row.operator("scene.nzt_prep_hi")
        
        row = layout.row()
        row.label(text="extra/cleanup ops:", icon='MESH_ICOSPHERE')
        row = layout.row()
        row.operator("scene.nzt_renamedata")
        row = layout.row()
        row.operator("scene.nzt_switchmattype")

        
        row = layout.row()
        row.label(text="Modelling Tools", icon='MESH_CUBE')
        row = layout.row()
        row.operator("object.calculate_weighted_normals")
        row = layout.row()
        row.operator("mesh.customdata_custom_splitnormals_clear")
        row = layout.row()

        row.operator("object.nzt_origintoselected")
        
        row = layout.row()
        row.label(text="NZT Object properties", icon='MESH_CUBE')
        row = layout.row()
        ob=bpy.context.object    
        if ob.type=='EMPTY':
            row.prop(bpy.context.object.nztroot,"is_lopo_root", text='Lowpoly root')
            if bpy.context.object.nztroot.is_lopo_root==True :
                row = layout.row()
                row.prop(bpy.context.object.nztroot,"hipo_target", text='hipoly:')
                     

def register():
    bpy.utils.register_class(nztprops)
    bpy.types.Scene.nztprops = bpy.props.PointerProperty(type=nztprops)

    bpy.utils.register_class(nztroot)
    bpy.types.Object.nztroot = bpy.props.PointerProperty(type=nztroot)
    
    
    
    bpy.utils.register_class(NZTPanel)
    bpy.utils.register_class(OpNZTGameAssetExport)
    bpy.utils.register_class(OpNZTBakeExport)
    bpy.utils.register_class(OpNZTPackExport)

    bpy.utils.register_class(OpNZTGameAssetPrepLoPo)
    bpy.utils.register_class(OpNZTGameAssetPrepHiPo)
    bpy.utils.register_class(OpNZTextrasDataNamefromObject)
    bpy.utils.register_class(OpNZTextrasSwitchMatType)

    bpy.utils.register_class(OpNZTorigintoselected)


def unregister():
    bpy.utils.unregister_class(nztprops)
    del(bpy.types.Scene.nztprops)
    
    bpy.utils.unregister_class(nztroot)
    del(bpy.types.Object.nztroot)
    
    
    bpy.utils.unregister_class(NZTPanel)
    bpy.utils.unregister_class(OpNZTGameAssetExport)
    bpy.utils.unregister_class(OpNZTBakeExport)
    bpy.utils.unregister_class(OpNZTPackExport)

    bpy.utils.unregister_class(OpNZTGameAssetPrepLoPo)
    bpy.utils.unregister_class(OpNZTGameAssetPrepHiPo)
    bpy.utils.unregister_class(OpNZTextrasDataNamefromObject)
    bpy.utils.unregister_class(OpNZTextrasSwitchMatType)    

    bpy.utils.unregister_class(OpNZTorigintoselected)


if __name__ == "__main__":
    register()
