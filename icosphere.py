import pygame
import numpy as np
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE


# Constants for centering the icosahedron on the screen
OFFSET_X = SCREEN_WIDTH // 2
OFFSET_Y = SCREEN_HEIGHT // 2


# Project the 3d vertex onto 2d using orthographic projection
def project(vertex):
    """
    Project a 3D vertex onto 2D using orthographic projection.

    Args:
        vertex (tuple): The 3D vertex.

    Returns:
        tuple: The 2D projection.
    """
    x = vertex[0] * SCALE + OFFSET_X
    y = -vertex[1] * SCALE + OFFSET_Y  # We invert the y-axis because Pygame's y-axis points downward
    return int(x), int(y)


# Function to rotate the icosphere around the z-axis (z is depth, in-to and out-of the screen)
# This is only used to initially change the rotation of the planet so the poles are at the top and bottom.
def rotate_vertices_z(verts: np.ndarray, theta_z: float) -> np.ndarray:
    """
    Rotate the vertices around the z-axis.

    Args:
        verts (list): List of vertices.
        theta_z (float): Rotation angle.

    Returns:
        numpy.ndarray: Rotated vertices.
    """
    # Z-axis rotation
    rotation_matrix_z = np.array([
        [np.cos(theta_z), -np.sin(theta_z), 0],
        [np.sin(theta_z), np.cos(theta_z), 0],
        [0, 0, 1]
    ])

    return np.dot(verts, rotation_matrix_z)


class Icosphere:
    # Define the vertices for an icosahedron
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    vertices = np.array([
        [-1, phi, 0],
        [1, phi, 0],
        [-1, -phi, 0],
        [1, -phi, 0],

        [0, -1, phi],
        [0, 1, phi],
        [0, -1, -phi],
        [0, 1, -phi],

        [phi, 0, -1],
        [phi, 0, 1],
        [-phi, 0, -1],
        [-phi, 0, 1],
    ])

    # Faces for the icosahedron
    faces = np.array([
        # 5 faces around point 0
        [0, 11, 5],
        [0, 5, 1],
        [0, 1, 7],
        [0, 7, 10],
        [0, 10, 11],

        # 5 adjacent faces
        [1, 5, 9],
        [5, 11, 4],
        [11, 10, 2],
        [10, 7, 6],
        [7, 1, 8],

        # 5 faces around point 3
        [3, 9, 4],
        [3, 4, 2],
        [3, 2, 6],
        [3, 6, 8],
        [3, 8, 9],

        # 5 adjacent faces
        [4, 9, 5],
        [2, 4, 11],
        [6, 2, 10],
        [8, 6, 7],
        [9, 8, 1],
    ])

    ITERATIONS = {
        'Debug': 0,
        'Tiny': 4,
        'Small': 6,
        'Normal': 8,
        'Large': 10,
        'Huge': 12
    }

    def __init__(self, iteration_name='Debug'):
        # Cumulative rotation angle for the x-axis
        self.cum_theta_x = 0.0
        self.need_redraw = True

        # Initial rotation to align the poles
        initial_theta_z = -np.pi / 6  # rotate by 30 degrees
        self.vertices = rotate_vertices_z(self.vertices, initial_theta_z)

        # Subdivision iterations
        self._subdivide(Icosphere.ITERATIONS[iteration_name])
        self._mapsize = iteration_name

        # Zoom level
        self._zoom_level = 1.0

    # Function to find the midpoints
    @staticmethod
    def _midpoint(p1, p2):
        return (p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2

    def _subdivide(self, iterations):
        for _ in range(iterations):
            new_faces = []
            for face in self.faces:
                a = self.vertices[face[0]]
                b = self.vertices[face[1]]
                c = self.vertices[face[2]]

                # Calculate the midpoints
                ab = self._midpoint(a, b)
                bc = self._midpoint(b, c)
                ca = self._midpoint(c, a)

                # Normalize the midpoints to push them out to the sphere's surface
                ab = ab / np.linalg.norm(ab)
                bc = bc / np.linalg.norm(bc)
                ca = ca / np.linalg.norm(ca)

                # Add midpoints to vertices list
                ab_idx = len(self.vertices)
                bc_idx = len(self.vertices) + 1
                ca_idx = len(self.vertices) + 2

                self.vertices = np.vstack([self.vertices, ab, bc, ca])

                # Create 4 new faces
                new_faces.append([face[0], ab_idx, ca_idx])
                new_faces.append([face[1], bc_idx, ab_idx])
                new_faces.append([face[2], ca_idx, bc_idx])
                new_faces.append([ab_idx, bc_idx, ca_idx])

            self.faces = np.array(new_faces)

            # Normalize all vertices to ensure they are on teh sphere's surface
            for i in range(len(self.vertices)):
                self.vertices[i] = self.vertices[i] / np.linalg.norm(self.vertices[i])

    # Function to free rotate the icosphere around its polar axis, and to tilt it back and forth
    # We'll lock the tilting later to prevent anyone from flipping the planet upside down.
    def rotate_vertices(self, loc_theta_y, loc_theta_x):
        """
        Rotate the vertices around both x and y-axis.

        Args:
            loc_theta_y (float): Y-axis rotation angle.
            loc_theta_x (float): X-axis rotation angle.
        """
        # Y-axis rotation
        rotation_matrix_y = np.array([
            [np.cos(loc_theta_y), 0, np.sin(loc_theta_y)],
            [0, 1, 0],
            [-np.sin(loc_theta_y), 0, np.cos(loc_theta_y)]
        ])

        # X-axis rotation
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, np.cos(loc_theta_x), -np.sin(loc_theta_x)],
            [0, np.sin(loc_theta_x), np.cos(loc_theta_x)]
        ])

        self.vertices = np.dot(self.vertices, rotation_matrix_y)
        self.vertices = np.dot(self.vertices, rotation_matrix_x)

    # Function to draw the icosphere
    def draw(self, screen):
        """
        Draw the icosphere on the provided screen.

        Args:
            screen (pygame.Surface): The surface on which the icosphere should be drawn.
        """
        for face in self.faces:
            v1 = project(self.vertices[face[0]])
            v2 = project(self.vertices[face[1]])
            v3 = project(self.vertices[face[2]])
            pygame.draw.polygon(screen, (255, 255, 255), [v1, v2, v3], 1)

    def handle_mouse_motion(self, dx, dy, rotation_speed):
        """
        Handle mouse motion events to rotate the icosphere.

        Args:
            dx (float): Change in x-position of the mouse.
            dy (float): Change in y-position of the mouse.
            rotation_speed (float): Speed at which the icosphere should rotate.
        """
        theta_y = rotation_speed * dx
        theta_x = rotation_speed * dy

        # Check if the cumulative rotation around x-axis is within the bounds of -80 and 80 degrees
        new_cum_theta_x = self.cum_theta_x + theta_x
        if -np.pi / 180 * 80 <= new_cum_theta_x <= np.pi / 180 * 80:
            self.cum_theta_x = new_cum_theta_x
            self.rotate_vertices(theta_y, theta_x)
        else:
            self.rotate_vertices(theta_y, 0)

        self.need_redraw = True  # Indicate that a redraw of the screen is needed, as it has been rotated.

    # Property to get the count of vertices
    @property
    def vertices_count(self):
        return len(self.vertices)

    # Property to get the count of faces
    @property
    def faces_count(self):
        return len(self.faces)

    # Property to get the current zoom level
    @property
    def zoom_level(self):
        return self._zoom_level

    # Property to get the current map size
    @property
    def mapsize(self):
        return self._mapsize

    # If you want to allow setting the zoom level in the future, you can add a setter method as well:
    @zoom_level.setter
    def zoom_level(self, value):
        # Here, you can include logic to check if the value is within an acceptable range or make any other
        # necessary adjustments.
        self._zoom_level = value
        self.need_redraw = True  # Indicate that a redraw is needed due to zoom level change.