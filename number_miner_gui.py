import json
import math
import os
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Number Miner - Infinity Protocol")

font = pygame.font.SysFont("consolas", 18)
big_font = pygame.font.SysFont("consolas", 24)

SAVE_FILE = "number_miner_gui_save.json"


class Game:
    def __init__(self):
        self.money = 0
        self.total_money = 0
        self.numbers = [0]
        self.operations = ["+"]
        self.miners = 1
        self.multiplier = 1.0
        self.auto_sell = False
        self.prestige = 0
        self.market = 1.0


game = Game()


def save_game():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(game.__dict__, f)


def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            game.__dict__.update(json.load(f))


load_game()


def format_num(n):
    if abs(n) > 1e6:
        return f"{n:.2e}"
    return str(round(n, 4))


def value(n):
    base = math.log10(abs(n) + 1) * 10
    return base * game.market * game.multiplier


def draw_text(text, x, y, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), (x, y))


def draw_big(text, x, y):
    screen.blit(big_font.render(text, True, (255, 255, 0)), (x, y))


class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, (self.rect.x + 5, self.rect.y + 5))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()


def idle_mine():
    for _ in range(int(game.miners * game.multiplier)):
        game.numbers.append(0)


def sell_all():
    total = 0
    for n in game.numbers:
        total += value(n)
    game.money += total
    game.total_money += total
    game.numbers.clear()


def buy_miner():
    if game.money >= 300:
        game.money -= 300
        game.miners += 1


def buy_multiply():
    if game.money >= 1000:
        game.money -= 1000
        game.operations.append("*")


def buy_power():
    if game.money >= 3000:
        game.money -= 3000
        game.operations.append("^")


def toggle_auto():
    if game.money >= 1500:
        game.money -= 1500
        game.auto_sell = True


def do_prestige():
    gain = int(math.log10(game.total_money + 1))
    if gain > 0:
        game.prestige += gain
        game.multiplier += gain * 0.5
        game.money = 0
        game.total_money = 0
        game.numbers = [0]
        game.operations = ["+"]
        game.miners = 1


def create_number():
    if len(game.numbers) >= 2:
        a = game.numbers[-1]
        b = game.numbers[-2]
        result = a + b
        game.numbers.append(result)


buttons = [
    Button(300, 100, 200, 40, "Create (+ last 2)", create_number),
    Button(300, 150, 200, 40, "Sell All", sell_all),
    Button(300, 200, 200, 40, "Buy Miner ($300)", buy_miner),
    Button(300, 250, 200, 40, "Unlock * ($1000)", buy_multiply),
    Button(300, 300, 200, 40, "Unlock ^ ($3000)", buy_power),
    Button(300, 350, 200, 40, "Auto Sell ($1500)", toggle_auto),
    Button(300, 400, 200, 40, "Prestige", do_prestige),
]

clock = pygame.time.Clock()
running = True
idle_timer = 0

while running:
    clock.tick(60)
    screen.fill((20, 20, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                b.click(event.pos)

    idle_timer += 1
    if idle_timer >= 60:
        idle_mine()
        idle_timer = 0

        if game.auto_sell:
            sell_all()

    draw_big("STATS", 20, 20)
    draw_text(f"Money: {format_num(game.money)}", 20, 70)
    draw_text(f"Miners: {game.miners}", 20, 100)
    draw_text(f"Multiplier: x{round(game.multiplier, 2)}", 20, 130)
    draw_text(f"Prestige: {game.prestige}", 20, 160)
    draw_text(f"Stored Numbers: {len(game.numbers)}", 20, 190)

    for b in buttons:
        b.draw()

    draw_big("NUMBERS", 650, 20)
    for i, n in enumerate(game.numbers[-20:]):
        draw_text(format_num(n), 650, 70 + i * 22)

    pygame.display.flip()

pygame.quit()
