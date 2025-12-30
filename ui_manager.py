import pygame
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
CYAN = (0, 255, 255)

class Button:
    def __init__(self, x, y, w, h, action_code, text=None, image_name=None, color=ORANGE):
        self.rect = pygame.Rect(x, y, w, h)
        self.action = action_code
        self.text = text
        self.color = color
        self.hover = False
        self.image = None
        self.original_image = None
        
        if image_name:
            path = f"assets/ui/buttons/{image_name}"
            if os.path.exists(path):
                try:
                    raw = pygame.image.load(path).convert_alpha()
                    self.image = pygame.transform.scale(raw, (w, h))
                    self.original_image = self.image
                except Exception as e:
                    print(f"Failed to load button {image_name}: {e}")
        
    def draw(self, screen, font):
        # Hover effect
        if self.hover and self.image:
            # Simple scale up effect or brightness
            # Let's just draw it slightly larger? Or cleaner: just draw normally.
            # Maybe slight tint? 
            # For simplicity, just draw.
            pass
            
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback to text button
            col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.hover else self.color
            pygame.draw.rect(screen, col, self.rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
            
            if self.text:
                txt_surf = font.render(self.text, True, WHITE)
                text_rect = txt_surf.get_rect(center=self.rect.center)
                screen.blit(txt_surf, text_rect)
        
    def check_hover(self, mx, my):
        self.hover = self.rect.collidepoint(mx, my)
        return self.hover

    def check_click(self, mx, my, click):
        if self.rect.collidepoint(mx, my) and click:
            return self.action
        return None

class SceneManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_scene = "MENU" # MENU, MODE_SEL, INPUT_SEL, GAME, OVER
        self.font_big = pygame.font.Font(None, 80)
        self.font_med = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 30)
        
        # Buttons for various screens
        cx = width // 2
        cy = height // 2
        
        # Menu (New Asset)
        self.btn_start = Button(cx - 100, cy + 50, 200, 80, "GOTO_MODE", image_name="btn_play.png")
        
        # Mode Select (No specific assets, using fallback text)
        self.btn_classic = Button(cx - 220, cy, 200, 60, "MODE_CLASSIC", text="CLASSIC", color=GREEN)
        self.btn_survival = Button(cx + 20, cy, 200, 60, "MODE_SURVIVAL", text="SURVIVAL", color=RED)
        
        # Input Select (No specific assets)
        self.btn_mouse = Button(cx - 220, cy, 200, 60, "INPUT_MOUSE", text="MOUSE", color=CYAN)
        self.btn_hand = Button(cx + 20, cy, 200, 60, "INPUT_HAND", text="CAMERA", color=ORANGE)
        
        # Game Over (New Assets)
        self.btn_home = Button(cx - 220, cy + 100, 200, 80, "GOTO_MENU", image_name="btn_home.png")
        self.btn_replay = Button(cx + 20, cy + 100, 200, 80, "RESTART", image_name="btn_replay.png")
        
        # In-Game Icons
        self.btn_pause = Button(width - 80, 20, 60, 60, "PAUSE", image_name="btn_pause_icon.png")

    def draw_menu(self, screen):
        # screen.fill((30, 30, 40)) # Handled in main
        title = self.font_big.render("FRUIT NINJA V3", True, ORANGE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        sub = self.font_small.render("Move hand/mouse to slice!", True, WHITE)
        screen.blit(sub, (self.width//2 - sub.get_width()//2, 180))
        
        self.btn_start.draw(screen, self.font_med)
        
    def draw_mode_select(self, screen):
        # screen.fill((40, 30, 30))
        title = self.font_med.render("SELECT MODE", True, WHITE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        self.btn_classic.draw(screen, self.font_med)
        self.btn_survival.draw(screen, self.font_med)

    def draw_input_select(self, screen):
        # screen.fill((30, 40, 40))
        title = self.font_med.render("SELECT CONTROL", True, WHITE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        self.btn_mouse.draw(screen, self.font_med)
        self.btn_hand.draw(screen, self.font_med)
        
    def draw_game(self, screen):
        # Overlay UI for game
        self.btn_pause.draw(screen, self.font_med)
        
    def draw_game_over(self, screen, score):
        # Overlay
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(180) # Darker
        s.fill(BLACK)
        screen.blit(s, (0,0))
        
        txt = self.font_big.render("GAME OVER", True, RED)
        screen.blit(txt, (self.width//2 - txt.get_width()//2, 150))
        
        sc = self.font_med.render(f"Final Score: {score}", True, WHITE)
        screen.blit(sc, (self.width//2 - sc.get_width()//2, 250))
        
        self.btn_home.draw(screen, self.font_med)
        self.btn_replay.draw(screen, self.font_med)

    def handle_input(self, scene, mx, my, click):
        if scene == "MENU":
            self.btn_start.check_hover(mx, my)
            return self.btn_start.check_click(mx, my, click)
            
        elif scene == "MODE_SEL":
            self.btn_classic.check_hover(mx, my)
            self.btn_survival.check_hover(mx, my)
            a1 = self.btn_classic.check_click(mx, my, click)
            a2 = self.btn_survival.check_click(mx, my, click)
            return a1 or a2
            
        elif scene == "INPUT_SEL":
            self.btn_mouse.check_hover(mx, my)
            self.btn_hand.check_hover(mx, my)
            a1 = self.btn_mouse.check_click(mx, my, click)
            a2 = self.btn_hand.check_click(mx, my, click)
            return a1 or a2
            
        elif scene == "GAME":
            self.btn_pause.check_hover(mx, my)
            return self.btn_pause.check_click(mx, my, click)
            
        elif scene == "OVER":
            self.btn_home.check_hover(mx, my)
            self.btn_replay.check_hover(mx, my)
            a1 = self.btn_home.check_click(mx, my, click)
            a2 = self.btn_replay.check_click(mx, my, click)
            return a1 or a2
            
        return None
