import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Function to load OBJ file
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

# Function to draw the loaded OBJ model
def draw_model(vertices, faces):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex_index in face:
            glVertex3fv(vertices[vertex_index - 1])
    glEnd()

# Function to normalize and scale the model
def normalize_and_scale(vertices, scale_factor):
    centroid = np.mean(vertices, axis=0)
    vertices -= centroid
    max_distance = np.max(np.linalg.norm(vertices, axis=1))
    vertices /= max_distance
    vertices *= scale_factor
    return vertices

# Main function to set up the Pygame and OpenGL environment
def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # Load the OBJ model
    vertices, faces = load_obj('./models/FinalBaseMesh.obj')

    # Normalize and scale the model
    scale_factor = 1.0  # Adjust this value to fit your model in the window
    vertices = normalize_and_scale(vertices, scale_factor)

    # Rotation speed (angle increment)
    rotation_speed = 2  # Increase this value to rotate faster

    # Main loop
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glRotatef(rotation_speed, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_model(vertices, faces)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
