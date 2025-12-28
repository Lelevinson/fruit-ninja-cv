import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
CYAN = (0, 255, 255)

class Button:
    def __init__(self, text, x, y, w, h, color, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action_code
        self.hover = False
        
    def draw(self, screen, font):
        col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.hover else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        
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
        
        # Menu
        self.btn_start = Button("START GAME", cx - 120, height//2 + 50, 240, 60, ORANGE, "GOTO_MODE")
        
        # Mode Select
        self.btn_classic = Button("CLASSIC", cx - 250, height//2, 200, 60, GREEN, "MODE_CLASSIC")
        self.btn_survival = Button("SURVIVAL", cx + 50, height//2, 200, 60, RED, "MODE_SURVIVAL")
        
        # Input Select
        self.btn_mouse = Button("MOUSE", cx - 250, height//2, 200, 60, CYAN, "INPUT_MOUSE")
        self.btn_hand = Button("CAMERA CHECK", cx + 50, height//2, 200, 60, ORANGE, "INPUT_HAND")
        
        # Game Over
        self.btn_restart = Button("MENU", cx - 100, height//2 + 100, 200, 60, ORANGE, "GOTO_MENU")

    def draw_menu(self, screen):
        screen.fill((30, 30, 40))
        title = self.font_big.render("FRUIT NINJA V3", True, ORANGE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        sub = self.font_small.render("Move hand/mouse to slice!", True, WHITE)
        screen.blit(sub, (self.width//2 - sub.get_width()//2, 180))
        
        self.btn_start.draw(screen, self.font_med)
        
    def draw_mode_select(self, screen):
        screen.fill((40, 30, 30))
        title = self.font_med.render("SELECT MODE", True, WHITE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        self.btn_classic.draw(screen, self.font_med)
        self.btn_survival.draw(screen, self.font_med)

    def draw_input_select(self, screen):
        screen.fill((30, 40, 40))
        title = self.font_med.render("SELECT CONTROL", True, WHITE)
        screen.blit(title, (self.width//2 - title.get_width()//2, 100))
        
        self.btn_mouse.draw(screen, self.font_med)
        self.btn_hand.draw(screen, self.font_med)
        
    def draw_game_over(self, screen, score):
        # Overlay
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(150)
        s.fill(BLACK)
        screen.blit(s, (0,0))
        
        txt = self.font_big.render("GAME OVER", True, RED)
        screen.blit(txt, (self.width//2 - txt.get_width()//2, 150))
        
        sc = self.font_med.render(f"Final Score: {score}", True, WHITE)
        screen.blit(sc, (self.width//2 - sc.get_width()//2, 250))
        
        self.btn_restart.draw(screen, self.font_med)

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
            
        elif scene == "OVER":
            self.btn_restart.check_hover(mx, my)
            return self.btn_restart.check_click(mx, my, click)
            
        return None
