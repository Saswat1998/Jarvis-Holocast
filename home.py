import os
import cv2
import mediapipe as mp
import pygame
import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from pygame.locals import *

pygame.init()

# Get the screen dimensions
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h

# Set the Pygame window to be windowed full screen
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("Home Interface")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 162, 232)
red = (255, 69, 0)
iron_blue = (0, 153, 255)
iron_yellow = (255, 223, 0)
iron_green = (34, 204, 34)

# Fonts
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 36)

# Button dimensions and positions
button_radius = 50
button_margin = 150
home_button = {"label": "Home", "pos": (screen_width // 2, screen_height // 2), "color": iron_blue, "action": "toggle_buttons"}
buttons = [
    {"label": "2D Image Loading", "pos": (0, 0), "color": iron_blue, "action": "load_images", "visible": False},
    {"label": "3D Model Loading", "pos": (0, 0), "color": iron_green, "action": "load_models", "visible": False},
    {"label": "Object Recognition", "pos": (0, 0), "color": iron_yellow, "action": "object_recognition", "visible": False}
]

# Define states for different interfaces
INTERFACE_HOME = "home"
INTERFACE_2D = "2d"
INTERFACE_3D = "3d"
INTERFACE_OBJECT_RECOGNITION = "object_recognition"

# Initialize state
current_interface = INTERFACE_HOME

buttons_visible = False
animation_start_time = 0
animation_duration = 1  # Duration of the button appearance animation in seconds

# Fade-in animation variables
info_alpha = 0
fade_in_speed = 10  # Speed of the fade-in animation
info_displayed = False
hand_detected = False  # Track if hand detection has occurred

cap = cv2.VideoCapture(1)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
pointer_pos = [screen_width // 2, screen_height // 2]

def get_weather_info():
    # This is a placeholder function. Replace this with actual weather fetching logic.
    return "Sunny 25°C"

def switch_to_home_interface():
    global current_interface, screen
    if current_interface == INTERFACE_3D:
        pygame.quit()
        pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Home Interface")
    current_interface = INTERFACE_HOME

def switch_to_2d_interface():
    global current_interface
    if current_interface == INTERFACE_3D:
        pygame.quit()
        pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("2D Image Loading Interface")
    current_interface = INTERFACE_2D

def switch_to_3d_interface():
    global current_interface, screen
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Model Loading Interface")
    current_interface = INTERFACE_3D

def switch_to_object_recognition_interface():
    global current_interface
    if current_interface == INTERFACE_3D:
        pygame.quit()
        pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Object Recognition Interface")
    current_interface = INTERFACE_OBJECT_RECOGNITION

def handle_interface_switching():
    global current_interface
    if os.path.exists("switch_to_home_command.txt"):
        current_interface = INTERFACE_HOME
        os.remove("switch_to_home_command.txt")
    elif os.path.exists("switch_to_2d_command.txt"):
        current_interface = INTERFACE_2D
        os.remove("switch_to_2d_command.txt")
    elif os.path.exists("switch_to_3d_command.txt"):
        current_interface = INTERFACE_3D
        os.remove("switch_to_3d_command.txt")
    elif os.path.exists("switch_to_object_recognition_command.txt"):
        current_interface = INTERFACE_OBJECT_RECOGNITION
        os.remove("switch_to_object_recognition_command.txt")

    if current_interface == INTERFACE_HOME:
        draw_home_interface()
    elif current_interface == INTERFACE_2D:
        load_images_interface()
    elif current_interface == INTERFACE_3D:
        load_models_interface()
    elif current_interface == INTERFACE_OBJECT_RECOGNITION:
        object_recognition_interface()

def render_text_centered(surface, text, initial_font, center, max_radius):
    font_size = initial_font.get_height()
    font = pygame.font.Font(None, font_size)

    # Reduce the font size until the text fits within the specified radius
    while font.size(text)[0] > max_radius * 2 or font.size(text)[1] > max_radius * 2:
        font_size -= 1
        font = pygame.font.Font(None, font_size)

    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

# Function to draw the rotating JARVIS logo
def draw_jarvis_logo(surface, text, center, radius, angle_offset):
    text_surface = small_font.render(text, True, iron_blue)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

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

def draw_home_interface():
    global info_alpha, info_displayed, hand_detected
    screen.fill(black)
    
    # Draw the home button
    pygame.draw.circle(screen, home_button["color"], home_button["pos"], button_radius)
    render_text_centered(screen, home_button["label"], font, home_button["pos"], button_radius)
    
    if buttons_visible:
        current_time = time.time()
        elapsed_time = current_time - animation_start_time
        animation_progress = min(elapsed_time / animation_duration, 1)
        
        angle_step = 360 / len(buttons)
        for i, button in enumerate(buttons):
            angle = math.radians(angle_step * i)
            target_x = home_button["pos"][0] + button_margin * math.cos(angle)
            target_y = home_button["pos"][1] + button_margin * math.sin(angle)
            button["pos"] = (home_button["pos"][0] + (target_x - home_button["pos"][0]) * animation_progress,
                             home_button["pos"][1] + (target_y - home_button["pos"][1]) * animation_progress)
            button["visible"] = animation_progress >= 1
            pygame.draw.circle(screen, button["color"], button["pos"], button_radius)
            render_text_centered(screen, button["label"], small_font, button["pos"], button_radius)

    # Hand detection
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)
        index_finger_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        pointer_pos[0] = screen_width - int(index_finger_tip.x * screen_width)
        pointer_pos[1] = int(index_finger_tip.y * screen_height)
        hand_detected = True

        # Start fade-in animation if not already displayed
        if not info_displayed and info_alpha < 255:
            info_alpha = min(info_alpha + fade_in_speed, 255)
            if info_alpha == 255:
                info_displayed = True

    # Draw time and weather only after hand is detected
    if hand_detected:
        if info_alpha > 0:
            time_text = small_font.render(time.strftime('%H:%M:%S'), True, blue)
            weather_text = small_font.render(get_weather_info(), True, blue)
            
            time_surface = pygame.Surface(time_text.get_size(), pygame.SRCALPHA)
            weather_surface = pygame.Surface(weather_text.get_size(), pygame.SRCALPHA)
            
            time_surface.blit(time_text, (0, 0))
            weather_surface.blit(weather_text, (0, 0))
            
            time_surface.set_alpha(info_alpha)
            weather_surface.set_alpha(info_alpha)
            
            screen.blit(time_surface, (20, 20))
            screen.blit(weather_surface, (screen_width - weather_text.get_width() - 20, 20))

    # Draw JARVIS logo if wake word is detected
    if os.path.exists("wake_word_detected.txt"):
        jarvis_center = (100, screen_height - 100)
        draw_jarvis_logo(screen, "JARVIS", jarvis_center, 50, pygame.time.get_ticks())

def load_images_interface():
    global screen
    pygame.display.set_caption("2D Image Loading Interface")

    # Load dustbin image
    dustbin_image = pygame.image.load('./Dustbin/dustbin.png')
    dustbin_rect = dustbin_image.get_rect()
    dustbin_rect.bottomright = (screen_width - 120, screen_height - 120)

    # Objects data
    objects = []

    selected_object = None
    is_dragging = False
    images_loaded = False

    # Animation variables
    current_image_index = 0
    image_display_time = 1200  # Time to display each image in milliseconds
    last_image_switch_time = pygame.time.get_ticks()

    def draw_glowing_circle(surface, color, center, radius, glow_radius):
        for i in range(glow_radius):
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, max(255 - 255 * (i / glow_radius), 0)), (radius, radius), radius)
            surface.blit(s, (center[0] - radius, center[1] - radius), special_flags=pygame.BLEND_RGBA_ADD)

    def load_images():
        images_folder = './images'
        max_image_size = (200, 200)
        image_objects = []
        for i, filename in enumerate(os.listdir(images_folder)):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img_path = os.path.join(images_folder, filename)
                image = pygame.image.load(img_path)
                image_rect = image.get_rect()

                if image_rect.width > max_image_size[0] or image_rect.height > max_image_size[1]:
                    image = pygame.transform.scale(image, max_image_size)
                    image_rect = image.get_rect()
                col = i % 4
                row = i // 4
                x = col * 200 + 100
                y = row * 200 + 100
                image_rect = image.get_rect(center=(x, y))
                image_objects.append({"type": "image", "image": image, "rect": image_rect, "zoom_factor": 1.0})
        return image_objects

    running = True

    while running:
        success, img = cap.read()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            if len(results.multi_hand_landmarks) == 1:
                hand = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

                index_finger_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                pointer_pos[0] = screen_width - int(index_finger_tip.x * screen_width)
                pointer_pos[1] = int(index_finger_tip.y * screen_height)

                thumb_tip = hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_x = screen_width - int(thumb_tip.x * screen_width)
                thumb_y = int(thumb_tip.y * screen_height)

                if abs(pointer_pos[0] - thumb_x) < 40 and abs(pointer_pos[1] - thumb_y) < 40:
                    if selected_object is None:
                        for i, obj in enumerate(objects):
                            if obj["type"] == "circle":
                                current_size = int(obj["size"] * obj["zoom_factor"])
                                if math.dist(pointer_pos, obj["pos"]) < current_size:
                                    selected_object = i
                                    is_dragging = True
                                    break
                            elif obj["type"] == "image":
                                if obj["rect"].collidepoint(pointer_pos):
                                    selected_object = i
                                    is_dragging = True
                                    break
                    else:
                        if objects[selected_object]["type"] == "circle":
                            objects[selected_object]["pos"] = pointer_pos
                        elif objects[selected_object]["type"] == "image":
                            objects[selected_object]["rect"].center = pointer_pos
                else:
                    if selected_object is not None:
                        obj = objects[selected_object]
                        if obj["type"] == "circle":
                            if dustbin_rect.collidepoint(obj["pos"]):
                                objects.pop(selected_object)
                        elif obj["type"] == "image":
                            if dustbin_rect.colliderect(obj["rect"]):
                                objects.pop(selected_object)
                    is_dragging = False
                    selected_object = None

            elif len(results.multi_hand_landmarks) == 2:
                hand1 = results.multi_hand_landmarks[0]
                hand2 = results.multi_hand_landmarks[1]
                mp_draw.draw_landmarks(img, hand1, mp_hands.HAND_CONNECTIONS)
                mp_draw.draw_landmarks(img, hand2, mp_hands.HAND_CONNECTIONS)

                index1 = hand1.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb1 = hand1.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index2 = hand2.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb2 = hand2.landmark[mp_hands.HandLandmark.THUMB_TIP]

                index1_x = screen_width - int(index1.x * screen_width)
                index1_y = int(index1.y * screen_height)
                thumb1_x = screen_width - int(thumb1.x * screen_width)
                thumb1_y = int(thumb1.y * screen_height)
                index2_x = screen_width - int(index2.x * screen_width)
                index2_y = int(index2.y * screen_height)
                thumb2_x = screen_width - int(thumb2.x * screen_width)
                thumb2_y = int(thumb2.y * screen_height)

                pinch1 = abs(index1_x - thumb1_x) < 40 and abs(index1_y - thumb1_y) < 40
                pinch2 = abs(index2_x - thumb2_x) < 40 and abs(index2_y - thumb2_y) < 40

                if pinch1 and pinch2:
                    distance = ((index2_x - index1_x) ** 2 + (index2_y - index1_y) ** 2) ** 0.5

                    if selected_object is not None:
                        objects[selected_object]["zoom_factor"] = distance / initial_distance
                        if objects[selected_object]["type"] == "image":
                            objects[selected_object]["rect"].size = (
                                int(objects[selected_object]["image"].get_width() * objects[selected_object]["zoom_factor"]),
                                int(objects[selected_object]["image"].get_height() * objects[selected_object]["zoom_factor"])
                            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os.remove("load_images_command.txt")
                running = False

        screen.fill(black)

        for x in range(0, screen_width, 50):
            pygame.draw.line(screen, iron_blue, (x, 0), (x, screen_height), 1)
        for y in range(0, screen_height, 50):
            pygame.draw.line(screen, iron_blue, (0, y), (screen_width, y), 1)

        for i, obj in enumerate(objects):
            if i <= current_image_index:
                if obj["type"] == "circle":
                    current_size = int(obj["size"] * obj["zoom_factor"])
                    draw_glowing_circle(screen, iron_yellow, obj["pos"], current_size, 100)
                    pygame.draw.circle(screen, iron_blue, obj["pos"], current_size)
                elif obj["type"] == "image":
                    scaled_image = pygame.transform.scale(obj["image"], obj["rect"].size)
                    screen.blit(scaled_image, obj["rect"])

        pygame.draw.circle(screen, white, pointer_pos, 10)

        text = font.render('JARVIS Interface', True, iron_green)
        screen.blit(text, (20, 20))

        angle = pygame.time.get_ticks() / 1000 * 90
        for i in range(4):
            length = 20
            end_pos = (
                pointer_pos[0] + math.cos(math.radians(angle + i * 90)) * length,
                pointer_pos[1] + math.sin(math.radians(angle + i * 90)) * length
            )
            pygame.draw.line(screen, red, pointer_pos, end_pos, 2)

        if os.path.exists("wake_word_detected.txt"):
            jarvis_center = (100, screen_height - 100)
            draw_jarvis_logo(screen, "JARVIS", jarvis_center, 50, angle)

        if os.path.exists("load_images_command.txt") and not images_loaded:
            objects += load_images()
            images_loaded = True

        if os.path.exists("switch_to_home_command.txt"):
            if os.path.exists("load_images_command.txt"):
                os.remove("load_images_command.txt")
            running = False
            return

        screen.blit(dustbin_image, dustbin_rect)

        for obj in objects:
            if obj["type"] == "circle":
                if dustbin_rect.collidepoint(obj["pos"]):
                    draw_glowing_circle(screen, red, obj["pos"], obj["size"], 20)
            elif obj["type"] == "image":
                if dustbin_rect.colliderect(obj["rect"]):
                    s = pygame.Surface(obj["rect"].size, pygame.SRCALPHA)
                    s.fill((255, 0, 0, 128))
                    screen.blit(s, obj["rect"])

        current_time = pygame.time.get_ticks()
        if current_time - last_image_switch_time > image_display_time:
            if current_image_index < len(objects) - 1:
                current_image_index += 1
                last_image_switch_time = current_time

        pygame.display.flip()

    cap.release()
    pygame.quit()
    switch_to_home_interface()

def load_obj(filename):
    vertices = []
    faces = []

    with open(filename) as file:
        for line in file:
            if line.startswith('v '):
                vertex = list(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = [int(index.split('/')[0]) for index in line.strip().split()[1:]]
                faces.append(face)

    return np.array(vertices), np.array(faces)

def draw_model(vertices, faces):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex_index in face:
            glVertex3fv(vertices[vertex_index - 1])
    glEnd()

def normalize_and_scale(vertices, scale_factor):
    centroid = np.mean(vertices, axis=0)
    vertices -= centroid
    max_distance = np.max(np.linalg.norm(vertices, axis=1))
    vertices /= max_distance
    vertices *= scale_factor
    return vertices

def load_models_interface():
    global screen
    print("Loading 3D Model Interface")
    screen = pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Model Loading Interface")
    gluPerspective(45, (screen_width / screen_height), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    vertices, faces = load_obj('./models/FinalBaseMesh.obj')
    vertices = normalize_and_scale(vertices, 1.0)
    rotation_speed = 2
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if os.path.exists("switch_to_home_command.txt"):
            running = False
            break

        glRotatef(rotation_speed, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_model(vertices, faces)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    switch_to_home_interface()

def object_recognition_interface():
    print("Loading Object Recognition Interface")
    # Place your object recognition code here

def main_loop():
    global screen, running, buttons_visible, animation_start_time
    running = True
    while running:
        handle_interface_switching()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if current_interface == INTERFACE_HOME:
                    if math.dist(mouse_pos, home_button["pos"]) <= button_radius:
                        buttons_visible = not buttons_visible
                        if buttons_visible:
                            animation_start_time = time.time()
                    for button in buttons:
                        if button["visible"] and math.dist(mouse_pos, button["pos"]) <= button_radius:
                            action = button["action"]
                            if action == "load_images":
                                switch_to_2d_interface()
                            elif action == "load_models":
                                switch_to_3d_interface()
                            elif action == "object_recognition":
                                switch_to_object_recognition_interface()

        pygame.display.flip()

main_loop()
pygame.quit()
