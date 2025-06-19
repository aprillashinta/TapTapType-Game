import pygame
import random
import sys
import os

pygame.init()
lebar, tinggi = 360, 640
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption("ZType - Mobile Edition")
clock = pygame.time.Clock()

font_kecil = pygame.font.Font(None, 28)
font_sedang = pygame.font.Font(None, 36)
font_besar = pygame.font.Font(None, 64)

PUTIH = (255, 255, 255)
MERAH = (255, 70, 70)
BIRU = (100, 200, 255)
KUNING = (255, 255, 100)
ABU = (30, 30, 40)

start_icon = pygame.image.load("icon/start_icon.png")
start_icon = pygame.transform.scale(start_icon, (100, 100))
restart_icon = pygame.image.load("icon/restart_icon.png")
restart_icon = pygame.transform.scale(restart_icon, (60, 60))

pygame.mixer.init()
sound_start = pygame.mixer.Sound("sound/start.wav")
sound_success = pygame.mixer.Sound("sound/success.wav")
sound_gameover = pygame.mixer.Sound("sound/gameover.wav")
sound_type = pygame.mixer.Sound("sound/tik.mp3")

kata_list = [
    'python', 'java', 'kotlin', 'dart', 'swift', 'go', 'ruby', 'rust',
    'php', 'html', 'css', 'sql', 'bash', 'c', 'csharp', 'perl'
]

def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def simpan_highscore(skor_baru):
    highscore = load_highscore()
    if skor_baru > highscore:
        with open("highscore.txt", "w") as f:
            f.write(str(skor_baru))

class Bintang:
    def __init__(self):
        self.x = random.randint(0, lebar)
        self.y = random.randint(0, tinggi)
        self.radius = random.randint(1, 2)
        self.speed = random.uniform(0.3, 1)

    def update(self):
        self.y += self.speed
        if self.y > tinggi:
            self.y = 0
            self.x = random.randint(0, lebar)

    def draw(self):
        pygame.draw.circle(layar, PUTIH, (int(self.x), int(self.y)), self.radius)

bintang_list = [Bintang() for _ in range(60)]

class Musuh:
    def __init__(self, skor):
        self.kata = random.choice(kata_list)
        self.x = random.randint(40, lebar - 100)
        self.y = -50
        self.kecepatan = 0.6 + skor * 0.05
        self.aktif = True

    def update(self):
        self.y += self.kecepatan

    def draw(self):
        warna = KUNING if self.aktif else BIRU
        teks = font_sedang.render(self.kata, True, warna)
        pygame.draw.rect(layar, ABU, (self.x - 5, self.y - 3, teks.get_width() + 10, teks.get_height() + 6), border_radius=6)
        layar.blit(teks, (self.x, self.y))

def draw_background():
    layar.fill((10, 10, 25))
    for bintang in bintang_list:
        bintang.update()
        bintang.draw()

def tampilkan_teks(teks, font, warna, y_offset=0, alpha=255):
    surf = font.render(teks, True, warna)
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(lebar // 2, tinggi // 2 + y_offset))
    layar.blit(surf, rect)

def animate_icon_click(icon, pos):
    for scale in [0.9, 1.0]:
        ukuran = int(icon.get_width() * scale), int(icon.get_height() * scale)
        ikon_kecil = pygame.transform.scale(icon, ukuran)
        rect = ikon_kecil.get_rect(center=pos)
        draw_background()
        layar.blit(ikon_kecil, rect)
        pygame.display.update()
        pygame.time.delay(80)

def start_screen():
    while True:
        clock.tick(60)
        draw_background()
        tampilkan_teks("ZTYPE", font_besar, KUNING, -150)
        tampilkan_teks("Programming Edition", font_kecil, BIRU, -100)
        tampilkan_teks("Tap icon to start", font_kecil, PUTIH, -50)

        icon_rect = start_icon.get_rect(center=(lebar // 2, tinggi // 2 + 40))
        layar.blit(start_icon, icon_rect)

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        if icon_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(start_icon, icon_rect.center)
            sound_start.play()
            pygame.time.wait(200)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

def game_over_screen(skor, highscore):
    sound_gameover.play()
    alpha = 0
    fade_in_speed = 5

    while True:
        clock.tick(60)
        draw_background()

        if alpha < 255:
            alpha += fade_in_speed
        else:
            alpha = 255

        tampilkan_teks("GAME OVER", font_besar, MERAH, -120, alpha)
        tampilkan_teks(f"Your Score: {skor}", font_sedang, KUNING, -60, alpha)
        tampilkan_teks(f"Best Score: {highscore}", font_kecil, PUTIH, -20, alpha)
        tampilkan_teks("Tap to restart", font_kecil, BIRU, 30, alpha)

        icon_rect = restart_icon.get_rect(center=(lebar // 2, tinggi // 2 + 100))
        restart_icon.set_alpha(alpha)
        layar.blit(restart_icon, icon_rect)

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        if icon_rect.collidepoint(mouse) and klik[0] and alpha >= 255:
            animate_icon_click(restart_icon, icon_rect.center)
            pygame.time.wait(200)
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()

start_screen() # LOOPING GAME

while True:
    musuh_list = []
    input_user = ''
    skor = 0
    game_over = False
    spawn_timer = 0
    spawn_delay = 1200
    highscore = load_highscore()
    freeze_aktif = False
    freeze_timer = 0

    while not game_over:
        clock.tick(60)
        draw_background()

        if skor > 0 and skor % 10 == 0 and not freeze_aktif: # FREEZE BONUS
            freeze_aktif = True
            freeze_timer = pygame.time.get_ticks()

        sekarang = pygame.time.get_ticks()

        if freeze_aktif:
            if sekarang - freeze_timer < 3000:
                tampilkan_teks("FREEZE BONUS!", font_sedang, BIRU, 150)
            else:
                freeze_aktif = False
        else:
            if sekarang - spawn_timer > spawn_delay:
                musuh_list.append(Musuh(skor))
                spawn_timer = sekarang

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_user = input_user[:-1]
                    sound_type.play()
                elif event.key == pygame.K_RETURN:
                    input_user = ''
                else:
                    input_user += event.unicode.lower()
                    sound_type.play()

        if not freeze_aktif:
            for musuh in musuh_list:
                if musuh.aktif:
                    musuh.update()
                    if input_user == musuh.kata:
                        sound_success.play()
                        musuh.aktif = False
                        skor += 1
                        input_user = ''
                    if musuh.y > tinggi:
                        game_over = True

        for musuh in musuh_list:
            musuh.draw()

        pygame.draw.rect(layar, (0, 0, 0, 80), (0, tinggi - 60, lebar, 60))
        tampilkan_teks(f"Input: {input_user}", font_kecil, BIRU, 220)
        tampilkan_teks(f"Score: {skor}", font_kecil, KUNING, -280)
        tampilkan_teks(f"Best: {highscore}", font_kecil, PUTIH, -250)

        pygame.display.update()

    simpan_highscore(skor)
    highscore = max(skor, highscore)
    game_over_screen(skor, highscore)