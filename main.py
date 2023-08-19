import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from icosphere import Icosphere
from ui_classes import Button, DebugMenu


# Function to draw labels attached to specified vertices
def draw_labels(local_screen, local_vertices, globe):
    # Define the indices for the North and South Pole vertices
    north_pole_index = 1
    south_pole_index = 2

    # Project the poles onto the screen
    north_pole_2d = globe.project(local_vertices[north_pole_index])
    south_pole_2d = globe.project(local_vertices[south_pole_index])

    # Fonts for specific labels
    pole_font = pygame.font.Font(None, 36)

    # Render the labels
    north_label = pole_font.render("N", True, (255, 64, 64))
    south_label = pole_font.render("S", True, (255, 64, 64))

    # Label offset to keep the label a bit away from the vertex
    offset = 10

    # Draw the labels
    local_screen.blit(north_label, (north_pole_2d[0], north_pole_2d[1] - offset))
    local_screen.blit(south_label, (south_pole_2d[0], south_pole_2d[1] - offset))


def main():
    # Initialize pygame
    pygame.init()

    # Set up the display & create an instance of the Icosphere.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Icosphere Map')
    globe = Icosphere('Small')

    # Variables for user-interactions
    # Mouse Dragging
    dragging = False
    prev_mouse_x, prev_mouse_y = 0, 0
    rotation_speed = 0.005  # Adjust as needed for faster/slower rotation

    # Bring in the Debug Button and Debug Menu
    debug_menu = DebugMenu(2, 54)
    debug_button = Button(2, 2, 70, 30, 'Debug', debug_menu)
    dragging_inside_debug_menu = False

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse event handling for rotation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if debug_button.rect.collidepoint(event.pos):
                    # Check if the Debug menu was clicked, and handle it.
                    debug_button.handle_event(event, globe)
                elif debug_menu.rect.collidepoint(event.pos):
                    dragging_inside_debug_menu = True
                else:
                    # If not clicking the Debug button, start dragging.
                    dragging = True
                    prev_mouse_x, prev_mouse_y = pygame.mouse.get_pos()

                if debug_menu.is_visible:
                    debug_menu.handle_event(event, globe)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    globe.zoom_in()
                elif event.button == 5:  # Mouse wheel down
                    globe.zoom_out()

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                dragging_inside_debug_menu = False

            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                dx = mx - prev_mouse_x
                dy = my - prev_mouse_y

                if dragging and not dragging_inside_debug_menu:
                    globe.handle_mouse_motion(dx, dy, rotation_speed)

                prev_mouse_x, prev_mouse_y = mx, my

        # Drawing
        if globe.need_redraw:
            screen.fill((64, 64, 64))  # Fill the screen with a dark gray background
            globe.draw(screen)  # Call the function to draw the icomap
            draw_labels(screen, globe.vertices, globe)  # Call the function to draw the labels
            globe.need_redraw = False  # Reset the redraw flag.
            debug_button.draw(screen)
            debug_menu.draw(screen, globe)
            pygame.display.flip()  # Update the full display Surface to the screen

    pygame.quit()


if __name__ == "__main__":
    main()
