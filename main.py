import pygame

def main():
    pygame.init()
    pygame.display.set_caption("Platformers name")
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False



if __name__ == "__main__":
    main()
