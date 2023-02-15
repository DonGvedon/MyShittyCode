from sprite import Sprites
from sprite import BulletSprite
from random import randint
from pygame.locals import *
import pygame
import time
import pymysql.cursors

try:
    connection = pymysql.connect(
        host='localhost',
        user='Gv3d0n',
        password='qwerty',
        database='game_score'
    )
    print('Oh yeah mister crabs')
except Exception as ex:
    print('NOOOOOOOOOOOO')


pygame.init()
pygame.time.set_timer(pygame.USEREVENT, 1500)
pygame.time.set_timer(pygame.USEREVENT_DROPFILE, 500)


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (0, 0, 0)
        self.active_color = (23, 204, 58)

    def draw_button(self, x, y, message, action=None, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(window, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1 and action is not None:
                pygame.time.delay(300)
                action()
        else:
            pygame.draw.rect(window, self.inactive_color, (x, y, self.width, self.height))

        print_text(message=message, x=x+10, y=y+5, font_size=font_size)


def print_text(message, x, y, font_color=(255, 0, 0), font_type='calibri', font_size=30):
    font_type = pygame.font.SysFont('Calibri', font_size)
    text = font_type.render(message, True, font_color)
    window.blit(text, (x, y))


class Constants:
    WIDTH = 750
    HEIGHT = 750
    FPS = 60
    White = (255, 255, 255)
    Green = (0, 255, 0)
    player_speed = 4
    enemy_speed = 3
    bullet_speed = 8
    player_health_counter = 0
    player_health = 3
    game_score = 0
    nickname = ''


window = pygame.display.set_mode((Constants.WIDTH, Constants.HEIGHT))
pygame.display.set_caption("Galaga")
pygame.display.set_icon(pygame.image.load("galaga_icon.png"))
bg_surf = pygame.image.load('bg.png')

clock = pygame.time.Clock()

enemy_data = [{'path': 'enemy1.png', 'score': 100},
              {'path': 'enemy2.png', 'score': 150},
              {'path': 'enemy3.png', 'score': 200}]

enemy_surf = [pygame.image.load(data['path']) for data in enemy_data]
enemies = pygame.sprite.Group()

player = pygame.image.load('main_hero.png')
player_rect = player.get_rect(center=(375, 700))

bullet_surf = pygame.image.load('bullet.png')
bullet_rect = bullet_surf.get_rect(center=(player_rect.x, player_rect.y))
bullets = pygame.sprite.Group()


class Text:
    font = pygame.font.SysFont('calibri', 36)
    text = font.render('Score: ', True, Constants.White)
    text_pos = text.get_rect(center=(56, 24))

    end_font = pygame.font.SysFont('calibri', 300)
    end_text = font.render('GAME OVER', True, Constants.White)
    end_text_pos = text.get_rect(center=(Constants.WIDTH // 2 - 50, Constants.HEIGHT // 2))


def spawn_enemy(group):
    enemy_speed = randint(1, 4)
    ind_x = randint(0, len(enemy_surf) - 1)
    x = randint(50, 700)
    y = 20
    return Sprites(x, y, enemy_speed, enemy_surf[ind_x], enemy_data[ind_x]['score'], group)


def spawn_bullet(group):
    x = player_rect.x + 35
    y = player_rect.y - 70
    bullet_speed = Constants.bullet_speed
    return BulletSprite(x, y, bullet_speed, bullet_surf, group)


def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 150
    bar_height = 25
    fill = (pct / 3) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, Constants.Green, fill_rect)
    pygame.draw.rect(surf, Constants.White, outline_rect, 2)


def pause():
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()

        window.blit(Text.end_text, Text.end_text_pos)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            menu_background()
        elif keys[pygame.K_ESCAPE]:
            exit()
        pygame.display.update()
        clock.tick(Constants.FPS)


def collide_enemies():
    for enemy in enemies:
        if player_rect.colliderect(enemy.rect):
            Constants.player_health -= 1
            enemy.kill()

    if Constants.player_health < 0:
        with connection.cursor() as cursor:
            cursor.execute("""show tables""")
            player_score = \
                f"update high_scores set scores = ('{Constants.game_score}') where name = ('{Constants.nickname}')"
            cursor.execute(player_score)
            connection.commit()
            cursor.execute("""select * from high_scores;""")
            print(cursor.fetchall())
        pause()


def collided(self, other_rect):
    return self.rect.colliderect(other_rect)


def shot_enemies():
    for enemy in enemies:
        for bullet in bullets:
            if bullet.rect.colliderect(enemy.rect):
                enemy.kill()
                bullet.kill()
                Constants.game_score += enemy.score


def menu_background():
    menu_back_ground = pygame.image.load('menu_bg.png')
    is_input_used = False
    input_text = ''

    while True:
        keys = pygame.key.get_pressed()
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()
            elif is_input_used and i.type == pygame.KEYDOWN:
                if i.key == pygame.K_RETURN:
                    Constants.nickname = input_text

                    with connection.cursor() as cursor:
                        cursor.execute("""show tables""")
                        player_name = f"insert into high_scores (name, scores) value ('{Constants.nickname}', 0)"
                        cursor.execute(player_name)
                        connection.commit()
                        cursor.execute("""select * from high_scores;""")
                        print(cursor.fetchall())

                    is_input_used = False
                    input_text = ''

                elif i.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if len(input_text) < 15:
                        input_text += i.unicode

        if keys[pygame.K_TAB]:
            is_input_used = True

        start_button = Button(150, 40)
        exit_button = Button(80, 40)

        window.blit(menu_back_ground, (0, 0))
        start_button.draw_button(300, 100, 'Start game', game_cycle)
        print_text('Press TAB to enter your name', 200, 650, (255, 10, 200))
        exit_button.draw_button(340, 700, 'Exit', exit)

        font = pygame.font.SysFont('Calibri', 30)
        img = font.render(input_text, True, (255, 0, 0))
        rect = img.get_rect()
        rect.topleft = (270, 600)
        cursor = Rect(rect.topright, (3, rect.height))
        rect.size = img.get_size()
        cursor.topleft = rect.topright
        window.blit(img, rect)
        if time.time() % 1 > 0.5:
            pygame.draw.rect(window, (255, 0, 0), cursor)

        print_text(input_text, 270, 600)

        pygame.display.update()
        clock.tick(Constants.FPS)


def game_cycle():
    while True:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()
            elif i.type == pygame.USEREVENT:
                spawn_enemy(enemies)
            elif i.type == pygame.USEREVENT_DROPFILE:
                spawn_bullet(bullets)
        keys = pygame.key.get_pressed()
        # control keys
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player_rect.y += Constants.player_speed
            if player_rect.y > Constants.HEIGHT:
                player_rect.y = 0
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            player_rect.y -= Constants.player_speed
            if player_rect.y < 0:
                player_rect.y = Constants.HEIGHT
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_rect.x += Constants.player_speed
            if player_rect.x > Constants.WIDTH:
                player_rect.x = 0
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_rect.x -= Constants.player_speed
            if player_rect.x < 0:
                player_rect.x = Constants.WIDTH

        # drawing
        window.blit(bg_surf, (0, 0))
        window.blit(player, player_rect)

        bullets.draw(window)
        bullets.update(Constants.WIDTH)
        enemies.draw(window)
        window.blit(Text.text, Text.text_pos)

        score_text = Text.font.render(str(Constants.game_score), True, Constants.White)
        score_text_pos = score_text.get_rect(center=(Text.text_pos.x + 150, Text.text_pos.y + 20))
        window.blit(score_text, score_text_pos)
        draw_health_bar(window, 580, 25, Constants.player_health)

        collide_enemies()
        enemies.update(Constants.WIDTH)
        shot_enemies()
        pygame.display.update()
        clock.tick(Constants.FPS)


menu_background()
