import os
import random
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
    quit_button = pygame.draw.rect(screen, (244, 0, 0), (800, 600, 100, 50))
    ext_text = font.render("Выйти", 1, pygame.Color('black'))
    screen.blit(ext_text, (817, 614))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos() >= (800, 600):
                    if pygame.mouse.get_pos() <= (900, 650):
                        pygame.quit();
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                return
        try:
            pygame.display.flip()
        except pygame.error:
            pass
        clock.tick(FPS)


def end_screen(d):
    global all_deaths, screen


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, chislo):
        super().__init__(all_sprites)
        self.chislo = chislo
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.scheat = pygame.time.get_ticks() / 1000

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        global now_direction
        if pygame.time.get_ticks() / 1000 > self.scheat:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (70, 70))
            if now_direction == "l":
                self.image = pygame.transform.flip(self.image, True, False)
            self.scheat = pygame.time.get_ticks() / 1000 + self.chislo

    def returnSelfFrames(self):
        sp = []
        for i in self.frames:
            sp.append(pygame.transform.scale(i, (70, 70)))
        return sp


def obrab(motion1):
    sk = 0
    s = 150 / clock.get_fps()
    if "r" in motion1:
        sk -= s
    if "l" in motion1:
        sk += s
    return sk


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tw, th):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.image = pygame.transform.scale(self.image, (tw, th))


def generate_level(level):
    x, y = None, None
    sp, keySP, doorSP, spikeSP = [], [], [], []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, tile_width, tile_height)
            elif level[y][x] == '#':
                sp.append((x, y))
                Tile('wall', x, y, tile_width, tile_height)
            elif level[y][x] == 'w':
                Tile('window', x, y, tile_width, tile_height)
            elif level[y][x] == 'y':
                Tile('sky', x, y, tile_width, tile_height)
            elif level[y][x] == 'k':
                Tile('empty', x, y, tile_width, tile_height)
                Tile('key', x, y, tile_width, tile_height)
                keySP.append((x, y))
            elif level[y][x] == 'd' and level[y + 1][x] == 'd':
                Tile('empty', x, y, tile_width, tile_height)
                Tile('empty', x, y + 1, tile_width, tile_height)
                Tile('door', x, y, tile_width, tile_height * 2)
                doorSP.append((x, y))
                doorSP.append((x, y + 1))
                sp.append((x, y))
                sp.append((x, y + 1))
            elif level[y][x] == 's':
                Tile('empty', x, y, tile_width, tile_height)
                Tile('spike', x, y, tile_width, tile_height)
                spikeSP.append((x, y))

    return x, y, sp, keySP, doorSP, spikeSP


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def peredel_xy(koord, chislo):
    if koord % chislo == 0:
        return koord // chislo - 1
    return (koord // chislo)


def canPstay(x, y):
    if ((peredel_xy(x, tile_width)), (peredel_xy(y, tile_height))) in list_of_xys:
        return True
    return False


def isPontheGround(x, y):
    if canPstay(x + 15, y + 71) or canPstay(x + 55, y + 71):
        return True
    return False


def isSthNear(x, y, list):
    if (peredel_xy(x + 14, tile_width), peredel_xy(y, tile_height)) in list:
        return True, peredel_xy(x + 14, tile_width), peredel_xy(y, tile_height)
    elif (peredel_xy(x + 14, tile_width), peredel_xy(y + 35, tile_height)) in list:
        return True, peredel_xy(x + 14, tile_width), peredel_xy(y + 35, tile_height)
    elif (peredel_xy(x + 14, tile_width), peredel_xy(y + 71, tile_height)) in list:
        return True, peredel_xy(x + 14, tile_width), peredel_xy(y + 71, tile_height)
    elif (peredel_xy(x + 35, tile_width), peredel_xy(y + 71, tile_height)) in list:
        return True, peredel_xy(x + 35, tile_width), peredel_xy(y + 71, tile_height)
    elif (peredel_xy(x + 56, tile_width), peredel_xy(y + 71, tile_height)) in list:
        return True, peredel_xy(x + 56, tile_width), peredel_xy(y + 71, tile_height)
    elif (peredel_xy(x + 56, tile_width), peredel_xy(y + 35, tile_height)) in list:
        return True, peredel_xy(x + 56, tile_width), peredel_xy(y + 35, tile_height)
    elif (peredel_xy(x + 56, tile_width), peredel_xy(y, tile_height)) in list:
        return True, peredel_xy(x + 56, tile_width), peredel_xy(y, tile_height)
    elif (peredel_xy(x + 35, tile_width), peredel_xy(y, tile_height)) in list:
        return True, peredel_xy(x + 35, tile_width), peredel_xy(y, tile_height)
    return False, -1, -1


def death():
    global last_player, diLevels, now_x, now_y, now_level, x_onmap, y_onmap, tiles_group
    global tile_width
    x_onmap, y_onmap = diLevels[now_height][0], diLevels[now_height][1]
    now_x, now_y = diLevels[now_height][2], diLevels[now_height][3]
    create_particles((now_x, now_y))
    last_player.rect = now_x, now_y
    while not now_level * tile_width * 16 < x_onmap < (now_level + 1) * tile_width * 16:
        if (now_level + 1) * tile_width * 16 > x_onmap:
            for sprite in tiles_group:
                sprite.rect = sprite.rect[0] + tile_width * 16, sprite.rect[1]
            last_player.rect = now_x, now_y
            now_level -= 1
        else:
            for sprite in tiles_group:
                sprite.rect = sprite.rect[0] - tile_width * 16, sprite.rect[1]
            last_player.rect = now_x, now_y
            now_level += 1


def main():
    global motion, now_direction, listOFkeys, last_player, diLevels
    global now_height, now_x, now_y, now_level, x_onmap, y_onmap, tiles_group, all_deaths
    pygame.display.flip()
    diLevels = {0: (630, 550, 630, 550), 1: (3920, 920, 550, 200), 2: (150, 2020, 150, 590),
                3: (4131, 2624, 771, 479)}
    now_x, now_y = 630, 550
    idle_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_idle.png"), 4, 1, now_x,
                                 now_y, 0.15)
    walk_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_walk.png"), 6, 1, 1200,
                                 1200, 0.12)
    run_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_run.png"), 6, 1, 1200,
                                1200, 0.12)
    jump_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_jump1.png"), 4, 1, 1200,
                                 1200, 0.12)
    last_player = idle_player
    playerKeys = 0
    running = True
    motion = ""
    jump_sk, sk_padeniya, kol_vo_prijkov = 0, 0, 0
    f_perehoda = False
    now_level, now_height = 0, 0
    all_deaths = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    motion += "r"
                elif event.key == pygame.K_d:
                    motion += "l"
                if event.key == pygame.K_SPACE:
                    x_onmap = now_x + now_level * tile_width * 16
                    y_onmap = now_y + now_height * tile_height * 13
                    fastPeremen = clock.get_fps()
                    if isPontheGround(x_onmap, y_onmap):
                        jump_sound.play()
                        jump_sk = 900 / clock.get_fps()
                    elif not isPontheGround(x_onmap, y_onmap) and kol_vo_prijkov < 2:
                        kol_vo_prijkov += 1
                        sk_padeniya = 1
                        jump_sk = 900 / clock.get_fps()
                if pygame.key.get_mods() == 4097:
                    shift = True
                else:
                    shift = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    motion = motion.replace("r", "")
                if event.key == pygame.K_d:
                    motion = motion.replace("l", "")
                if pygame.key.get_mods() != 4097:
                    shift = False
        x_onmap = now_x + now_level * tile_width * 16
        y_onmap = now_y + now_height * tile_height * 13
        if jump_sk != 0:
            if canPstay(x_onmap + 16, y_onmap - 1) or canPstay(x_onmap + 54, y_onmap - 1) or \
                    canPstay(x_onmap + 35, y_onmap - 1):
                jump_sk = 0
            else:
                now_y -= jump_sk
                jump_sk -= 50 / clock.get_fps()
                if jump_sk < 0:
                    jump_sk = 0
                last_player.rect = 1200, 1200
                jump_player.rect = now_x, now_y
                last_player = jump_player
        x_onmap = now_x + now_level * tile_width * 16
        y_onmap = now_y + now_height * tile_height * 13
        motion_chisel = obrab(motion)
        if (canPstay(x_onmap + 56, y_onmap + 7) or canPstay(x_onmap + 56, y_onmap + 65) \
            or canPstay(x_onmap + 56, y_onmap + 35)) and motion_chisel > 0:
            motion_chisel = 0
        if (canPstay(x_onmap + 14, y_onmap + 7) or canPstay(x_onmap + 14, y_onmap + 65) \
            or canPstay(x_onmap + 14, y_onmap + 35)) and motion_chisel < 0:
            motion_chisel = 0
        if motion_chisel == 0:
            if isPontheGround(x_onmap, y_onmap):
                last_player.rect = 1000, 1000
                idle_player.rect = now_x, now_y
                last_player = idle_player
        else:
            x_onmap = now_x + now_level * tile_width * 16
            y_onmap = now_y + now_height * tile_height * 13
            if shift:
                if isPontheGround(x_onmap, y_onmap):
                    last_player.rect = 1000, 1000
                    now_x += motion_chisel * 2
                    run_player.rect = now_x, now_y
                    last_player = run_player
                else:
                    now_x += motion_chisel * 2
                    last_player.rect = now_x, now_y
            else:
                if isPontheGround(x_onmap, y_onmap):
                    last_player.rect = 1000, 1000
                    now_x += motion_chisel
                    walk_player.rect = now_x, now_y
                    last_player = walk_player
                else:
                    now_x += motion_chisel
                    last_player.rect = now_x, now_y
            if motion_chisel > 0:
                now_direction = "r"
            else:
                now_direction = "l"
        x_onmap = now_x + now_level * tile_width * 16
        y_onmap = now_y + now_height * tile_height * 13
        if not isPontheGround(x_onmap, y_onmap) and jump_sk <= 0:
            now_y = now_y + sk_padeniya
            if sk_padeniya <= 900 / clock.get_fps():
                sk_padeniya += 50 / clock.get_fps()
            last_player.rect = 1000, 1000
            jump_player.rect = now_x, now_y
            last_player = jump_player
        x_onmap = now_x + now_level * tile_width * 16
        y_onmap = now_y + now_height * tile_height * 13
        while canPstay(x_onmap + 35, y_onmap + 70):
            now_y -= 1
            last_player.rect = now_x, now_y
            y_onmap = now_y + now_height * tile_height * 13
        while canPstay(x_onmap + 35, y_onmap):
            now_y += 1
            last_player.rect = now_x, now_y
            y_onmap = now_y + now_height * tile_height * 13
        while canPstay(x_onmap + 55, y_onmap + 7) or canPstay(x_onmap + 55, y_onmap + 65) \
                or canPstay(x_onmap + 55, y_onmap + 35):
            now_x = now_x - 1
            last_player.rect = now_x, now_y
            x_onmap = now_x + now_level * tile_width * 16
        while canPstay(x_onmap + 15, y_onmap + 35) or canPstay(x_onmap + 15, y_onmap + 7) \
                or canPstay(x_onmap + 15, y_onmap + 65):
            now_x = now_x + 1
            last_player.rect = now_x, now_y
            x_onmap = now_x + now_level * tile_width * 16
        if isPontheGround(x_onmap, y_onmap):
            sk_padeniya = 1
            kol_vo_prijkov = 1
        x_onmap = now_x + now_level * tile_width * 16
        y_onmap = now_y + now_height * tile_height * 13
        key_f, key_x, key_y = isSthNear(x_onmap, y_onmap, listOFkeys)
        if key_f:
            key_f = False
            playerKeys += 1
            Tile('empty', key_x - now_level * 16, key_y - now_height * 13, tile_width, tile_height)
            listOFkeys.remove((key_x, key_y))
            idle_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_idle.png"), 4, 1, 1200,
                                         1200, 0.12)
            walk_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_walk.png"), 6, 1, 1200,
                                         1200, 0.12)
            run_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_run.png"), 6, 1, 1200,
                                        1200, 0.12)
            jump_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_jump1.png"), 4, 1, 1200,
                                         1200, 0.12)
        door_f, door_x, door_y = isSthNear(x_onmap, y_onmap, listOfdoors)
        if door_f:
            door_f = False
            if playerKeys > 0:
                playerKeys -= 1
                listOfdoors.remove((door_x, door_y))
                list_of_xys.remove((door_x, door_y))
                Tile('empty', door_x - now_level * 16, door_y - now_height * 13,
                     tile_width, tile_height)
                if (door_x, door_y - 1) in listOfdoors:
                    listOfdoors.remove((door_x, door_y - 1))
                    list_of_xys.remove((door_x, door_y - 1))
                    Tile('empty', door_x - now_level * 16, door_y - 1 - now_height * 13,
                         tile_width, tile_height)
                elif (door_x, door_y + 1) in listOfdoors:
                    listOfdoors.remove((door_x, door_y + 1))
                    list_of_xys.remove((door_x, door_y + 1))
                    Tile('empty', door_x - now_level * 16, door_y + 1 - now_height * 13,
                         tile_width, tile_height)
                idle_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_idle.png"), 4, 1,
                                             1200, 1200, 0.12)
                walk_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_walk.png"), 6, 1,
                                             1200, 1200, 0.12)
                run_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_run.png"), 6, 1, 1200,
                                            1200, 0.12)
                jump_player = AnimatedSprite(load_image("3 SteamMan\SteamMan_jump1.png"), 4, 1,
                                             1200, 1200, 0.12)
                doorOpened.play()
        spike_f, spike_x, spike_y = isSthNear(x_onmap, y_onmap, lOFspikes)
        if spike_f:
            spike_f = False
            death()
            all_deaths += 1
        if not now_level * tile_width * 16 < x_onmap < (now_level + 1) * tile_width * 16:
            if (now_level + 1) * tile_width * 16 > x_onmap:
                for sprite in tiles_group:
                    sprite.rect = sprite.rect[0] + tile_width * 16, sprite.rect[1]
                now_x = 1100
                last_player.rect = now_x, now_y
                now_level -= 1
                x_onmap = now_x + tile_width * 16 * now_level
            else:
                for sprite in tiles_group:
                    sprite.rect = sprite.rect[0] - tile_width * 16, sprite.rect[1]
                now_x = 2
                last_player.rect = now_x, now_y
                now_level += 1
                x_onmap = now_x + tile_width * 16 * now_level
        if not now_height * tile_height * 13 < y_onmap < (now_height + 1) * tile_height * 13:
            if (now_height + 1) * tile_height * 13 > y_onmap:
                for sprite in tiles_group:
                    sprite.rect = sprite.rect[0], sprite.rect[1] + tile_height * 13
                now_y = 600
                last_player.rect = now_x, now_y
                now_height -= 1
                y_onmap = now_y + tile_height * 13 * now_height
            else:
                for sprite in tiles_group:
                    sprite.rect = sprite.rect[0], sprite.rect[1] - tile_height * 13
                now_y = 100
                last_player.rect = now_y, now_y
                now_height += 1
                y_onmap = now_y + tile_height * 13 * now_height
        if x_onmap < 0:
            running = False
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        clock.tick(FPS)
        pygame.display.flip()
    screen.fill(pygame.Color("black"))
    intro_text = ["The tale of chelik", "",
                  "Вот вы и прошли демо версию",
                  f"вы молодец ведь вы умерли всего {all_deaths} раз.",
                  "Возможно, если мы привлечем инвестиции,",
                  "то в будущем будет продолжение."]
    fon = pygame.transform.scale(load_image('end_fon.jfif'), (WIDTH, HEIGHT))
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
    quit_button = pygame.draw.rect(screen, (244, 0, 0), (800, 600, 100, 50))
    ext_text = font.render("Выйти", 1, pygame.Color('black'))
    screen.blit(ext_text, (817, 614))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos() >= (800, 600):
                    if pygame.mouse.get_pos() <= (900, 650):
                        terminate()
                        running = False
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                return
        try:
            pygame.display.flip()
        except pygame.error:
            pass
        clock.tick(FPS)
    return True


if __name__ == "__main__":
    pygame.init()
    pygame.display.init()
    pygame.mixer.init()
    shift = False
    now_direction = "r"
    size = WIDTH, HEIGHT = 1120, 715
    FPS = 50
    gravity = 0.25
    screen_rect = (0, 0, WIDTH, HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("The tale of chelik")
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()


    class Particle(pygame.sprite.Sprite):
        fire = [load_image("star.png")]
        for scale in (5, 10, 20):
            fire.append(pygame.transform.scale(fire[0], (scale, scale)))

        def __init__(self, pos, dx, dy):
            super().__init__(all_sprites)
            self.image = random.choice(self.fire)
            self.rect = self.image.get_rect()
            self.velocity = [dx, dy]
            self.rect.x, self.rect.y = pos
            self.gravity = gravity

        def update(self):
            self.velocity[1] += self.gravity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            if not self.rect.colliderect(screen_rect):
                self.kill()


    def create_particles(position):
        particle_count = 20
        numbers = range(-5, 6)
        for _ in range(particle_count):
            Particle(position, random.choice(numbers), random.choice(numbers))


    try:
        start_screen()
    except pygame.error:
        print("Ну и зачем ты заходил?")
        exit(0)
    screen = pygame.display.set_mode(size)
    tile_images = {'wall': load_image('box.png'), 'empty': load_image('wall.png'),
                   'door': load_image("Basic_Door_Pixel.png"),
                   'window': load_image("window.png"), "key": load_image("key1.png"),
                   'spike': load_image('Spike_Pixel.png'), 'sky': load_image("sky.png")}
    tile_width, tile_height = WIDTH // 16, HEIGHT // 13
    level_map = load_level('map1.txt')
    level_x, level_y, list_of_xys, listOFkeys, listOfdoors, lOFspikes = generate_level(level_map)
    misic = pygame.mixer.Sound("fon_music2.wav")
    misic.play(loops=1000)
    jump_sound = pygame.mixer.Sound("jump_sound.wav")
    doorOpened = pygame.mixer.Sound("doorOpened.wav")
    for i in range(10):
        clock.tick(FPS)
    last_flag = main()
    if not last_flag:
        pygame.quit()
