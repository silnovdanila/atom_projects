import os
import sys

import pygame


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["The tale of chelik", "",
                  "Правила игры",
                  "От вас требуется немного, ",
                  "лишь любым способом пройти",
                  "от левого нижнего до правого нижнего угла.",
                  "Постарайтесь пройти как можно больше уровней.",
                  "Удачи Chelick."]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.x = x
        self.y = y

    def update(self):
        self.rect = self.rect.move(self.x, self.y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.schet = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        global now_direction
        if pygame.time.get_ticks() / 1000 > self.schet * 0.15:
            self.schet += 1
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (100, 100))
            if now_direction == "l":
                self.image = pygame.transform.flip(self.image, True, False)


def main():
    global now_x, now_y, motion, now_direction
    pygame.display.flip()
    now_x, now_y = 50, 50
    idle_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_idle.png"), 4, 1, now_x, now_y)
    walk_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_walk.png"), 6, 1, 1000, 1000)
    run_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_run.png"), 6, 1, 1000, 1000)
    last_player = idle_player
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    motion = "l"
                elif event.key == pygame.K_d:
                    motion = "r"
                if pygame.key.get_mods() == 4097:
                    shift = True
                else:
                    shift = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_KP_ENTER:
                    print("K_KP_ENTER")
                if event.key == pygame.K_SPACE:
                    real_time_but = "space"
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    motion = "s"
                if 4097 not in pygame.key.get_pressed():
                    shift = False
        if motion == "r":
            if shift:
                now_direction = "r"
                last_player.rect = 1000, 1000
                now_x += 5
                run_player.rect = now_x, now_y
                last_player = run_player
            else:
                now_direction = "r"
                last_player.rect = 1000, 1000
                now_x += 3
                walk_player.rect = now_x, now_y
                last_player = walk_player
        elif motion == "l":
            if shift:
                now_direction = "l"
                last_player.rect = 1000, 1000
                now_x -= 5
                run_player.rect = now_x, now_y
                last_player = run_player
            else:
                now_direction = "l"
                last_player.rect = 1000, 1000
                now_x -= 3
                walk_player.rect = now_x, now_y
                last_player = walk_player
        else:
            last_player.rect = 1000, 1000
            idle_player.rect = now_x, now_y
            last_player = idle_player

        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    FPS = 50
    motion = "s"
    shift = False
    now_direction = "r"
    size = WIDTH, HEIGHT = 700, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("The tale of chelik")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    start_screen()
    main()
