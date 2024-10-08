import pygame
import json
import os
import math

pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Interactive Interface")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 162, 232)
red = (255, 69, 0)
iron_blue = (0, 153, 255)
iron_yellow = (255, 223, 0)
iron_green = (34, 204, 34)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Initial zoom factor
zoom_factor = 1.0

# Objects data
objects = [
    {"pos": [200, 200], "size": 50, "zoom_factor": 1.0},
    {"pos": [400, 300], "size": 50, "zoom_factor": 1.0},
    {"pos": [600, 400], "size": 50, "zoom_factor": 1.0}
]
selected_object = None
pointer_pos = [screen_width // 2, screen_height // 2]
is_dragging = False

# Delay to allow hand_gesture.py to write initial data
pygame.time.wait(2000)

# Function to draw a glowing circle
def draw_glowing_circle(surface, color, center, radius, glow_radius):
    for i in range(glow_radius):
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, max(255 - 255 * (i / glow_radius), 0)), (radius, radius), radius)
        surface.blit(s, (center[0] - radius, center[1] - radius), special_flags=pygame.BLEND_RGBA_ADD)

# Function to draw the rotating JARVIS logo
def draw_jarvis_logo(surface, text, center, radius, angle_offset):
    # Draw the text
    text_surface = small_font.render(text, True, iron_blue)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

    # Draw the rotating ring
    num_segments = 60
    angle_step = 360 / num_segments
    current_angle = pygame.time.get_ticks() / 10 % 360

    for i in range(num_segments):
        segment_angle = current_angle + i * angle_step
        x = center[0] + radius * math.cos(math.radians(segment_angle))
        y = center[1] + radius * math.sin(math.radians(segment_angle))
        end_x = center[0] + (radius + 5) * math.cos(math.radians(segment_angle))
        end_y = center[1] + (radius + 5) * math.sin(math.radians(segment_angle))

        color = iron_yellow if i % 2 == 0 else iron_blue
        pygame.draw.line(surface, color, (x, y), (end_x, end_y), 2)

# Main loop
running = True
while running:
    # Read gesture data from the file
    if os.path.exists('gesture_data.json'):
        try:
            with open('gesture_data.json', 'r') as f:
                gesture_data = json.load(f)

            # Move pointer based on hand movement
            if gesture_data.get("gesture") == "pinch_move":
                pointer_pos = [gesture_data["x"], gesture_data["y"]]
                if selected_object is not None and is_dragging:
                    objects[selected_object]["pos"] = pointer_pos

            # Handle zoom gesture
            if gesture_data.get("gesture") == "pinch_zoom" and selected_object is not None:
                objects[selected_object]["zoom_factor"] = gesture_data["zoom_factor"]

            # Check if pointer is over any object and select it for dragging
            if gesture_data.get("gesture") == "pinch_move":
                for i, obj in enumerate(objects):
                    current_size = int(obj["size"] * obj["zoom_factor"])
                    if math.dist(pointer_pos, obj["pos"]) < current_size:
                        selected_object = i
                        is_dragging = True
                        break
                else:
                    selected_object = None
                    is_dragging = False

        except json.JSONDecodeError:
            pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(black)

    # Draw the background grid
    for x in range(0, screen_width, 50):
        pygame.draw.line(screen, iron_blue, (x, 0), (x, screen_height), 1)
    for y in range(0, screen_height, 50):
        pygame.draw.line(screen, iron_blue, (0, y), (screen_width, y), 1)

    # Draw the objects
    for i, obj in enumerate(objects):
        current_size = int(obj["size"] * obj["zoom_factor"])
        draw_glowing_circle(screen, iron_yellow, obj["pos"], current_size, 100)
        pygame.draw.circle(screen, iron_blue, obj["pos"], current_size)

    # Draw the pointer
    pygame.draw.circle(screen, white, pointer_pos, 10)

    # Draw text
    text = font.render('JARVIS Interface', True, iron_green)
    screen.blit(text, (20, 20))

    # Draw rotating lines around the pointer
    angle = pygame.time.get_ticks() / 1000 * 90  # Rotate at 90 degrees per second
    for i in range(4):
        length = 20
        end_pos = (
            pointer_pos[0] + math.cos(math.radians(angle + i * 90)) * length,
            pointer_pos[1] + math.sin(math.radians(angle + i * 90)) * length
        )
        pygame.draw.line(screen, red, pointer_pos, end_pos, 2)

    # Draw JARVIS logo in the bottom left corner
    jarvis_center = (100, screen_height - 100)
    draw_jarvis_logo(screen, "JARVIS", jarvis_center, 50, angle)

    pygame.display.flip()

pygame.quit()
