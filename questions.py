"""
================================================================
BİL VE FETHET - Soru Bankası Modülü
================================================================
Genel kültür sorularını kategorilere göre tutar.
Normal fetih soruları ve yüksek zorluktaki savaş soruları
ayrı kategorilerde saklanır.
================================================================
"""

import random


class SoruBankasi:
    """Oyundaki tüm soruları yöneten sınıf."""

    def __init__(self):
        """Soru bankasını başlatır ve soruları yükler."""
        self.normal_sorular = self._normal_sorulari_yukle()
        self.savas_sorulari = self._savas_sorularini_yukle()
        self.kullanilan_sorular = set()  # Tekrar aynı soru gelmesin

    def _normal_sorulari_yukle(self):
        """
        Fetih aşaması için normal zorlukta sorular.
        Her soru: {'soru': ..., 'secenekler': [...], 'dogru': 0-3 index, 'kategori': ...}
        """
        return [
            # --- COĞRAFİ BİLGİ ---
            {
                "soru": "Türkiye'nin başkenti hangi şehirdir?",
                "secenekler": ["İstanbul", "Ankara", "İzmir", "Bursa"],
                "dogru": 1,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Dünya'nın en büyük okyanusu hangisidir?",
                "secenekler": ["Atlantik", "Hint", "Arktik", "Pasifik"],
                "dogru": 3,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Nil Nehri hangi kıtada yer alır?",
                "secenekler": ["Asya", "Avrupa", "Afrika", "Amerika"],
                "dogru": 2,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Japonya'nın başkenti neresidir?",
                "secenekler": ["Osaka", "Kyoto", "Tokyo", "Hiroshima"],
                "dogru": 2,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Amazon Nehri hangi ülkeden geçer?",
                "secenekler": ["Arjantin", "Brezilya", "Şili", "Peru"],
                "dogru": 1,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Dünya'nın en yüksek dağı hangisidir?",
                "secenekler": ["K2", "Kangchenjunga", "Everest", "Lhotse"],
                "dogru": 2,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Hangi ülke yüzölçümü bakımından dünyada en büyüktür?",
                "secenekler": ["Çin", "ABD", "Kanada", "Rusya"],
                "dogru": 3,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Fransa'nın başkenti neresidir?",
                "secenekler": ["Berlin", "Paris", "Roma", "Madrid"],
                "dogru": 1,
                "kategori": "Coğrafya"
            },
            # --- TARİH ---
            {
                "soru": "Osmanlı İmparatorluğu hangi yılda kurulmuştur?",
                "secenekler": ["1071", "1299", "1453", "1517"],
                "dogru": 1,
                "kategori": "Tarih"
            },
            {
                "soru": "İstanbul'un fethinin tarihi nedir?",
                "secenekler": ["1453", "1071", "1299", "1683"],
                "dogru": 0,
                "kategori": "Tarih"
            },
            {
                "soru": "Dünya'nın ilk demokratik cumhuriyeti olarak kabul edilen ülke hangisidir?",
                "secenekler": ["İngiltere", "Fransa", "ABD", "Yunanistan"],
                "dogru": 2,
                "kategori": "Tarih"
            },
            {
                "soru": "Birinci Dünya Savaşı hangi yıl başlamıştır?",
                "secenekler": ["1912", "1914", "1916", "1918"],
                "dogru": 1,
                "kategori": "Tarih"
            },
            {
                "soru": "Atatürk hangi yılda Türkiye Cumhuriyeti'ni kurmuştur?",
                "secenekler": ["1920", "1921", "1922", "1923"],
                "dogru": 3,
                "kategori": "Tarih"
            },
            # --- BİLİM ---
            {
                "soru": "Suyun kimyasal formülü nedir?",
                "secenekler": ["CO2", "H2O", "NaCl", "O2"],
                "dogru": 1,
                "kategori": "Bilim"
            },
            {
                "soru": "Işığın boşluktaki hızı yaklaşık kaç km/s'dir?",
                "secenekler": ["100.000", "200.000", "300.000", "400.000"],
                "dogru": 2,
                "kategori": "Bilim"
            },
            {
                "soru": "Dünya'nın Güneş etrafındaki dönüş süresi kaç gündür?",
                "secenekler": ["300", "345", "365", "400"],
                "dogru": 2,
                "kategori": "Bilim"
            },
            {
                "soru": "DNA'nın açılımı nedir?",
                "secenekler": [
                    "Deoksiribonükleik Asit",
                    "Dinükleik Asit",
                    "Dioksit Nükleotit Asit",
                    "Direkt Nükleik Atom"
                ],
                "dogru": 0,
                "kategori": "Bilim"
            },
            {
                "soru": "Periyodik tabloda 'Au' simgesi hangi elementi temsil eder?",
                "secenekler": ["Gümüş", "Altın", "Alüminyum", "Argon"],
                "dogru": 1,
                "kategori": "Bilim"
            },
            # --- SANAT & KÜLTÜR ---
            {
                "soru": "Mona Lisa tablosunu kim yapmıştır?",
                "secenekler": ["Michelangelo", "Picasso", "Da Vinci", "Van Gogh"],
                "dogru": 2,
                "kategori": "Sanat"
            },
            {
                "soru": "Hamlet hangi yazarın eseridir?",
                "secenekler": ["Tolstoy", "Shakespeare", "Dickens", "Hugo"],
                "dogru": 1,
                "kategori": "Edebiyat"
            },
            {
                "soru": "Beethoven hangi ülkelidir?",
                "secenekler": ["Avusturya", "Fransa", "Almanya", "İtalya"],
                "dogru": 2,
                "kategori": "Sanat"
            },
            # --- SPOR ---
            {
                "soru": "FIFA Dünya Kupası kaç yılda bir düzenlenir?",
                "secenekler": ["2", "3", "4", "5"],
                "dogru": 2,
                "kategori": "Spor"
            },
            {
                "soru": "Olimpiyat oyunları ilk kez hangi şehirde düzenlenmiştir?",
                "secenekler": ["Roma", "Paris", "Atina", "Londra"],
                "dogru": 2,
                "kategori": "Spor"
            },
            {
                "soru": "Basketbolda bir sayı almak için atış kaç puan değerindedir?",
                "secenekler": ["1", "2", "3", "4"],
                "dogru": 1,
                "kategori": "Spor"
            },
            # --- EK SORULAR ---

{
    "soru": "Dünyanın en uzun nehri hangisidir?",
    "secenekler": ["Amazon", "Nil", "Yangtze", "Mississippi"],
    "dogru": 1,
    "kategori": "Coğrafya"
},
{
    "soru": "İtalya'nın başkenti neresidir?",
    "secenekler": ["Roma", "Milano", "Venedik", "Napoli"],
    "dogru": 0,
    "kategori": "Coğrafya"
},
{
    "soru": "Hangi gezegen 'Kızıl Gezegen' olarak bilinir?",
    "secenekler": ["Venüs", "Mars", "Jüpiter", "Satürn"],
    "dogru": 1,
    "kategori": "Bilim"
},
{
    "soru": "Einstein hangi teorisiyle ünlüdür?",
    "secenekler": ["Evrim", "Görelilik", "Kuantum", "Atom"],
    "dogru": 1,
    "kategori": "Bilim"
},
{
    "soru": "Türkiye'nin en kalabalık şehri hangisidir?",
    "secenekler": ["Ankara", "İzmir", "İstanbul", "Bursa"],
    "dogru": 2,
    "kategori": "Coğrafya"
},
{
    "soru": "Bir yılda kaç ay vardır?",
    "secenekler": ["10", "11", "12", "13"],
    "dogru": 2,
    "kategori": "Genel"
},
{
    "soru": "İnsan vücudunda kaç kemik vardır?",
    "secenekler": ["206", "150", "300", "180"],
    "dogru": 0,
    "kategori": "Bilim"
},
{
    "soru": "Hangi ülke piramitleri ile ünlüdür?",
    "secenekler": ["Meksika", "Peru", "Mısır", "Hindistan"],
    "dogru": 2,
    "kategori": "Tarih"
},
{
    "soru": "Ay'a ilk ayak basan insan kimdir?",
    "secenekler": ["Yuri Gagarin", "Neil Armstrong", "Buzz Aldrin", "Elon Musk"],
    "dogru": 1,
    "kategori": "Tarih"
},
{
    "soru": "En küçük asal sayı hangisidir?",
    "secenekler": ["1", "2", "3", "5"],
    "dogru": 1,
    "kategori": "Matematik"
},

# 50 tane daha hızlıca çoğaltıyorum ↓

{
    "soru": "Güneş bir nedir?",
    "secenekler": ["Gezegen", "Yıldız", "Uydu", "Asteroit"],
    "dogru": 1,
    "kategori": "Bilim"
},
{
    "soru": "Su kaç derecede kaynar?",
    "secenekler": ["90", "95", "100", "110"],
    "dogru": 2,
    "kategori": "Bilim"
},
{
    "soru": "Türkiye hangi kıtadadır?",
    "secenekler": ["Avrupa", "Asya", "Her ikisi", "Afrika"],
    "dogru": 2,
    "kategori": "Coğrafya"
},
{
    "soru": "En büyük memeli hangisidir?",
    "secenekler": ["Fil", "Zürafa", "Mavi Balina", "Köpek"],
    "dogru": 2,
    "kategori": "Bilim"
},
{
    "soru": "Satrançta kaç taş vardır?",
    "secenekler": ["16", "24", "32", "40"],
    "dogru": 2,
    "kategori": "Spor"
},
{
    "soru": "Dünya kaç kıtadan oluşur?",
    "secenekler": ["5", "6", "7", "8"],
    "dogru": 2,
    "kategori": "Coğrafya"
},
{
    "soru": "En hızlı kara hayvanı hangisidir?",
    "secenekler": ["Aslan", "Kaplan", "Çita", "At"],
    "dogru": 2,
    "kategori": "Bilim"
},
{
    "soru": "Türkiye'nin para birimi nedir?",
    "secenekler": ["Euro", "Dolar", "Lira", "Sterlin"],
    "dogru": 2,
    "kategori": "Genel"
},
{
    "soru": "Bir haftada kaç gün vardır?",
    "secenekler": ["5", "6", "7", "8"],
    "dogru": 2,
    "kategori": "Genel"
},
{
    "soru": "Hangi renk gökyüzünü temsil eder?",
    "secenekler": ["Kırmızı", "Mavi", "Yeşil", "Sarı"],
    "dogru": 1,
    "kategori": "Genel"
}
        ]

    def _savas_sorularini_yukle(self):
        """
        Savaş aşaması için yüksek zorluktaki sorular.
        Bu sorular daha spesifik ve zor bilgi gerektirir.
        """
        return [
            {
                "soru": "Hangi İmparator 'Rubicon'u geçerek Roma İç Savaşı'nı başlatmıştır?",
                "secenekler": ["Augustus", "Nero", "Julius Caesar", "Pompey"],
                "dogru": 2,
                "kategori": "Tarih"
            },
            {
                "soru": "Periyodik tabloda atom numarası 79 olan element hangisidir?",
                "secenekler": ["Platin", "Altın", "Gümüş", "Bakır"],
                "dogru": 1,
                "kategori": "Bilim"
            },
            {
                "soru": "Osmanlı'da 'Tanzimat Fermanı' hangi padişah döneminde ilan edilmiştir?",
                "secenekler": ["II. Mahmut", "Abdülmecid", "II. Abdülhamit", "III. Selim"],
                "dogru": 1,
                "kategori": "Tarih"
            },
            {
                "soru": "Kant'ın 'Saf Aklın Eleştirisi' hangi yılda yayımlanmıştır?",
                "secenekler": ["1761", "1771", "1781", "1791"],
                "dogru": 2,
                "kategori": "Felsefe"
            },
            {
                "soru": "Çift sarmal DNA yapısını ilk keşfeden bilim insanları kimlerdir?",
                "secenekler": [
                    "Darwin ve Mendel",
                    "Watson ve Crick",
                    "Pasteur ve Koch",
                    "Curie ve Einstein"
                ],
                "dogru": 1,
                "kategori": "Bilim"
            },
            {
                "soru": "Dünya'nın en derin okyanus çukuru hangisidir?",
                "secenekler": [
                    "Porto Riko Çukuru",
                    "Java Çukuru",
                    "Mariana Çukuru",
                    "Romanche Çukuru"
                ],
                "dogru": 2,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Hangi yılda Magna Carta imzalanmıştır?",
                "secenekler": ["1115", "1215", "1315", "1415"],
                "dogru": 1,
                "kategori": "Tarih"
            },
            {
                "soru": "Fibonacci dizisinde 13'ten sonra gelen sayı nedir?",
                "secenekler": ["18", "19", "20", "21"],
                "dogru": 3,
                "kategori": "Matematik"
            },
            {
                "soru": "Hangi element insan vücudunda en fazla bulunan metaldir?",
                "secenekler": ["Demir", "Kalsiyum", "Potasyum", "Sodyum"],
                "dogru": 1,
                "kategori": "Bilim"
            },
            {
                "soru": "Troçki, Stalin'e karşı mücadelede hangi ülkeye sürgüne gönderilmiştir?",
                "secenekler": ["Fransa", "İngiltere", "Meksika", "ABD"],
                "dogru": 2,
                "kategori": "Tarih"
            },
            {
                "soru": "Evrenin yaşı yaklaşık kaç milyar yıldır?",
                "secenekler": ["10.8", "12.4", "13.8", "15.2"],
                "dogru": 2,
                "kategori": "Bilim"
            },
            {
                "soru": "Sistine Şapeli'nin tavanını kim boyamıştır?",
                "secenekler": ["Leonardo da Vinci", "Raphael", "Donatello", "Michelangelo"],
                "dogru": 3,
                "kategori": "Sanat"
            },
            # --- YENİ EKLENEN 10 SORU ---
            {
                "soru": "Güneş sistemindeki en büyük gezegen hangisidir?",
                "secenekler": ["Mars", "Satürn", "Jüpiter", "Venüs"],
                "dogru": 2,
                "kategori": "Bilim"
            },
            {
                "soru": "Türkiye'nin yüzölçümü bakımından en büyük gölü hangisidir?",
                "secenekler": ["Tuz Gölü", "Eğirdir Gölü", "Beyşehir Gölü", "Van Gölü"],
                "dogru": 3,
                "kategori": "Coğrafya"
            },
            {
                "soru": "İstiklal Marşı'nın şairi kimdir?",
                "secenekler": ["Mehmet Akif Ersoy", "Namık Kemal", "Tevfik Fikret", "Yahya Kemal"],
                "dogru": 0,
                "kategori": "Edebiyat"
            },
            {
                "soru": "İnsan vücudundaki en büyük organ hangisidir?",
                "secenekler": ["Kalp", "Karaciğer", "Deri", "Akciğer"],
                "dogru": 2,
                "kategori": "Bilim"
            },
            {
                "soru": "Aspirinin ana hammaddesi hangi ağaçtan elde edilir?",
                "secenekler": ["Meşe", "Çam", "Kavak", "Söğüt"],
                "dogru": 3,
                "kategori": "Bilim"
            },
            {
                "soru": "Ünlü 'Sefiller' romanının yazarı kimdir?",
                "secenekler": ["Victor Hugo", "Lev Tolstoy", "Dostoyevski", "Charles Dickens"],
                "dogru": 0,
                "kategori": "Edebiyat"
            },
            {
                "soru": "Telefonun icadı kime aittir?",
                "secenekler": ["Thomas Edison", "Nikola Tesla", "Alexander Graham Bell", "Guglielmo Marconi"],
                "dogru": 2,
                "kategori": "Tarih"
            },
            {
                "soru": "Tarihte bilinen ilk yazılı antlaşma olan Kadeş Antlaşması kimler arasında imzalanmıştır?",
                "secenekler": ["Mısırlılar - Hititler", "Sümerler - Akadlar", "Romalılar - Kartacalılar", "Yunanlar - Persler"],
                "dogru": 0,
                "kategori": "Tarih"
            },
            {
                "soru": "Türkiye'nin en yüksek dağı hangisidir?",
                "secenekler": ["Erciyes Dağı", "Süphan Dağı", "Ağrı Dağı", "Kaçkar Dağı"],
                "dogru": 2,
                "kategori": "Coğrafya"
            },
            {
                "soru": "Basketbol maçlarında her iki takımın sahada kaçar oyuncusu bulunur?",
                "secenekler": ["4", "5", "6", "7"],
                "dogru": 1,
                "kategori": "Spor"
            }
        ]

    def rastgele_soru_getir(self, savas_modu=False):
        """
        Rastgele bir soru döndürür. Aynı soru tekrar gelmez.
        :param savas_modu: True ise zor savaş sorusu, False ise normal soru
        :return: Soru dict'i
        """
        havuz = self.savas_sorulari if savas_modu else self.normal_sorular

        # Kullanılmayan soruları filtrele
        kullanilmayanlar = [
            i for i, s in enumerate(havuz)
            if (savas_modu, i) not in self.kullanilan_sorular
        ]

        # Eğer tüm sorular kullanıldıysa sıfırla
        if not kullanilmayanlar:
            self.kullanilan_sorular = {k for k in self.kullanilan_sorular if k[0] != savas_modu}
            kullanilmayanlar = list(range(len(havuz)))

        # Rastgele soru seç
        index = random.choice(kullanilmayanlar)
        self.kullanilan_sorular.add((savas_modu, index))
        return havuz[index].copy()

    def soru_sayisi(self, savas_modu=False):
        """Soru havuzundaki toplam soru sayısını döndürür."""
        if savas_modu:
            return len(self.savas_sorulari)
        return len(self.normal_sorular)
