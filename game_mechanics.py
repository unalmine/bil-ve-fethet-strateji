"""
================================================================
BİL VE FETHET - Oyun Mekaniği Modülü
================================================================
"""

import random
from questions import SoruBankasi

RENKLER = {
    "Sarı":   (255, 215, 0),
    "Kırmızı": (220, 50, 50),
    "Mavi":   (50, 120, 220),
    "Boş":    (60, 65, 75),
    "Seçili": (255, 255, 255),
}

RENK_HEX = {
    "Sarı":    "#FFD700",
    "Kırmızı": "#DC3232",
    "Mavi":    "#3278DC",
}

class Oyuncu:
    def __init__(self, ad, renk_adi, bot=False):
        self.ad = ad
        self.renk_adi = renk_adi
        self.renk_rgb = RENKLER[renk_adi]
        self.bot = bot

        # İstatistikler ve Kaynaklar
        self.skor = 0
        self.altin = 200     # BAŞLANGIÇ ALTINI
        self.asker = 100     # BAŞLANGIÇ ASKERİ
        self.fethedilen_bolge_sayisi = 0
        self.kazanilan_savas = 0
        self.dogru_cevap_sayisi = 0
        self.elendi = False

    def kaynak_guncelle(self, altin_farki, asker_farki):
        """Asker ve Altın değerlerini günceller."""
        self.altin = max(0, self.altin + altin_farki)
        self.asker = max(0, self.asker + asker_farki)

    def skor_ekle(self, miktar):
        self.skor += miktar

    def bolge_fethetti(self, adet=1):
        self.fethedilen_bolge_sayisi += adet
        self.skor_ekle(100 * adet)

    def savasi_kazandi(self):
        self.kazanilan_savas += 1
        self.skor_ekle(250)

    def dogru_cevap_verdi(self, savas_modu=False):
        self.dogru_cevap_sayisi += 1
        bonus = 150 if savas_modu else 50
        self.skor_ekle(bonus)

class Bolge:
    def __init__(self, bolge_id, ad, merkez_x, merkez_y, komsu_idler=None):
        self.id = bolge_id
        self.ad = ad
        self.merkez_x = merkez_x
        self.merkez_y = merkez_y
        self.komsu_idler = komsu_idler or []
        self.sahip = None
        self.asker_sayisi = 0

    @property
    def renk_rgb(self):
        if self.sahip is None:
            return RENKLER["Boş"]
        return self.sahip.renk_rgb

    def fethedeldi(self, oyuncu, asker=10):
        self.sahip = oyuncu
        self.asker_sayisi = asker

def harita_bolgelerini_olustur():
    bolge_verileri = [
        (0,  "Kanada",          190, 120), (1,  "ABD",             175, 210), (2,  "Meksika",         155, 290),
        (3,  "Küba",            210, 295), (4,  "Kolombiya",       205, 370), (5,  "Brezilya",        240, 450),
        (6,  "Arjantin",        225, 560), (7,  "İngiltere",       430, 130), (8,  "Fransa",          460, 175),
        (9,  "İspanya",         440, 215), (10, "Almanya",         495, 155), (11, "İtalya",          500, 200),
        (12, "Polonya",         530, 145), (13, "Ukrayna",         570, 160), (14, "İsveç",           510, 110),
        (15, "Türkiye",         590, 210), (16, "Fas",             440, 270), (17, "Libya",           500, 280),
        (18, "Mısır",           560, 275), (19, "Nijerya",         470, 360), (20, "Etiyopya",        570, 360),
        (21, "Kongo",           510, 410), (22, "G.Afrika",        510, 510), (23, "Suudi Arabistan", 620, 290),
        (24, "İran",            650, 250), (25, "Kazakistan",      680, 185), (26, "Rusya",           700, 120),
        (27, "Çin",             780, 230), (28, "Hindistan",       720, 300), (29, "Japonya",         870, 210),
        (30, "Güney Kore",      840, 230), (31, "Vietnam",         820, 310), (32, "Endonezya",       840, 390),
        (33, "Avustralya",      880, 490), (34, "Yeni Zelanda",    960, 560),
    ]

    komsuluklar = [
        (0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (3, 4), (2, 4), (7, 8), (7, 10), (8, 9), (8, 10), (8, 11),
        (10, 11), (10, 12), (12, 13), (13, 15), (14, 10), (9, 16), (11, 17), (15, 18), (16, 17), (17, 18), (16, 19), (17, 19),
        (18, 20), (19, 21), (20, 21), (21, 22), (15, 23), (15, 24), (13, 25), (23, 24), (24, 25), (24, 28), (25, 26),
        (26, 27), (27, 28), (27, 31), (27, 30), (27, 29), (28, 31), (30, 29), (31, 32), (32, 33), (33, 34),
        (7, 0), (9, 0), (26, 0), (29, 1),
    ]

    bolgeler = {}
    for bid, ad, mx, my in bolge_verileri:
        bolgeler[bid] = Bolge(bid, ad, mx, my)

    for b1, b2 in komsuluklar:
        if b2 not in bolgeler[b1].komsu_idler:
            bolgeler[b1].komsu_idler.append(b2)
        if b1 not in bolgeler[b2].komsu_idler:
            bolgeler[b2].komsu_idler.append(b1)

    return bolgeler

class OyunDurumu:
    FAZ_MENU          = "menu"
    FAZ_FETIH         = "fetih" 
    FAZ_SAVAS         = "savas"
    FAZ_SORU          = "soru"
    FAZ_OYUN_BITTI    = "bitti"
    FAZ_SKOR_TABLOSU  = "skor"

    def __init__(self):
        self.faz = self.FAZ_MENU
        self.bolgeler = {}
        self.oyuncular = []
        self.aktif_oyuncu_index = 0
        self.tur = 1
        self.maks_tur = 30
        self.soru_bankasi = SoruBankasi()
        self.mevcut_soru = None
        self.secilen_bolge = None
        self.savas_savunan = None
        self.oyun_baslangic_zamani = 0
        self.kazanan = None
        self.durum_mesaji = ""

    def yeni_oyun_baslat(self, oyuncu_listesi):
        import time
        self.oyuncular = []
        self.aktif_oyuncu_index = 0
        self.tur = 1
        self.kazanan = None
        self.mevcut_soru = None
        self.secilen_bolge = None
        self.oyun_baslangic_zamani = time.time()

        for ad, renk, bot in oyuncu_listesi:
            self.oyuncular.append(Oyuncu(ad, renk, bot))

        self.bolgeler = harita_bolgelerini_olustur()
        self.faz = self.FAZ_FETIH
        self.durum_mesajini_guncelle()

    @property
    def aktif_oyuncu(self):
        return self.oyuncular[self.aktif_oyuncu_index]

    def sonraki_oyuncuya_gec(self):
        aktif_sayisi = len([o for o in self.oyuncular if not o.elendi])
        if aktif_sayisi <= 1:
            self.oyunu_bitir()
            return

        for _ in range(len(self.oyuncular)):
            self.aktif_oyuncu_index = (self.aktif_oyuncu_index + 1) % len(self.oyuncular)
            if not self.aktif_oyuncu.elendi:
                break

        if self.aktif_oyuncu_index == 0:
            self.tur += 1
            if self.tur > self.maks_tur:
                self.oyunu_bitir()
                return

        if not self.bos_bolgeler_var_mi():
            self.faz = self.FAZ_SAVAS
        else:
            self.faz = self.FAZ_FETIH

        self.durum_mesajini_guncelle()

    def bos_bolgeler_var_mi(self):
        return any(b.sahip is None for b in self.bolgeler.values())
    
    def asker_satin_al(self):
        """Altın harcayarak orduyu güçlendirir."""
        oyuncu = self.aktif_oyuncu
        if oyuncu.bot: return False # Botlar otomatik alıyor, butona basamaz
        
        maliyet = 50
        miktar = 25
        
        if oyuncu.altin >= maliyet:
            oyuncu.kaynak_guncelle(altin_farki=-maliyet, asker_farki=miktar)
            self.durum_mesaji = f"💰 {oyuncu.ad} {maliyet} Altın karşılığında {miktar} asker kiraladı!"
            return True
        else:
            self.durum_mesaji = "❌ Yetersiz altın! En az 50 altına ihtiyacınız var."
            return False

    def bolgeye_tikla(self, bolge_id):
        bolge = self.bolgeler.get(bolge_id)
        if bolge is None:
            return 'gecersiz'

        # Kendi bölgesi kontrolü
        if bolge.sahip == self.aktif_oyuncu:
            self.durum_mesaji = "❌ Kendi bölgenize saldıramazsınız!"
            return 'gecersiz'

        # --- YENİ: ORDU VE ALTIN KONTROLÜ (PARALI ASKER SİSTEMİ) ---
        if self.aktif_oyuncu.asker < 10:
            if self.aktif_oyuncu.altin >= 50:
                self.aktif_oyuncu.kaynak_guncelle(altin_farki=-50, asker_farki=30)
                self.durum_mesaji = f"💰 {self.aktif_oyuncu.ad}, 50 Altın ödeyerek 30 Paralı Asker kiraladı!"
            else:
                self.durum_mesaji = "❌ Askeriniz yok ve ordu kuracak altınınız kalmadı! Çöküş kapıda..."
                return 'gecersiz'
        # -----------------------------------------------------------

        # Eğer boş bölgeyse doğrudan fethet (Savaşsız soru)
        if bolge.sahip is None:
            self.secilen_bolge = bolge
            self.mevcut_soru = self.soru_bankasi.rastgele_soru_getir(savas_modu=False)
            self.faz = self.FAZ_SORU
            return 'soru_sor'

        # Eğer rakibin bölgesiyse KOMŞULUK kontrolü yap
        oyuncunun_bolgeleri = self.oyuncunun_bolgelerini_getir(self.aktif_oyuncu)
        komsu_mu = any(bolge_id in self.bolgeler[ob].komsu_idler for ob in oyuncunun_bolgeleri)

        if not komsu_mu and len(oyuncunun_bolgeleri) > 0:
            self.durum_mesaji = "❌ Yalnızca komşu olduğunuz bölgelere saldırabilirsiniz!"
            return 'gecersiz'

        # KOMŞUYA DOĞRUDAN SALDIRI
        self.secilen_bolge = bolge
        self.savas_savunan = bolge.sahip
        self.mevcut_soru = self.soru_bankasi.rastgele_soru_getir(savas_modu=True)
        self.faz = self.FAZ_SORU
        return 'soru_sor'

    def cevap_isle(self, secilen_index, savunma_dogru=False):
        dogru_index = self.mevcut_soru["dogru"]
        dogru_mu = (secilen_index == dogru_index)
        savas_modu = (self.savas_savunan is not None)

        if not savas_modu:
            # --- BOŞ TOPRAK FETİH ---
            if dogru_mu:
                self.aktif_oyuncu.kaynak_guncelle(altin_farki=100, asker_farki=50) # Ödül
                self.secilen_bolge.fethedeldi(self.aktif_oyuncu, asker=20)
                self.aktif_oyuncu.bolge_fethetti()
                self.aktif_oyuncu.dogru_cevap_verdi()
                self.durum_mesaji = f"✅ {self.aktif_oyuncu.ad} fethetti! (+100 💰, +50 ⚔️)"
                self._eleme_kontrol()
                sonuc = 'dogru'
            else:
                self.aktif_oyuncu.kaynak_guncelle(altin_farki=-50, asker_farki=-20) # Ceza
                self.durum_mesaji = f"❌ Yanlış! (-50 💰, -20 ⚔️) Doğru cevap: {self.mevcut_soru['secenekler'][dogru_index]}"
                sonuc = 'yanlis'

        else:
            # --- PVP SAVAŞ MODU (Rakibe Saldırı) ---
            if dogru_mu and not savunma_dogru:
                # Saldıran net kazandı
                onceki_sahip = self.secilen_bolge.sahip
                self.aktif_oyuncu.kaynak_guncelle(altin_farki=200, asker_farki=-10) # Zafer ganimeti, az kayıp
                self.savas_savunan.kaynak_guncelle(altin_farki=-100, asker_farki=-40)
                
                self.secilen_bolge.fethedeldi(self.aktif_oyuncu, asker=30)
                self.aktif_oyuncu.bolge_fethetti()
                self.aktif_oyuncu.dogru_cevap_verdi(savas_modu=True)
                self.aktif_oyuncu.savasi_kazandi()
                self.durum_mesaji = f"⚔️ Zafer! {self.aktif_oyuncu.ad} '{self.secilen_bolge.ad}'ı ele geçirdi! (+200 💰)"
                self._eleme_kontrol_oyuncu(onceki_sahip)
                sonuc = 'savas_kazandi'
                
            elif savunma_dogru and not dogru_mu:
                # Savunan net kazandı
                self.aktif_oyuncu.kaynak_guncelle(altin_farki=-150, asker_farki=-50) # Ağır ceza
                self.savas_savunan.kaynak_guncelle(altin_farki=100, asker_farki=-5)
                
                self.savas_savunan.dogru_cevap_verdi(savas_modu=True)
                self.savas_savunan.savasi_kazandi()
                self.durum_mesaji = f"🛡️ {self.savas_savunan.ad} savundu! Saldıran ağır kayıp verdi (-150 💰, -50 ⚔️)."
                sonuc = 'savas_kaybetti'
            else:
                # İkisi de bildi veya ikisi de bilemedi: ZAR (ŞANS) SİSTEMİ
                if random.random() > 0.5:
                    onceki_sahip = self.secilen_bolge.sahip
                    self.aktif_oyuncu.kaynak_guncelle(altin_farki=100, asker_farki=-30)
                    self.savas_savunan.kaynak_guncelle(altin_farki=-50, asker_farki=-30)
                    
                    self.secilen_bolge.fethedeldi(self.aktif_oyuncu, asker=10)
                    self.aktif_oyuncu.bolge_fethetti()
                    self.aktif_oyuncu.savasi_kazandi()
                    self.durum_mesaji = f"🎲 Şans faktörü! İki ordu da yoruldu ama {self.aktif_oyuncu.ad} toprağı aldı!"
                    self._eleme_kontrol_oyuncu(onceki_sahip)
                    sonuc = 'savas_kazandi'
                else:
                    self.aktif_oyuncu.kaynak_guncelle(altin_farki=-100, asker_farki=-40)
                    self.savas_savunan.kaynak_guncelle(altin_farki=50, asker_farki=-20)
                    
                    self.savas_savunan.savasi_kazandi()
                    self.durum_mesaji = f"🎲 Şans faktörü! {self.savas_savunan.ad} son anda savunmayı başardı!"
                    sonuc = 'savas_kaybetti'

        self.mevcut_soru = None
        self.secilen_bolge = None
        self.savas_savunan = None

        if self._kazanan_var_mi():
            self.oyunu_bitir()
            return sonuc

        if not self.bos_bolgeler_var_mi():
            self.faz = self.FAZ_SAVAS
        else:
            self.faz = self.FAZ_FETIH

        return sonuc

    def oyuncunun_bolgelerini_getir(self, oyuncu):
        return [bid for bid, b in self.bolgeler.items() if b.sahip == oyuncu]

    def _eleme_kontrol(self):
        for oyuncu in self.oyuncular:
            if not oyuncu.elendi:
                bolge_sayisi = len(self.oyuncunun_bolgelerini_getir(oyuncu))
                # YENİ KURAL: Toprağı kalmayan VEYA (Askeri < 10 ve Altını < 50) olan elenir
                if (bolge_sayisi == 0 and self.tur > 2) or (oyuncu.asker < 10 and oyuncu.altin < 50):
                    self._oyuncuyu_ele(oyuncu)

    def _eleme_kontrol_oyuncu(self, oyuncu):
        if oyuncu and not oyuncu.elendi:
            bolge_sayisi = len(self.oyuncunun_bolgelerini_getir(oyuncu))
            if bolge_sayisi == 0 or (oyuncu.asker < 10 and oyuncu.altin < 50):
                self._oyuncuyu_ele(oyuncu)

    def _oyuncuyu_ele(self, oyuncu):
        """YENİ: Oyuncuyu eler ve topraklarını 'Boş/İsyancı' statüsüne geçirir."""
        oyuncu.elendi = True
        oyuncu.altin = 0
        oyuncu.asker = 0
        
        # İmparatorluk Çöküşü: Oyuncunun tüm bölgeleri bağımsızlığını ilan eder
        kendi_bolgeleri = self.oyuncunun_bolgelerini_getir(oyuncu)
        for bid in kendi_bolgeleri:
            self.bolgeler[bid].sahip = None
            self.bolgeler[bid].asker_sayisi = 0
            
        print(f"[İMPARATORLUK ÇÖKTÜ] {oyuncu.ad} yıkıldı! Tüm toprakları sahipsiz kaldı.")
        self.durum_mesaji = f"🏴 {oyuncu.ad} çöktü! Topraklarında isyan çıktı ve sahipsiz kaldı."

    def _kazanan_var_mi(self):
        aktifler = [o for o in self.oyuncular if not o.elendi]
        return len(aktifler) == 1

    def oyunu_bitir(self):
        aktifler = [o for o in self.oyuncular if not o.elendi]
        if aktifler:
            self.kazanan = max(aktifler, key=lambda o: len(self.oyuncunun_bolgelerini_getir(o)))
        else:
            self.kazanan = max(self.oyuncular, key=lambda o: o.skor)

        self.faz = self.FAZ_OYUN_BITTI

    def durum_mesajini_guncelle(self):
        self.durum_mesaji = f"🗺️ {self.aktif_oyuncu.ad}'ın sırası — Boş bir toprağa VEYA sınır komşusu düşmana saldır!"

    def bot_hamlesi_yap(self):
        bot = self.aktif_oyuncu
        if not bot.bot:
            return None

        bos = [bid for bid, b in self.bolgeler.items() if b.sahip is None]
        kendi_bolgeleri = self.oyuncunun_bolgelerini_getir(bot)

        hedefler = set()
        for kb in kendi_bolgeleri:
            for komsu_id in self.bolgeler[kb].komsu_idler:
                if self.bolgeler[komsu_id].sahip != bot:
                    hedefler.add(komsu_id)

        # Bot Mantığı: Eğer askeri gücü varsa ve komşusu varsa %40 ihtimalle direkt rakibe saldırır (Agresif Bot)
        if hedefler and (not bos or (bot.asker > 150 and random.random() < 0.40)):
            return random.choice(list(hedefler))
        
        # Yoksa veya şans tutmadıysa boş yerleri alır
        if bos:
            return random.choice(bos)

        # Hamle yapacak hiçbir yer yoksa (çok nadir)
        return None

    def istatistikleri_getir(self):
        ozet = []
        for oyuncu in self.oyuncular:
            bolge_sayisi = len(self.oyuncunun_bolgelerini_getir(oyuncu))
            ozet.append({
                "ad": oyuncu.ad,
                "renk": oyuncu.renk_adi,
                "skor": oyuncu.skor,
                "bolge": bolge_sayisi,
                "savas": oyuncu.kazanilan_savas,
                "dogru_cevap": oyuncu.dogru_cevap_sayisi,
                "elendi": oyuncu.elendi
            })
        return ozet