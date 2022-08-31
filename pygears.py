import logging
from os.path import isdir
from os import mkdir

class pygears():
    def __init__(self, project_name="project_1") -> None:
        self._project_name = project_name
        self._G4_world = None
        self._existing_solids = []
        self._existing_volu = []
        self._existing_physical_volu = []
        self._defined_rotations = []
        self._geometry_txt = f"//This is geometry for {project_name}"
        self._available_bool_operations = ["SUBTRACTION"]
        pass
    
    def G4Box(self, name=None, hx=None, hy=None, hz=None, unit="mm"):
        # SOLID
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
    
    def bool_createSolid(self, solid_name=None, bool_operation=None, solid_1=None, solid_2=None, rotation=None, translation=[0,0,0]):
        #:solid crate SUBTRACTION cube cuboid r000 0 0 0
        fun_arguments = {"solid_name":solid_name, "bool_operation":bool_operation, "solid_1":solid_1, "solid_2":solid_2, "rotation":rotation}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"bool_createSolid: {arg} is not defined.")
                return
        
        if not (bool_operation.upper() in self._available_bool_operations):
            logging.error(f"bool_createSolid: {bool_operation} is not available, check _available_bool_operations.")
            return 
        
        txt_boolSolid = f"\n:SOLID {solid_name} {bool_operation} {solid_1} {solid_2} {rotation} {translation[0]} {translation[1]} {translation[2]}"
        
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
                        copy_number=None):
        
        fun_arguments = {"rotation_matrix_name":rotation_matrix_name,"logical_volu_name":logical_volu_name, "parent_volu_name":parent_volu_name, "copy_number":copy_number}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4PVPlacement: {arg} is not defined.")
                return
        
        if physical_volu_name is None:
            physical_volu_name = logical_volu_name
        
        rotation_exist = 0
        for rot in self._defined_rotations:
            if rotation_matrix_name == rot[0]:
                rotation_exist = 1
                break
        
        if rotation_exist==0:
            logging.error(f"G4VPhysicalVolume: rotation matrix {rotation_matrix_name} must be defined before using it.")
            return
        
        txt_G4VPhysicalVolume = f":PLACE {physical_volu_name} {copy_number} {parent_volu_name} {rotation_matrix_name} {translation_position[0]} {translation_position[1]} {translation_position[2]}"
        self._existing_physical_volu.append([physical_volu_name, copy_number, parent_volu_name, rotation_matrix_name, translation_position])
        
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
    
    def write_geometry_to_file(self):
        """Writes generated geometry to geometry file
        """
        self._geometry_txt += "\n"
        print(self._geometry_txt)
        output_file = self._folder_name + self._file_name
        with open(output_file, "w") as f:
            f.write(self._geometry_txt)
        logging.info(f"write_geometry_to_file: geometry saved in {output_file}.")
        return
    
    def set_geomtry_file(self, file_name=None, folder_name=""):
        """Function sets output file where geometry is saved

        Args:
            file_name (str, optional): Name of output file. Defaults to None.
            folder_name (str, optional): Folder where geometry file is saved. Defaults to "".
        """
        if file_name is None:
            logging.error("set_geomtry_file: file_name not defined.")
            return
        
        self._file_name = file_name
        self._folder_name = folder_name
        
        if self._file_name[-2:] != "tg":
            self._file_name += ".tg"
        
        if self._folder_name[-1] != "/":
            self._folder_name += "/"
            
        if not isdir(self._folder_name):
            mkdir(self._folder_name)
            logging.info(f"set_geomtry_file: folder {self._folder_name} created")
                
        
    def new_line(self):
        self._geometry_txt += "\n"

myproject = pygears()

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
#:volu crate_air cuboid G4_AIR
#:PLACE crate_air 2 world r000 0 0 0
#:vis crate_air OFF
myproject.G4LogicalVolume("cuboid", "G4_AIR", volu_name="crate_air")
myproject.G4PVPlacement("r000", [0,0,0], logical_volu_name="crate_air", parent_volu_name="world", copy_number=2)
myproject.vis_logicalVolume("crate_air", 0)


myproject.new_line()
#:PLACE aerogel 0 crate_air r000 0 0 -100
myproject.G4PVPlacement("r000", [0, 0, -100], logical_volu_name="aerogel", parent_volu_name="crate_air", copy_number=2)

myproject.set_geomtry_file(file_name="mygeo", folder_name="example/geos_2")
myproject.write_geometry_to_file()