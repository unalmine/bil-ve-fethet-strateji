"""
================================================================
BİL VE FETHET - Veritabanı Yönetim Modülü
================================================================
Bu modül SQLite veritabanı işlemlerini yönetir.
Skor tablosu, maç geçmişi ve oyuncu istatistiklerini saklar.
================================================================
"""

import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """Oyun veritabanı işlemlerini yöneten ana sınıf."""

    def __init__(self, db_path="skorlar.db"):
        """
        Veritabanı bağlantısını başlatır ve tabloları oluşturur.
        :param db_path: SQLite veritabanı dosyasının yolu
        """
        self.db_path = db_path
        self.baglanti = None
        self.veritabani_olustur()

    def baglan(self):
        """Veritabanına bağlantı açar."""
        self.baglanti = sqlite3.connect(self.db_path)
        self.baglanti.row_factory = sqlite3.Row  # Sonuçları dict gibi kullanmak için
        return self.baglanti.cursor()

    def baglantiyi_kapat(self):
        """Veritabanı bağlantısını güvenli şekilde kapatır."""
        if self.baglanti:
            self.baglanti.commit()
            self.baglanti.close()
            self.baglanti = None

    def veritabani_olustur(self):
        """
        Gerekli tüm tabloları oluşturur.
        Eğer tablolar zaten varsa, üzerine yazmaz.
        """
        cursor = self.baglan()

        # --- Oyuncu skorları tablosu ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oyuncu_skorlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oyuncu_adi TEXT NOT NULL,
                renk TEXT NOT NULL,
                skor INTEGER DEFAULT 0,
                fethedilen_bolge INTEGER DEFAULT 0,
                kazanilan_savas INTEGER DEFAULT 0,
                dogru_cevap INTEGER DEFAULT 0,
                oyun_tarihi TEXT NOT NULL
            )
        """)

        # --- Maç geçmişi tablosu ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mac_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kazanan_oyuncu TEXT NOT NULL,
                kazanan_renk TEXT NOT NULL,
                toplam_tur INTEGER DEFAULT 0,
                oyun_tarihi TEXT NOT NULL,
                sure_saniye INTEGER DEFAULT 0
            )
        """)

        # --- En yüksek skorlar tablosu (Leaderboard) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS en_yuksek_skorlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oyuncu_adi TEXT NOT NULL,
                en_yuksek_skor INTEGER DEFAULT 0,
                toplam_mac INTEGER DEFAULT 0,
                toplam_galibiyet INTEGER DEFAULT 0,
                son_oynama TEXT NOT NULL
            )
        """)

        self.baglantiyi_kapat()
        print(f"[DB] Veritabanı hazır: {self.db_path}")

    def oyun_sonucunu_kaydet(self, oyuncular, kazanan, toplam_tur, sure_saniye=0):
        """
        Oyun bitiminde tüm oyuncu verilerini ve maç sonucunu kaydeder.
        :param oyuncular: Oyuncu nesnelerinin listesi
        :param kazanan: Kazanan oyuncu nesnesi
        :param toplam_tur: Toplam oynanan tur sayısı
        :param sure_saniye: Oyunun toplam süresi (saniye)
        """
        cursor = self.baglan()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Her oyuncunun skorunu kaydet
        for oyuncu in oyuncular:
            cursor.execute("""
                INSERT INTO oyuncu_skorlari 
                (oyuncu_adi, renk, skor, fethedilen_bolge, kazanilan_savas, dogru_cevap, oyun_tarihi)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                oyuncu.ad,
                oyuncu.renk_adi,
                oyuncu.skor,
                oyuncu.fethedilen_bolge_sayisi,
                oyuncu.kazanilan_savas,
                oyuncu.dogru_cevap_sayisi,
                tarih
            ))

        # Maç sonucunu kaydet
        cursor.execute("""
            INSERT INTO mac_gecmisi 
            (kazanan_oyuncu, kazanan_renk, toplam_tur, oyun_tarihi, sure_saniye)
            VALUES (?, ?, ?, ?, ?)
        """, (kazanan.ad, kazanan.renk_adi, toplam_tur, tarih, sure_saniye))

        # En yüksek skor tablosunu güncelle
        self._en_yuksek_skor_guncelle(cursor, kazanan, tarih)

        self.baglantiyi_kapat()
        print(f"[DB] Oyun sonucu kaydedildi. Kazanan: {kazanan.ad}")

    def _en_yuksek_skor_guncelle(self, cursor, kazanan, tarih):
        """
        Kazanan oyuncunun en yüksek skor tablosunu günceller.
        Oyuncu yoksa yeni kayıt oluşturur, varsa günceller.
        """
        # Oyuncu mevcut mu kontrol et
        mevcut = cursor.execute(
            "SELECT * FROM en_yuksek_skorlar WHERE oyuncu_adi = ?",
            (kazanan.ad,)
        ).fetchone()

        if mevcut:
            # Mevcut kaydı güncelle
            yeni_skor = max(mevcut['en_yuksek_skor'], kazanan.skor)
            cursor.execute("""
                UPDATE en_yuksek_skorlar 
                SET en_yuksek_skor = ?, toplam_mac = toplam_mac + 1,
                    toplam_galibiyet = toplam_galibiyet + 1, son_oynama = ?
                WHERE oyuncu_adi = ?
            """, (yeni_skor, tarih, kazanan.ad))
        else:
            # Yeni kayıt oluştur
            cursor.execute("""
                INSERT INTO en_yuksek_skorlar 
                (oyuncu_adi, en_yuksek_skor, toplam_mac, toplam_galibiyet, son_oynama)
                VALUES (?, ?, 1, 1, ?)
            """, (kazanan.ad, kazanan.skor, tarih))

    def skor_tablosunu_getir(self, limit=10):
        """
        En yüksek skorları döndürür.
        :param limit: Kaç kayıt getirileceği
        :return: Skor listesi (liste of dict)
        """
        cursor = self.baglan()
        sonuclar = cursor.execute("""
            SELECT oyuncu_adi, en_yuksek_skor, toplam_mac, 
                   toplam_galibiyet, son_oynama
            FROM en_yuksek_skorlar
            ORDER BY en_yuksek_skor DESC
            LIMIT ?
        """, (limit,)).fetchall()
        self.baglantiyi_kapat()
        return [dict(row) for row in sonuclar]

    def mac_gecmisini_getir(self, limit=10):
        """
        Son maç geçmişini döndürür.
        :param limit: Kaç maç getirileceği
        :return: Maç listesi
        """
        cursor = self.baglan()
        sonuclar = cursor.execute("""
            SELECT kazanan_oyuncu, kazanan_renk, toplam_tur, 
                   oyun_tarihi, sure_saniye
            FROM mac_gecmisi
            ORDER BY oyun_tarihi DESC
            LIMIT ?
        """, (limit,)).fetchall()
        self.baglantiyi_kapat()
        return [dict(row) for row in sonuclar]

    def en_cok_fetih_yapan(self):
        """
        Tüm zamanlarda en çok bölge fetheden oyuncuyu döndürür.
        :return: Oyuncu adı ve toplam fetih sayısı
        """
        cursor = self.baglan()
        sonuc = cursor.execute("""
            SELECT oyuncu_adi, SUM(fethedilen_bolge) as toplam_fetih
            FROM oyuncu_skorlari
            GROUP BY oyuncu_adi
            ORDER BY toplam_fetih DESC
            LIMIT 1
        """).fetchone()
        self.baglantiyi_kapat()
        if sonuc:
            return dict(sonuc)
        return None
