import logging

class pygears():
    def __init__(self, project_name="project_1") -> None:
        self._project_name = project_name
        self._G4_world = None
        self._existing_solids = []
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
        
    def create_geometry_file(self):
        print(self._geometry_txt)
        return

myproject = pygears()
myproject.G4Box("world", 10, 10, 10)
myproject.create_geometry_file()