#todo  make single for SP bake


#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------
 
#    Addon info
bl_info = {
    'name': 'NiZu-ToolS',
    'author': 'Ni Zu',
    'location': '3D view',
    'category': 'Scene',
    "version": (0, 42)
    }

import bpy , os , sys , random , subprocess

context=bpy.context
sce=context.scene




class nztprops(bpy.types.PropertyGroup):
    bakemeshespath:bpy.props.StringProperty(subtype="DIR_PATH", default='//bake-meshes')
    engineroot: bpy.props.StringProperty(subtype="DIR_PATH")
    packerpath: bpy.props.StringProperty(subtype="FILE_PATH",default='C:\steam\steamapps\common\IPackThat\IPackThat.exe')

    unity5:bpy.props.BoolProperty()
    writefbx:bpy.props.BoolProperty(description='complete export writing fbx or just place objects in staging scene')
    
    
class nztroot(bpy.types.PropertyGroup):
    is_lopo_root:bpy.props.BoolProperty(description='is this object the root-parent of a set of lowpoly chunks, for baking')
    is_asset_root:bpy.props.BoolProperty(description='is this object the root-parent of a set of lowpoly chunks, for export')
    
    hipo_target:bpy.props.StringProperty(description='name of hipoly root-parent corresponding to this lowpoly') 
    
    lock_uv1:bpy.props.BoolProperty(description='lock 2nd uv channel, if disabled uv1 will be a non-overlapping repack of all islands in all lowpoly chunks')
    
    lightmap_uv1:bpy.props.BoolProperty(description='if enabled uv1 will be repacked to 0-1 space for lightmap, if disabled it will be scaled to have consistent scale between objects, for detailmaps') 
    
    
    uv1_padding:bpy.props.FloatProperty(default=0.006,description= 'padding for uv1 repack')
                
    uv1_scale:bpy.props.FloatProperty(default=1,description= 'scale for uv1 repack')
               
#class NZTprepcollections(bpy.types.Operator):
#    """prepare meshes for hipoly and texturing"""
#    bl_idname="scene.nztprepcollections"    
#    bl_label= "Prepare standard collections"
#    
#     
#    def execute(self, context):
#    
#        lopocollname=
#        bpy.data.collections.new(name=lopocollname)    
#        if not 'low-poly' in bpy.data.collections:    
#            bpy.data.collections.new(name='low-poly')
#        bpy.data.collections['low-poly'].children.link(bpy.data.collections[lopocollname])
#    
#    
#        return {'FINISHED'}
    


########################################
#
#    PREPARE OPERATORS
#
########################################

class NZTpreplopo(bpy.types.Operator):
    """prepare meshes for hipoly and texturing"""
    bl_idname="scene.nztpreplopo"    
    bl_label= "Prep Lowpoly"
    bl_options= {'REGISTER','UNDO'}
    
    assetname = bpy.props.StringProperty(default='x-asset')
    
     
    def execute(self, context):
    
#        N=0
#        for ob in bpy.data.objects:
#            if ob.name.startswith('x-asset'):
#                N=N+1
#        defassetname='x-asset-'+str(N) #.zfill(2)
        
        bpy.ops.ed.undo_push()
        lopos=[]

        for ob in context.selected_objects:
            if ob.type=='MESH':
                lopos.append(ob)    
        for ob in lopos:
            if ob.name.endswith('-lopo'):
                ob.data.name = ob.name
                pass
            else:
#                for group in ob.users_group:
#                    if group.name == 'extra':
#                        pass
#                else:
                ob.name = ob.name+'-lopo'
                ob.data.name = ob.name
                
                
        bpy.ops.view3d.snap_cursor_to_selected()
        sce.cursor.location[2]=0
        bpy.ops.object.add()
        activeob=context.view_layer.objects.active
        activeob.empty_display_type='CIRCLE'
        activeob.nztroot.is_lopo_root=True
        activeob.nztroot.is_asset_root=True
                        
        activeob.name=self.assetname
        
        lopocollname=self.assetname
        
        if not lopocollname in bpy.data.collections:
            bpy.data.collections.new(name=lopocollname)    
        
        if not 'low-poly' in bpy.data.collections:    
            bpy.data.collections.new(name='low-poly')

        if not 'low-poly' in sce.collection.children:
            sce.collection.children.link(bpy.data.collections['low-poly'])
        
        if not lopocollname in bpy.data.collections['low-poly'].children:
            bpy.data.collections['low-poly'].children.link(bpy.data.collections[lopocollname])
    

        for ob in lopos:
            ob.select_set(True)
            context.view_layer.objects.active=ob
            bpy.ops.object.collection_link(collection='low-poly')
            bpy.ops.object.collection_link(collection=lopocollname)
      
        context.view_layer.objects.active=bpy.data.objects[self.assetname]        
        bpy.ops.object.parent_set(keep_transform=True)  
        bpy.ops.object.collection_link(collection='low-poly')
        
        
        return {'FINISHED'}
    
    




class OpNZTGameAssetPrepHiPo(bpy.types.Operator):
    "create a duplicate set of meshes for hipoly "
    bl_idname = "scene.nzt_prep_hi"
    bl_label = "Prep Hipoly"
    
     
    def execute(self, context):
        hipocollname=['lopo-root-not-found']
        for ob in context.selected_objects:
            if ob.type=='EMPTY':
                ob.nztroot.hipo_target = ob.name.split('.')[0]+'-root-hipo' 
                hipocollname=ob.name.replace('-lopo','') +'-hipo'        
        
        if not hipocollname in bpy.data.collections:
            bpy.data.collections.new(name=hipocollname)    
        
        if not 'high-poly' in bpy.data.collections:    
            bpy.data.collections.new(name='high-poly')
        
        if not 'high-poly' in sce.collection.children:
            sce.collection.children.link(bpy.data.collections['high-poly'])
        
        if not hipocollname in bpy.data.collections['high-poly'].children:
            bpy.data.collections['high-poly'].children.link(bpy.data.collections[hipocollname])
    
        
        
        bpy.ops.object.duplicate_move() 
        
        for ob in context.selected_objects:
            
            context.view_layer.objects.active=ob
            bpy.ops.object.collection_link(collection='high-poly')
            bpy.ops.object.collection_link(collection=hipocollname)

            bpy.data.collections['low-poly'].objects.unlink(ob)

            if ob.type=='MESH':
                ob.name = ob.name.replace('-lopo','-hipo')           
                ob.name = ob.name.split('.')[0] 
                ob.data.name = ob.name 

            if ob.type=='EMPTY':
                ob.name = ob.name.split('.')[0]+'root-hipo' 
                ob.nztroot.is_lopo_root=False
                ob.nztroot.hipo_target=''
                                        
        return {'FINISHED'}
    

class OpNZTPrepUVchannels(bpy.types.Operator):
    "add/prepare standard uv0-uv1 channels for selected objects"
    bl_idname = "scene.nzt_prepuvs"
    bl_label = "prep-uvs"
     
    def execute(self, context): 
        
        for obj in context.selected_objects:
            context.view_layer.objects.active=obj
            
        
            UVs=obj.data.uv_layers
            if UVs:

    # 1st channel always renamed uv0 , 2nd = uv1
            
                UVs[0].name='uv0'

                
                if len(UVs) ==1 :
                    
                    bpy.ops.mesh.uv_texture_add()
                    UVs[1].name ='uv1'                    
                    
                elif len(UVs) >=2 :
                    
                    if UVs[1].name =='uv1':
                        pass

    #                elif root.nztroot.lock_uv1 ==True:
    #                    HasUV1=True
    #                    UVs[1].name ='uv1'
    #                    print('custom uv1 found')
    #                    pass
    #                    

                    else:    
                        obj.data.uv_layers.active=obj.data.uv_layers[1]
                        UVs[1].name ='uv1'
     
            else:
                bpy.ops.uv.smart_project()
                UVs[0].name='uv0'
                bpy.ops.mesh.uv_texture_add()
                UVs[1].name ='uv1'
                print('no UVs found, adding dummy')  


        return {'FINISHED'}
 
########################################
#
#    EXPORT OPERATORS
#
########################################
    

class OpNZTGameAssetExport(bpy.types.Operator):
    "export meshes for game asset"
    bl_idname = "scene.nzt_export"
    bl_label = "Export Asset"
     
    def execute(self, context):

        print('exporting current scene game assets ')


# check if staging scene exists :
 
        origscene=context.scene
        sce=context.scene

        if  ('stg-'+sce.name ) in bpy.data.scenes:

        #cleanup stg--scn
            print('cleanup')
            
            context.window.scene=bpy.data.scenes[('stg-'+sce.name )]
            sce=context.scene            
            bpy.ops.object.select_all(action='DESELECT')


##### TODO cleanup using exported object collection

            for ob in sce.objects:
               if ob.type=='EMPTY':
                   ob.select_set(False)
               else:
                   ob.name='deleteme'
                   ob.data.name='deleteme'
                   ob.select_set(True)
            
            bpy.ops.object.delete()
            context.window.scene=origscene
            sce=context.scene
                
    #else create it
        else:
            bpy.ops.scene.new(type='EMPTY')    
            sce.name=('stg-'+origscene.name ) 
            context.window.scene=origscene
            sce=context.scene

# create list of export assets from parenting and names:


        roots=[]
        for obj in context.visible_objects:


            if obj.type=='EMPTY':
                if obj.nztroot.is_asset_root==True:
                    roots.append(obj)    





        for root in roots:
            
# toggle for repacking or not uv1 for roots with custom uv1
            if root.nztroot.lock_uv1==True:
                HasUV1=True
            else:
                HasUV1=False             
            
#set cursor to asset pivot
            context.view_layer.objects.active=root
            bpy.ops.view3d.snap_cursor_to_active()

#Select parts of asset    
            bpy.ops.object.select_pattern(pattern=root.name,extend=False)
            bpy.ops.object.select_hierarchy(direction='CHILD')

#create copy of parts for export, store selection list , apply modifiers

            bpy.ops.object.duplicate()
            context.view_layer.objects.active=context.selected_objects[0]
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True)
            bpy.ops.object.convert(target='MESH')

# set all obs to use object material, used to have a different set of mat names in unity            
# only replace by-object material assignment if not using that link mode already.


            for ob in context.selected_objects:
                context.view_layer.objects.active=ob
                for slot in ob.material_slots:
                    slotmat=slot.material
                    if slot.link=='DATA': 
                        slot.link='OBJECT'
                        slot.material=slotmat

  

# clear leftover empty parents in case dupligroups were used (broken, because make real leaves objects unselected now..)
            
            sel = context.selected_objects
            meshes = [ob for ob in sel if ob.type == 'MESH']
            bpy.ops.object.select_all(action='DESELECT')

##          bpy.ops.object.duplicates_make_real()


            for obj in sel:
                if obj.type=='EMPTY':
                    obj.select_set(True)
                    bpy.ops.object.delete(use_global=False)
    
            for obj in sel:
                obj.select_set(True)
            
            context.view_layer.objects.active=context.selected_objects[0]    
                        

# prepare each part for join:


            for obj in meshes:
                context.view_layer.objects.active = obj
                
                
    #clear deltas used for exploded bake
                obj.delta_location=[0,0,0]            
                
                
                scale=obj.scale
    # fix negative scaling causing flipped normals on join   

                if scale[0]<0 or scale[1]<0 or scale[2] <0 :

                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.reveal()

                    bpy.ops.mesh.select_all(action='SELECT')

                    bpy.ops.mesh.flip_normals() # just flip normals

                    bpy.ops.object.mode_set()
            
    # normals cleanup , fix join with custom normal parts
                
        #if mesh is using auto-smooth and has no custom data, apply automooth as sharp edges , then  add custom normals        

                if obj.data.use_auto_smooth==True and obj.data.has_custom_normals==False :
                    sharpangle=obj.data.auto_smooth_angle
                else:
                    sharpangle=180
                    obj.data.use_auto_smooth=True

                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='DESELECT')
                context.tool_settings.mesh_select_mode = (False,True,False)
                bpy.ops.mesh.edges_select_sharp(sharpness=sharpangle)                    
                bpy.ops.mesh.mark_sharp()

         #also make borders of mesh sharp                       
                bpy.ops.mesh.select_all(action='SELECT')
                    
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.mark_sharp()

                    
                bpy.ops.object.mode_set()    
                obj.data.use_auto_smooth=True

                bpy.ops.mesh.customdata_custom_splitnormals_add()   

            
    #UVs cleanup    


                UVs=obj.data.uv_layers
                if UVs:

        # 1st channel always renamed uv0 , 2nd = uv1
                
                    UVs[0].name='uv0'
        
                    
                    if len(UVs) ==1 :
                        
                        bpy.ops.mesh.uv_texture_add()
                        UVs[1].name ='uv1'                    
                        print('only 1  uv found, adding copy for lm')

                        HasUV1=False
                        
                    elif len(UVs) >=2 :
                        
                        if UVs[1].name =='uv1':
                            HasUV1=True
                            print('custom uv1 found')
                            pass

                        elif root.nztroot.lock_uv1 ==True:
                            HasUV1=True
                            UVs[1].name ='uv1'
                            print('custom uv1 found')
                            pass
                            

                        else:    
                            obj.data.uv_layers.active=obj.data.uv_layers[1]
                            bpy.ops.mesh.uv_texture_remove()
                            bpy.ops.mesh.uv_texture_add()
                            UVs[1].name ='uv1'
                            print('2nd uv not named, copying uv0 to uv1 for repack')

                else:
                    bpy.ops.uv.smart_project()
                    UVs[0].name='uv0'
                    bpy.ops.mesh.uv_texture_add()
                    UVs[1].name ='uv1'
                    print('no UVs found, adding dummy')


# join mesh parts of asset  and weld verts.

            bpy.ops.object.join()

            context.view_layer.objects.active = context.selected_objects[0]
            context.view_layer.objects.active.name =root.name+'-joined'
    
    
            dataname =(root.name+'-joined')[2:]
            for mesh in bpy.data.meshes:
                if mesh.name ==dataname:
                    mesh.name=dataname+'old' 
            
            context.view_layer.objects.active.data.name =dataname

                        
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.001)

            bpy.ops.object.mode_set()
            
            
            
            obj=bpy.data.objects[root.name+'-joined']           

## forced repack of channel 1..

            obj.data.uv_layers.active=obj.data.uv_layers[1]
            

            if HasUV1==False :
                bpy.ops.object.editmode_toggle()
     
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='SELECT')
                                
                Di=obj.dimensions
                obscale=(max(Di)+Di[0]+Di[0]+Di[0])*0.25   
                
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.average_islands_scale()

    #            bpy.ops.uv.shotgunpack()
                
                lmpadding=root.nztroot.uv1_padding
                
                lmscale=root.nztroot.uv1_scale
                                        
                bpy.ops.uv.pack_islands(rotate=False, margin=(lmpadding))

                if root.nztroot.lightmap_uv1==False:
                    origarea = context.area.type
                    context.area.ui_type = 'UV'
                    context.area.type = 'IMAGE_EDITOR'
                    bpy.ops.transform.resize(value=(obscale*lmscale,obscale*lmscale,obscale*lmscale))
                    context.area.type = origarea

#  weld verts.
            bpy.ops.object.mode_set()
            
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001      )

            bpy.ops.object.mode_set()
                 
             

# apply transform and set orignin to asset root empty location

            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')            




# Final links and parenting 

        
        bpy.ops.object.select_all(action='DESELECT')

        print ('-----------------final links:',roots)

# duplicate parents to export scene

        for root in roots:
            
            bpy.ops.object.select_all(action='DESELECT')
            
            
            if root.parent!=None and bpy.data.objects.get(root.parent.name[2:]) is None:
         
                
                bpy.ops.object.add()
                activeob=context.view_layer.objects.active
                activeob.empty_display_type='SINGLE_ARROW'
                activeob.name=root.parent.name[2:]
                activeob.location=root.parent.location
                bpy.ops.object.make_links_scene(scene=('stg-'+sce.name ))
                bpy.ops.object.delete()


##### TODO multiple levels of hierarchy, parents creation 



# re-parent joined objects

        for root in roots:
            print('start :',root.name)
            joinedroot=bpy.data.objects[(root.name+'-joined')]
            bpy.ops.object.select_all(action='DESELECT')

            joinedroot.select_set(True)
            context.view_layer.objects.active=joinedroot

            
                
            try:
                bpy.ops.object.parent_clear(type= 'CLEAR_KEEP_TRANSFORM')
                exportparent=bpy.data.objects[(root.parent.name[2:])]
                print('exportparent:  ', exportparent.name)
                joinedroot.parent=exportparent       
                joinedroot.matrix_parent_inverse = exportparent.matrix_world.inverted()

                print('parent assigned' )
            except:
                print ('parent skipped') 

            joinedroot.name=joinedroot.name[2:-7]            

# link joined objects To staging scene                
            bpy.ops.object.make_links_scene(scene=('stg-'+sce.name ))
            print('made links')
 
 
 
            bpy.ops.object.delete()
 
                        
        # go to staging scene
        origscene=context.scene
        context.window.scene=bpy.data.scenes[('stg-'+origscene.name )]
        sce=context.scene            
          
 
# in staging scene, export fbx file to game directory  

        if origscene.nztprops.writefbx:  
            expdir=bpy.path.abspath(sce.nztprops.engineroot)
            if not os.path.exists(expdir):
                os.makedirs(expdir)
        
            

# find each object with no parent (top level) to export as separate fbx file.
             
            toplevelobjects = [obj for obj in sce.objects if (obj.parent==None)]

            for obj in toplevelobjects:            
                bpy.ops.object.select_all(action='DESELECT')
                
                obj.select_set(True)
                context.view_layer.objects.active=obj
                bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
                
                filename=obj.name
                exppath=expdir+filename+'.fbx'

                bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,bake_anim=False,apply_unit_scale=not(sce.nztprops.unity5))
                        
 
 
 
        
            context.window.scene=origscene
            sce=context.scene

        print('finished')
        return {'FINISHED'}


class OpNZTBakeExport(bpy.types.Operator):
    "export bake meshes for game asset"
    bl_idname = "scene.nzt_bakeexport"
    bl_label = "Export for bake"
     
    def execute(self, context):

        print('exporting bake meshes ')
        roots=[]
        for obj in context.visible_objects:
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
                context.view_layer.objects.active=root
                bpy.ops.object.select_hierarchy(direction='CHILD',extend=True)

                exppath=bpy.path.abspath(sce.nztprops.bakemeshespath)+'\\'+sce.name +'-'+step+'.fbx'
                print('started export', exppath)
                bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,apply_unit_scale=False)

        return {'FINISHED'}

class OpNZTPackExport(bpy.types.Operator):
    "export mesh for IPack That "
    bl_idname = "scene.nzt_packexport"
    bl_label = "Export for UVPack"
     
    def execute(self, context):

        print('exporting for uv pack')
        exppath=bpy.path.abspath((sce.nztprops.bakemeshespath)+'\packme.fbx')
        packapp= (sce.nztprops.packerpath) 

        obj=context.selected_objects[0]

        obname=obj.name
        
        obj.name='packme-temp'

        bpy.ops.export_scene.fbx(filepath=(exppath),use_selection=True, global_scale=1, check_existing=False, mesh_smooth_type='OFF', bake_space_transform=True,apply_unit_scale=False)

        subprocess.run(str(packapp+' '+exppath))
        
        bpy.ops.import_scene.fbx(filepath=(exppath),global_scale=1)
        
        bpy.ops.object.select_pattern(pattern='packme-temp',extend=False)
        context.view_layer.objects.active=bpy.data.objects['packme-temp.001']
        bpy.ops.object.join_uvs()
    
        bpy.ops.object.select_pattern(pattern='packme-temp.001',extend=False)    
        bpy.ops.object.delete()    

        bpy.data.objects['packme-temp'].name=obname

      
        return {'FINISHED'}
    
########################################
#
#    EXTRA OPERATORS
#
########################################    
    
    
class OpNZTextrasDataNamefromObject(bpy.types.Operator):
    "rename object data as object's name"
    bl_idname = "scene.nzt_renamedata"
    bl_label = "rename data"

    def execute(self, context):
        for ob in context.selected_objects:
            ob.data.name=ob.name
        
        return {'FINISHED'}

class OpNZTextrasSwitchMatType(bpy.types.Operator):
    "switch materials between data and object link type"
    bl_idname = "scene.nzt_switchmattype"
    bl_label = "switch material link type"

    def execute(self, context):
        for ob in context.selected_objects:
            for slot in ob.material_slots:
                if slot.link=='OBJECT':
                    slot.link='DATA'
                else:     
                    slot.link='OBJECT'
        
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
    




##########################
#
#   USER INTERFACE
#
##########################

class NZT_PT_ToolPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "NiZu-Tools Shelf-042"
    bl_idname = "NZT_PT_ToolPanel"

    bl_space_type = 'VIEW_3D'
#    bl_region_type = 'TOOLS'
    bl_region_type = 'UI'
    bl_category = 'NZT'   
    def draw(self, context):
 
        
        layout = self.layout   
        row = layout.row()
        row.label(text="Export:", icon='MESH_ICOSPHERE')        
        row = layout.row()
        row.operator("scene.nzt_export")
        row = layout.row()
        row.operator("scene.nzt_bakeexport")
        row = layout.row()
        row.operator("scene.nzt_packexport")

        row = layout.row()
        row.label(text="Prepare", icon='MESH_ICOSPHERE')
        row = layout.row(align=True)
        row.operator("scene.nztpreplopo")
        row.operator("scene.nzt_prep_hi")
        row = layout.row(align=True)
        row.operator("scene.nzt_prepuvs")        
###
        row = layout.row()
        row.label(text="Extra Tools", icon='MESH_CUBE')
        row = layout.row()
        row.operator("scene.nzt_switchmattype")
        row = layout.row()
        row.operator("mesh.customdata_custom_splitnormals_clear")
        row = layout.row()

        row.operator("object.nzt_origintoselected")

        
        
class NZTUiPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "NZT-Settings"
#    bl_idname = "OBJECT_PT_NZT"
    bl_space_type = 'VIEW_3D'
#    bl_region_type = 'TOOLS'
    bl_region_type = 'UI'
    bl_category = 'NZT'   

    def draw(self, context):
        layout = self.layout

        sce = context.scene

        row = layout.row()
        row.label(text="mesh export paths:  ", icon='WORLD_DATA')
        
        row = layout.row()
        row.prop(sce.nztprops,"engineroot",text='game')
        row = layout.row()
        row.prop(sce.nztprops,"bakemeshespath",text='bake')
        row = layout.row()
        row.prop(sce.nztprops,"writefbx",text='write .fbx')
        row = layout.row()
        row.prop(sce.nztprops,"unity5",text='unity5 scale')
        row = layout.row()
        row.prop(sce.nztprops,"packerpath",text='uvpack app')
    

        
        row = layout.row()
        row.label(text="NZT Object properties", icon='MESH_CUBE')
        row = layout.row()
        ob=context.object    
        objType = getattr(ob, 'type', '')
        if objType=='EMPTY':
            row.prop(context.object.nztroot,"is_lopo_root", text='Lowpoly root')
            row = layout.row()
            if context.object.nztroot.is_lopo_root==True :
                row.prop(context.object.nztroot,"hipo_target", text='hipoly:')
                row = layout.row()
            row.prop(context.object.nztroot,"is_asset_root", text='export root')
            if context.object.nztroot.is_asset_root==True :
                row.prop(context.object.nztroot,"lock_uv1", text='lock_uv1')
                if context.object.nztroot.lock_uv1==False :
                    row = layout.row()
                    row.prop(context.object.nztroot,"lightmap_uv1", text='lightmap_uv1')
                    row = layout.row()
                    row.prop(context.object.nztroot,'uv1_padding')     
                    row = layout.row()
                    row.prop(context.object.nztroot,'uv1_scale')

       
       
NZTclasses=(NZT_PT_ToolPanel,NZTUiPanel,OpNZTGameAssetExport,OpNZTBakeExport,OpNZTPackExport,NZTpreplopo,OpNZTGameAssetPrepHiPo,OpNZTPrepUVchannels,OpNZTextrasSwitchMatType,OpNZTorigintoselected,)   



def register():
    for NZTclass in NZTclasses:
        bpy.utils.register_class(NZTclass)    

    bpy.utils.register_class(nztprops)
    bpy.types.Scene.nztprops = bpy.props.PointerProperty(type=nztprops)
    bpy.utils.register_class(nztroot)
    bpy.types.Object.nztroot = bpy.props.PointerProperty(type=nztroot)


def unregister():

    for NZTclass in NZTclasses:
        bpy.utils.unregister_class(NZTclass)    

    bpy.utils.unregister_class(nztprops)
    del(bpy.types.Scene.nztprops)
    bpy.utils.unregister_class(nztroot)
    del(bpy.types.Object.nztroot)



    
#register, unregister = bpy.utils.register_classes_factory(NZTclasses) 
    


if __name__ == "__main__":
    register()

