import pygame
import random
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (80, 80, 80)

def wrap(x, y, width, height):
    return x % width, y % height


def get_distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


class Player:
    def __init__(self, width, height):
        self.x = width / 2
        self.y = height / 2

        self.angle = 90
        self.velX = 0
        self.velY = 0

        self.turnSpeed = 4
        self.speed = 0.15
        self.radius = 12

        self.multiShot = False
        self.bigShot = False

        self.fireDelay = 20
        self.cooldown = 0

    def move(self, keys, width, height):
        if keys[pygame.K_LEFT]:
            self.angle += self.turnSpeed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.turnSpeed

        if keys[pygame.K_UP]:
            rad = math.radians(self.angle)
            self.velX += math.cos(rad) * self.speed
            self.velY -= math.sin(rad) * self.speed

        self.x += self.velX
        self.y += self.velY

        self.velX *= 0.99
        self.velY *= 0.99

        self.x, self.y = wrap(self.x, self.y, width, height)

        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self, screen):
        rad = math.radians(self.angle)

        tip = (self.x + math.cos(rad) * 18, self.y - math.sin(rad) * 18)
        left = (self.x + math.cos(rad + 2.5) * 14, self.y - math.sin(rad + 2.5) * 14)
        right = (self.x + math.cos(rad - 2.5) * 14, self.y - math.sin(rad - 2.5) * 14)

        pygame.draw.polygon(screen, WHITE, [tip, left, right], 2)

    def shoot(self):
        if self.cooldown > 0:
            return []

        self.cooldown = self.fireDelay
        bullets = []

        if self.multiShot:
            bullets.append(Bullet(self.x, self.y, self.angle + 10, self.bigShot))
            bullets.append(Bullet(self.x, self.y, self.angle - 10, self.bigShot))
        else:
            bullets.append(Bullet(self.x, self.y, self.angle, self.bigShot))

        return bullets


class Bullet:
    def __init__(self, x, y, angle, big):
        self.x = x
        self.y = y
        self.life = 60

        speed = 5 if big else 8
        self.radius = 8 if big else 3

        rad = math.radians(angle)
        self.dx = math.cos(rad) * speed
        self.dy = -math.sin(rad) * speed

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)


class Asteroid:
    def __init__(self, width, height, x=None, y=None, size=3):
        self.size = size
        self.radius = size * 15

        if x is not None and y is not None:
            self.x, self.y = x, y
        else:
            edge = random.randint(0, 3)

            if edge == 0:
                self.x = random.randint(0, width)
                self.y = 0
            elif edge == 1:
                self.x = random.randint(0, width)
                self.y = height
            elif edge == 2:
                self.x = 0
                self.y = random.randint(0, height)
            else:
                self.x = width
                self.y = random.randint(0, height)

        angle = random.randint(0, 360)
        speed = random.uniform(1, 2.5)

        rad = math.radians(angle)
        self.dx = math.cos(rad) * speed
        self.dy = math.sin(rad) * speed

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        self.x, self.y = wrap(self.x, self.y, width, height)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)
    smallFont = pygame.font.SysFont("arial", 18)
    player = Player(WIDTH, HEIGHT)
    bullets = []
    asteroids = [Asteroid(WIDTH, HEIGHT) for _ in range(5)]
    score = 0
    running = True
    upgradeMenu = False
    nextUpgrade = 100
    ASTEROID_CAP = 20
    spawnTimer = 0
    spawnDelay = 60
    box1 = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 70, 180, 140)
    box2 = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 - 70, 180, 140)
    box3 = pygame.Rect(WIDTH//2 + 140, HEIGHT//2 - 70, 180, 140)
    gameOver = False

    while running:
        clock.tick(60)

        if not gameOver and not upgradeMenu:
            spawnTimer += 1

        if spawnTimer >= spawnDelay:
            spawnTimer = 0

        if len(asteroids) < ASTEROID_CAP:
            asteroids.append(Asteroid(WIDTH, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if not upgradeMenu and event.key == pygame.K_SPACE:
                    bullets.extend(player.shoot())

            if upgradeMenu and event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()

                if box1.collidepoint(mouse):
                    player.multiShot = True
                elif box2.collidepoint(mouse):
                    player.bigShot = True
                    player.fireDelay = 35
                elif box3.collidepoint(mouse):
                    player.fireDelay = max(5, player.fireDelay - 5)

                upgradeMenu = False
                nextUpgrade += 100

        if not upgradeMenu and not gameOver:
            keys = pygame.key.get_pressed()
            player.move(keys, WIDTH, HEIGHT)

            for b in bullets[:]:
                b.move()

                if b.life <= 0:
                    bullets.remove(b)
                    continue

                if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
                    bullets.remove(b)

            for a in asteroids:
                a.move(WIDTH, HEIGHT)

            for b in bullets[:]:
                for a in asteroids[:]:
                    if get_distance(b.x, b.y, a.x, a.y) < a.radius:
                        if b in bullets:
                            bullets.remove(b)
                        if a in asteroids:
                            asteroids.remove(a)

                        score += 10

                        if a.size > 1:
                            asteroids.append(Asteroid(WIDTH, HEIGHT, a.x, a.y, a.size - 1))
                            asteroids.append(Asteroid(WIDTH, HEIGHT, a.x, a.y, a.size - 1))

                        break

            for a in asteroids:
                if get_distance(player.x, player.y, a.x, a.y) < a.radius + player.radius:
                    gameOver = True

            if score >= nextUpgrade:
                upgradeMenu = True

        screen.fill(BLACK)
        player.draw(screen)

        for b in bullets:
            b.draw(screen)

        for a in asteroids:
            a.draw(screen)

        scoreText = font.render(f"Score: {score}", True, WHITE)
        screen.blit(scoreText, (10, 10))

        if upgradeMenu:
            pygame.draw.rect(screen, GRAY, box1)
            pygame.draw.rect(screen, GRAY, box2)
            pygame.draw.rect(screen, GRAY, box3)

            pygame.draw.rect(screen, WHITE, box1, 2)
            pygame.draw.rect(screen, WHITE, box2, 2)
            pygame.draw.rect(screen, WHITE, box3, 2)

            t1 = smallFont.render("Double Shot", True, WHITE)
            t2 = smallFont.render("Big Bullets", True, WHITE)
            t3 = smallFont.render("Fire Rate Up", True, WHITE)

            screen.blit(t1, t1.get_rect(center=box1.center))
            screen.blit(t2, t2.get_rect(center=box2.center))
            screen.blit(t3, t3.get_rect(center=box3.center))

        if gameOver:
            overText = font.render("GAME OVER", True, WHITE)
            scoreText = font.render(f"Final Score: {score}", True, WHITE)
            restartText = smallFont.render("Press ESC to quit", True, WHITE)
            screen.blit(overText, overText.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            screen.blit(scoreText, scoreText.get_rect(center=(WIDTH//2, HEIGHT//2)))
            screen.blit(restartText, restartText.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()