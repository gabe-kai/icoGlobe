import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from ui_classes import Button, DebugMenu, GameMenu


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


class GameManager:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Set up the display & create an instance of the Icosphere.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Icosphere Map')

        self.globe = None

        # Variables for user-interactions
        self.dragging = False
        self.prev_mouse_x, self.prev_mouse_y = 0, 0
        self.rotation_speed = 0.005  # Adjust as needed for faster/slower rotation

        # UI Initialization
        self.debug_menu = DebugMenu(2, 54, self)  # Pass the GameManager instance to DebugMenu
        self.debug_button = Button(2, 2, 70, 30, 'Debug', self.debug_menu)

        self.game_menu = GameMenu(SCREEN_WIDTH, SCREEN_HEIGHT, self)
        self.game_button = Button(SCREEN_WIDTH - 72, 2, 70, 30, 'Game', self.game_menu)

        self.dragging_inside_debug_menu = False

    def set_globe(self, globe):
        self.globe = globe
        self.globe.need_redraw = True

    def main(self):
        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Check for QuitDialog's decision
                quit_decision = self.game_menu.quit_dialog.handle_quit_dialog_event(event)
                if quit_decision == "QUIT":
                    running = False

                # Mouse event handling
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Button interactions
                    if self.game_button.rect.collidepoint(event.pos):
                        self.game_button.handle_button_event(event)
                    elif self.debug_button.rect.collidepoint(event.pos):
                        self.debug_button.handle_button_event(event)
                    # Game menu interactions
                    elif self.game_menu.quit_dialog.rect.collidepoint(event.pos):
                        self.game_menu.quit_dialog.handle_quit_dialog_event(event)
                    elif self.game_menu.rect.collidepoint(event.pos):
                        self.game_menu.handle_game_menu_event(event)
                    # Debug menu interactions
                    elif self.debug_menu.is_visible:
                        self.debug_menu.handle_debug_menu_event(event)
                    elif self.debug_menu.rect.collidepoint(event.pos):
                        self.dragging_inside_debug_menu = True
                # if event.type == pygame.MOUSEBUTTONDOWN:
                    # Globe interactions
                    elif self.globe:
                        if event.button == 4:  # Mouse wheel up
                            self.globe.zoom_in()
                        elif event.button == 5:  # Mouse wheel down
                            self.globe.zoom_out()
                    else:
                        # If not clicking the buttons, start dragging.
                        self.dragging = True
                        self.prev_mouse_x, self.prev_mouse_y = pygame.mouse.get_pos()

                # Mouse button release handling
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    self.dragging_inside_debug_menu = False

                # Moues motion handling
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    mx, my = pygame.mouse.get_pos()
                    dx = mx - self.prev_mouse_x
                    dy = my - self.prev_mouse_y

                    if self.dragging and not self.dragging_inside_debug_menu:
                        self.globe.handle_mouse_motion(dx, dy, self.rotation_speed)

                    self.prev_mouse_x, self.prev_mouse_y = mx, my

            self.screen.fill((64, 64, 64))  # Fill the screen with a dark gray background

            # Draw the globe-related items (if the globe exists)
            if self.globe:
                if self.globe.need_redraw:
                    self.globe.draw(self.screen)  # Call the function to draw the icomap
                    draw_labels(self.screen, self.globe.vertices, self.globe)  # Call the function to draw the labels
                    self.globe.need_redraw = True  # The should be False to reset the redraw flag after a redraw.

            # Draw the UI-related elements that should always be there.
            self.debug_button.draw(self.screen)
            self.debug_menu.draw(self.screen, self.globe)
            self.game_button.draw(self.screen)
            self.game_menu.draw(self.screen)
            self.game_menu.quit_dialog.draw(self.screen)

            pygame.display.flip()  # Update the full display Surface to the screen

        pygame.quit()


if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.main()
