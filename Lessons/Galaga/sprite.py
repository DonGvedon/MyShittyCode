import pygame


class Sprites(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, surf, score, group):
        pygame.sprite.Sprite.__init__(self)
        self.image = surf
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.score = score
        self.add(group)

    def update(self, *args):
        if self.rect.y < args[0] - 60:
            self.rect.y += self.speed
        else:
            self.kill()


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, surf, group):
        pygame.sprite.Sprite.__init__(self)
        self.image = surf
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.add(group)

    def update(self, *args):
        if self.rect.y > 0:
            self.rect.y -= self.speed
        else:
            self.kill()
