import logging

class pygears():
    def __init__(self, project_name="project_1") -> None:
        self._project_name = project_name
        self._G4_world = None
        self._existing_solids = []
        self._existing_volu = []
        self._existing_physical_volu = []
        self._defined_rotations = []
        self._geometry_txt = f"#This is geometry for {project_name}"
        pass
    
    def G4Box(self, name=None, hx=None, hy=None, hz=None):
        # SOLID
        solid_type = "BOX"
        fun_arguments = {"name":name, "hx":hx, "hy":hy, "hz":hz}
        for arg, val in fun_arguments.items():
            if val is None:
                logging.error(f"G4Box: {arg} is not defined.")
                return
            
        #Create G4Box
        txt_G4Box = f":SOLID {name} {solid_type} {hx} {hy} {hz}"
        self._existing_solids.append([name, solid_type, hx, hy, hz])
        
        self._geometry_txt += "\n" + txt_G4Box
    
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
                        bool_operator=None,
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
        
        txt_G4VPhysicalVolume = f":PLACE {logical_volu_name} {copy_number} {parent_volu_name} {rotation_matrix_name} {translation_position[0]} {translation_position[1]} {translation_position[2]}"
        self._existing_physical_volu.append([logical_volu_name, copy_number, parent_volu_name, rotation_matrix_name, translation_position])
        
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
        
        txt_vis = f"\n:vis {logical_volu_name} "
        txt_vis += "ON" if flag else "OFF"    
        
        self._geometry_txt += txt_vis
    
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
    
    def create_geometry_file(self):
        print(self._geometry_txt)
        return
    
    def new_line(self):
        self._geometry_txt += "\n"

myproject = pygears()

myproject.G4Box("world", 10, 10, 10)
myproject.G4LogicalVolume("world", "Air", "world")
myproject.vis_logicalVolume("world", 0)

myproject.new_line()

myproject.CreateRotation("ry90", 0, 90, 0)
myproject.CreateRotation("r000", 0, 0, 0)

myproject.new_line()

myproject.G4Box("mybox", 1, 1, 1)
myproject.G4LogicalVolume("mybox", "Air", "mybox")
myproject.G4VPhysicalVolume("r000", logical_volu_name="mybox", parent_volu_name="world", copy_number=0)

myproject.create_geometry_file()