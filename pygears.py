import logging
from os.path import isdir
from os import mkdir

class pygears():
    def __init__(self, project_name="project_1", sub_project=0, sub_project_name="sub_project") -> None:
        self._project_name = project_name
        self._G4_world = None
        self._existing_solids = []
        self._existing_volu = []
        self._existing_physical_volu = []
        self._defined_rotations = []
        
        self._available_bool_operations = ["SUBTRACTION"]
        self._sub_project = sub_project
        self._sub_project_name = sub_project_name
        self._folder_name = ""
        self._geometry_txt = f"//This is geometry for {project_name}" + f", subproject: {self._sub_project_name}" if sub_project else ""
        
        self._main_project = None
        self._list_sub_projects = []
        pass
    
    def G4Box(self, name=None, hx=None, hy=None, hz=None, unit="mm"):
        """Creates a SOLID object

        Args:
            name (str, optional): Name of the BOX object. Defaults to None.
            hx (float, optional): x dimension. Defaults to None.
            hy (float, optional): y dimension. Defaults to None.
            hz (float, optional): z dimension. Defaults to None.
            unit (str, optional): Length unit. Defaults to "mm".
        """
        
        solid_type = "BOX"
        fun_arguments = {"name":name, "hx":hx, "hy":hy, "hz":hz}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4Box: {arg} is not defined.")
                return
            
        #Create G4Box
        txt_G4Box = f":SOLID {name} {solid_type} {hx}*{unit} {hy}*{unit} {hz}*{unit}"
        self._existing_solids.append([name, solid_type, hx, hy, hz, unit])
        
        self._geometry_txt += "\n" + txt_G4Box
    
    def bool_createSolid(self, solid_name=None, bool_operation=None, solid_1=None, solid_2=None, rotation=None, translation=[0,0,0], unit="mm"):
        #:solid crate SUBTRACTION cube cuboid r000 0 0 0
        fun_arguments = {"solid_name":solid_name, "bool_operation":bool_operation, "solid_1":solid_1, "solid_2":solid_2, "rotation":rotation}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"bool_createSolid: {arg} is not defined.")
                return
        
        if not (bool_operation.upper() in self._available_bool_operations):
            logging.error(f"bool_createSolid: {bool_operation} is not available, check _available_bool_operations.")
            return 
        
        txt_boolSolid = f"\n:SOLID {solid_name} {bool_operation} {solid_1} {solid_2} {rotation} {translation[0]}*{unit} {translation[1]}*{unit} {translation[2]}*{unit}"
        
        self._geometry_txt += txt_boolSolid
        
        return
    
    def G4LogicalVolume(self, solid_name=None, material_name=None, volu_name=None):
        fun_arguments = {"solid_name":solid_name, "material_name":material_name, "volu_name":volu_name}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4LogicalVolume: {arg} is not defined.")
                return
        
        txt_G4LogicalVolume = f":VOLU {volu_name} {solid_name} {material_name}"
        self._existing_volu.append([volu_name, solid_name, material_name])
        
        self._geometry_txt += "\n" + txt_G4LogicalVolume
        
        return
    
    def G4PVPlacement(self,
                        rotation_matrix_name=None,
                        translation_position=[0,0,0],
                        logical_volu_name=None,
                        physical_volu_name=None,
                        parent_volu_name=None,
                        copy_number=None,
                        unit="mm"):
        
        """For placing physical volume in space

        Args:
            rotation_matrix_name (str, a must): Name of rotation matrix, must be predefined.
            translation_position (float array[3], optional): Translation vector for placing physical volume. Defaults to [0,0,0].
            logical_volu_name (str, a must): Name of logical volume to be placed as physical.
            physical_volu_name (str, optional): Name of pyhsical volume. Defaults to logical_volu_name.
            parent_volu_name (str, a must): Name of the parent volume in which the physical volue is placed.
            copy_number (int, a must): Copy number of physical volume.
            unit (str, optional): Length units. Defaults to mm.
        """
        
        fun_arguments = {"rotation_matrix_name":rotation_matrix_name,"logical_volu_name":logical_volu_name, "parent_volu_name":parent_volu_name, "copy_number":copy_number}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4PVPlacement: {arg} is not defined.")
                return
        
        if physical_volu_name is None:
            physical_volu_name = logical_volu_name
        
        # Skip this check if this is subproject and main project is defined
        rotation_exist = 0 if self._main_project is None else 1
        for rot in self._defined_rotations:
            if rotation_matrix_name == rot[0]:
                rotation_exist = 1
                break
        
        if rotation_exist==0:
            logging.error(f"G4VPhysicalVolume: rotation matrix {rotation_matrix_name} must be defined before using it.")
            return
        
        txt_G4VPhysicalVolume = f":PLACE {physical_volu_name} {copy_number} {parent_volu_name} {rotation_matrix_name} {translation_position[0]}*{unit} {translation_position[1]}*{unit} {translation_position[2]}*{unit}"
        self._existing_physical_volu.append([physical_volu_name, copy_number, parent_volu_name, rotation_matrix_name, translation_position, unit])
        
        self._geometry_txt += "\n" + txt_G4VPhysicalVolume
        
        return
        
    def vis_logicalVolume(self, logical_volu_name=None, flag=0):
        # Set the visualization ON or OFF
        if logical_volu_name is None:
            logging.error("vis_physicalVolume: logical_volu_name is note defined.")
            return

        volu_exists = 0
        for vol in self._existing_volu:
            if logical_volu_name == vol[0]:
                volu_exists = 1
                break
            
        if volu_exists == 0:
            logging.warning(f"vis_logicalVolume: {logical_volu_name} does not exist.")
            return
        
        txt_vis = f"\n:VIS {logical_volu_name} "
        txt_vis += "ON" if flag else "OFF"    
        
        self._geometry_txt += txt_vis
    
    def set_color_logicVolume(self, logical_volu_name=None, rgb=[1,1,1]):
        if logical_volu_name is None:
            logging.error("set_color_logicVolume: logical_volu_name is not defined.")
            return
        
        self._geometry_txt += f"\n:COLOR {logical_volu_name} {rgb[0]} {rgb[1]} {rgb[2]}"
    
    def CreateRotation(self, rot_name=None, rx=0, ry=0, rz=0):
        
        if rot_name is None:
            logging.error("CreateRotation: rot_name is not defined.")
            return
               
        txt_rot = f"\n:rotm {rot_name} {rx} {ry} {rz}"
        self._defined_rotations.append([rot_name, rx, ry, rz])
        self._geometry_txt += txt_rot
    
    def G4Material(self, material_name=None, atomic_number=None, molecular_mass=None, density=None):
        #Material made of one element
        fun_arguments = {"material_name":material_name, "atomic_number":atomic_number, "molecular_mass":molecular_mass, "density":density}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4Material: {arg} is not defined.")
                return
        
        txt_material = f":MATE {material_name} {atomic_number} {molecular_mass} {density}"
        self._geometry_txt += "\n" + txt_material  
                
        return
    
    def MIXT_BY_NATOMS(self, material_name=None, density=None, n_components=None, *argv):
        fun_arguments = {"material_name":material_name, "density":density, "n_components":n_components}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"MIXT_BY_NATOMS: {arg} is not defined.")
                return
            
        #parse components
        if len(argv) != n_components*2:
            logging.error("MIXT_BY_NATOMS: number of components is incorrect.")
            return
        
        components = {}
        
        i = 0
        while i < len(argv):
            components[argv[i]] = argv[i+1]
            i += 2
        
        #:MIXT_BY_NATOMS CO2 1.8182E-3 2 C 1 O 2
        txt_mixt_by_natoms = f"\n:MIXT_BY_NATOMS {material_name} {density} {n_components}"
        for key, val in components.items():
            txt_mixt_by_natoms += f" {key} {val}"
            
        self._geometry_txt += txt_mixt_by_natoms
                        
        return
    
    
    def G4_MIXT_BY_VOLUME(self, material_name=None, density=None, n_components=None, *argv):
        fun_arguments = {"material_name":material_name, "density":density, "n_components":n_components}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4_MIXT_BY_VOLUME: {arg} is not defined.")
                return
            
        #parse components
        if len(argv) != n_components*2:
            logging.error("G4_MIXT_BY_VOLUME: number of components is incorrect.")
            return
        
        components = {}
        
        i = 0
        while i < len(argv):
            components[argv[i]] = argv[i+1]
            i += 2
        
        #MIXT_BY_VOLUME M_aerogel 0.1 4 G4_O 0.48 G4_H 0.01 G4_Si 0.45 G4_C 0.06
        txt_mixt_by_vol = f"\n:MIXT_BY_VOLUME {material_name} {density} {n_components}"
        for key, val in components.items():
            txt_mixt_by_vol += f" {key} {val}"
            
        self._geometry_txt += txt_mixt_by_vol
                        
        return
    
    def get_geometry_txt(self):
        # This is due to bug-1, it can be removed if gears fixs the bug
        output = self._geometry_txt + "\n"
        return output
    
    def write_geometry_to_file(self):
        """Writes generated geometry to geometry file
        """
        output_txt = self.get_geometry_txt()
        
        print(output_txt)
        
        output_file = self._folder_name + self._file_name
        with open(output_file, "w") as f:
            f.write(output_txt)
        logging.info(f"write_geometry_to_file: geometry saved in {output_file}.")
        
        for subproject in self._list_sub_projects:
            print(f"**** START: {subproject._sub_project_name} ****")
            print(subproject.get_geometry_txt())
            print(f"**** END: {subproject._sub_project_name} ****\n")
            
            output_file = self._folder_name + subproject._sub_project_name + ".tg"
            with open(output_file, "w") as f:
                f.write(subproject.get_geometry_txt())
        
        return
    
    def set_geometry_file(self, file_name=None, folder_name=""):
        """Function sets output file where geometry is saved. Recommended: run script in same folder as gears.mac file is

        Args:
            file_name (str, optional): Name of output file. Defaults to None.
            folder_name (str, optional): Folder where geometry file is saved. Defaults to "".
        """
        if file_name is None:
            logging.error("set_geometry_file: file_name not defined.")
            return
        
        self._file_name = file_name
        self._folder_name = folder_name
        
        if self._file_name[-2:] != "tg":
            self._file_name += ".tg"
        
        if self._folder_name[-1] != "/":
            self._folder_name += "/"
            
        if not isdir(self._folder_name):
            mkdir(self._folder_name)
            logging.info(f"set_geometry_file: folder {self._folder_name} created")
            
                
    def set_main_project(self, main_project=None):
        if main_project is None:
            logging.error("set_main_project: main_project is not defined")
            return
        if main_project._sub_project != 0:
            logging.error(f"set_main_project: subproject: '{main_project._sub_project_name}' is not main project. Sub_project#: {main_project._sub_project}")
            return
        self._main_project = main_project    
        return
    
    def set_subproject(self, subproject=None, bypass_include=None):
        """Sets a project as subproject. Subproject must have self._sub_project > 0! Please use set_geometry_file before this function

        Args:
            subproject (pygears object, optional): A pygears object defined as sub-project. Defaults to None.
        """
        if subproject is None:
            logging.error("set_subproject: subproject is not defined.")
            return
        if subproject._sub_project < self._sub_project:
            logging.error(f"set_subproject: {subproject._sub_project_name} is not a sub-project. val: {subproject._sub_project}")
            return
        
        self._list_sub_projects.append(subproject)
        
        if bypass_include is None:
            self._geometry_txt += f"\n#include {self._folder_name + subproject._sub_project_name}.tg"
        else:
            self._geometry_txt += "\n"+bypass_include
        
    def new_line(self):
        self._geometry_txt += "\n"

myproject = pygears()
myproject.set_geometry_file(file_name="mygeo", folder_name="example/geos_2")

myproject.G4Box("world", 2, 2, 2, "m")
myproject.G4LogicalVolume("world", "G4_Galactic", "world")
myproject.vis_logicalVolume("world", 0)

myproject.new_line()
myproject.CreateRotation("ry90", 0, 90, 0)
myproject.CreateRotation("r000", 0, 0, 0)
myproject.CreateRotation("ry45", 0, 45, 0)
myproject.CreateRotation("ry180", 0, 180, 0)
myproject.CreateRotation("rz90", 0, 0, 90)

myproject.new_line()
myproject.G4_MIXT_BY_VOLUME("M_aerogel", 0.1, 4, "G4_O", 0.48, "G4_H", 0.01, "G4_Si", 0.45, "G4_C", 0.06)
myproject.G4Box("aerogel", 60, 60, 10)
myproject.G4LogicalVolume("aerogel", "M_aerogel", "aerogel")
myproject.set_color_logicVolume("aerogel", [1,0,0])

myproject.new_line()
myproject.G4Box("cube", 500, 280, 280)
myproject.G4Box("cuboid", 498, 278, 278)
myproject.bool_createSolid("crate", bool_operation="SUBTRACTION", solid_1="cube", solid_2="cuboid", rotation="r000", translation=[0,0,0])
myproject.G4LogicalVolume("crate", "G4_Al", "crate")
myproject.set_color_logicVolume("crate", rgb=[0.4, 0.4, 0.4])
myproject.G4PVPlacement("r000", [0,0,0], "crate", "crate", "world", copy_number=1)
myproject.vis_logicalVolume("crate", flag=0)

myproject.new_line()
""":volu crate_air cuboid G4_AIR
:PLACE crate_air 2 world r000 0 0 0
:vis crate_air OFF"""
myproject.G4LogicalVolume("cuboid", "G4_AIR", volu_name="crate_air")
myproject.G4PVPlacement("r000", [0,0,0], logical_volu_name="crate_air", parent_volu_name="world", copy_number=2)
myproject.vis_logicalVolume("crate_air", 0)


myproject.new_line()
#:PLACE aerogel 0 crate_air r000 0 0 -100
myproject.G4PVPlacement("r000", [0, 0, -100], logical_volu_name="aerogel", parent_volu_name="crate_air", copy_number=0)

# MIRROR
myproject.new_line()
"""// Place mirror on the beam, 2mm thick Silver
:volu mirror BOX 50*mm 50*mm 1*mm G4_Al
:color mirror 0. 0.5 0.5
:rotm rMiror 0  45  0
:PLACE mirror 4 crate_air rMiror 0 0 0"""
myproject.G4Box("mirror", 50, 50, 1)
myproject.G4LogicalVolume("mirror", "G4_Al", "mirror")
myproject.set_color_logicVolume("mirror", [0, 0.5, 0.5])
myproject.CreateRotation("rotm", 0, 45, 0)
myproject.G4PVPlacement("rotm", [0, 0, 0], "mirror", parent_volu_name="crate_air", copy_number=4)

# PMT
"""
// Place PMT window, 2mm thick
:volu pmt(S) BOX 70*mm 70*mm 0.5*mm G4_SILICON_DIOXIDE
:color pmt(S) 0.9 0.9 0.
:PLACE pmt(S) 5 crate_air ry90 259.5*mm 0 0
"""
myproject.new_line()
myproject.G4Box("pmt", 70, 70, 0.5)
myproject.G4LogicalVolume("pmt", "G4_SILICON_DIOXIDE",  "pmt")
myproject.set_color_logicVolume("pmt", [0.9, 0.9, 0])
myproject.G4PVPlacement("ry90", [259.5, 0, 0], "pmt", parent_volu_name="crate_air", copy_number=5)

# Geometry in a file
mwpc_file = pygears(sub_project=1, sub_project_name="mwpc")
mwpc_file.set_main_project(myproject)
"""
:MIXT_BY_NATOMS CO2 1.8182E-3 2 C 1 O 2
:MIXT_BY_VOLUME GasMWPC (41.17/22.4/1000) 2 G4_Ar 0.7 CO2 0.3 

:VOLU mwpc(S) BOX 25 25 2.5 GasMWPC
:color mwpc(S) 0. 1. 0.
:PLACE mwpc(S) 6 world r000 0 0 280+5
:PLACE mwpc(S) 7 world ry180 0 0 -280-5
"""

mwpc_file.MIXT_BY_NATOMS("CO2", 1.8182E-3, 2, "C", 1, "O", 2)
mwpc_file.G4_MIXT_BY_VOLUME("GasMWPC", (41.17/22.4/1000), 2, "G4_Ar", 0.7, "CO2", 0.3)
mwpc_file.G4Box("mwpc", 25, 25, 2.5)
mwpc_file.G4LogicalVolume("mwpc", "GasMWPC", "mwpc")
mwpc_file.set_color_logicVolume("mwpc", [0, 1, 0])
mwpc_file.G4PVPlacement("r000", [0, 0, 280+5], "mwpc", parent_volu_name="world", copy_number=6)
mwpc_file.G4PVPlacement("ry180", [0, 0, -280-5], "mwpc", parent_volu_name="world", copy_number=7)

#myproject will now place sub-project mwpc_file in a dedicated file
myproject.new_line()
myproject.set_subproject(mwpc_file, bypass_include="#include geos_2/mwpc.tg")


myproject.write_geometry_to_file()