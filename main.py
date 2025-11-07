import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("Dino Game with Laser Attack")

game_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 24)


# Classes
class Cloud(pygame.sprite.Sprite):
    def __init__(self, image, x_pos, y_pos):
        super().__init__()
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        self.rect.x -= 1


class Laser(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, direction):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.direction = direction
        # Создаем лазер с градиентом программно
        self.image = pygame.Surface((60, 6), pygame.SRCALPHA)
        # Рисуем градиент от красного к желтому
        for i in range(60):
            color_value = max(100, 255 - (i * 2))
            alpha = 255 - (i * 3)
            color = (255, color_value, 0, alpha)
            pygame.draw.rect(self.image, color, (i, 0, 1, 6))
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.speed = 15

    def update(self):
        self.x_pos += self.speed * self.direction
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

        # Удаляем лазер, если он ушел за экран
        if self.x_pos > 1300 or self.x_pos < -100:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.size = 5
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 165, 0), (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.lifetime = 10

    def update(self):
        self.lifetime -= 1
        # Увеличиваем размер взрыва
        self.size += 1
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        alpha = max(0, 255 * self.lifetime // 10)
        pygame.draw.circle(self.image, (255, 165, 0, alpha), (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

        if self.lifetime <= 0:
            self.kill()


class Dino(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.running_sprites = []
        self.ducking_sprites = []

        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("Assets/Dino/DinoRun1.png"), (80, 100)))
        self.running_sprites.append(pygame.transform.scale(
            pygame.image.load("Assets/Dino/DinoRun2.png"), (80, 100)))

        self.ducking_sprites.append(pygame.transform.scale(
            pygame.image.load(f"Assets/Dino/DinoDuck1.png"), (110, 60)))
        self.ducking_sprites.append(pygame.transform.scale(
            pygame.image.load(f"Assets/Dino/DinoDuck2.png"), (110, 60)))

        self.jump_sprite = pygame.transform.scale(
            pygame.image.load("Assets/Dino/DinoJump.png"), (80, 100))

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.current_image = 0
        self.image = self.running_sprites[self.current_image]
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 20,
                                  self.rect.width - 40, self.rect.height - 30)
        self.jump_velocity = 0
        self.gravity = 0.8
        self.is_jumping = False
        self.ducking = False
        self.ground_y = 360

        # Система атаки - УВЕЛИЧИВАЕМ КД ЕЩЕ В 2 РАЗА
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_duration = 10
        self.attack_cooldown_max = 450  # 225 * 2 = 450 кадров (7.5 секунд)
        # Создаем спрайты атаки из существующих
        self.attacking_sprites = [
            pygame.transform.scale(pygame.image.load("Assets/Dino/DinoRun1.png"), (90, 110)),
            pygame.transform.scale(pygame.image.load("Assets/Dino/DinoRun2.png"), (100, 120))
        ]

    def jump(self):
        if not self.is_jumping and self.rect.centery >= self.ground_y:
            self.jump_velocity = -18
            self.is_jumping = True

    def duck(self):
        if not self.is_jumping:
            self.ducking = True
            self.rect.centery = 380
            self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 10,
                                      self.rect.width - 40, self.rect.height - 20)

    def unduck(self):
        self.ducking = False
        self.rect.centery = self.ground_y
        self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 20,
                                  self.rect.width - 40, self.rect.height - 30)

    def attack(self):
        if self.attack_cooldown <= 0 and not game_over:
            self.is_attacking = True
            self.attack_cooldown = self.attack_cooldown_max
            # Создаем лазер
            laser_x = self.rect.right + 10
            laser_y = self.rect.centery - 10
            new_laser = Laser(laser_x, laser_y, 1)
            laser_group.add(new_laser)
            return True
        return False

    def apply_gravity(self):
        if self.is_jumping:
            self.jump_velocity += self.gravity
            self.rect.centery += self.jump_velocity

            if self.ducking:
                self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 10,
                                          self.rect.width - 40, self.rect.height - 20)
            else:
                self.hitbox = pygame.Rect(self.rect.x + 20, self.rect.y + 20,
                                          self.rect.width - 40, self.rect.height - 30)

            if self.rect.centery >= self.ground_y:
                self.rect.centery = self.ground_y
                self.is_jumping = False
                self.jump_velocity = 0

    def update(self):
        self.animate()
        self.apply_gravity()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.is_attacking and self.attack_duration <= 0:
            self.is_attacking = False
            self.attack_duration = 10

    def animate(self):
        if self.is_attacking:
            self.attack_duration -= 1
            if self.attack_duration > 5:
                self.image = self.attacking_sprites[1]
            else:
                self.image = self.attacking_sprites[0]
        elif self.is_jumping:
            self.image = self.jump_sprite
        elif self.ducking:
            self.current_image += 0.05
            if self.current_image >= 2:
                self.current_image = 0
            self.image = self.ducking_sprites[int(self.current_image)]
        else:
            self.current_image += 0.05
            if self.current_image >= 2:
                self.current_image = 0
            self.image = self.running_sprites[int(self.current_image)]


class Cactus(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.sprites = []
        for i in range(1, 4):
            current_sprite = pygame.transform.scale(
                pygame.image.load(f"Assets/Cactus/SmallCactus{i}.png"), (100, 100))
            self.sprites.append(current_sprite)
        for i in range(1, 4):
            current_sprite = pygame.transform.scale(
                pygame.image.load(f"Assets/Cactus/LargeCactus{i}.png"), (100, 100))
            self.sprites.append(current_sprite)
        self.image = random.choice(self.sprites)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = pygame.Rect(self.rect.x + 10, self.rect.y + 10,
                                  self.rect.width - 20, self.rect.height - 20)

    def update(self):
        self.x_pos -= game_speed
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = pygame.Rect(self.rect.x + 10, self.rect.y + 10,
                                  self.rect.width - 20, self.rect.height - 20)


class Ptero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x_pos = 1300
        self.y_pos = random.choice([280, 295, 350])
        self.sprites = []
        self.sprites.append(
            pygame.transform.scale(
                pygame.image.load("Assets/Bird/Bird1.png"), (84, 62)))
        self.sprites.append(
            pygame.transform.scale(
                pygame.image.load("Assets/Bird/Bird2.png"), (84, 62)))
        self.current_image = 0
        self.image = self.sprites[self.current_image]
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = pygame.Rect(self.rect.x + 15, self.rect.y + 15,
                                  self.rect.width - 30, self.rect.height - 30)

    def update(self):
        self.animate()
        self.x_pos -= game_speed
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = pygame.Rect(self.rect.x + 15, self.rect.y + 15,
                                  self.rect.width - 30, self.rect.height - 30)

    def animate(self):
        self.current_image += 0.025
        if self.current_image >= 2:
            self.current_image = 0
        self.image = self.sprites[int(self.current_image)]


# Variables
game_speed = 8
player_score = 0
game_over = False
game_started = False  # Добавляем флаг начала игры
obstacle_timer = 0
obstacle_spawn = False
obstacle_cooldown = 1200

# Surfaces
ground = pygame.image.load("Assets/Other/Track.png")
ground = pygame.transform.scale(ground, (1280, 20))
ground_x = 0
ground_rect = ground.get_rect(center=(640, 400))
cloud = pygame.image.load("Assets/Other/Cloud.png")
cloud = pygame.transform.scale(cloud, (200, 80))

# Groups
cloud_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
dino_group = pygame.sprite.GroupSingle()
ptero_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

# Objects
dinosaur = Dino(50, 360)
dino_group.add(dinosaur)

# Events
CLOUD_EVENT = pygame.USEREVENT
pygame.time.set_timer(CLOUD_EVENT, 3000)


# Functions
def check_collision():
    dino = dino_group.sprite
    for obstacle in obstacle_group:
        if dino.hitbox.colliderect(obstacle.hitbox):
            return True
    return False


def check_laser_collisions():
    lasers_to_remove = []
    obstacles_to_remove = []

    for laser in laser_group:
        for obstacle in obstacle_group:
            if laser.rect.colliderect(obstacle.hitbox):
                lasers_to_remove.append(laser)
                obstacles_to_remove.append(obstacle)
                create_explosion(obstacle.rect.centerx, obstacle.rect.centery)
                break

    # Удаляем столкнувшиеся объекты
    for laser in lasers_to_remove:
        laser.kill()
    for obstacle in obstacles_to_remove:
        obstacle.kill()

    return len(obstacles_to_remove) > 0


def create_explosion(x, y):
    explosion = Explosion(x, y)
    explosion_group.add(explosion)


def create_menu_laser():
    """Создает лазер для главного меню такой же как в игре"""
    # Позиция изо рта динозавра (примерно)
    laser_x = 700  # Начало изо рта динозавра
    laser_y = 350  # Высота рта динозавра
    # Создаем поверхность для лазера как в игре
    laser_surface = pygame.Surface((200, 6), pygame.SRCALPHA)
    # Рисуем градиент от красного к желтому как в игре
    for i in range(200):
        color_value = max(100, 255 - (i * 1))
        alpha = 255 - (i * 1)
        color = (255, color_value, 0, alpha)
        pygame.draw.rect(laser_surface, color, (i, 0, 1, 6))
    return laser_surface, (laser_x, laser_y)


def draw_main_menu():
    screen.fill("white")

    # Заголовок LaserDino
    title_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 48)
    title_text = title_font.render("LaserDino", True, (83, 83, 83))
    title_rect = title_text.get_rect(center=(640, 200))
    screen.blit(title_text, title_rect)

    # Динозавр
    dino_img = pygame.transform.scale(pygame.image.load("Assets/Dino/DinoRun1.png"), (120, 150))
    dino_rect = dino_img.get_rect(center=(580, 350))
    screen.blit(dino_img, dino_rect)

    # Лазер изо рта динозавра (такой же как в игре)
    laser_surface, laser_pos = create_menu_laser()
    screen.blit(laser_surface, laser_pos)

    # Сообщение "press any key to start"
    start_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 24)
    start_text = start_font.render("PRESS ANY KEY TO START", True, (83, 83, 83))
    start_rect = start_text.get_rect(center=(640, 500))
    screen.blit(start_text, start_rect)

    # Подсказка управления
    controls_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 18)
    controls_text = controls_font.render("Z: SHOOT LASER   SPACE: JUMP   DOWN: DUCK", True, (150, 150, 150))
    controls_rect = controls_text.get_rect(center=(640, 580))
    screen.blit(controls_text, controls_rect)


def draw_game_over():
    screen.fill("white")

    # Текст Game Over
    game_over_text = game_font.render("GAME OVER", True, "black")
    game_over_rect = game_over_text.get_rect(center=(640, 250))
    screen.blit(game_over_text, game_over_rect)

    # Финальный счет
    score_text = game_font.render(f"SCORE: {int(player_score)}", True, "black")
    score_rect = score_text.get_rect(center=(640, 320))
    screen.blit(score_text, score_rect)

    # Сообщение "press any key to restart"
    restart_text = game_font.render("PRESS ANY KEY TO RESTART", True, (83, 83, 83))
    restart_rect = restart_text.get_rect(center=(640, 400))
    screen.blit(restart_text, restart_rect)


def reset_game():
    global game_speed, player_score, game_over, obstacle_timer, obstacle_spawn, ground_x
    game_speed = 8
    player_score = 0
    game_over = False
    obstacle_timer = 0
    obstacle_spawn = False
    ground_x = 0

    # Очищаем все группы
    cloud_group.empty()
    obstacle_group.empty()
    laser_group.empty()
    explosion_group.empty()

    # Сбрасываем динозавра
    dinosaur.rect.center = (50, 360)
    dinosaur.is_jumping = False
    dinosaur.ducking = False
    dinosaur.attack_cooldown = 0
    dinosaur.is_attacking = False


def draw_hud():
    # Очки
    score_text = game_font.render(f"{int(player_score)}", True, "black")
    score_rect = score_text.get_rect(topright=(1260, 10))
    screen.blit(score_text, score_rect)

    # Индикатор перезарядки лазера - ТОЛЬКО ПОЛОСКА
    cooldown_width = 150
    if dinosaur.attack_cooldown > 0:
        cooldown_percent = dinosaur.attack_cooldown / dinosaur.attack_cooldown_max
        # Фон индикатора
        pygame.draw.rect(screen, (100, 100, 100), (50, 50, cooldown_width, 20))
        # Заливка индикатора
        pygame.draw.rect(screen, (0, 255, 0), (50, 50, cooldown_width * (1 - cooldown_percent), 20))
        # Рамка
        pygame.draw.rect(screen, (0, 0, 0), (50, 50, cooldown_width, 20), 2)
    else:
        # Надпись когда лазер готов
        ready_text = game_font.render("Laser READY!", True, (83, 83, 83))
        screen.blit(ready_text, (50, 20))

    # Подсказка управления
    if player_score < 50:  # Показываем только в начале игры
        controls_text = game_font.render("Z: Shoot Laser", True, "gray")
        screen.blit(controls_text, (50, 80))


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == CLOUD_EVENT and game_started and not game_over:
            current_cloud_y = random.randint(50, 300)
            current_cloud = Cloud(cloud, 1380, current_cloud_y)
            cloud_group.add(current_cloud)

        if event.type == pygame.KEYDOWN:
            # Обработка начала игры из меню
            if not game_started:
                game_started = True
                reset_game()

            # Обработка рестарта после Game Over
            elif game_over:
                reset_game()

            # Игровые действия
            elif game_started and not game_over:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    dinosaur.jump()
                # Стрельба лазером на Z
                if event.key == pygame.K_z:
                    dinosaur.attack()

    # Управление приседанием (удержание клавиши)
    if game_started and not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and not dinosaur.is_jumping:
            dinosaur.duck()
        else:
            if dinosaur.ducking:
                dinosaur.unduck()

    screen.fill("white")

    # Отображение соответствующего экрана
    if not game_started:
        # Главное меню
        draw_main_menu()

    elif game_over:
        # Экран Game Over
        draw_game_over()

    else:
        # Основная игра
        # Collisions
        if check_collision():
            game_over = True

        # Проверяем столкновения лазеров
        check_laser_collisions()

        game_speed += 0.0025

        if pygame.time.get_ticks() - obstacle_timer >= obstacle_cooldown:
            obstacle_spawn = True

        if obstacle_spawn:
            obstacle_random = random.randint(1, 50)
            if obstacle_random in range(1, 25):
                new_obstacle = Cactus(1280, 340)
                obstacle_group.add(new_obstacle)
                obstacle_timer = pygame.time.get_ticks()
                obstacle_spawn = False
            elif obstacle_random in range(25, 35):
                new_obstacle = Ptero()
                obstacle_group.add(new_obstacle)
                obstacle_timer = pygame.time.get_ticks()
                obstacle_spawn = False

        player_score += 0.1

        # Обновление групп
        cloud_group.update()
        obstacle_group.update()
        dino_group.update()
        laser_group.update()
        explosion_group.update()

        # Отрисовка
        cloud_group.draw(screen)
        obstacle_group.draw(screen)
        dino_group.draw(screen)
        laser_group.draw(screen)
        explosion_group.draw(screen)

        # Земля
        ground_x -= game_speed
        screen.blit(ground, (ground_x, 360))
        screen.blit(ground, (ground_x + 1280, 360))
        if ground_x <= -1280:
            ground_x = 0

        # HUD
        draw_hud()

    clock.tick(60)
    pygame.display.update()