# ⚔️ Bil ve Fethet: Strateji ve Bilgi Savaşı

Bu proje, klasik bir trivia (bilgi yarışması) oyununu derinlemesine bir dünya hakimiyeti stratejisiyle birleştiren, Python ve Pygame kullanılarak geliştirilmiş bir masaüstü oyunudur. 

## 🚀 Temel Özellikler

* **Dinamik Harita Sistemi:** Yuvarlak node yapısıyla birbirine bağlı, stratejik öneme sahip bölgelerden oluşan dünya haritası.
* **Ekonomi ve Lojistik:** * **Altın (Para):** Doğru cevaplarla kazanılan, ordu kurmak için kullanılan temel kaynak.
    * **Asker Gücü:** Saldırı ve savunma için kritik öneme sahip askeri birimler.
* **Erken PvP Mekaniği:** Boş bölgelerin bitmesini beklemeden sınır komşusu olan rakiplere doğrudan saldırı imkanı.
* **Gelişmiş Yapay Zeka:** Kendi stratejisini belirleyen, toprak fetheden ve agresif hamleler yapabilen botlar.
* **İmparatorluk Çöküşü:** Ekonomisi veya ordusu tamamen biten oyuncuların topraklarının isyan ederek tarafsız (gri) hale gelmesi.
* **Ses Desteği:** Epik arka plan müzikleri ve aksiyon efektleri.

## 🕹️ Nasıl Oynanır?

1.  **Başlangıç:** Oyun başında her oyuncu (insan ve botlar) zar atarak sıralamasını belirler.
2.  **Fetih:** Boş bir toprağa tıklayın ve gelen soruyu doğru cevaplayarak sınırlarınızı genişletin.
3.  **Savaş:** Komşu bir rakip toprağına tıklayarak savaş başlatın. Siz ve rakibiniz aynı soruya cevap verirsiniz; daha hızlı ve doğru cevap veren toprağı alır.
4.  **İkmal:** Altınınız biriktiğinde sol alt paneldeki **"Asker Satın Al"** butonuyla ordunuzu güçlendirin.
5.  **Galibiyet:** Haritanın tamamını ele geçiren veya 30 tur sonunda en yüksek puana ulaşan imparatorluk kazanır.

## 🛠️ Kurulum ve Çalıştırma

Bilgisayarınızda Python yüklü olduğundan emin olun, ardından terminale şu komutu girin:

```bash
pip install pygame
python main.py
