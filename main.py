import pygame
import sys
import random
import cv2
import numpy as np

# Modules
from audio_manager import AudioManager
from input_manager import MouseInput, HandInput
from ui_manager import SceneManager
from game_engine import ClassicMode, SurvivalMode
from game_objects import Blade, Fruit, Bomb, SlicedFruit, Explosion

# Colors
WHITE = (255, 255, 255)

# Config
WIDTH, HEIGHT = 800, 600 # Keeping larger window for menu usability
FPS = 60
MIN_CUT_VELOCITY = 150 # Rescaled 

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Ninja Final")
    clock = pygame.time.Clock()
    
    # Systems
    audio = AudioManager()
    ui = SceneManager(WIDTH, HEIGHT)
    
    # Game State Variables
    input_provider = None
    game_mode = None
    blade = Blade()
    
    all_sprites = pygame.sprite.Group()
    fruits = pygame.sprite.Group() # Only active fruits (not slices or bombs)
    
    # Start Music
    audio.play_music("menu")
    
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        click = False
        
        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    
        # --- SCENE LOGIC ---
        
        if ui.current_scene == "MENU":
            action = ui.handle_input("MENU", mx, my, click)
            ui.draw_menu(screen)
            if action == "GOTO_MODE":
                ui.current_scene = "MODE_SEL"
                audio.play_sfx("start")

        elif ui.current_scene == "MODE_SEL":
            action = ui.handle_input("MODE_SEL", mx, my, click)
            ui.draw_mode_select(screen)
            if action == "MODE_CLASSIC":
                game_mode = ClassicMode()
                ui.current_scene = "INPUT_SEL"
                audio.play_sfx("start")
            elif action == "MODE_SURVIVAL":
                game_mode = SurvivalMode()
                ui.current_scene = "INPUT_SEL"
                audio.play_sfx("start")
                
        elif ui.current_scene == "INPUT_SEL":
            action = ui.handle_input("INPUT_SEL", mx, my, click)
            ui.draw_input_select(screen)
            
            if action: # Selection made
                # Init Input
                if action == "INPUT_MOUSE":
                    input_provider = MouseInput(WIDTH, HEIGHT)
                elif action == "INPUT_HAND":
                    input_provider = HandInput(WIDTH, HEIGHT)
                
                # Start Game
                ui.current_scene = "GAME"
                audio.play_music("game_slow")
                # Reset sprites
                all_sprites.empty()
                fruits.empty()
                blade = Blade()

        elif ui.current_scene == "GAME":
            # 1. Update Input
            ix, iy, velocity, is_paused = input_provider.get_input()
            
            # Draw Background (Camera or Default)
            if hasattr(input_provider, 'get_frame'):
                frame = input_provider.get_frame()
                if frame is not None:
                     # Convert and scale
                     img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                     img_rgb = np.rot90(img_rgb)
                     surf = pygame.surfarray.make_surface(img_rgb)
                     surf = pygame.transform.flip(surf, True, False)
                     screen.blit(pygame.transform.scale(surf, (WIDTH, HEIGHT)), (0,0))
                else:
                    screen.fill((50, 50, 50))
            else:
                screen.fill((20, 20, 20)) # Dark background for mouse mode
            
            # 2. Update Logic
            if not is_paused:
                # Update Blade
                if ix is not None:
                    blade.update(ix, iy)
                
                # Spawner
                if random.randint(1, 40) == 1:
                    # Spawn logic
                    spawn_x = random.randint(100, WIDTH-100)
                    spawn_y = HEIGHT + 20
                    
                    if random.randint(1, 5) == 1: # 20% Bomb
                        b = Bomb(spawn_x, spawn_y, WIDTH, HEIGHT)
                        all_sprites.add(b)
                        fruits.add(b)
                    else:
                        f = Fruit(spawn_x, spawn_y, WIDTH, HEIGHT)
                        all_sprites.add(f)
                        fruits.add(f)
                
                all_sprites.update()
                
                # Collisions
                segments = blade.get_segments()
                if velocity > MIN_CUT_VELOCITY and segments:
                    hit_count = 0 
                    # We iterate copy because we modify group
                    for entity in list(fruits):
                        if entity.check_slice(segments):
                            hit_count += 1
                            
                            if isinstance(entity, Bomb):
                                # Hit Bomb
                                audio.play_sfx("bomb")
                                boom = Explosion(entity.pos_x, entity.pos_y)
                                all_sprites.add(boom)
                                entity.kill()
                                game_mode.on_bomb()
                                
                            else:
                                # Hit Fruit
                                audio.play_sfx("splat")
                                pts = game_mode.on_slice(entity)
                                
                                # Spawn halves
                                h1 = SlicedFruit(entity.pos_x, entity.pos_y, entity.fruit_type, 1)
                                h2 = SlicedFruit(entity.pos_x, entity.pos_y, entity.fruit_type, 2)
                                all_sprites.add(h1)
                                all_sprites.add(h2)
                                entity.kill()
                    
                    # Combo Sound
                    if hit_count > 1:
                        audio.play_sfx("combo")

                # Check dropped fruits
                for entity in list(fruits):
                     if entity.rect.top > HEIGHT:
                         if not isinstance(entity, Bomb): # Dropping bomb is fine
                             game_mode.on_miss()
                             entity.kill()
                         else:
                             entity.kill()

                # Check Game Over
                if game_mode.game_over:
                    ui.current_scene = "OVER"
                    audio.play_sfx("over")
                    audio.stop_music()
            
            # 3. Draw Game
            all_sprites.draw(screen)
            blade.draw(screen)
            
            # UI Overlay
            # Pause Text
            if is_paused:
                txt = ui.font_big.render("PAUSED", True, (255, 255, 0))
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
            
            # HUD
            hud = ui.font_small.render(game_mode.get_status(), True, WHITE)
            screen.blit(hud, (20, 20))

        elif ui.current_scene == "OVER":
            # Keep drawing game in background (static)
            all_sprites.draw(screen)
            action = ui.handle_input("OVER", mx, my, click)
            ui.draw_game_over(screen, game_mode.score)
            
            if action == "GOTO_MENU":
                # Cleanup
                if input_provider:
                    input_provider.cleanup()
                    input_provider = None
                ui.current_scene = "MENU"
                audio.play_music("menu")

        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
