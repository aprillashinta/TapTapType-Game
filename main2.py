import pygame, random, sys, os, math

pygame.init()
lebar, tinggi = 360, 640
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption("TapTapType")
clock = pygame.time.Clock()

font_kecil = pygame.font.Font("font/Poppins-Regular.ttf", 16)
font_sedang = pygame.font.Font("font/Poppins-SemiBold.ttf", 22)
font_besar = pygame.font.Font("font/Poppins-Bold.ttf", 36)

PUTIH = (255, 255, 255)
MERAH = (255, 70, 70)
BIRU = (100, 200, 255)
KUNING = (255, 255, 100)
ABU = (30, 30, 40)
CREAM = (255, 245, 220)

start_icon = pygame.image.load("icon/start_icon.png")
start_icon = pygame.transform.scale(start_icon, (80, 80))
restart_icon = pygame.image.load("icon/restart_icon.png")
restart_icon = pygame.transform.scale(restart_icon, (50, 50))

pygame.mixer.init()
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.aktif = True
        sound_shoot.play()

    def update(self):
        self.y -= 6
        if self.y < 0:
            self.aktif = False

    def draw(self):
        pygame.draw.line(layar, BIRU, (self.x, self.y), (self.x, self.y - 10), 2)

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

mode = start_screen()

while True:
    musuh_list = []
    peluru_list = []
    ledakan_list = []
    skor = 0
    game_over = False
    spawn_timer = 0
    spawn_delay = 1200
    highscore = load_highscore()
    freeze_aktif = False
    freeze_timer = 0
    nyawa = 3

    while not game_over:
        clock.tick(60)
        draw_background()

        sekarang = pygame.time.get_ticks()

        if skor > 0 and skor % 10 == 0 and not freeze_aktif:
            freeze_aktif = True
            freeze_timer = sekarang

        if freeze_aktif:
            waktu_berjalan = sekarang - freeze_timer
            sisa_waktu = max(0, 3 - waktu_berjalan // 1000)
            tampilkan_teks_dengan_bayangan("FREEZE BONUS!", font_sedang, BIRU, 130)
            tampilkan_teks_dengan_bayangan(f"{sisa_waktu}", font_besar, KUNING, 180)

            if waktu_berjalan >= 3000:
                freeze_aktif = False

        else:
            if sekarang - spawn_timer > spawn_delay:
                musuh_list.append(Musuh(skor, mode))
                spawn_timer = sekarang

            for musuh in musuh_list:
                if musuh.aktif:
                    musuh.update()
                    if musuh.y > tinggi:
                        nyawa -= 1
                        musuh.aktif = False
                        if nyawa == 0:
                            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if musuh_list:
                    huruf = event.unicode.lower()
                    for musuh in musuh_list:
                        if musuh.aktif and musuh.kata.startswith(huruf):
                            peluru_list.append(Peluru(musuh.x + 20, musuh.y + 15))
                            panjang_kata = len(musuh.kata)
                            musuh.kata = musuh.kata[1:]
                            sound_type.play()
                            if musuh.kata == "":
                                sound_success.play()
                                ledakan_list.append(Ledakan(musuh.x + 20, musuh.y + 15))
                                musuh.aktif = False
                                if freeze_aktif:
                                    skor += 5 + panjang_kata
                                else:
                                    skor += panjang_kata
                            break

        for peluru in peluru_list[:]:
            peluru.update()
            if not peluru.aktif:
                peluru_list.remove(peluru)

        for musuh in musuh_list:
            if musuh.aktif:
                musuh.draw()

        for peluru in peluru_list:
            peluru.draw()

        for ledakan in ledakan_list[:]:
            ledakan.update()
            ledakan.draw()
            if ledakan.selesai:
                ledakan_list.remove(ledakan)

        tampilkan_teks_dengan_bayangan(f"Score: {skor}", font_kecil, KUNING, -280)
        tampilkan_teks_dengan_bayangan(f"Best: {highscore}", font_kecil, PUTIH, -250)
        tampilkan_nyawa_hex(nyawa)

        pygame.display.update()

    simpan_highscore(skor)
    highscore = max(skor, highscore)

    sound_gameover.play()
    alpha = 0
    fade_in_speed = 5
    accuracy = 100
    wpm = skor * 2

    overlay = pygame.Surface((lebar, tinggi), pygame.SRCALPHA)

    while True:
        clock.tick(60)
        draw_background()

        overlay.fill((0, 0, 0, 180))
        layar.blit(overlay, (0, 0))

        if alpha < 255:
            alpha += fade_in_speed
        else:
            alpha = 255

        teks = font_besar.render("GAME OVER", True, MERAH)
        bayangan = font_besar.render("GAME OVER", True, (0, 0, 0))
        layar.blit(bayangan, (lebar//2 - teks.get_width()//2 + 2, tinggi//2 - 120 + 2))
        layar.blit(teks, (lebar//2 - teks.get_width()//2, tinggi//2 - 120))

        tampilkan_teks_dengan_bayangan(f"Final Score: {skor}", font_sedang, KUNING, -50, alpha)
        tampilkan_teks_dengan_bayangan(f"Best Score: {highscore}", font_kecil, PUTIH, -15, alpha)
        tampilkan_teks_dengan_bayangan(f"Accuracy: {accuracy}%", font_kecil, BIRU, 20, alpha)
        tampilkan_teks_dengan_bayangan(f"WPM: {wpm}", font_kecil, BIRU, 50, alpha)
        tampilkan_teks_dengan_bayangan("Tap to restart", font_kecil, PUTIH, 100, alpha)

        icon_rect = restart_icon.get_rect(center=(lebar // 2, tinggi // 2 + 160))
        restart_icon.set_alpha(alpha)
        layar.blit(restart_icon, icon_rect)

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        if icon_rect.collidepoint(mouse) and klik[0] and alpha >= 255:
            animate_icon_click(restart_icon, icon_rect.center)
            pygame.time.wait(200)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
