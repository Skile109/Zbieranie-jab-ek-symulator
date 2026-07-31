import pygame
import random
import math
import sys

pygame.init()

W, H = 1000, 700
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Zbieranie Jablek")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 22, True)
small = pygame.font.SysFont("Arial", 16)

# kolory
SKY = (120, 200, 240)
GRASS = (80, 170, 60)
BROWN = (120, 80, 45)
LEAF1 = (50, 150, 60)
LEAF2 = (70, 180, 70)
APPLE = (230, 40, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GREEN = (70, 170, 80)
ORANGE = (240, 140, 0)
RED = (220, 60, 60)
BLUE = (50, 120, 220)
GOLD = (255, 200, 0)

coins = 0
basket = 0
capacity = 4
shop_open = False

toast = ""
toast_time = 0

def toast_msg(t):
    global toast, toast_time
    toast = t
    toast_time = pygame.time.get_ticks() + 2000

# Rozszerzone pozycje jabłek dla WIĘKSZEGO drzewa
# [x_offset, y_offset, obecne_na_drzewie (bool), aktualny_rozmiar (float)]
MAX_APPLE_SIZE = 18.0

apples = [
    [-110, -110, True, MAX_APPLE_SIZE],
    [-50, -160, True, MAX_APPLE_SIZE],
    [50, -160, True, MAX_APPLE_SIZE],
    [110, -110, True, MAX_APPLE_SIZE],
    [-130, -30, True, MAX_APPLE_SIZE],
    [-60, -60, True, MAX_APPLE_SIZE],
    [0, -100, True, MAX_APPLE_SIZE],
    [60, -60, True, MAX_APPLE_SIZE],
    [130, -30, True, MAX_APPLE_SIZE],
    [-70, 30, True, MAX_APPLE_SIZE],
    [0, 20, True, MAX_APPLE_SIZE],
    [70, 30, True, MAX_APPLE_SIZE]
]

# koszyki
baskets = [
    ["Drewniany", 10, 20, BROWN, False],
    ["Niebieski", 25, 60, BLUE, False],
    ["Czerwony", 50, 150, RED, False],
    ["Zloty", 100, 400, GOLD, False]
]

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

        t = font.render(self.text, True, WHITE)
        screen.blit(t, t.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)

def tree():
    x = W // 2
    y = H - 50

    # Grubszy i wyższy pień
    pygame.draw.rect(screen, BROWN, (x - 45, y - 280, 90, 280))

    # Znacznie większa korona drzewa (duże nakładające się koła)
    pygame.draw.circle(screen, LEAF1, (x, y - 360), 150)
    pygame.draw.circle(screen, LEAF2, (x - 110, y - 310), 120)
    pygame.draw.circle(screen, LEAF2, (x + 110, y - 310), 120)
    pygame.draw.circle(screen, LEAF1, (x - 60, y - 230), 110)
    pygame.draw.circle(screen, LEAF1, (x + 60, y - 230), 110)

def apple_pos(a):
    # Dopasowane do nowego, wyższego środka korony drzewa
    return (W // 2 + a[0], H - 50 - 320 + a[1])

def draw_apple(x, y, radius):
    r = int(radius)
    if r < 2:
        r = 2
    pygame.draw.circle(screen, APPLE, (x, y), r)
    # Błysk światła
    highlight_r = max(1, int(r * 0.25))
    offset = max(1, int(r * 0.35))
    pygame.draw.circle(screen, WHITE, (x - offset, y - offset), highlight_r)

sell = Button(W - 280, 15, 120, 45, "Sprzedaj", GREEN)
shop = Button(W - 150, 15, 110, 45, "Sklep", ORANGE)

# Szybkie odnawianie (co 700 ms)
pygame.time.set_timer(pygame.USEREVENT, 700)

running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.USEREVENT:
            empty = [a for a in apples if not a[2]]
            if empty:
                chosen = random.choice(empty)
                chosen[2] = True
                chosen[3] = 2.0  # Zaczyna rosnąć od małego pączka

        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = e.pos

            if shop_open:
                box = pygame.Rect(W // 2 - 250, H // 2 - 230, 500, 460)
                close = pygame.Rect(box.right - 45, box.top + 10, 35, 35)

                if close.collidepoint(pos):
                    shop_open = False
                else:
                    for i, b in enumerate(baskets):
                        buy = pygame.Rect(box.x + 350, box.y + 70 + i * 90, 100, 45)
                        if buy.collidepoint(pos):
                            if not b[4]:
                                if coins >= b[2]:
                                    coins -= b[2]
                                    capacity = b[1]
                                    b[4] = True
                                    toast_msg("Kupiono koszyk")
                                else:
                                    toast_msg("Za malo monet")
            else:
                if sell.hit(pos):
                    if basket > 0:
                        coins += basket * 2
                        basket = 0
                    else:
                        toast_msg("Brak jablek")

                elif shop.hit(pos):
                    shop_open = True

                else:
                    for a in apples:
                        # Można zebrać, gdy jabłko urosło do co najmniej promienia 10
                        if a[2] and a[3] >= 10:
                            x, y = apple_pos(a)
                            if math.dist(pos, (x, y)) < 30:
                                if basket < capacity:
                                    a[2] = False
                                    basket += 1
                                else:
                                    toast_msg("Koszyk pelny")

    # Aktualizacja wzrostu jabłek do maksymalnego promienia 18
    for a in apples:
        if a[2] and a[3] < MAX_APPLE_SIZE:
            a[3] += 0.2  # Tempo wzrostu

    screen.fill(SKY)
    pygame.draw.rect(screen, GRASS, (0, H - 100, W, 100))

    tree()

    # Rysowanie jabłek
    for a in apples:
        if a[2]:
            draw_apple(*apple_pos(a), a[3])

    pygame.draw.rect(screen, WHITE, (15, 15, 300, 45), border_radius=10)
    screen.blit(
        font.render(f"Coins: {coins}  Koszyk: {basket}/{capacity}", True, BLACK),
        (25, 25)
    )

    sell.draw()
    shop.draw()

    if shop_open:
        dark = pygame.Surface((W, H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 120))
        screen.blit(dark, (0, 0))

        box = pygame.Rect(W // 2 - 250, H // 2 - 230, 500, 460)
        pygame.draw.rect(screen, WHITE, box, border_radius=20)
        screen.blit(font.render("Sklep z koszykami", True, BLACK), (box.x + 20, box.y + 20))
        screen.blit(font.render("X", True, RED), (box.right - 40, box.top + 15))

        for i, b in enumerate(baskets):
            y = box.y + 70 + i * 90
            pygame.draw.rect(screen, b[3], (box.x + 20, y, 60, 60), border_radius=15)
            screen.blit(
                small.render(f"{b[0]}  {b[1]} jablek  {b[2]} monet", True, BLACK),
                (box.x + 100, y + 15)
            )
            pygame.draw.rect(screen, GREEN, (box.x + 350, y + 10, 100, 45), border_radius=8)
            screen.blit(small.render("Kup", True, WHITE), (box.x + 385, y + 25))

    if pygame.time.get_ticks() < toast_time:
        screen.blit(font.render(toast, True, WHITE), (W // 2 - 100, H - 130))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()