import pygame, random, sys, os, math

pygame.init()
lebar, tinggi = 360, 640
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption("TapTapType")
clock = pygame.time.Clock()

# Font
font_kecil = pygame.font.Font("font/Poppins-Regular.ttf", 16)
font_sedang = pygame.font.Font("font/Poppins-SemiBold.ttf", 22)
font_besar = pygame.font.Font("font/Poppins-Bold.ttf", 36)

# Warna
PUTIH = (255, 255, 255)
MERAH = (255, 70, 70)
BIRU = (100, 200, 255)
KUNING = (255, 255, 100)
ABU = (30, 30, 40)
CREAM = (255, 245, 220)

# Asset
start_icon = pygame.transform.scale(pygame.image.load("icon/start_icon.png"), (80, 80))
restart_icon = pygame.transform.scale(pygame.image.load("icon/restart_icon.png"), (50, 50))
player_img_raw = pygame.transform.scale(pygame.image.load("icon/player.png"), (40, 40))
home_icon = pygame.transform.scale(pygame.image.load("icon/home_icon.png"), (58, 58))

# Sound
pygame.mixer.init()
pygame.mixer.music.load("sound/bekson.mp3")  # BACKSOUND
pygame.mixer.music.set_volume(0.4)

sound_start = pygame.mixer.Sound("sound/start.wav")
sound_success = pygame.mixer.Sound("sound/success.wav")
sound_gameover = pygame.mixer.Sound("sound/gameover.wav")
sound_type = pygame.mixer.Sound("sound/tik.mp3")
sound_shoot = pygame.mixer.Sound("sound/shoot.wav")

kata_list = [
    'python', 'java', 'kotlin', 'dart', 'swift', 'go', 'ruby', 'rust',
    'php', 'html', 'css', 'sql', 'bash', 'c', 'perl'
]

def load_highscore():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            return int(f.read())
    return 0

def simpan_highscore(skor_baru):
    if skor_baru > load_highscore():
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

class Player:
    def __init__(self):
        self.x = lebar // 2
        self.y = tinggi - 50
        self.angle = 0

    def update_angle(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        self.angle = math.degrees(math.atan2(-dy, dx)) - 90

    def draw(self):
        rotated_img = pygame.transform.rotate(player_img_raw, self.angle)
        rect = rotated_img.get_rect(center=(self.x, self.y))
        layar.blit(rotated_img, rect)

class Musuh:
    def __init__(self, skor, mode):
        self.kata = random.choice(kata_list)
        self.x = random.randint(40, lebar - 100)
        self.y = -50
        multiplier = {"easy": 0.04, "normal": 0.07, "expert": 0.1}
        bonus_factor = 0.02 if skor > 0 and skor % 10 == 0 else 0
        self.kecepatan = 0.6 + skor * (multiplier[mode] + bonus_factor)
        self.aktif = True

    def update(self):
        self.y += self.kecepatan

    def draw(self):
        warna = KUNING if self.aktif else BIRU
        teks = font_sedang.render(self.kata, True, warna)
        pygame.draw.rect(layar, ABU, (self.x - 5, self.y - 3, teks.get_width() + 10, teks.get_height() + 6), border_radius=6)
        layar.blit(teks, (self.x, self.y))

class Peluru:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        angle = math.atan2(target_y - y, target_x - x)
        self.vx = 6 * math.cos(angle)
        self.vy = 6 * math.sin(angle)
        self.aktif = True
        sound_shoot.play()

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > lebar or self.y < 0 or self.y > tinggi:
            self.aktif = False

    def draw(self):
        panjang = 10
        akhir_x = self.x + (self.vx / math.hypot(self.vx, self.vy)) * panjang
        akhir_y = self.y + (self.vy / math.hypot(self.vx, self.vy)) * panjang
        pygame.draw.line(layar, BIRU, (self.x, self.y), (akhir_x, akhir_y), 2)

class Ledakan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.maks_radius = 20
        self.selesai = False

    def update(self):
        self.radius += 2
        if self.radius >= self.maks_radius:
            self.selesai = True

    def draw(self):
        if not self.selesai:
            pygame.draw.circle(layar, KUNING, (int(self.x), int(self.y)), self.radius, 2)

def tampilkan_nyawa_hex(jumlah):
    sisi = 14
    x_tengah = lebar - 30
    y_tengah = 20
    poin = []
    for i in range(6):
        sudut = math.radians(60 * i)
        x = x_tengah + sisi * math.cos(sudut)
        y = y_tengah + sisi * math.sin(sudut)
        poin.append((x, y))
    pygame.draw.polygon(layar, CREAM, poin)
    teks = font_kecil.render(str(jumlah), True, (50, 50, 50))
    rect = teks.get_rect(center=(x_tengah, y_tengah))
    layar.blit(teks, rect)

def draw_background():
    layar.fill((10, 10, 25))
    for bintang in bintang_list:
        bintang.update()
        bintang.draw()

def tampilkan_teks_dengan_bayangan(teks, font, warna, y_offset=0, alpha=255):
    shadow = font.render(teks, True, (0, 0, 0))
    surf = font.render(teks, True, warna)
    surf.set_alpha(alpha)
    shadow.set_alpha(alpha)
    rect = surf.get_rect(center=(lebar // 2, tinggi // 2 + y_offset))
    layar.blit(shadow, (rect.x + 2, rect.y + 2))
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
    pygame.mixer.music.play(-1)  # MULAI BACKSOUND
    mode_list = ["Easy", "Normal", "Expert"]
    index = 0
    while True:
        clock.tick(60)
        draw_background()
        tampilkan_teks_dengan_bayangan("TapTapType", font_besar, KUNING, -150)
        tampilkan_teks_dengan_bayangan("Programming Edition", font_kecil, BIRU, -100)
        mode_teks = f"< {mode_list[index]} >"
        tampilkan_teks_dengan_bayangan(mode_teks, font_sedang, PUTIH, -40)

        icon_rect = start_icon.get_rect(center=(lebar // 2, tinggi // 2 + 60))
        layar.blit(start_icon, icon_rect)
        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    index = (index - 1) % len(mode_list)
                elif event.key == pygame.K_RIGHT:
                    index = (index + 1) % len(mode_list)

        if icon_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(start_icon, icon_rect.center)
            sound_start.play()
            pygame.time.wait(200)
            return mode_list[index].lower()

        pygame.display.update()

def game_over_screen(skor, highscore, accuracy, wpm):
    pygame.mixer.music.stop()  # STOP BACKSOUND
    while True:
        clock.tick(60)
        draw_background()
        tampilkan_teks_dengan_bayangan("GAME OVER", font_besar, MERAH, -160)
        tampilkan_teks_dengan_bayangan(f"Final Score: {skor}", font_sedang, PUTIH, -80)
        tampilkan_teks_dengan_bayangan(f"Best Score: {highscore}", font_kecil, KUNING, -40)
        tampilkan_teks_dengan_bayangan(f"Accuracy: {accuracy:.1f}%", font_kecil, BIRU, 10)
        tampilkan_teks_dengan_bayangan(f"WPM: {wpm:.1f}", font_kecil, BIRU, 40)

        jarak = (restart_icon.get_width() // 2) + (home_icon.get_width() // 2) + 20
        restart_rect = restart_icon.get_rect(center=(lebar // 2 - jarak // 2, tinggi // 2 + 120))
        home_rect = home_icon.get_rect(center=(lebar // 2 + jarak // 2, tinggi // 2 + 120))

        layar.blit(restart_icon, restart_rect)
        layar.blit(home_icon, home_rect)

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if restart_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(restart_icon, restart_rect.center)
            return "restart"

        if home_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(home_icon, home_rect.center)
            return "home"

        pygame.display.update()

def pause_menu():
    while True:
        clock.tick(60)
        draw_background()
        tampilkan_teks_dengan_bayangan("Game Dihentikan", font_kecil, PUTIH, -220)

        popup_rect = pygame.Rect(40, 180, lebar - 80, 280)
        pygame.draw.rect(layar, (20, 20, 30, 180), popup_rect, border_radius=16)
        pygame.draw.rect(layar, ABU, popup_rect, border_radius=16)

        teks_pause = font_besar.render("PAUSED", True, KUNING)
        teks_rect = teks_pause.get_rect(center=(lebar // 2, 220))
        layar.blit(teks_pause, teks_rect)

        resume_rect = restart_icon.get_rect(center=(lebar // 2 - 60, 320))
        home_rect = home_icon.get_rect(center=(lebar // 2 + 60, 320))

        layar.blit(restart_icon, resume_rect)
        layar.blit(home_icon, home_rect)

        teks_resume = font_kecil.render("Resume", True, PUTIH)
        teks_home = font_kecil.render("Home", True, PUTIH)
        layar.blit(teks_resume, teks_resume.get_rect(center=(resume_rect.centerx, resume_rect.bottom + 15)))
        layar.blit(teks_home, teks_home.get_rect(center=(home_rect.centerx, home_rect.bottom + 15)))

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if resume_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(restart_icon, resume_rect.center)
            return "resume"
        elif home_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(home_icon, home_rect.center)
            pygame.mixer.music.stop()  # STOP BACKSOUND JUGA
            return "home"

        pygame.display.update()

def main_game(mode):
    # ... (Tidak berubah dari sebelumnya, tetap panggil pygame.mixer.music.play dari start_screen)
    # Fungsi ini tetap sama
    # ...
    pass  # Gunakan versi main_game yang sudah kamu punya (tidak diubah di bagian ini)

# Loop utama
while True:
    mode = start_screen()
    while True:
        hasil = main_game(mode)
        if hasil == "home":
            break  # kembali ke start screen
