import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ==================== Parameters ====================
scale = 1
motor_length = 8 * scale
core_radius = 3.2 * scale
winding_offset = 0.25 * scale
num_poles = 6

# ==================== Collection ====================
motor_collection = bpy.data.collections.new("Induction_Motor")
bpy.context.scene.collection.children.link(motor_collection)

# ==================== Material Setup ====================
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    return mat

mat_stator = create_material("Stator_Material", (0.2, 0.2, 0.2, 1))
mat_core = create_material("Core_Material", (0.6, 0.6, 0.6, 1))
mat_rotor = create_material("Rotor_Material", (0.4, 0.4, 0.4, 1))
mat_winding = create_material("Winding_Material", (0.1, 0.2, 1, 1))
mat_shaft = create_material("Shaft_Material", (0.8, 0.8, 0.8, 1))
mat_warning = create_material("Warning_Material", (1, 0, 0, 1))
mat_safe = create_material("Safe_Material", (0, 1, 0, 1))

# ==================== Geometry Creation ====================
def create_object(primitive, name, **kwargs):
    getattr(bpy.ops.mesh, primitive)(**kwargs)
    obj = bpy.context.object
    obj.name = name
    motor_collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj

def create_stator():
    stator = create_object("primitive_cylinder_add", "Stator",
                           radius=3.5*scale, depth=motor_length, location=(0, 0, 0))
    stator.data.materials.append(mat_stator)
    return stator

def create_core():
    core = create_object("primitive_cylinder_add", "Laminated_Core",
                         radius=core_radius, depth=motor_length-0.2, location=(0, 0, 0))
    core.data.materials.append(mat_core)
    bpy.ops.object.shade_smooth()
    return core

def create_rotor():
    rotor = create_object("primitive_cylinder_add", "Rotor",
                          radius=1.5*scale, depth=motor_length-1, location=(0, 0, 0))
    rotor.data.materials.append(mat_rotor)
    bpy.ops.object.shade_smooth()
    return rotor

def create_windings():
    winding_objs = []
    for i in range(num_poles):
        angle = i * (360 / num_poles)
        x = (core_radius - winding_offset) * math.cos(math.radians(angle))
        y = (core_radius - winding_offset) * math.sin(math.radians(angle))
        winding = create_object("primitive_torus_add", f"Winding_{i+1}",
                                location=(x, y, 0),
                                rotation=(math.radians(90), 0, math.radians(angle)),
                                major_radius=0.2 * scale, minor_radius=0.05 * scale)
        winding.scale = (2, 2, 0.8)
        winding.data.materials.append(mat_winding)
        winding_objs.append(winding)
    return winding_objs

def create_shaft():
    shaft = create_object("primitive_cylinder_add", "Shaft",
                          radius=0.3*scale, depth=12*scale, location=(0, 0, 0))
    shaft.data.materials.append(mat_shaft)
    return shaft

def create_bearings():
    b1 = create_object("primitive_torus_add", "Bearing1",
                       location=(0, 0, 4*scale), major_radius=0.5*scale, minor_radius=0.1*scale)
    b2 = create_object("primitive_torus_add", "Bearing2",
                       location=(0, 0, -4*scale), major_radius=0.5*scale, minor_radius=0.1*scale)
    return [b1, b2]

def create_fan():
    fan = create_object("primitive_cylinder_add", "Fan",
                        radius=2*scale, depth=0.5*scale, location=(0, 0, 4.5*scale))
    return fan

def create_fan_cover():
    cover = create_object("primitive_cylinder_add", "Fan_Cover",
                          radius=2.3*scale, depth=0.2*scale, location=(0, 0, 5*scale))
    return cover

def create_terminal_box():
    terminal = create_object("primitive_cube_add", "Terminal_Box",
                             size=1*scale, location=(3.5*scale, 0, 0))
    return terminal

def create_inlet_outlet():
    inlet = create_object("primitive_cylinder_add", "Inlet",
                          radius=0.4*scale, depth=1*scale, location=(3.5*scale, 0, 1*scale))
    outlet = create_object("primitive_cylinder_add", "Outlet",
                           radius=0.4*scale, depth=1*scale, location=(-3.5*scale, 0, -1*scale))
    return [inlet, outlet]

# ==================== Dynamic Color Function ====================
def update_motor_visuals(temp, vibration, voltage, current):
    critical = temp > 70 or current > 50
    warning = vibration > 50
    undervolt = voltage < 200 or current < 10

    for obj in bpy.data.objects:
        if "Rotor" in obj.name or "Winding" in obj.name:
            if critical:
                obj.data.materials[0] = mat_warning
            elif warning:
                obj.data.materials[0] = create_material("Vibration_Warning", (1, 1, 0, 1))
            elif undervolt:
                obj.data.materials[0] = create_material("LowPower_Warning", (0.2, 0.2, 1, 1))
            else:
                obj.data.materials[0] = mat_safe

# ==================== Sensor Simulator ====================
def simulate_sensor_readings():
    temp = random.uniform(60, 90)
    vibration = random.uniform(20, 80)
    voltage = random.uniform(180, 230)
    current = random.uniform(5, 60)
    update_motor_visuals(temp, vibration, voltage, current)

# ==================== Animation for Rotor ====================
def animate_rotor(obj, frame_start=1, frame_end=120):
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame_start)
    obj.rotation_euler[2] = math.radians(360)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame_end)

# ==================== Camera and Light Setup ====================
def setup_scene():
    bpy.ops.object.camera_add(location=(10, -10, 10), rotation=(math.radians(60), 0, math.radians(45)))
    cam = bpy.context.object
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    light = bpy.context.object
    light.data.energy = 4

    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -5))
    ground = bpy.context.object
    ground.name = "Ground"

# ==================== Master Function ====================
def build_induction_motor():
    create_stator()
    create_core()
    rotor = create_rotor()
    create_windings()
    create_shaft()
    create_bearings()
    create_fan()
    create_fan_cover()
    create_terminal_box()
    create_inlet_outlet()
    setup_scene()
    animate_rotor(rotor)
    simulate_sensor_readings()

# ==================== Run ====================
build_induction_motor()
