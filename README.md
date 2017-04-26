# NZ-Tools
my Blender shelf tools (Substance and Unity export)


![alt text](https://nizuvault.files.wordpress.com/2017/04/croppercapture64.jpg)


UI and operators description (DRAFT)

///Configuration options :

– Game (game assets directoty) :  the ‘asset folder’ of your Unity project, assets will be exported in a '/meshes' subfolder.  

-Bake (bake meshes directory) : where to save fbx files for Substance bakes.

–packer path : path to the executable of ‘iPackThat’ (to be moved in addong config, not per-scene config ..) 
I’m using this app for better packing of uvs, but it’s not FOSS, and i hear support isn’t great, works well for me , but be aware and check this thread if you plan to buy it : polycount.com/discussion/comment/2542014

-Unity 5 checkbox : just changes the ‘use units scale’ parameter in fbx export to work with unity 5 or unity 4

///Mesh preparation ops :

–prepare lowpoly: Used after modelling  the chunks of the lowpoly model.  Adds ‘-lopo’  suffix to selected objects ( for Substance bakes pairing) parent all objects to a root empty  (to define what to export to substance and later what to join in a single mesh/asset for Unity)

–prepare hipoly: Used after (mostly) finishing lowpoly model  but before finishing uvs and applying mirrors and other modifiers.

Duplicates selected objects, changes suffix to -hipo, parents to a root empty defining a group of hipoly chunks matching lowpoly.

///Export ops:

–Export for pack : Very tied to the rest of my personal workflow , i use texture atlas to manage unwrapping multiple objects together, but use IPackThat to do final packing, so this quickly exports the joined mesh for packing and imports back after.

–Export for bake: exports 2 fbx files (low and hipoly) to subfolder ready to be used in Substance, will export all visible objects tagged with the ‘roots’ parenting .

–Export asset: Export all visible lowpoly roots as fbx files to use in game engine.

It does a bunch of clean up operations, mostly to do a clean join of the meshes previously split into chunks ( weld, preserving custom normals, unflipping negative scale parts, etc..)  And some commands to repack the main uvs into something good for lightmap in Unity (not overlapping, uniform scale for all models .. approximately)

///Cleanup ops :

–rename data:  renames object data as object,  this is helpful sometimes to keep track of what is the ‘original’ version of a chunk of model that gets duplicated a lot. Normally that’s handled as an instance (using same mesh data) but if that link needs to be broken for some reason, having the mesh data named meaningfully helps to rebuild links.

–switch material link type: Blender allows a material to be assigned by mesh data or by object, this switches this assignment for all selected objects (the material chosen for other type remains stored).  So you can have all objects using 1 material when exporting to Substance to define a texture sheet, and when exporting to unity, some pieces (including individual instances) can have other variants (like, using same base textures but different detail or shader)

///Modelling tools :

–Weighted normals :  calls the script by Simon Lusenc , that does a great job of ‘automatic’ custom normals editing, often as good as what you can do manually with data transfers and Blend4web tools.

–Clear custom normals : just a button for that op. , i use it often, my workflow with custom normals is basically :  try Weighted N. script , if result is not good try adding some sharp edges, if that’s still not good (mesh too lowpoly to improve with custom normals) then clear custom normals and use base tools. Only exception is sometimes i use Blend4web to average and flatten normals on a plane that is flat but is showing bad diagonal normals.

–Origin to selected :  Just reduces 2 clicks to 1 for the operation of setting pivot of object to selected vertex 😀

///Object properties :
These properties are normally set automatically following the workflow (prep lowpoly , then hipoly) but can be used to check or fix properties of selected object, only available/used for root empties (for now)
-"lowpoly root" checkbox : if this empty is the root for a lowpoly/asset group
-"hipoly:" text field : if above is true, which is the name of corresponding hipoly group.
Groups made of instances of original pieces, can be left with the 'hipoly' empty, and used only to export to engine.


