import pygame
from config.config import CONFIG


class SettingsMenu:
    """Pygame-based settings menu for adjusting volume and sensitivity."""

    def __init__(self):
        self.screen = None
        self.font = None
        self.running = False
        self.volume_slider = 0
        self.sensitivity_slider = 0
        self.dragging_volume = False
        self.dragging_sensitivity = False

    def init(self) -> None:
        """Initialize Pygame for settings menu."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Piano Settings")
        self.font = pygame.font.SysFont(None, 32)
        self.volume_slider = int(CONFIG["volume"] * 100)
        self.sensitivity_slider = CONFIG["sensitivity"]
        self.running = True

    def draw_slider(
        self, label: str, value: int, pos: tuple, min_val: int, max_val: int
    ) -> None:
        """Draw a simple slider."""
        if self.screen is None or self.font is None:
            return
        text = self.font.render(f"{label}: {value}", True, (255, 255, 255))
        self.screen.blit(text, pos)
        pygame.draw.rect(self.screen, (200, 200, 200), (pos[0], pos[1] + 40, 200, 10))
        slider_pos = pos[0] + int((value - min_val) / (max_val - min_val) * 200)
        pygame.draw.circle(self.screen, (0, 0, 255), (slider_pos, pos[1] + 45), 10)

    def run(self) -> bool:
        """Run the settings menu loop."""
        if not self.running:
            return False
        if self.screen is None or self.font is None:
            return False

        self.screen.fill((0, 0, 0))
        self.draw_slider("Volume", self.volume_slider, (50, 50), 0, 100)
        self.draw_slider("Sensitivity", self.sensitivity_slider, (50, 150), 500, 2000)

        save_text = self.font.render("Press S to Save & Exit", True, (255, 255, 255))
        self.screen.blit(save_text, (50, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    CONFIG["volume"] = self.volume_slider / 100
                    CONFIG["sensitivity"] = self.sensitivity_slider
                    CONFIG["hit_velocity_threshold"] = self.sensitivity_slider
                    pygame.mixer.music.set_volume(CONFIG["volume"])
                    self.running = False
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    50 <= event.pos[0] <= 250 and 90 <= event.pos[1] <= 100
                ):  # Volume slider bar
                    self.dragging_volume = True
                    self.update_slider_value(event.pos, "volume")
                elif (
                    50 <= event.pos[0] <= 250 and 190 <= event.pos[1] <= 200
                ):  # Sensitivity slider bar
                    self.dragging_sensitivity = True
                    self.update_slider_value(event.pos, "sensitivity")
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_volume = False
                self.dragging_sensitivity = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_volume:
                    self.update_slider_value(event.pos, "volume")
                elif self.dragging_sensitivity:
                    self.update_slider_value(event.pos, "sensitivity")

        return True

    def update_slider_value(self, pos: tuple, slider_type: str) -> None:
        """Atualiza o valor do slider baseado na posição do mouse."""
        if slider_type == "volume":
            self.volume_slider = int((pos[0] - 50) / 200 * 100)
            self.volume_slider = max(
                0, min(100, self.volume_slider)
            )  # Limita entre 0 e 100
        elif slider_type == "sensitivity":
            self.sensitivity_slider = int(500 + (pos[0] - 50) / 200 * 1500)
            self.sensitivity_slider = max(
                500, min(2000, self.sensitivity_slider)
            )  # Limita entre 500 e 2000

    def cleanup(self) -> None:
        """Cleanup Pygame."""
        pygame.quit()
