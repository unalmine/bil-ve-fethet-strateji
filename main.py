"""
================================================================
BİL VE FETHET - Ana Oyun Döngüsü
================================================================
Oyunu başlatan, tüm modülleri birbirine bağlayan ve
ana event döngüsünü yöneten dosya.

ÇALIŞTIRMAK İÇİN:
    python main.py

GEREKLİ KURULUM:
    pip install pygame

================================================================
"""




import pygame
import sys
import time
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/music/background.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# Kendi modüllerimizi import ediyoruz
from ui_manager import UIManager, Renk
from game_mechanics import OyunDurumu, RENK_HEX
from database import DatabaseManager


# ================================================================
# OYUN BAŞLATMA AYARLARI
# ================================================================

EKRAN_GENISLIK = 1280
EKRAN_YUKSEKLIK = 760
FPS = 60  # Kare hızı

# Varsayılan oyuncu konfigürasyonu
VARSAYILAN_OYUNCULAR = [
    ("Oyuncu 1", "Sarı",    False),   # İnsan oyuncu
    ("Bot Kırmızı", "Kırmızı", True), # Bot
    ("Bot Mavi",  "Mavi",   True),    # Bot
]


# ================================================================
# ANA OYUN SINIFI
# ================================================================

class BilVeFethet:
    """
    Oyunun tüm bileşenlerini bir araya getiren ve
    ana döngüyü yöneten ana sınıf.
    """

    def __init__(self):
        """Tüm sistemi başlatır."""
        print("=" * 60)
        print("  BİL VE FETHET - Başlatılıyor...")
        print("=" * 60)

        # Temel pygame başlatma
        pygame.init()
        self.saat = pygame.time.Clock()

        # Modülleri başlat
        self.ui = UIManager(EKRAN_GENISLIK, EKRAN_YUKSEKLIK)
        self.oyun = OyunDurumu()
        self.db = DatabaseManager("skorlar.db")

        # Ekran durumu
        self.calisıyor = True
        self.mevcut_ekran = "menu"   # menu | oyun | skor | bitti

        # Popup / soru durumu
        self.soru_aktif = False
        self.soru_secilen_index = -1   # Oyuncunun seçtiği şık
        self.soru_sonuc_goster = False # Doğru/yanlış gösterimi
        self.soru_bitis_zamani = 0     # Sonuç gösterim süresi
        self.soru_buton_alanlar = {}   # Popup tıklama alanları

        # Bot gecikme (botlar anında hamle yapmasın)
        self.bot_hamle_zamani = 0
        self.bot_hamle_bekleme = 1.5   # saniye

        # Hover efekti için
        self.hover_bolge = None

        print("[OYUN] Sistem hazır. Ana menü açılıyor.")

    def calistir(self):
        """Ana oyun döngüsü — Oyun bu fonksiyon çalıştığı sürece devam eder."""
        while self.calisıyor:
            # Animasyon zamanlayıcısını ilerlet
            self.ui.zamanı_guncelle()

            # Event'leri işle
            self._eventleri_isle()

            # Oyun mantığını güncelle
            self._oyun_mantigini_guncelle()

            # Ekranı çiz
            self._ekrani_ciz()

            # EKRANI GÜNCELLE (EKSİK OLAN VE DONMAYA SEBEP OLAN SATIR BURASI!)
            pygame.display.update()

            # FPS sınırla
            self.saat.tick(FPS)

        # Temiz çıkış
        pygame.quit()
        sys.exit()

    # ================================================================
    # EVENT İŞLEME
    # ================================================================

    def _eventleri_isle(self):
        """Tüm pygame event'lerini yakalar ve işler."""
        for event in pygame.event.get():

            # Pencereyi kapat
            if event.type == pygame.QUIT:
                self.calisıyor = False

            # Klavye
            elif event.type == pygame.KEYDOWN:
                self._klavye_eventi(event)

            # Mouse tıklama
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    self._mouse_tiklama(event.pos)

            # Mouse hareketi (hover)
            elif event.type == pygame.MOUSEMOTION:
                self._mouse_hareket(event.pos)

    def _klavye_eventi(self, event):
        """Klavye olaylarını işler."""
        if event.key == pygame.K_ESCAPE:
            if self.mevcut_ekran == "oyun":
                self.mevcut_ekran = "menu"
            elif self.mevcut_ekran == "skor":
                self.mevcut_ekran = "menu"

        # Hızlı test için boşluk tuşu soru geçişi
        if event.key == pygame.K_SPACE and self.soru_sonuc_goster:
            self._soruyu_kapat()

    def _mouse_hareket(self, pos):
        """Mouse hareketini takip eder (hover efektleri için)."""
        if self.mevcut_ekran == "oyun" and not self.soru_aktif:
            self.hover_bolge = self.ui.mouse_hangi_bolgede(
                self.oyun.bolgeler, pos[0], pos[1]
            )
            self.ui.hover_bolge = self.hover_bolge

    def _mouse_tiklama(self, pos):
        """Mouse tıklamalarını mevcut ekrana göre yönlendirir."""
        x, y = pos

        # ---- ANA MENÜ ----
        if self.mevcut_ekran == "menu":
            butonlar = self.ui.menu_buton_rects()
            if butonlar["yeni_oyun"].collidepoint(x, y):
                self._yeni_oyun_baslat()
            elif butonlar["skor"].collidepoint(x, y):
                self.mevcut_ekran = "skor"
            elif butonlar["cikis"].collidepoint(x, y):
                self.calisıyor = False

        # ---- OYUN EKRANI ----
        elif self.mevcut_ekran == "oyun":
            if self.soru_aktif:
                self._soru_tiklama(x, y)
            else:
                # YENİ: ASKER ALMA BUTONU KONTROLÜ
                asker_al_rect = self.ui.asker_al_buton_rect()
                if asker_al_rect.collidepoint(x, y):
                    self.oyun.asker_satin_al()
                else:
                    self._harita_tiklama(x, y)

        # ---- SKOR TABLOSU ----
        elif self.mevcut_ekran == "skor":
            cx = EKRAN_GENISLIK // 2
            geri_rect = pygame.Rect(cx - 110, EKRAN_YUKSEKLIK - 86, 220, 52)
            if geri_rect.collidepoint(x, y):
                self.mevcut_ekran = "menu"

        # ---- OYUN BİTTİ ----
        elif self.mevcut_ekran == "bitti":
            butonlar = self.ui.oyun_bitti_buton_rects()
            if butonlar["tekrar"].collidepoint(x, y):
                self._yeni_oyun_baslat()
            elif butonlar["ana_menu"].collidepoint(x, y):
                self.mevcut_ekran = "menu"

    def _harita_tiklama(self, x, y):
        """Haritada bir bölgeye tıklandığında çağrılır."""
        # Sol HUD alanına tıklandıysa işlem yapma
        if x < self.ui.HUD_GENISLIK:
            return

        # Aktif oyuncu bot ise insan tıklamasını engelle
        if self.oyun.aktif_oyuncu.bot:
            return

        bolge_id = self.ui.mouse_hangi_bolgede(self.oyun.bolgeler, x, y)
        if bolge_id is None:
            return

        sonuc = self.oyun.bolgeye_tikla(bolge_id)

        if sonuc == 'soru_sor':
            self._soruyu_ac()
        elif sonuc == 'gecersiz':
            pass  # Mesaj oyun durumunda güncellendi

    def _soru_tiklama(self, x, y):
        """Soru popup'ındaki şıklara tıklandığında çağrılır."""
        if self.soru_sonuc_goster:
            # Sonuç gösteriliyorsa tıklama soruyu kapatır
            self._soruyu_kapat()
            return

        # Şık butonlarına tıklama kontrolü
        for index, rect in self.soru_buton_alanlar.items():
            if rect.collidepoint(x, y):
                self._cevap_ver(index)
                break

    # ================================================================
    # SORU MANTIĞI
    # ================================================================

    def _soruyu_ac(self):
        """Soru popup'ını aktif hale getirir."""
        self.soru_aktif = True
        self.soru_secilen_index = -1
        self.soru_sonuc_goster = False

    def _cevap_ver(self, secilen_index):
        """
        Oyuncu bir şık seçtiğinde çağrılır.
        Savaş modunda botun cevabını da simüle eder.
        """
        self.soru_secilen_index = secilen_index
        savas_modu = (self.oyun.savas_savunan is not None)
        savunma_dogru = False

        # Savaş modunda savunan taraf (bot veya insan) da cevap verir
        if savas_modu:
            savunan = self.oyun.savas_savunan
            if savunan.bot:
                # Bot %60 ihtimalle doğru cevap verir
                dogru_index = self.oyun.mevcut_soru['dogru']
                if random.random() < 0.60:
                    savunma_dogru = True
                    print(f"[BOT] {savunan.ad} doğru savundu!")
                else:
                    print(f"[BOT] {savunan.ad} savunmayı kaybetti.")

        # Cevabı işle
        sonuc = self.oyun.cevap_isle(secilen_index, savunma_dogru)

        # Sonucu göster
        self.soru_sonuc_goster = True
        self.soru_bitis_zamani = time.time() + 2.0  # 2 saniye sonra kapat

        print(f"[SORU] Sonuç: {sonuc}, Seçilen: {secilen_index}")

        # Oyun bittiyse kaydet
        if self.oyun.faz == OyunDurumu.FAZ_OYUN_BITTI:
            self._oyun_bitisini_isle()

    def _soruyu_kapat(self):
        """Soru popup'ını kapatır ve sırayı ilerletir."""
        self.soru_aktif = False
        self.soru_secilen_index = -1
        self.soru_sonuc_goster = False

        # Oyun bitmemişse sırayı ilerlet
        if self.oyun.faz not in (OyunDurumu.FAZ_OYUN_BITTI, OyunDurumu.FAZ_MENU):
            self.oyun.sonraki_oyuncuya_gec()
            # Bot sırasıysa zamanlayıcı kur
            if self.oyun.aktif_oyuncu.bot and not self.oyun.aktif_oyuncu.elendi:
                self.bot_hamle_zamani = time.time() + self.bot_hamle_bekleme

    # ================================================================
    # BOT MANTIĞI
    # ================================================================

    def _bot_hamlesi_gerceklestir(self):
        """Bot oyuncusunun hamlesi için otomatik işlemler."""
        if not self.oyun.aktif_oyuncu.bot:
            return
        if self.soru_aktif:
            return
        if time.time() < self.bot_hamle_zamani:
            return

        # Bot bir bölge seç
        bolge_id = self.oyun.bot_hamlesi_yap()
        if bolge_id is None:
            # Geçerli hamle yok, sırayı geç
            self.oyun.sonraki_oyuncuya_gec()
            self._bot_zamanlayicisini_guncelle()
            return

        sonuc = self.oyun.bolgeye_tikla(bolge_id)
        if sonuc == 'soru_sor':
            # Bot soruyu otomatik yanıtlar
            dogru_index = self.oyun.mevcut_soru['dogru']
            # Botlar %70 ihtimalle doğru cevap verir
            if random.random() < 0.70:
                bot_secim = dogru_index
            else:
                yanlis_secenekler = [i for i in range(4) if i != dogru_index]
                bot_secim = random.choice(yanlis_secenekler)

            # Kısa bir gecikme sonrası cevap ver gibi göster
            self._soruyu_ac()
            # Otomatik cevap için zamanlayıcı — sonraki döngüde işlenir
            self.bot_cevap_zamani = time.time() + 0.8
            self.bot_cevap_index = bot_secim
        else:
            self._bot_zamanlayicisini_guncelle()

    def _bot_zamanlayicisini_guncelle(self):
        """Bot için bir sonraki hamle bekleme süresini ayarlar."""
        self.bot_hamle_zamani = time.time() + self.bot_hamle_bekleme

    # ================================================================
    # OYUN YÖNETİMİ
    # ================================================================

    def _oyun_mantigini_guncelle(self):
        """Her frame'de oyun durumunu günceller."""
        if self.mevcut_ekran != "oyun":
            return

        # Oyun bittiyse ekranı değiştir
        if self.oyun.faz == OyunDurumu.FAZ_OYUN_BITTI:
            self.mevcut_ekran = "bitti"
            return

        # Soru sonucu gösteriliyorsa ve süre dolduysa kapat
        if self.soru_sonuc_goster and time.time() > self.soru_bitis_zamani:
            self._soruyu_kapat()
            return

        # Bot sorusunu otomatik cevapla
        if hasattr(self, 'bot_cevap_zamani') and self.soru_aktif and not self.soru_sonuc_goster:
            if time.time() > self.bot_cevap_zamani:
                self._cevap_ver(self.bot_cevap_index)
                del self.bot_cevap_zamani
                del self.bot_cevap_index
                return

        # Bot hamlesi zamanı geldiyse
        if (self.oyun.aktif_oyuncu.bot and
                not self.soru_aktif and
                not self.oyun.aktif_oyuncu.elendi):
            self._bot_hamlesi_gerceklestir()

    def _yeni_oyun_baslat(self):
        """Yeni bir oyun başlatır."""
        self.oyun.yeni_oyun_baslat(VARSAYILAN_OYUNCULAR)
        self.mevcut_ekran = "oyun"
        self.soru_aktif = False
        self.soru_sonuc_goster = False

        # --- ÇÖZÜM: FARE TIKLAMASINI SIFIRLAMA ---
        # Menüden oyuna geçerken yapılan çift tıklamanın haritaya yansımasını engeller
        pygame.time.delay(200)  # 0.2 saniye bekle
        pygame.event.clear()    # Geçmişte kalan tüm tıklamaları temizle
        # ----------------------------------------

        # İlk oyuncu botsa zamanlayıcı kur
        if self.oyun.aktif_oyuncu.bot:
            self.bot_hamle_zamani = time.time() + self.bot_hamle_bekleme

        print("[OYUN] Yeni oyun başlatıldı!")

    def _oyun_bitisini_isle(self):
        """Oyun sona erdiğinde veritabanına kaydeder."""
        import time as t
        sure = int(t.time() - self.oyun.oyun_baslangic_zamani)
        self.db.oyun_sonucunu_kaydet(
            self.oyun.oyuncular,
            self.oyun.kazanan,
            self.oyun.tur,
            sure
        )
        print(f"[DB] Oyun kaydedildi. Süre: {sure}s")

    # ================================================================
    # EKRAN ÇİZİMİ
    # ================================================================

    def _ekrani_ciz(self):
        """Mevcut ekrana göre doğru çizim fonksiyonunu çağırır."""

        if self.mevcut_ekran == "menu":
            # Hover kontrolü
            mx, my = pygame.mouse.get_pos()
            butonlar = self.ui.menu_buton_rects()
            hover = None
            for anahtar, rect in butonlar.items():
                if rect.collidepoint(mx, my):
                    hover = anahtar
            self.ui.ana_menu_ciz(hover_buton=hover)

        elif self.mevcut_ekran == "oyun":
            # Önce oyun ekranını çiz
            self.ui.oyun_ekrani_ciz(self.oyun)

            # Soru popup'ı varsa üstüne çiz
            if self.soru_aktif and self.oyun.mevcut_soru:
                savas = (self.oyun.savas_savunan is not None) or \
                        (self.oyun.faz == OyunDurumu.FAZ_SORU and
                         hasattr(self.oyun, '_savas_sorusu') and self.oyun._savas_sorusu)

                self.soru_buton_alanlar = self.ui.soru_popup_ciz(
                    soru_dict=self.oyun.mevcut_soru,
                    secili_index=self.soru_secilen_index,
                    dogru_goster=self.soru_sonuc_goster,
                    oyuncu_adi=self.oyun.aktif_oyuncu.ad,
                    savas_modu=False
                )

        elif self.mevcut_ekran == "skor":
            skorlar = self.db.skor_tablosunu_getir(limit=10)
            maclar = self.db.mac_gecmisini_getir(limit=10)
            self.ui.skor_tablosu_ciz(skorlar, maclar)

        elif self.mevcut_ekran == "bitti":
            self.ui.oyun_bitti_ekrani_ciz(self.oyun)


# ================================================================
# GİRİŞ NOKTASI
# ================================================================

def main():
    """Oyunu başlatan ana fonksiyon."""
    print("\n" + "=" * 60)
    print("       ⚔️   BİL VE FETHET  ⚔️")
    print("   Trivia × Harita Strateji Oyunu")
    print("=" * 60)
    print("\nKontroller:")
    print("  Sol Tık  — Bölge seç / Şık seç")
    print("  ESC      — Ana menüye dön")
    print("  BOŞLUK   — Soru sonucunu geç")
    print("=" * 60 + "\n")

    oyun = BilVeFethet()
    oyun.calistir()


if __name__ == "__main__":
    main()
