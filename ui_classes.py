import pygame


class Button:
    def __init__(self, x, y, width, height, text, menu):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.menu = menu

    def draw(self, screen):
        pygame.draw.rect(screen, (128, 128, 128), self.rect)
        font = pygame.font.Font('assets/fonts/Urbanist-Bold.ttf', 20)

        label = font.render(self.text, 1, (255, 255, 255))
        label_width, label_height = label.get_size()
        center_x = (self.rect.width - label_width) // 2
        center_y = (self.rect.height - label_height) // 2

        screen.blit(label, (self.rect.x + center_x, self.rect.y + center_y))

    def handle_event(self, event, globe):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.menu.toggle_visibility(globe)


class DebugMenu:

    TAB_WIDTH = 100
    TAB_HEIGHT = 20

    def __init__(self, x, y):
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
                self.scroll_area.content = [
                    "Map Size: {}".format(globe.mapsize),
                    "Vertices: {}".format(globe.vertices_count),
                    "Faces: {}".format(globe.faces_count),
                    "Zoom: {:.2f}".format(globe.normalized_scale)
                ]
                self.scroll_area.draw(screen)

    def toggle_visibility(self, globe):
        self.is_visible = not self.is_visible
        globe.need_redraw = True

    def handle_event(self, event, globe):
        if self.is_visible:
            if self.active_tab == "Planet Info":
                self.scroll_area.handle_event(event, globe)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, tab in enumerate(self.tabs):
                tab_x = self.rect.x + i * self.TAB_WIDTH
                tab_y = self.rect.y - self.TAB_HEIGHT
                tab_rect = pygame.Rect(tab_x, tab_y, self.TAB_WIDTH, 20)
                if tab_rect.collidepoint(event.pos):
                    self.active_tab = tab
                    globe.need_redraw = True
                    break


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

    def handle_event(self, event, globe):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                self.offset_y = min(self.offset_y + self.scroll_speed, 0)
            elif event.button == 5:  # Mouse wheel down
                max_offset = -(len(self.content) * 15 - self.rect.height)
                self.offset_y = max(self.offset_y - self.scroll_speed, max_offset)
        globe.need_redraw = True

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
