import pygame
from icosphere import Icosphere


class Button:
    def __init__(self, x, y, width, height, text, menu, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.menu = menu
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, (128, 128, 128), self.rect)
        font = pygame.font.Font('assets/fonts/Urbanist-Bold.ttf', 20)

        label = font.render(self.text, 1, (255, 255, 255))
        label_width, label_height = label.get_size()
        center_x = (self.rect.width - label_width) // 2
        center_y = (self.rect.height - label_height) // 2

        screen.blit(label, (self.rect.x + center_x, self.rect.y + center_y))

    def handle_button_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.action:  # Check if an action is provided
                self.action()  # Execute that action
            else:
                self.menu.toggle_visibility()


class DebugMenu:

    TAB_WIDTH = 100
    TAB_HEIGHT = 20

    def __init__(self, x, y, game_manager):
        self.game_manager = game_manager
        self.rect = pygame.Rect(x, y, 400, 200)  # You can adjust width and height as needed
        self.tabs = ['Console', 'Planet Info', 'Unit Info']
        self.is_visible = False
        self.active_tab = None
        self.scroll_area = ScrollableArea(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10,
                                          self.rect.height - 30)

    def draw(self, screen, globe):
        if self.is_visible:
            # Create a semi-transparent surface for the background
            semi_transparent_surface = pygame.Surface((self.rect.width, self.rect.height))
            semi_transparent_surface.set_alpha(224)  # Semi-transparent
            semi_transparent_surface.fill((220, 220, 220))  # Fill with the color
            screen.blit(semi_transparent_surface, (self.rect.x, self.rect.y))

            menu_font = pygame.font.Font('assets/fonts/Urbanist-Regular.ttf', 14)

            # Draw the tabs
            for i, tab in enumerate(self.tabs):
                tab_x = self.rect.x + i * (self.TAB_WIDTH + 3)
                tab_y = self.rect.y - self.TAB_HEIGHT
                pygame.draw.rect(screen, (220, 220, 220), (tab_x, tab_y, self.TAB_WIDTH, self.TAB_HEIGHT),
                                 border_top_left_radius=10, border_top_right_radius=10)
                tab_surface = menu_font.render(tab, True, (0, 0, 0))
                surface_width, surface_height = tab_surface.get_size()
                center_x = tab_x + (self.TAB_WIDTH - surface_width) // 2
                center_y = tab_y + (self.TAB_HEIGHT - surface_height) // 2

                screen.blit(tab_surface, (center_x, center_y))

            if self.active_tab == "Planet Info":
                if globe is None:
                    self.scroll_area.content = [
                        "The planet has not been generated yet..."
                    ]
                    self.scroll_area.draw(screen)
                else:
                    self.scroll_area.content = [
                        "Map Size: {}".format(globe.mapsize),
                        "Total Vertices: {}".format(globe.vertices_count),
                        "Total Faces: {}".format(globe.faces_count),
                        "Vertices on Screen: {}".format(globe.drawn_vertices_count),
                        "Faces on Screen: {}".format(globe.drawn_faces_count),
                        "Zoom: {:.2f}".format(globe.normalized_scale)
                    ]
                    self.scroll_area.draw(screen)

    def toggle_visibility(self):
        self.is_visible = not self.is_visible
        return True

    def handle_debug_menu_event(self, event):
        if self.is_visible:
            if self.active_tab == "Planet Info":
                self.scroll_area.handle_scrollable_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, tab in enumerate(self.tabs):
                tab_x = self.rect.x + i * self.TAB_WIDTH
                tab_y = self.rect.y - self.TAB_HEIGHT
                tab_rect = pygame.Rect(tab_x, tab_y, self.TAB_WIDTH, 20)
                if tab_rect.collidepoint(event.pos):
                    self.active_tab = tab
                    break


class GameMenu:
    MENU_WIDTH = 130
    MENU_HEIGHT = 210

    def __init__(self, screen_width, screen_height, game_manager):
        # Calculate x, y for centered position
        x = (screen_width - self.MENU_WIDTH) // 2
        y = (screen_height - self.MENU_HEIGHT) // 2

        self.game_manager = game_manager
        self.rect = pygame.Rect(x, y, self.MENU_WIDTH, self.MENU_HEIGHT)
        self.game_buttons = [
            Button(self.rect.x + 10, self.rect.y + 10, 110, 40, 'New Game', self),
            Button(self.rect.x + 10, self.rect.y + 60, 110, 40, 'Load Game', self),
            Button(self.rect.x + 10, self.rect.y + 110, 110, 40, 'Options', self),
            Button(self.rect.x + 10, self.rect.y + 160, 110, 40, 'Quit', self)
        ]
        self.is_visible = False
        self.quit_dialog = QuitDialog(screen_width, screen_height, self)

    def draw(self, screen):
        if self.is_visible:
            semi_transparent_surface = pygame.Surface((self.MENU_WIDTH, self.MENU_HEIGHT))
            semi_transparent_surface.set_alpha(224)  # Semi-transparent
            semi_transparent_surface.fill((220, 220, 220))
            screen.blit(semi_transparent_surface, (self.rect.x, self.rect.y))

            for game_button in self.game_buttons:
                game_button.draw(screen)

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def handle_game_menu_event(self, event):
        # If the QuitDialog is visible, do not process any events for GameMenu
        if self.quit_dialog.is_visible:
            return

        if self.is_visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for game_button in self.game_buttons:
                    if game_button.rect.collidepoint(event.pos):
                        game_button.handle_button_event(event)
                        if game_button.text == 'New Game':
                            new_globe = Icosphere("Tiny")
                            self.game_manager.set_globe(new_globe)
                        if game_button.text == 'Quit':
                            self.quit_dialog.toggle_visibility()  # Show the quit dialog


class QuitDialog:
    DIALOG_WIDTH = 290
    DIALOG_HEIGHT = 130

    def __init__(self, screen_width, screen_height, parent_menu):
        # Calculate x, y for centered position
        x = (screen_width - self.DIALOG_WIDTH) // 2
        y = (screen_height - self.DIALOG_HEIGHT) // 2

        self.rect = pygame.Rect(x, y, self.DIALOG_WIDTH, self.DIALOG_HEIGHT)
        self.parent_menu = parent_menu
        self.is_visible = False

        # Buttons for the dialog
        self.yes_button = Button(self.rect.x + 10, self.rect.y + 90, 130, 30, 'Yes, quit',
                                 self, action=pygame.quit)
        self.no_button = Button(self.rect.x + 150, self.rect.y + 90, 130, 30, 'No, don’t quit', self)

    def draw(self, screen):
        if self.is_visible:
            # Create a semi-transparent surface for the background
            semi_transparent_surface = pygame.Surface((self.DIALOG_WIDTH, self.DIALOG_HEIGHT))
            semi_transparent_surface.set_alpha(224)  # Semi-transparent
            semi_transparent_surface.fill((220, 220, 220))
            screen.blit(semi_transparent_surface, (self.rect.x, self.rect.y))

            # Draw the dialog question
            font = pygame.font.Font('assets/fonts/Urbanist-Regular.ttf', 16)
            label = font.render("Quit the game?", True, (0, 0, 0))
            label_width, label_height = label.get_size()
            screen.blit(label, (self.rect.x + (self.DIALOG_WIDTH - label_width) // 2, self.rect.y + 30))

            # Draw the buttons
            self.yes_button.draw(screen)
            self.no_button.draw(screen)

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def handle_quit_dialog_event(self, event):
        if self.is_visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.yes_button.rect.collidepoint(event.pos):
                    return 'QUIT'  # Signal that we want to exit the game
                elif self.no_button.rect.collidepoint(event.pos):
                    self.toggle_visibility()  # Hide this dialog
                    self.parent_menu.toggle_visibility()  # Show the parent game menu again


class ScrollableArea:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content = []
        self.offset_y = 0
        self.font = pygame.font.Font('assets/fonts/Urbanist-Light.ttf', 13)
        self.scroll_speed = 10
        self.scrollbar_width = 10
        self.scrollbar_color = (50, 50, 50)

    def add_line(self, text):
        self.content.append(text)

    def handle_scrollable_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.offset_y = min(self.offset_y + self.scroll_speed, 0)
            elif event.button == 5:  # Mouse wheel down
                max_offset = -(len(self.content) * 15 - self.rect.height)
                self.offset_y = max(self.offset_y - self.scroll_speed, max_offset)

    def draw(self, screen):
        visible_area = screen.subsurface(self.rect)
        y = self.offset_y
        for line in self.content:
            text_surface = self.font.render(line, True, (0, 0, 0))
            visible_area.blit(text_surface, (5, y))
            y += 15

        # Compute the scrollbar height and position
        total_content_height = len(self.content) * 15
        ratio_visible = self.rect.height / total_content_height
        scrollbar_height = max(self.rect.height * ratio_visible, 10)  # Ensure it doesn't become too small
        scrollbar_height = min(scrollbar_height, self.rect.height)  # Ensure it doesn't become taller than the pane

        scrollbar_y = -self.offset_y * (self.rect.height / total_content_height)

        scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y + scrollbar_y,
                                     self.scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, self.scrollbar_color, scrollbar_rect)
