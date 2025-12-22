import pygame
import random
import time
from collections import deque
import physics

# Basic Colors
RED = (255, 50, 50)
GREEN = (50, 255, 50)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

class Blade:
    def __init__(self):
        # Stores (x, y, timestamp)
        self.points = deque(maxlen=20) 
        self.color = (0, 255, 255) # Cyan for high contrast
        self.min_width = 5
        self.max_width = 25
        self.fade_speed = 5 # How fast trail fades

    def update(self, x, y):
        current_time = time.time()
        self.points.append((x, y, current_time))
        
        # Remove old points (older than 0.2s) to keep trail short & responsive
        while self.points:
            if current_time - self.points[0][2] > 0.15:
                self.points.popleft()
            else:
                break
                
    def draw(self, screen):
        if len(self.points) < 2:
            return
            
        # Draw connected lines with varying thickness
        # Newest points = thickest
        points_list = list(self.points)
        for i in range(len(points_list) - 1):
            p1 = points_list[i]
            p2 = points_list[i+1]
            
            # Ratio: 0 (oldest) to 1 (newest)
            ratio = i / len(points_list)
            width = int(self.min_width + (self.max_width - self.min_width) * ratio)
            
            # Draw line segment
            # Note: Pygame lines with width > 1 have gaps at corners. 
            # Ideally draw circles at joints, but lines are fast.
            start_pos = (p1[0], p1[1])
            end_pos = (p2[0], p2[1])
            pygame.draw.line(screen, self.color, start_pos, end_pos, width)
            pygame.draw.circle(screen, self.color, end_pos, width // 2)

    def get_segments(self):
        """Returns list of line segments ((x1,y1), (x2,y2)) currently active."""
        segments = []
        pts = list(self.points)
        for i in range(len(pts) - 1):
            segments.append(((pts[i][0], pts[i][1]), (pts[i+1][0], pts[i+1][1])))
        return segments

import os

class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, fruit_type=None):
        super().__init__()
        
        # Available types in assets
        types = ["apple", "banana", "coconut", "orange", "pineapple", "watermelon"]
        if fruit_type is None:
            self.fruit_type = random.choice(types)
        else:
            self.fruit_type = fruit_type

        # Load Image
        # Try loading small version for performance if exists, else normal
        try:
            path = f"assets/{self.fruit_type}_small.png"
            if not os.path.exists(path):
                path = f"assets/{self.fruit_type}.png"
            
            raw_image = pygame.image.load(path).convert_alpha()
            # If standard ones are huge (300KB+ pngs might be large), we might need scaling.
            # Based on file sizes, _small are ~10KB, likely icons. Large are ~300KB.
            
            if "small" not in path:
                # Scale down large images to decent game size
                self.image = pygame.transform.scale(raw_image, (70, 70))
            else:
                self.image = raw_image
                
        except Exception as e:
            # Fallback
            # print(f"Error loading {self.fruit_type}: {e}")
            self.radius = 35
            self.color = random.choice([RED, ORANGE, GREEN])
            self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width // 2 # Approx radius for collision
        self.screen_h = height
        
        # Physics
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_x = random.uniform(-1.5, 1.5) # Even slower horizontal
        self.vel_y = random.uniform(-10, -7.5) # Tuned for low gravity
        self.gravity = 0.08                    # 40% slower feel (Floaty)
        
    def update(self):
        self.vel_y += self.gravity
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        if self.rect.top > self.screen_h:
            self.kill()
            
    def check_slice(self, segments):
        """
        Check collision against a list of blade segments.
        Using swept-circle (capsule) collision.
        """
        center = (self.pos_x, self.pos_y)
        for p1, p2 in segments:
            # We treat the blade as having a thickness
            # Let's say effective blade radius is 5px
            if physics.check_capsule_circle_collision(p1, p2, 15, center, self.radius): # Increased blade radius for leniency
                return True
        return False

class SlicedFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, fruit_type, half_id):
        super().__init__()
        # Load half image
        # half_id is 1 or 2
        try:
            path = f"assets/{fruit_type}_half_{half_id}_small.png"
            if not os.path.exists(path):
                # Retry without small
                path = f"assets/{fruit_type}_half_{half_id}.png"
            
            raw = pygame.image.load(path).convert_alpha()
            if "small" not in path:
                 self.image = pygame.transform.scale(raw, (60, 60))
            else:
                 self.image = raw
        except:
            # Fallback
            self.image = pygame.Surface((30, 30))
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Physics to fly apart
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.gravity = 0.12 # Slow fall
        
        # Push apart based on ID
        if half_id == 1:
            self.vel_x = random.uniform(-4, -1)
            self.angle_speed = 2
        else:
            self.vel_x = random.uniform(1, 4)
            self.angle_speed = -2
            
        self.vel_y = random.uniform(-3, -1) # Little pop up
        
        # Rotation logic
        self.original_image = self.image
        self.angle = 0
        self.alpha = 255 # For fading if we want (optional)

    def update(self):
        self.vel_y += self.gravity
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        
        # Rotate
        self.angle += self.angle_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))
        
        if self.rect.top > 800: # Cleanup
            self.kill()

class Bomb(Fruit):
    def __init__(self, x, y, width, height):
        # Initialize parent logic partially but override image
        super().__init__(x, y, width, height, fruit_type="bomb")
        
        # Load Bomb Image specifically
        try:
            path = "assets/bomb_small.png"
            if not os.path.exists(path):
                path = "assets/bomb.png"
            
            raw_image = pygame.image.load(path).convert_alpha()
            if "small" not in path:
                self.image = pygame.transform.scale(raw_image, (80, 80)) 
            else:
                self.image = raw_image
        except:
             # Fallback
            self.radius = 40
            self.color = (50, 50, 50)
            self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            pygame.draw.circle(self.image, (255, 0, 0), (self.radius, self.radius), 15)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.radius = self.rect.width // 2

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            # Use specific explosion asset
            path = "assets/explosion_small.png"
            if not os.path.exists(path):
                 path = "assets/explosion.png"
            
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (150, 150)) # big boom
        except:
            self.image = pygame.Surface((100, 100))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 30 # frames (0.5 sec at 60fps)
        self.original_image = self.image

    def update(self):
        self.timer -= 1
        # Simple fade
        alpha = int((self.timer / 30) * 255)
        self.image.set_alpha(alpha)
        
        if self.timer <= 0:
            self.kill()
