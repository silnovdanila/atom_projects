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
                  "Удачи тебе, Chelick."]

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


def obrab(motion1):
    sk = 0
    if "r" in motion1:
        sk -= 3
    if "l" in motion1:
        sk += 3
    return sk


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
            elif level[y][x] == 'w':
                Tile('window', x, y)
    return x, y

def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def main():
    global now_x, now_y, motion, now_direction
    pygame.display.flip()
    now_x, now_y = 50, 50
    idle_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_idle.png"), 4, 1, now_x, now_y)
    walk_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_walk.png"), 6, 1, 1200, 1200)
    run_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_run.png"), 6, 1, 1200, 1200)
    jump_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_jump.png"), 6, 1, 1200, 1200)
    last_player = idle_player
    running = True
    motion = ""
    jump_sk, sk_padeniya = 0, 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    motion += "r"
                elif event.key == pygame.K_d:
                    motion += "l"
                if event.key == pygame.K_SPACE:
                    if (now_y + 101) > 700:
                        jump_sk += 35
                if pygame.key.get_mods() == 4097:
                    shift = True
                else:
                    shift = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_KP_ENTER:
                    print("K_KP_ENTER")
                if event.key == pygame.K_a:
                    motion = motion.replace("r", "")
                if event.key == pygame.K_d:
                    motion = motion.replace("l", "")
                if pygame.key.get_mods() != 4097:
                    shift = False
        if jump_sk != 0:
            now_y -= jump_sk
            jump_sk -= 1
            last_player.rect = 1200, 1200
            jump_player.rect = now_x, now_y
            last_player = jump_player
        motion_chisel = obrab(motion)
        if motion_chisel == 0:
            last_player.rect = 1000, 1000
            idle_player.rect = now_x, now_y
            last_player = idle_player
        else:
            last_player.rect = 1000, 1000
            if shift:
                now_x += motion_chisel * 2
                run_player.rect = now_x, now_y
                last_player = run_player
            else:
                now_x += motion_chisel
                walk_player.rect = now_x, now_y
                last_player = walk_player
            if motion_chisel > 0:
                now_direction = "r"
            else:
                now_direction = "l"
        if (now_y + 100) < 700:
            if (700 - (now_y + 100)) < sk_padeniya:
                sk_padeniya = 700 - (now_y + 100)
            now_y = now_y + sk_padeniya
            sk_padeniya += 1
            last_player.rect = 1000, 1000
            jump_player.rect = now_x, now_y
            last_player = jump_player
        if (now_y + 100) >= 700:
            sk_padeniya = 1
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    pygame.init()
    shift = False
    now_direction = "r"
    size = WIDTH, HEIGHT = 1020, 700
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("The tale of chelik")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    tile_images = {'wall': load_image('box.png'),
    'empty': load_image('wall.png'), 'window': load_image("window.png")}
    tile_width, tile_height = WIDTH / 16, HEIGHT / 13
    FPS = 50
    level_map = load_level('map1.txt')
    level_x, level_y = generate_level(level_map)
    start_screen()
    main()
