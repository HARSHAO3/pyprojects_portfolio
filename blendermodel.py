import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scale = 1

def create_stator():
    bpy.ops.mesh.primitive_cylinder_add(radius=3.5*scale, depth=8*scale, location=(0, 0, 0))
    stator = bpy.context.object
    stator.name = "Stator"

def create_core():
    bpy.ops.mesh.primitive_cylinder_add(radius=3.2*scale, depth=7.8*scale, location=(0, 0, 0))
    core = bpy.context.object
    core.name = "Laminated_Core"
    core.select_set(True)
    bpy.ops.object.shade_smooth()

def create_rotor():
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5*scale, depth=7*scale, location=(0, 0, 0))
    rotor = bpy.context.object
    rotor.name = "Rotor"
    rotor.select_set(True)
    bpy.ops.object.shade_smooth()

def create_windings():
    num_poles = 6
    radius_offset = 0.3 * scale
    winding_radius = 3.2 * scale - radius_offset
    winding_length = 7.8 * scale

    for i in range(num_poles):
        angle = i * (360 / num_poles)
        x = winding_radius * math.cos(math.radians(angle))
        y = winding_radius * math.sin(math.radians(angle))
        
        bpy.ops.mesh.primitive_torus_add(
            location=(x, y, 0),
            rotation=(math.radians(90), 0, math.radians(angle)),
            major_radius=0.25 * scale,
            minor_radius=0.05 * scale,
        )
        winding = bpy.context.object
        winding.name = f"Winding_{i+1}"
        winding.scale = (2, 2, winding_length / 8)
        winding.active_material = bpy.data.materials.new(name="Winding_Material")
        winding.active_material.diffuse_color = (0, 0, 1, 1)

def create_shaft():
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3*scale, depth=12*scale, location=(0, 0, 0))
    shaft = bpy.context.object
    shaft.name = "Shaft"

def create_bearing():
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5*scale, minor_radius=0.1*scale, location=(0, 0, 4*scale))
    bearing1 = bpy.context.object
    bearing1.name = "Bearing1"
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5*scale, minor_radius=0.1*scale, location=(0, 0, -4*scale))
    bearing2 = bpy.context.object
    bearing2.name = "Bearing2"

def create_fan():
    bpy.ops.mesh.primitive_cylinder_add(radius=2*scale, depth=0.5*scale, location=(0, 0, 4.5*scale))
    fan = bpy.context.object
    fan.name = "Fan"

def create_fan_cover():
    bpy.ops.mesh.primitive_cylinder_add(radius=2.3*scale, depth=0.2*scale, location=(0, 0, 5*scale))
    cover = bpy.context.object
    cover.name = "Fan_Cover"

def create_terminal_box():
    bpy.ops.mesh.primitive_cube_add(size=1*scale, location=(3.5*scale, 0, 0))
    terminal_box = bpy.context.object
    terminal_box.name = "Terminal_Box"

def create_inlet_outlet():
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4*scale, depth=1*scale, location=(3.5*scale, 0, 1*scale))
    inlet = bpy.context.object
    inlet.name = "Inlet"
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4*scale, depth=1*scale, location=(-3.5*scale, 0, -1*scale))
    outlet = bpy.context.object
    outlet.name = "Outlet"

def assemble_motor():
    create_stator()
    create_core()
    create_rotor()
    create_windings()
    create_bearing()
    create_shaft()
    create_fan()
    create_fan_cover()
    create_terminal_box()
    create_inlet_outlet()

def update_motor_colors(temp, vibration, voltage, current):
    for obj in bpy.data.objects:
        if "Stator" in obj.name or "Rotor" in obj.name or "Winding" in obj.name:
            if temp > 70 or current > 50:
                obj.active_material.diffuse_color = (1, 0, 0, 1)
            elif vibration > 50:
                obj.active_material.diffuse_color = (1, 1, 0, 1)
            elif voltage < 200 or current < 10:
                obj.active_material.diffuse_color = (0, 0, 1, 1)
            else:
                obj.active_material.diffuse_color = (0, 1, 0, 1)

def get_sensor_data():
    temp = 65
    vibration = 40
    voltage = 220
    current = 45
    update_motor_colors(temp, vibration, voltage, current)

assemble_motor()
get_sensor_data()
