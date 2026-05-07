"""
================================================================
BİL VE FETHET - Arayüz Yönetim Modülü (Pygame GUI)
================================================================
Tüm ekran çizim işlemlerini, animasyonları, popup pencerelerini
ve kullanıcı etkileşimini yöneten sınıf.
================================================================
"""

import pygame
import math
import time

# ================================================================
# RENK PALETİ
# ================================================================
class Renk:
    """Oyun genelinde kullanılan renk sabitleri."""
    # Ana Arka Plan
    ARKAPLAN        = (15, 17, 23)
    ARKAPLAN_2      = (22, 25, 35)
    PANEL_BG        = (28, 32, 45)
    PANEL_KENAR     = (45, 52, 72)

    # Metin
    METIN_ANA       = (230, 235, 245)
    METIN_IKINCIL   = (140, 150, 170)
    METIN_VURGU     = (255, 215, 0)

    # Oyuncu renkleri
    SARI            = (255, 215, 0)
    KIRMIZI         = (220, 60, 60)
    MAVI            = (60, 130, 220)

    # Harita
    HARITA_BOS      = (45, 52, 65)
    HARITA_BOS_KENAR = (65, 75, 95)
    DENIZ           = (20, 35, 60)
    HARITA_IZGARA   = (30, 40, 55)

    # Buton durumları
    BUTON_ANA       = (50, 60, 85)
    BUTON_HOVER     = (70, 85, 120)
    BUTON_AKTIF     = (255, 215, 0)
    BUTON_TEHLIKE   = (180, 50, 50)
    BUTON_BASARI    = (50, 160, 90)

    # Popup
    POPUP_BG        = (20, 23, 32)
    POPUP_KENAR     = (255, 215, 0)
    SECILI_YANLIS   = (180, 50, 50)
    SECILI_DOGRU    = (50, 160, 90)

    # HUD
    HUD_BG          = (18, 21, 30)
    HUD_KENAR       = (40, 50, 70)

    # Şeffaflık overlay
    OVERLAY         = (0, 0, 0, 180)


# ================================================================
# YARDIMCI FONKSİYONLAR
# ================================================================

def yumusak_renk(renk, hedef, adim=0.1):
    """İki renk arasında lineer interpolasyon (animasyon için)."""
    return tuple(int(renk[i] + (hedef[i] - renk[i]) * adim) for i in range(3))

def daire_cerceve_ciz(yuzey, renk, merkez, yaricap, kalinlik=2):
    """Yarı saydam daire çerçeve çizer."""
    pygame.draw.circle(yuzey, renk, merkez, yaricap, kalinlik)

def parlak_panel_ciz(yuzey, rect, renk=Renk.PANEL_BG, kenar_renk=Renk.PANEL_KENAR, radius=12):
    """Köşeleri yuvarlak, kenarlıklı modern panel çizer."""
    pygame.draw.rect(yuzey, renk, rect, border_radius=radius)
    pygame.draw.rect(yuzey, kenar_renk, rect, 2, border_radius=radius)

def metin_ciz(yuzey, metin, font, renk, x, y, hizalama="sol"):
    """Hizalamayı destekleyen metin çizici."""
    yuzey_obj = font.render(str(metin), True, renk)
    rect = yuzey_obj.get_rect()
    if hizalama == "merkez":
        rect.centerx, rect.centery = x, y
    elif hizalama == "sag":
        rect.right, rect.centery = x, y
    else:
        rect.left, rect.centery = x, y
    yuzey.blit(yuzey_obj, rect)
    return rect


# ================================================================
# ANA ARAYÜZ SINIFI
# ================================================================

class UIManager:
    """
    Tüm ekran çizim operasyonlarını yöneten sınıf.
    OyunDurumu'ndan bağımsız olarak sadece görselleştirme yapar.
    """

    def __init__(self, ekran_genislik=1280, ekran_yukseklik=760):
        """Pygame ekranını ve tüm fontları başlatır."""
        pygame.init()
        pygame.display.set_caption("⚔️  BİL VE FETHET  ⚔️")

        # Ekran
        self.ekran = pygame.display.set_mode(
            (ekran_genislik, ekran_yukseklik),
            pygame.RESIZABLE
        )
        self.genislik = ekran_genislik
        self.yukseklik = ekran_yukseklik

        # Font yükleme (sistem fontları kullanılır)
        self._fontlari_yukle()

        # Harita alanı boyutları
        self.HUD_GENISLIK = 260
        self.HARITA_X = self.HUD_GENISLIK
        self.HARITA_GENISLIK = ekran_genislik - self.HUD_GENISLIK
        self.HARITA_YUKSEKLIK = ekran_yukseklik - 60  # Alt bar için yer
        self.ALT_BAR_Y = ekran_yukseklik - 60

        # Animasyon değişkenleri
        self.zaman = 0
        self.hover_bolge = None       # Mouse üzerindeki bölge
        self.secili_bolge_anim = 0    # Seçim animasyonu sayacı
        self.mesaj_zamani = 0         # Durum mesajı gösterim süresi
        self.popup_acik = False

        # Harita ölçekleme faktörü (bölge koordinatları 1200x700 için tanımlandı)
        self.harita_olcek_x = self.HARITA_GENISLIK / 1000
        self.harita_olcek_y = self.HARITA_YUKSEKLIK / 620
        self.harita_offset_x = self.HARITA_X + 10
        self.harita_offset_y = 40

        # Yıldız arka plan için
        import random
        self.yildizlar = [
            (random.randint(0, ekran_genislik), random.randint(0, ekran_yukseklik),
             random.uniform(0.3, 1.2))
            for _ in range(120)
        ]

        print("[UI] Arayüz başlatıldı.")

    def _fontlari_yukle(self):
        """Sistem fontlarını yükler, bulamazsa varsayılanı kullanır."""
        denemeler = [
            ["Segoe UI", "Ubuntu", "DejaVu Sans", None],   # Normal
            ["Segoe UI Bold", "Ubuntu Bold", "DejaVu Sans", None],  # Kalın
        ]

        def font_yukle(isimler, boyut):
            for isim in isimler:
                try:
                    if isim:
                        f = pygame.font.SysFont(isim, boyut)
                        return f
                except:
                    pass
            return pygame.font.Font(None, boyut)

        # Çeşitli boyutlarda fontlar
        self.font_dev     = font_yukle(denemeler[1], 64)   # Başlık
        self.font_buyuk   = font_yukle(denemeler[1], 40)   # HUD başlık
        self.font_orta    = font_yukle(denemeler[0], 28)   # Normal metin
        self.font_kucuk   = font_yukle(denemeler[0], 20)   # Küçük etiket
        self.font_mini    = font_yukle(denemeler[0], 16)   # En küçük
        self.font_soru    = font_yukle(denemeler[0], 22)   # Soru metni

    def zamanı_guncelle(self):
        """Her frame'de animasyon zamanlayıcısını ilerletir."""
        self.zaman += 0.02

    # ================================================================
    # ANA EKRANLAR
    # ================================================================

    def ana_menu_ciz(self, hover_buton=None):
        """Ana menü ekranını çizer."""
        self.ekran.fill(Renk.ARKAPLAN)
        self._yildiz_arkaplan_ciz()

        cx = self.genislik // 2
        cy = self.yukseklik // 2

        # --- Parlayan başlık çizgisi ---
        self._dekoratif_cizgi_ciz(cx, cy - 200)

        # --- Ana başlık ---
        title_y = cy - 160
        # Gölge efekti
        for offset in [(3, 3), (2, 2), (1, 1)]:
            golge = self.font_dev.render("BİL VE FETHET", True, (20, 20, 20))
            r = golge.get_rect(center=(cx + offset[0], title_y + offset[1]))
            self.ekran.blit(golge, r)
        # Ana metin
        baslik = self.font_dev.render("BİL VE FETHET", True, Renk.SARI)
        r = baslik.get_rect(center=(cx, title_y))
        self.ekran.blit(baslik, r)

        # Alt başlık
        alt = self.font_orta.render("Trivia × Harita Stratejisi", True, Renk.METIN_IKINCIL)
        self.ekran.blit(alt, alt.get_rect(center=(cx, title_y + 55)))

        # --- Menü butonları ---
        butonlar = [
            ("🗺️  YENİ OYUN",         cy - 20,  "yeni_oyun",  Renk.BUTON_ANA),
            ("🏆  SKOR TABLOSU",       cy + 60,  "skor",       Renk.BUTON_ANA),
            ("❌  ÇIKIŞ",              cy + 140, "cikis",      Renk.BUTON_TEHLIKE),
        ]

        for metin, y, anahtar, renk in butonlar:
            aktif = (hover_buton == anahtar)
            self._menu_butonu_ciz(metin, cx, y, renk, aktif, genislik=340)

        # Versiyon
        ver = self.font_mini.render("v1.0 — Python Pygame", True, Renk.METIN_IKINCIL)
        self.ekran.blit(ver, (20, self.yukseklik - 30))

        pygame.display.flip()

    def oyun_ekrani_ciz(self, oyun_durumu):
        """
        Ana oyun ekranını çizer.
        Harita + HUD + Alt Bar
        """
        self.ekran.fill(Renk.ARKAPLAN)
        self._yildiz_arkaplan_ciz()

        # Harita arka planı (deniz)
        harita_rect = pygame.Rect(self.HARITA_X, 0, self.HARITA_GENISLIK, self.HARITA_YUKSEKLIK)
        pygame.draw.rect(self.ekran, Renk.DENIZ, harita_rect)

        # Bölgeleri çiz
        self._bolgeler_ciz(oyun_durumu.bolgeler)

        # HUD (sol panel)
        self._hud_ciz(oyun_durumu)

        # Alt durum barı
        self._alt_bar_ciz(oyun_durumu)

        # Üst başlık şeridi
        self._ust_serit_ciz(oyun_durumu)
        # NOT: display.flip() KASITLI OLARAK KALDIRILDI.
        # Popup varsa üstüne çizilip main.py'de tek seferde flip yapılır → titreme önlenir.
    
    def asker_al_buton_rect(self):
        """Butonun tıklama alanını belirler."""
        return pygame.Rect(15, self.yukseklik - 120, self.HUD_GENISLIK - 30, 45)

    def _asker_al_butonu_ciz(self, aktif_oyuncu):
        """Asker alma butonunu görselleştirir."""
        rect = self.asker_al_buton_rect()
        hover = rect.collidepoint(pygame.mouse.get_pos())
        can_buy = not aktif_oyuncu.bot and aktif_oyuncu.altin >= 50
        
        # Renk ve stil belirleme
        bg = Renk.BUTON_HOVER if hover and can_buy else Renk.BUTON_ANA
        if not can_buy: bg = (40, 45, 60) # Pasif hali
        kenar = Renk.SARI if hover and can_buy else Renk.PANEL_KENAR
        
        parlak_panel_ciz(self.ekran, rect, bg, kenar, radius=8)
        
        metin = self.font_kucuk.render("⚔️ ASKER SATIN AL (50 G)", True, Renk.METIN_ANA if can_buy else Renk.METIN_IKINCIL)
        self.ekran.blit(metin, metin.get_rect(center=rect.center))

    def skor_tablosu_ciz(self, skor_listesi, mac_gecmisi):
        """Skor tablosu ekranını çizer."""
        self.ekran.fill(Renk.ARKAPLAN)
        self._yildiz_arkaplan_ciz()

        cx = self.genislik // 2

        # Başlık
        baslik = self.font_buyuk.render("🏆  SKOR TABLOSU", True, Renk.SARI)
        self.ekran.blit(baslik, baslik.get_rect(center=(cx, 60)))

        pygame.draw.line(self.ekran, Renk.PANEL_KENAR,
                         (cx - 300, 90), (cx + 300, 90), 1)

        # En yüksek skorlar tablosu
        sol_x = 80
        self._skor_tablosu_panel_ciz(sol_x, 110, 500, skor_listesi)

        # Maç geçmişi
        sag_x = 640
        self._mac_gecmisi_panel_ciz(sag_x, 110, 560, mac_gecmisi)

        # Geri butonu
        self._menu_butonu_ciz("◀  GERİ DÖN", cx, self.yukseklik - 60,
                              Renk.BUTON_ANA, False, genislik=220)

        pygame.display.flip()

    def oyun_bitti_ekrani_ciz(self, oyun_durumu):
        """Oyun sonu ekranını çizer."""
        self.ekran.fill(Renk.ARKAPLAN)
        self._yildiz_arkaplan_ciz()
        kazanan = oyun_durumu.kazanan

        cx, cy = self.genislik // 2, self.yukseklik // 2

        # Büyük kutlama paneli
        panel_rect = pygame.Rect(cx - 400, cy - 220, 800, 440)
        parlak_panel_ciz(self.ekran, panel_rect, Renk.PANEL_BG, Renk.SARI, radius=20)

        # Kazanan adı
        k_renk = Renk.SARI if kazanan.renk_adi == "Sarı" else \
                 Renk.KIRMIZI if kazanan.renk_adi == "Kırmızı" else Renk.MAVI
        kazanan_metin = self.font_dev.render(f"🏆 {kazanan.ad}", True, k_renk)
        self.ekran.blit(kazanan_metin, kazanan_metin.get_rect(center=(cx, cy - 140)))

        alt = self.font_buyuk.render("OYUNU KAZANDI!", True, Renk.METIN_ANA)
        self.ekran.blit(alt, alt.get_rect(center=(cx, cy - 75)))

        # İstatistikler
        istatistikler = oyun_durumu.istatistikleri_getir()
        y_off = cy - 10
        for i, ist in enumerate(istatistikler):
            renk = Renk.SARI if ist["renk"] == "Sarı" else \
                   Renk.KIRMIZI if ist["renk"] == "Kırmızı" else Renk.MAVI
            metin = f"{ist['ad']}:  {ist['skor']} puan  |  {ist['bolge']} bölge  |  {ist['savas']} savaş"
            m = self.font_orta.render(metin, True, renk if ist["ad"] == kazanan.ad else Renk.METIN_IKINCIL)
            self.ekran.blit(m, m.get_rect(center=(cx, y_off + i * 40)))

        # Butonlar
        self._menu_butonu_ciz("🔄  TEKRAR OYNA", cx - 130, cy + 160, Renk.BUTON_BASARI, False, 230)
        self._menu_butonu_ciz("🏠  ANA MENÜ", cx + 130, cy + 160, Renk.BUTON_ANA, False, 230)

        pygame.display.flip()

    # ================================================================
    # POPUP - SORU PENCERESİ
    # ================================================================

    def soru_popup_ciz(self, soru_dict, secili_index=-1, dogru_goster=False,
                       oyuncu_adi="", savas_modu=False):
        """
        Soru popup penceresini çizer.
        :param soru_dict: Soru verisi
        :param secili_index: Oyuncunun seçtiği şık (-1 = seçilmedi)
        :param dogru_goster: True ise doğru cevabı yeşil ile göster
        :param oyuncu_adi: Soru sorulan oyuncunun adı
        :param savas_modu: True ise savaş sorusu göstergesi ekle
        """
        # Yarı saydam overlay
        overlay = pygame.Surface((self.genislik, self.yukseklik), pygame.SRCALPHA)
        overlay.fill((0, 0, 8, 200))
        self.ekran.blit(overlay, (0, 0))

        cx, cy = self.genislik // 2, self.yukseklik // 2
        popup_g, popup_y = 720, 460
        popup_rect = pygame.Rect(cx - popup_g // 2, cy - popup_y // 2, popup_g, popup_y)

        # Popup arka planı
        parlak_panel_ciz(self.ekran, popup_rect, Renk.POPUP_BG, Renk.POPUP_KENAR, radius=18)

        iy = popup_rect.top + 30  # İçerik Y başlangıcı

        # Savaş moduysa kırmızı badge
        if savas_modu:
            badge = self.font_kucuk.render("⚔️  SAVAŞ SORUSU — YÜKSEK ZORLUK", True, Renk.KIRMIZI)
            self.ekran.blit(badge, badge.get_rect(center=(cx, iy)))
            iy += 32
        else:
            # Kategori
            kategori = self.font_kucuk.render(f"📚 {soru_dict.get('kategori','')}", True, Renk.METIN_IKINCIL)
            self.ekran.blit(kategori, kategori.get_rect(center=(cx, iy)))
            iy += 30

        # Oyuncu adı
        ad_renk = self.font_orta.render(f"{oyuncu_adi}'ın Sorusu", True, Renk.METIN_VURGU)
        self.ekran.blit(ad_renk, ad_renk.get_rect(center=(cx, iy)))
        iy += 40

        # Soru metni (satır kaydırmalı)
        soru_satirlari = self._satirlara_bol(soru_dict['soru'], self.font_soru, popup_g - 80)
        for satir in soru_satirlari:
            s = self.font_soru.render(satir, True, Renk.METIN_ANA)
            self.ekran.blit(s, s.get_rect(center=(cx, iy)))
            iy += 34
        iy += 15

        # Şık butonları
        harfler = ["A", "B", "C", "D"]
        secenekler = soru_dict['secenekler']
        dogru_index = soru_dict['dogru']
        buton_g, buton_y_boyut = 300, 46
        sol_x = cx - buton_g - 12
        sag_x = cx + 12

        for i, (harf, secenek) in enumerate(zip(harfler, secenekler)):
            # Pozisyon: 2 sütun grid
            bx = sol_x if i % 2 == 0 else sag_x
            by = iy + (i // 2) * (buton_y_boyut + 14)
            rect = pygame.Rect(bx, by, buton_g, buton_y_boyut)

            # Buton rengi belirleme
            if dogru_goster and i == dogru_index:
                bg = Renk.SECILI_DOGRU
                kenar = (100, 220, 130)
            elif dogru_goster and i == secili_index and i != dogru_index:
                bg = Renk.SECILI_YANLIS
                kenar = (230, 80, 80)
            elif i == secili_index and not dogru_goster:
                bg = Renk.BUTON_HOVER
                kenar = Renk.SARI
            else:
                bg = Renk.BUTON_ANA
                kenar = Renk.PANEL_KENAR

            parlak_panel_ciz(self.ekran, rect, bg, kenar, radius=10)

            # Harf rozeti
            rozet_rect = pygame.Rect(bx + 10, by + 10, 26, 26)
            pygame.draw.rect(self.ekran, kenar, rozet_rect, border_radius=6)
            h = self.font_kucuk.render(harf, True, Renk.ARKAPLAN)
            self.ekran.blit(h, h.get_rect(center=rozet_rect.center))

            # Seçenek metni
            secenek_kisa = secenek[:38] + "..." if len(secenek) > 38 else secenek
            s = self.font_kucuk.render(secenek_kisa, True, Renk.METIN_ANA)
            self.ekran.blit(s, (bx + 44, by + buton_y_boyut // 2 - s.get_height() // 2))

        pygame.display.flip()

        # Tıklama alanlarını döndür (main.py'de kullanılacak)
        areas = {}
        for i in range(len(secenekler)):
            bx = sol_x if i % 2 == 0 else sag_x
            by = iy + (i // 2) * (buton_y_boyut + 14)
            areas[i] = pygame.Rect(bx, by, buton_g, buton_y_boyut)
        return areas

    # ================================================================
    # YARDIMCI ÇİZİM FONKSİYONLARI
    # ================================================================

    def _yildiz_arkaplan_ciz(self):
        """Hafif hareket eden yıldız arka planı."""
        for x, y, parlaklik in self.yildizlar:
            alfa = int(80 + 40 * math.sin(self.zaman + parlaklik * 10))
            boyut = 1 if parlaklik < 0.7 else 2
            renk = (alfa, alfa, alfa + 20)
            pygame.draw.circle(self.ekran, renk, (int(x), int(y)), boyut)

    def _dekoratif_cizgi_ciz(self, cx, y):
        """Başlık altındaki dekoratif altın çizgiler."""
        pygame.draw.line(self.ekran, Renk.SARI, (cx - 280, y), (cx - 40, y), 2)
        pygame.draw.line(self.ekran, Renk.SARI, (cx + 40, y), (cx + 280, y), 2)
        pygame.draw.circle(self.ekran, Renk.SARI, (cx, y), 5)

    def _menu_butonu_ciz(self, metin, cx, cy, renk, aktif, genislik=280):
        """Ana menü butonu çizer."""
        yukseklik = 52
        rect = pygame.Rect(cx - genislik // 2, cy - yukseklik // 2, genislik, yukseklik)
        bg = Renk.BUTON_HOVER if aktif else renk
        kenar = Renk.SARI if aktif else Renk.PANEL_KENAR
        parlak_panel_ciz(self.ekran, rect, bg, kenar, radius=12)
        m = self.font_orta.render(metin, True, Renk.SARI if aktif else Renk.METIN_ANA)
        self.ekran.blit(m, m.get_rect(center=(cx, cy)))
        return rect

    def _bolgeler_ciz(self, bolgeler):
        """Tüm harita bölgelerini çizer."""
        for bolge_id, bolge in bolgeler.items():
            bx = int(bolge.merkez_x * self.harita_olcek_x) + self.harita_offset_x
            by = int(bolge.merkez_y * self.harita_olcek_y) + self.harita_offset_y

            # Hover animasyonu
            yaricap = 26
            hover = (self.hover_bolge == bolge_id)
            if hover:
                yaricap = 30
                # Parlama efekti
                ic_renk = tuple(min(255, c + 30) for c in bolge.renk_rgb)
            else:
                ic_renk = bolge.renk_rgb

            # Gölge
            pygame.draw.circle(self.ekran, (5, 8, 15), (bx + 3, by + 3), yaricap)

            # Ana daire
            pygame.draw.circle(self.ekran, ic_renk, (bx, by), yaricap)

            # Kenar çizgisi
            kenar_renk = Renk.SARI if hover else (
                tuple(max(0, c - 30) for c in ic_renk)
            )
            pygame.draw.circle(self.ekran, kenar_renk, (bx, by), yaricap, 2)

            # Asker sembolü
            if bolge.sahip is not None and bolge.asker_sayisi > 0:
                asker = self.font_mini.render("★", True, Renk.ARKAPLAN)
                self.ekran.blit(asker, asker.get_rect(center=(bx, by)))

            # Bölge adı
            ad_renk = Renk.METIN_ANA if hover else Renk.METIN_IKINCIL
            ad = self.font_mini.render(bolge.ad, True, ad_renk)
            self.ekran.blit(ad, ad.get_rect(center=(bx, by + yaricap + 12)))

            # Komşu çizgileri (ince, yarı saydam)
            for komsu_id in bolge.komsu_idler:
                if komsu_id > bolge_id:  # Her çizgiyi bir kez çiz
                    komsu = bolgeler[komsu_id]
                    kx = int(komsu.merkez_x * self.harita_olcek_x) + self.harita_offset_x
                    ky = int(komsu.merkez_y * self.harita_olcek_y) + self.harita_offset_y
                    pygame.draw.line(self.ekran, Renk.HARITA_IZGARA,
                                     (bx, by), (kx, ky), 1)

    def _hud_ciz(self, oyun_durumu):
        """Sol taraftaki HUD panelini çizer."""
        panel_rect = pygame.Rect(0, 0, self.HUD_GENISLIK, self.yukseklik)
        parlak_panel_ciz(self.ekran, panel_rect, Renk.HUD_BG, Renk.HUD_KENAR, radius=0)

        y = 20

        # Oyun başlığı
        baslik = self.font_orta.render("⚔️ BİL VE FETHET", True, Renk.SARI)
        self.ekran.blit(baslik, baslik.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 38

        # Tur bilgisi
        tur_str = f"TUR  {oyun_durumu.tur}  /  {oyun_durumu.maks_tur}"
        tur = self.font_kucuk.render(tur_str, True, Renk.METIN_IKINCIL)
        self.ekran.blit(tur, tur.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 28

        pygame.draw.line(self.ekran, Renk.PANEL_KENAR, (15, y), (self.HUD_GENISLIK - 15, y), 1)
        y += 18

        # Faz göstergesi
        faz_metinler = {
            "fetih": "📍 FETİH FAZASI",
            "savas": "⚔️  SAVAŞ FAZASI",
            "soru":  "❓  SORU ZAMANI",
        }
        faz_str = faz_metinler.get(oyun_durumu.faz, "")
        faz_renk = Renk.SARI if oyun_durumu.faz == "savas" else Renk.MAVI
        faz = self.font_kucuk.render(faz_str, True, faz_renk)
        self.ekran.blit(faz, faz.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 35

        # Her oyuncu için kart
        toplam_bolge = len(oyun_durumu.bolgeler)
        for oyuncu in oyun_durumu.oyuncular:
            oyuncu_bolge_sayisi = len(oyun_durumu.oyuncunun_bolgelerini_getir(oyuncu))
            aktif = (oyuncu == oyun_durumu.aktif_oyuncu and not oyun_durumu.aktif_oyuncu.elendi)
            self._oyuncu_karti_ciz(oyuncu, oyuncu_bolge_sayisi, toplam_bolge, y, aktif)
            y += 145

        # Boş bölge sayısı
        bos = sum(1 for b in oyun_durumu.bolgeler.values() if b.sahip is None)
        bos_str = f"Boş Bölge: {bos}"
        b_txt = self.font_kucuk.render(bos_str, True, Renk.METIN_IKINCIL)
    def _hud_ciz(self, oyun_durumu):
        """Sol taraftaki HUD panelini çizer."""
        panel_rect = pygame.Rect(0, 0, self.HUD_GENISLIK, self.yukseklik)
        parlak_panel_ciz(self.ekran, panel_rect, Renk.HUD_BG, Renk.HUD_KENAR, radius=0)

        y = 20

        # Oyun başlığı
        baslik = self.font_orta.render("⚔️ BİL VE FETHET", True, Renk.SARI)
        self.ekran.blit(baslik, baslik.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 38

        # Tur bilgisi
        tur_str = f"TUR  {oyun_durumu.tur}  /  {oyun_durumu.maks_tur}"
        tur = self.font_kucuk.render(tur_str, True, Renk.METIN_IKINCIL)
        self.ekran.blit(tur, tur.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 28

        pygame.draw.line(self.ekran, Renk.PANEL_KENAR, (15, y), (self.HUD_GENISLIK - 15, y), 1)
        y += 18

        # Faz göstergesi
        faz_metinler = {
            "fetih": "📍 FETİH FAZASI",
            "savas": "⚔️  SAVAŞ FAZASI",
            "soru":  "❓  SORU ZAMANI",
        }
        faz_str = faz_metinler.get(oyun_durumu.faz, "")
        faz_renk = Renk.SARI if oyun_durumu.faz == "savas" else Renk.MAVI
        faz = self.font_kucuk.render(faz_str, True, faz_renk)
        self.ekran.blit(faz, faz.get_rect(centerx=self.HUD_GENISLIK // 2, y=y))
        y += 35

        # Her oyuncu için kart
        toplam_bolge = len(oyun_durumu.bolgeler)
        for oyuncu in oyun_durumu.oyuncular:
            oyuncu_bolge_sayisi = len(oyun_durumu.oyuncunun_bolgelerini_getir(oyuncu))
            aktif = (oyuncu == oyun_durumu.aktif_oyuncu and not oyun_durumu.aktif_oyuncu.elendi)
            self._oyuncu_karti_ciz(oyuncu, oyuncu_bolge_sayisi, toplam_bolge, y, aktif)
            y += 145

        # Boş bölge sayısı
        bos = sum(1 for b in oyun_durumu.bolgeler.values() if b.sahip is None)
        bos_str = f"Boş Bölge: {bos}"
        b_txt = self.font_kucuk.render(bos_str, True, Renk.METIN_IKINCIL)
        self.ekran.blit(b_txt, b_txt.get_rect(centerx=self.HUD_GENISLIK // 2, y=y + 10))

        # --- İŞTE EKSİK OLAN SATIR BURASI! BUTONU EKRANA ÇAĞIRIYORUZ ---
        if hasattr(self, '_asker_al_butonu_ciz'):
            self._asker_al_butonu_ciz(oyun_durumu.aktif_oyuncu)
        # ----------------------------------------------------------------
    def _oyuncu_karti_ciz(self, oyuncu, bolge_sayisi, toplam_bolge, y, aktif):
        """Bir oyuncunun HUD kartını çizer."""
        renk = Renk.SARI if oyuncu.renk_adi == "Sarı" else \
               Renk.KIRMIZI if oyuncu.renk_adi == "Kırmızı" else Renk.MAVI

        kart_rect = pygame.Rect(10, y, self.HUD_GENISLIK - 20, 130)
        kenar = renk if aktif else Renk.PANEL_KENAR
        bg = (35, 40, 55) if aktif else Renk.PANEL_BG
        parlak_panel_ciz(self.ekran, kart_rect, bg, kenar, radius=10)

        if aktif:
            # Aktif oyuncu göstergesi
            pygame.draw.rect(self.ekran, renk, pygame.Rect(10, y, 4, 130), border_radius=4)

        iy = y + 12
        cx = self.HUD_GENISLIK // 2

        # Oyuncu renk dairesi + ismi
        pygame.draw.circle(self.ekran, renk, (28, iy + 10), 10)
        pygame.draw.circle(self.ekran, (0, 0, 0), (28, iy + 10), 10, 2)
        elendi_str = " (ELENDİ)" if oyuncu.elendi else (" ←" if aktif else "")
        ad_renk = renk if aktif else Renk.METIN_IKINCIL
        ad = self.font_kucuk.render(f"{oyuncu.ad}{elendi_str}", True, ad_renk)
        self.ekran.blit(ad, (42, iy + 3))

        iy += 28

        # Skor
        skor = self.font_orta.render(f"{oyuncu.skor:,}", True, Renk.METIN_ANA)
        self.ekran.blit(skor, skor.get_rect(centerx=cx, y=iy))
        iy += 30

        # İlerleme çubuğu (bölge yüzdesi)
        oran = bolge_sayisi / max(toplam_bolge, 1)
        bar_rect = pygame.Rect(20, iy, self.HUD_GENISLIK - 40, 14)
        pygame.draw.rect(self.ekran, Renk.PANEL_KENAR, bar_rect, border_radius=7)
        if oran > 0:
            dolu_rect = pygame.Rect(20, iy, int((self.HUD_GENISLIK - 40) * oran), 14)
            pygame.draw.rect(self.ekran, renk, dolu_rect, border_radius=7)
        iy += 22

        # Bölge / Savaş sayısı
        detay = self.font_mini.render(
            f"🗺 {bolge_sayisi} bölge  |  ⚔ {oyuncu.kazanilan_savas} galibiyet",
            True, Renk.METIN_IKINCIL
        )
        self.ekran.blit(detay, detay.get_rect(centerx=cx, y=iy))

    def _alt_bar_ciz(self, oyun_durumu):
        """Ekranın altındaki durum mesajı barını çizer."""
        rect = pygame.Rect(self.HARITA_X, self.ALT_BAR_Y, self.HARITA_GENISLIK, 60)
        parlak_panel_ciz(self.ekran, rect, Renk.HUD_BG, Renk.HUD_KENAR, radius=0)

        mesaj = self.font_kucuk.render(oyun_durumu.durum_mesaji, True, Renk.METIN_ANA)
        self.ekran.blit(mesaj, mesaj.get_rect(
            centery=self.ALT_BAR_Y + 30,
            left=self.HARITA_X + 20
        ))

    def _ust_serit_ciz(self, oyun_durumu):
        """Haritanın üstündeki ince başlık şeridini çizer."""
        rect = pygame.Rect(self.HARITA_X, 0, self.HARITA_GENISLIK, 38)
        parlak_panel_ciz(self.ekran, rect, Renk.HUD_BG, Renk.HUD_KENAR, radius=0)
        baslik = self.font_kucuk.render("DÜNYA HARİTASI  —  TIKLAYABİLİRSİNİZ", True, Renk.METIN_IKINCIL)
        self.ekran.blit(baslik, baslik.get_rect(centerx=self.HARITA_X + self.HARITA_GENISLIK // 2, centery=19))

    def _skor_tablosu_panel_ciz(self, x, y, genislik, skor_listesi):
        """Skor tablosu sol panel."""
        panel_rect = pygame.Rect(x, y, genislik, 480)
        parlak_panel_ciz(self.ekran, panel_rect, Renk.PANEL_BG, Renk.PANEL_KENAR)

        baslik = self.font_orta.render("En Yüksek Skorlar", True, Renk.SARI)
        self.ekran.blit(baslik, (x + 20, y + 16))

        sutun_y = y + 56
        if not skor_listesi:
            bos = self.font_kucuk.render("Henüz kayıtlı skor yok.", True, Renk.METIN_IKINCIL)
            self.ekran.blit(bos, (x + 20, sutun_y))
            return

        basliklar = ["#", "Oyuncu", "Skor", "Maç", "Galibiyet"]
        for i, (h, gx) in enumerate(zip(basliklar, [x + 20, x + 60, x + 220, x + 330, x + 400])):
            b = self.font_mini.render(h, True, Renk.METIN_IKINCIL)
            self.ekran.blit(b, (gx, sutun_y))
        sutun_y += 26

        pygame.draw.line(self.ekran, Renk.PANEL_KENAR, (x + 15, sutun_y), (x + genislik - 15, sutun_y), 1)
        sutun_y += 10

        for i, skor in enumerate(skor_listesi[:10]):
            if i % 2 == 0:
                satir_rect = pygame.Rect(x + 10, sutun_y - 2, genislik - 20, 28)
                pygame.draw.rect(self.ekran, (32, 37, 52), satir_rect, border_radius=5)

            veriler = [str(i + 1), skor['oyuncu_adi'], str(skor['en_yuksek_skor']),
                       str(skor['toplam_mac']), str(skor['toplam_galibiyet'])]
            for d, gx in zip(veriler, [x + 20, x + 60, x + 220, x + 330, x + 400]):
                renk = Renk.SARI if i == 0 else Renk.METIN_ANA
                m = self.font_kucuk.render(d, True, renk)
                self.ekran.blit(m, (gx, sutun_y + 2))
            sutun_y += 30

    def _mac_gecmisi_panel_ciz(self, x, y, genislik, mac_gecmisi):
        """Maç geçmişi sağ panel."""
        panel_rect = pygame.Rect(x, y, genislik, 480)
        parlak_panel_ciz(self.ekran, panel_rect, Renk.PANEL_BG, Renk.PANEL_KENAR)

        baslik = self.font_orta.render("Son Maçlar", True, Renk.SARI)
        self.ekran.blit(baslik, (x + 20, y + 16))

        row_y = y + 56
        if not mac_gecmisi:
            bos = self.font_kucuk.render("Henüz maç oynanmadı.", True, Renk.METIN_IKINCIL)
            self.ekran.blit(bos, (x + 20, row_y))
            return

        for i, mac in enumerate(mac_gecmisi[:10]):
            if i % 2 == 0:
                satir_rect = pygame.Rect(x + 10, row_y - 2, genislik - 20, 28)
                pygame.draw.rect(self.ekran, (32, 37, 52), satir_rect, border_radius=5)

            r_renk = Renk.SARI if mac['kazanan_renk'] == "Sarı" else \
                     Renk.KIRMIZI if mac['kazanan_renk'] == "Kırmızı" else Renk.MAVI
            kazanan_m = self.font_kucuk.render(f"🏆 {mac['kazanan_oyuncu']}", True, r_renk)
            self.ekran.blit(kazanan_m, (x + 20, row_y + 2))

            tarih_m = self.font_mini.render(mac['oyun_tarihi'][:16], True, Renk.METIN_IKINCIL)
            self.ekran.blit(tarih_m, (x + 300, row_y + 4))
            row_y += 30

    @staticmethod
    def _satirlara_bol(metin, font, maks_genislik):
        """Uzun metni belirli genişliğe sığacak satırlara böler."""
        kelimeler = metin.split()
        satirlar = []
        mevcut = ""
        for kelime in kelimeler:
            test = f"{mevcut} {kelime}".strip()
            if font.size(test)[0] <= maks_genislik:
                mevcut = test
            else:
                if mevcut:
                    satirlar.append(mevcut)
                mevcut = kelime
        if mevcut:
            satirlar.append(mevcut)
        return satirlar

    def bolge_koordinat_al(self, bolgeler, bolge_id):
        """Bir bölgenin ekran koordinatlarını hesaplar."""
        bolge = bolgeler[bolge_id]
        bx = int(bolge.merkez_x * self.harita_olcek_x) + self.harita_offset_x
        by = int(bolge.merkez_y * self.harita_olcek_y) + self.harita_offset_y
        return bx, by

    def mouse_hangi_bolgede(self, bolgeler, mouse_x, mouse_y, yaricap=30):
        """
        Mouse pozisyonuna göre hangi bölgeye tıklandığını bulur.
        :return: bolge_id veya None
        """
        for bolge_id, bolge in bolgeler.items():
            bx = int(bolge.merkez_x * self.harita_olcek_x) + self.harita_offset_x
            by = int(bolge.merkez_y * self.harita_olcek_y) + self.harita_offset_y
            uzaklik = math.sqrt((mouse_x - bx) ** 2 + (mouse_y - by) ** 2)
            if uzaklik <= yaricap:
                return bolge_id
        return None

    def menu_buton_rects(self):
        """Ana menü buton dikdörtgenlerini döndürür (tıklama kontrolü için)."""
        cx, cy = self.genislik // 2, self.yukseklik // 2
        return {
            "yeni_oyun": pygame.Rect(cx - 170, cy - 46, 340, 52),
            "skor":      pygame.Rect(cx - 170, cy + 34, 340, 52),
            "cikis":     pygame.Rect(cx - 170, cy + 114, 340, 52),
        }
    def _oyuncu_karti_ciz(self, oyuncu, bolge_sayisi, toplam_bolge, y, aktif):
        """Bir oyuncunun HUD kartını çizer."""
        renk = Renk.SARI if oyuncu.renk_adi == "Sarı" else \
               Renk.KIRMIZI if oyuncu.renk_adi == "Kırmızı" else Renk.MAVI

        kart_rect = pygame.Rect(10, y, self.HUD_GENISLIK - 20, 130)
        kenar = renk if aktif else Renk.PANEL_KENAR
        bg = (35, 40, 55) if aktif else Renk.PANEL_BG
        parlak_panel_ciz(self.ekran, kart_rect, bg, kenar, radius=10)

        if aktif:
            pygame.draw.rect(self.ekran, renk, pygame.Rect(10, y, 4, 130), border_radius=4)

        iy = y + 12
        cx = self.HUD_GENISLIK // 2

        # Oyuncu renk dairesi + ismi
        pygame.draw.circle(self.ekran, renk, (28, iy + 10), 10)
        pygame.draw.circle(self.ekran, (0, 0, 0), (28, iy + 10), 10, 2)
        elendi_str = " (ELENDİ)" if oyuncu.elendi else (" ←" if aktif else "")
        ad_renk = renk if aktif else Renk.METIN_IKINCIL
        ad = self.font_kucuk.render(f"{oyuncu.ad}{elendi_str}", True, ad_renk)
        self.ekran.blit(ad, (42, iy + 3))

        iy += 26

        # --- YENİ EKLENEN KISIM: ALTIN, ASKER VE SKOR EKRANI ---
        # Fontu küçülttük (font_kucuk) ve metinleri kısalttık ki kutuya tam sığsın
        kaynak_metni = f"Altın: {oyuncu.altin}  |  Asker: {oyuncu.asker}"
        k_render = self.font_kucuk.render(kaynak_metni, True, Renk.METIN_VURGU)
        self.ekran.blit(k_render, k_render.get_rect(centerx=cx, y=iy))
        iy += 22  # Boşluğu hafif kıstık
        
        skor_metni = f"Puan: {oyuncu.skor:,}"
        s_render = self.font_mini.render(skor_metni, True, Renk.METIN_ANA)
        self.ekran.blit(s_render, s_render.get_rect(centerx=cx, y=iy))
        iy += 20
        # -----------------------------------------------------

        # İlerleme çubuğu (bölge yüzdesi)
        oran = bolge_sayisi / max(toplam_bolge, 1)
        bar_rect = pygame.Rect(20, iy, self.HUD_GENISLIK - 40, 10)
        pygame.draw.rect(self.ekran, Renk.PANEL_KENAR, bar_rect, border_radius=5)
        if oran > 0:
            dolu_rect = pygame.Rect(20, iy, int((self.HUD_GENISLIK - 40) * oran), 10)
            pygame.draw.rect(self.ekran, renk, dolu_rect, border_radius=5)
        iy += 18

        # Bölge / Savaş sayısı
        detay = self.font_mini.render(
            f"🗺 {bolge_sayisi} bölge  |  🏆 {oyuncu.kazanilan_savas} galibiyet",
            True, Renk.METIN_IKINCIL
        )
        self.ekran.blit(detay, detay.get_rect(centerx=cx, y=iy))

    def oyun_bitti_buton_rects(self):
        """Oyun sonu ekranı buton dikdörtgenleri."""
        cx, cy = self.genislik // 2, self.yukseklik // 2
        return {
            "tekrar":   pygame.Rect(cx - 245, cy + 134, 230, 52),
            "ana_menu": pygame.Rect(cx + 15, cy + 134, 230, 52),
        }