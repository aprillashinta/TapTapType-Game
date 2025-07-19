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
BIRU = (0, 180, 255)
KUNING = (255, 255, 100)
ABU = (30, 30, 40)

# Icon
start_icon = pygame.transform.scale(pygame.image.load("icon/start_icon.png"), (80, 80))
restart_icon = pygame.transform.scale(pygame.image.load("icon/restart_icon.png"), (50, 50))
resume_icon = pygame.transform.scale(pygame.image.load("icon/resume_icon.png"), (50, 50))
player_img_raw = pygame.transform.scale(pygame.image.load("icon/player.png"), (40, 40))
home_icon = pygame.transform.scale(pygame.image.load("icon/home_icon.png"), (58, 58))
pause_icon = pygame.transform.scale(pygame.image.load("icon/pause_icon.png"), (36, 36))

# Sound
pygame.mixer.init()
pygame.mixer.music.load("sound/bekson.mp3")
pygame.mixer.music.set_volume(0.4)
sound_start = pygame.mixer.Sound("sound/start.wav")
sound_success = pygame.mixer.Sound("sound/success.wav")
sound_gameover = pygame.mixer.Sound("sound/gameover.wav")
sound_type = pygame.mixer.Sound("sound/tik.mp3")
sound_shoot = pygame.mixer.Sound("sound/shoot.wav")

kata_list = [
    'python', 'java', 'kotlin', 'dart', 'swift', 'go', 'ruby', 'rust', 'django',
    'php', 'html', 'css', 'sql', 'bash', 'c', 'perl', 'node', 'react', 'angular',
    'laravel', 'nextjs', 'nextjs', 'mongodb', 'nosql', 'vue', 'loop', 'git'
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
        self.vx = 10 * math.cos(angle)
        self.vy = 10 * math.sin(angle)
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

    warna_biru = (0, 180, 255)
    pygame.draw.polygon(layar, warna_biru, poin)

    teks = font_kecil.render(str(jumlah), True, (255, 255, 255))
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

        resume_rect = resume_icon.get_rect(center=(lebar // 2 - 80, 320))
        restart_rect = restart_icon.get_rect(center=(lebar // 2, 320))
        home_rect = home_icon.get_rect(center=(lebar // 2 + 80, 320))

        layar.blit(resume_icon, resume_rect)
        layar.blit(restart_icon, restart_rect)
        layar.blit(home_icon, home_rect)

        teks_resume = font_kecil.render("Resume", True, PUTIH)
        teks_restart = font_kecil.render("Restart", True, PUTIH)
        teks_home = font_kecil.render("Home", True, PUTIH)

        layar.blit(teks_resume, teks_resume.get_rect(center=(resume_rect.centerx, resume_rect.bottom + 15)))
        layar.blit(teks_restart, teks_restart.get_rect(center=(restart_rect.centerx, restart_rect.bottom + 15)))
        layar.blit(teks_home, teks_home.get_rect(center=(home_rect.centerx, home_rect.bottom + 15)))

        mouse = pygame.mouse.get_pos()
        klik = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if resume_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(resume_icon, resume_rect.center)
            return "resume"
        elif restart_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(restart_icon, restart_rect.center)
            return "restart"
        elif home_rect.collidepoint(mouse) and klik[0]:
            animate_icon_click(home_icon, home_rect.center)
            pygame.mixer.music.stop()
            return "home"

        pygame.display.update()
        
# def pause_menu():
#     while True:
#         clock.tick(60)
#         draw_background()
#         tampilkan_teks_dengan_bayangan("Game Dihentikan", font_kecil, PUTIH, -220)

#         popup_rect = pygame.Rect(40, 180, lebar - 80, 280)
#         pygame.draw.rect(layar, (20, 20, 30, 180), popup_rect, border_radius=16)
#         pygame.draw.rect(layar, ABU, popup_rect, border_radius=16)

#         teks_pause = font_besar.render("PAUSED", True, KUNING)
#         layar.blit(teks_pause, teks_pause.get_rect(center=(lebar // 2, 220)))

#         mouse = pygame.mouse.get_pos()
#         klik = pygame.mouse.get_pressed()
#         for tombol in tombol_list:
#             icon, label, value, offset = tombol.values()
#             rect = icon.get_rect(center=(lebar // 2 + offset, 320))
#             layar.blit(icon, rect)

#             teks = font_kecil.render(label, True, PUTIH)
#             layar.blit(teks, teks.get_rect(center=(rect.centerx, rect.bottom + 15)))

#             if rect.collidepoint(mouse) and klik[0]:
#                 animate_icon_click(icon, rect.center)
#                 if value == "home":
#                     pygame.mixer.music.stop()
#                 return value

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#         pygame.display.update()


def start_screen():
    pygame.mixer.music.play(-1)
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

def main_game(mode):
    musuh_list, peluru_list, ledakan_list = [], [], []
    skor, nyawa, game_over = 0, 3, False
    spawn_timer, spawn_delay = 0, 1200
    highscore = load_highscore()
    freeze_aktif, freeze_timer = False, 0
    player = Player()
    jumlah_tekanan = 0
    jumlah_huruf_benar = 0
    waktu_mulai = pygame.time.get_ticks()

    while not game_over:
        clock.tick(60)
        draw_background()

        sekarang = pygame.time.get_ticks()
        if skor > 0 and skor % 10 == 0 and not freeze_aktif:
            freeze_aktif = True
            freeze_timer = sekarang

        if freeze_aktif:
            waktu_berjalan = sekarang - freeze_timer
            tampilkan_teks_dengan_bayangan("FREEZE BONUS!", font_sedang, BIRU, 130)
            tampilkan_teks_dengan_bayangan(f"{max(0, 3 - waktu_berjalan // 1000)}", font_besar, KUNING, 180)
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_icon.get_rect(topleft=(lebar - 52, 42)).collidepoint(event.pos):
                    hasil = pause_menu()
                    if hasil == "home":
                        return "home"
                    elif hasil == "restart":
                        return "restart"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    hasil = pause_menu()
                    if hasil == "home":
                        return "home"
                    elif hasil == "restart":
                        return "restart"
                else:
                    huruf = event.unicode.lower()
                    jumlah_tekanan += 1
                    for musuh in musuh_list:
                        if musuh.aktif and musuh.kata.startswith(huruf):
                            jumlah_huruf_benar += 1
                            player.update_angle(musuh.x, musuh.y)
                            peluru_list.append(Peluru(player.x, player.y - 20, musuh.x, musuh.y))
                            panjang = len(musuh.kata)
                            musuh.kata = musuh.kata[1:]
                            sound_type.play()
                            if musuh.kata == "":
                                sound_success.play()
                                ledakan_list.append(Ledakan(musuh.x + 20, musuh.y + 15))
                                musuh.aktif = False
                                skor += 5 + panjang if freeze_aktif else panjang
                            break

        for musuh in musuh_list:
            if musuh.aktif:
                musuh.draw()

        for peluru in peluru_list[:]:
            peluru.update()
            peluru.draw()
            if not peluru.aktif:
                peluru_list.remove(peluru)

        for ledakan in ledakan_list[:]:
            ledakan.update()
            ledakan.draw()
            if ledakan.selesai:
                ledakan_list.remove(ledakan)

        player.draw()

        pause_rect = pause_icon.get_rect(topleft=(lebar - 52, 42))
        layar.blit(pause_icon, pause_rect)

        tampilkan_teks_dengan_bayangan(f"Score: {skor}", font_kecil, KUNING, -280)
        tampilkan_teks_dengan_bayangan(f"Best: {highscore}", font_kecil, PUTIH, -250)
        tampilkan_nyawa_hex(nyawa)
        pygame.display.update()

    durasi = (pygame.time.get_ticks() - waktu_mulai) / 1000
    wpm = (jumlah_huruf_benar / 5) / (durasi / 60) if durasi > 0 else 0
    accuracy = (jumlah_huruf_benar / jumlah_tekanan) * 100 if jumlah_tekanan > 0 else 0
    simpan_highscore(skor)
    sound_gameover.play()
    return game_over_screen(skor, max(skor, highscore), accuracy, wpm)

def game_over_screen(skor, highscore, akurasi, wpm):
    while True:
        clock.tick(60)
        draw_background()
        tampilkan_teks_dengan_bayangan("GAME OVER", font_besar, MERAH, -150)
        tampilkan_teks_dengan_bayangan(f"Final Score: {skor}", font_sedang, KUNING, -80)
        tampilkan_teks_dengan_bayangan(f"Best Score: {highscore}", font_sedang, PUTIH, -40)
        tampilkan_teks_dengan_bayangan(f"Akurasi: {akurasi:.1f}%", font_kecil, PUTIH, 20)
        tampilkan_teks_dengan_bayangan(f"WPM: {round(wpm)}", font_kecil, PUTIH, 50)

        restart_rect = restart_icon.get_rect(center=(lebar // 2 - 40, tinggi // 2 + 120))
        home_rect = home_icon.get_rect(center=(lebar // 2 + 40, tinggi // 2 + 120))

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

while True:
    mode = start_screen()
    while True:
        hasil = main_game(mode)
        if hasil == "home":
            break
        elif hasil == "restart":
            continue