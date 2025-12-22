import pygame
import cv2
import sys
import numpy as np
import random
from sensors import WebcamStream, HandTracker
from game_objects import Blade, Fruit, Bomb, SlicedFruit, Explosion

# ----- CONFIG -----
WIDTH, HEIGHT = 640, 480
FPS = 60
MIN_CUT_VELOCITY = 200 # Adjusted for lower resolution (pixels are fewer)

def map_coordinates(cam_x, cam_y, cam_w, cam_h, screen_w, screen_h):
    # Map camera coordinates to screen coordinates
    # We flip output horizontally to mirror the user
    # So cam_x=0 (left) -> screen_x=WIDTH (right)
    # But HandTracker usually flips image, so let's check.
    # Our sensors.py processes the flipped frame logic internally OR we flip here.
    # New sensors logic: 
    #   HandTracker processing RGB frame. 
    # Let's flip the coordinates manually here if we want mirror control.
    
    # Simple linear map
    sx = int((cam_x / cam_w) * screen_w)
    sy = int((cam_y / cam_h) * screen_h)
    return sx, sy

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja V2 - High Performance")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)

    # Initialize Threaded Camera
    # Note: WebcamStream starts a thread to read frames
    webcam = WebcamStream(src=0, width=WIDTH, height=HEIGHT).start()
    
    # Initialize Tracker
    tracker = HandTracker(detection_con=0.6, track_con=0.6)
    
    # Game State
    blade = Blade()
    all_sprites = pygame.sprite.Group()
    fruits = pygame.sprite.Group()
    
    score = 0
    
    # Wait for camera to warm up
    while webcam.read() is None:
        pass
        
    running = True
    while running:
        # 1. Capture & Tracking
        frame = webcam.read()
        
        # Flip frame for display/interaction (Mirror logic)
        # It feels more natural if you move right, hand goes right on screen (which is mirrored)
        frame = cv2.flip(frame, 1)
        
        # Track Hand
        fh, fw, _ = frame.shape
        tx, ty, velocity, is_palm_open = tracker.find_position(frame)
        
        # 2. Input Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update Blade only if not paused by Palm
        if is_palm_open:
            # Maybe show "PAUSE" or "SHIELD"
            pass # Don't update blade position, effectively stopping cuts
        elif tx is not None:
             # Map camera to screen
             # Since we flipped the frame beforehand, coordinates are already 'mirrored' relative to raw cam
             sx, sy = map_coordinates(tx, ty, fw, fh, WIDTH, HEIGHT)
             blade.update(sx, sy)
        else:
             pass
             
        # 3. Game Logic
        # Spawning
        # 3. Game Logic
        # Spawning
        if random.randint(1, 40) == 1:
            fx = random.randint(100, WIDTH-100)
            fy = HEIGHT + 20
            
            # 20% chance of Bomb (1 in 5)
            if random.randint(1, 5) == 1:
                obj = Bomb(fx, fy, WIDTH, HEIGHT)
            else:
                obj = Fruit(fx, fy, WIDTH, HEIGHT)
                
            all_sprites.add(obj)
            fruits.add(obj)
            
        all_sprites.update()
        
        # Collision
        segments = blade.get_segments()
        
        # Only check collision if moving fast AND NOT PALM
        if velocity > MIN_CUT_VELOCITY and segments and not is_palm_open:
            for entity in fruits:
                if entity.check_slice(segments):
                    if isinstance(entity, Bomb):
                        # GAME OVER TRIGGER
                        score -= 5 # Punishment
                        
                        # Boom Effect
                        boom = Explosion(entity.pos_x, entity.pos_y)
                        all_sprites.add(boom)
                        
                        entity.kill()
                    else:
                        # Slice Effect
                        # Spawn two halves
                        half1 = SlicedFruit(entity.pos_x, entity.pos_y, entity.fruit_type, 1)
                        half2 = SlicedFruit(entity.pos_x, entity.pos_y, entity.fruit_type, 2)
                        all_sprites.add(half1)
                        all_sprites.add(half2)
                        
                        entity.kill()
                        score += 1
        
        # 4. Rendering
        # Draw Background (Webcam)
        # Convert to Surface
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb = np.rot90(img_rgb)
        frame_surface = pygame.surfarray.make_surface(img_rgb)
        frame_surface = pygame.transform.flip(frame_surface, True, False) # Pygame rotation fix
        screen.blit(pygame.transform.scale(frame_surface, (WIDTH, HEIGHT)), (0, 0))
        
        # Draw Game
        all_sprites.draw(screen)
        blade.draw(screen)
        
        # UI
        score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_surf, (20, 20))
        
        # Palm Status
        if is_palm_open:
            pause_surf = font.render("PAUSED / PALM", True, (255, 255, 0))
            screen.blit(pause_surf, (WIDTH//2 - 100, HEIGHT//2))
        
        # Debug Info
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surf = font.render(fps_text, True, (0, 255, 0))
        screen.blit(fps_surf, (WIDTH - 150, 20))
        
        # debug_surf = font.render(f"Vel: {int(velocity)}", True, (200, 200, 200))
        # screen.blit(debug_surf, (20, 80)) # Uncomment to debug velocity threshold
        
        pygame.display.flip()
        clock.tick(FPS)
        
    webcam.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
