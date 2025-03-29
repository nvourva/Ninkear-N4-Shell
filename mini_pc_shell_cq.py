import cadquery as cq

def create_corner_base():
    # Create corner extension
    corner_extension = cq.Workplane("XY") \
        .rect(5, 5) \
        .extrude(1.5)
    
    return corner_extension

def create_mini_pc_shell():
    # Shell external dimensions
    length = 114  # mm
    width = 106   # mm
    height = 38   # mm
    wall_thickness = 1.5  # mm
    
    # Top cutout dimensions
    cutout_length = 80  # mm
    cutout_width = 80   # mm
    
    # Back face cutout dimensions
    back_cutout_length = 89  # mm
    back_cutout_width = 27   # mm
    
    # Create the outer shell
    outer_shell = cq.Workplane("XY") \
        .rect(length, width) \
        .extrude(height)
    
    # Create the inner cavity by subtracting the wall thickness
    inner_shell = cq.Workplane("XY") \
        .rect(length - (2 * wall_thickness), width - (2 * wall_thickness)) \
        .extrude(height - wall_thickness) \

    # Create the bottom lip where the bottom panel rests.
    bottom_lip = cq.Workplane("XY") \
        .rect(length - (2 * 0.4), width - (2 * 0.4)) \
        .extrude(1.8)
        
    # Subtract bottom lip from outer shell
    shell_with_lip = outer_shell.cut(bottom_lip)
    
    # Subtract inner cavity from shell with lip.
    shell_with_cavity = shell_with_lip.cut(inner_shell)
    
    # Create the top cutout
    top_cutout = cq.Workplane("XY") \
        .moveTo(0, 0) \
        .rect(cutout_length, cutout_width) \
        .extrude(wall_thickness)
    
    # Center the cutout on the top surface
    centered_cutout = top_cutout \
        .translate((0, 0, height - wall_thickness))
    
    # Cut out the top surface
    shell_with_cutout = shell_with_cavity.cut(centered_cutout)
    
    # Create front face cutout
    front_cutout = cq.Workplane("XZ") \
        .rect(60, 10) \
        .extrude(wall_thickness)
    
    # Position the front cutout
    # 20mm from right side, 6mm from bottom
    # Translate to front face (along Y-axis) and adjust position
    positioned_front_cutout = front_cutout \
        .rotate((0,0,0), (1,0,0), 0) \
        .translate((-length/2 + 60/2 + 20, width/2, 12 ))
    
    # Cut out the front surface
    shell_with_front_cutout = shell_with_cutout.cut(positioned_front_cutout)
    
    # Create back face cutout
    back_cutout = cq.Workplane("XZ") \
        .rect(back_cutout_length, back_cutout_width) \
        .extrude(wall_thickness)
    
    # Position the back cutout
    # Center it on the back face
    positioned_back_cutout = back_cutout \
        .rotate((0,0,0), (1,0,0), 0) \
        .translate((-length/2 + back_cutout_length/2 + 13, -51.5, back_cutout_width/2 + 7.5))
    
    # Cut out the back surface
    shell_with_back_cutout = shell_with_front_cutout.cut(positioned_back_cutout)
    
    # Create base corner piece
    corner_base = create_corner_base()
    
    # Calculate corner positions
    corner_offset = 38
    corners = [
        (corner_offset, corner_offset),     # Top right
        (corner_offset, -corner_offset),    # Bottom right
        (-corner_offset, corner_offset),    # Top left
        (-corner_offset, -corner_offset)    # Bottom left
    ]
    
    # Add corner extensions with mount points
    for x, y in corners:
        
        # Translate the corner base to the correct position
        positioned_corner_base = corner_base \
            .translate((x, y, height - wall_thickness))
        
        shell_with_back_cutout = shell_with_back_cutout.union(positioned_corner_base)
    
    # Create the structure to hold the fan.
    fan_box = cq.Workplane("XY") \
        .rect(84, 84) \
        .extrude(25)

    # Create the inner cavity by subtracting the wall thickness
    inner_fan_box = cq.Workplane("XY") \
    .rect(81, 81) \
    .extrude(25)
    
    # Hollow the fan box structure
    fan_box_shell = fan_box.cut(inner_fan_box)
    
    #Move the fan box to its proper location.
    position_fan_box_shell = fan_box_shell.translate((0,0,height))
    
    mini_pc_shell = shell_with_back_cutout.union(position_fan_box_shell)
    
    #Create the screw pillar
    screw_pillar = cq.Workplane("XY") \
        .rect(9, 9) \
        .extrude(19)

    # It needs  holes for the standoffs
    screw_pillar_hole = cq.Workplane("XY") \
        .circle(2) \
        .extrude(6)
    
    # Drill da hole
    screw_pillar_with_hole = screw_pillar.cut(screw_pillar_hole)
    
    # Screw pillar offsets
    screw_pillar_offset_long = length/2 - 4.5 - 3.5
    screw_pillar_offset_short = width/2 - 4.5 - 3.5
    
    screw_pillars = [
        (screw_pillar_offset_long, screw_pillar_offset_short),     # Top right
        (screw_pillar_offset_long, -screw_pillar_offset_short),    # Bottom right
        (-screw_pillar_offset_long, screw_pillar_offset_short),    # Top left
        (-screw_pillar_offset_long, -screw_pillar_offset_short)    # Bottom left
    ]
    
    #Let's add the pillars
    for x, y in screw_pillars:
        
        # Translate the screw pillars to the correct position
        positioned_pillars = screw_pillar_with_hole \
            .translate((x, y, height -19 - wall_thickness))
        
        mini_pc_shell = mini_pc_shell.union(positioned_pillars)

    return mini_pc_shell

# Generate the shell
result = create_mini_pc_shell()