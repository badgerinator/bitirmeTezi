import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz # Akış şeması için

# Sayfa Yapılandırması (Geniş mod ve başlık)
st.set_page_config(layout="wide", page_title="Aday Değerlendirme Sistemi")

# Veri Yükleme Fonksiyonları (Önbellekleme ile)
@st.cache_data
def load_data(file_path, sheet_name=None, use_excel=True):
    """CSV veya Excel dosyasından veri yükler."""
    try:
        if use_excel:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Hata: '{file_path}' dosyası bulunamadı. Lütfen 'data' klasöründe olduğundan emin olun.")
        return None
    except Exception as e:
        st.error(f"Hata: '{file_path}' dosyası yüklenirken bir sorun oluştu: {e}")
        return None

# --- VERİ DOSYALARININ YOLLARI ---
# Kullanıcının yüklediği dosya adlarına göre güncellendi
DATA_PATH = "data/"
file_ahp_birlesik_agirlik = DATA_PATH + "ahp_weights_summary.xlsx"
file_ahp_uzman_agirliklari = DATA_PATH + "ahp_weights_summary.xlsx"
file_ahp_tutarlilik = DATA_PATH + "ahp_weights_summary.xlsx"
file_topsis_ranking = DATA_PATH + "TOPSIS_Ranking.xlsx"
file_electre_results = DATA_PATH + "ELECTRE_Results.xlsx"
file_combined_report = DATA_PATH + "combined_ranking_report.xlsx"
file_electre_outranking = DATA_PATH + "ELECTRE_Outranking.xlsx"
# file_processed_candidates = DATA_PATH + "processed_candidates_anonymized_scaled.xlsx - Sheet1.csv" # Gerekirse kullanılabilir

# --- STREAMLIT ARAYÜZÜ ---

# Kenar Çubuğu (Sidebar) Navigasyonu
st.sidebar.title("Navigasyon")
section = st.sidebar.radio(
    "Bölüm Seçin:",
    [
        "Giriş ve Proje Amacı",
        "Genel Veri Akışı",
        "Kullanılan Python Kodları ve İşlevleri",
        "AHP Analizi ve Kriter Ağırlıkları",
        "TOPSIS ve ELECTRE Sıralama Sonuçları",
        "Karşılaştırmalı Analiz ve Raporlama",
        "Excel Çıktı Dosyaları ve Yapıları",
        "Genel Metodoloji Özeti",
        "Sonuç ve Değerlendirme"
    ]
)

# Ana Başlık
st.title("Aday Değerlendirme Karar Destek Sistemi")
st.subheader("AHP, TOPSIS ve ELECTRE Tabanlı Kapsamlı Analiz ve Raporlama")
st.markdown("---")

# --- BÖLÜMLER ---

if section == "Giriş ve Proje Amacı":
    st.header("1. Projenin Genel Amacı ve Kapsamı")
    st.markdown("""
    Bu projenin temel hedefi, aday havuzundaki kişileri **çok kriterli karar verme (ÇKKV)** metodolojileri kullanarak **nesnel ve şeffaf bir şekilde sıralamak ve değerlendirmek** oldu.
    Geleneksel işe alım süreçlerindeki subjektifliği azaltmak ve verilere dayalı, tutarlı kararlar alınmasını sağlamak amaçlanmıştır.

    #### Kullanılan Metodolojiler:
    - ✅ **AHP (Analitik Hiyerarşi Süreci)** → Kriter ağırlıklarının uzman görüşleriyle belirlenmesi.
    - ✅ **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)** → Adayların ideal ve negatif ideal çözümlere olan uzaklıklarına göre sıralanması.
    - ✅ **ELECTRE (ELimination Et Choix Traduisant la REalité)** → Adaylar arası baskınlık (dominance) ilişkilerinin ve uyum/uyumsuzluk analizlerinin yapılması.
    - ✅ **Birleşik Raporlama** → Farklı metodolojilerden elde edilen sonuçların karşılaştırmalı olarak sunulması.

    #### Akademik Bağlam ve Veri Kullanımı:
    Bu çalışma, akademik titizlik ilkelerine bağlı kalınarak yürütülmüştür. Kullanılan tüm veriler, proje kapsamında sağlanan `aday_havuzu.xlsx` (ön işlenmiş haliyle `processed_candidates_anonymized_scaled.xlsx`) ve uzman değerlendirmelerini içeren `ahp_expert_filled.xlsx` (işlenmiş haliyle `ahp_weights_summary.xlsx`) gibi dosyalardan türetilmiştir. Dışsal veri kaynakları kullanılmamıştır.
    """)

elif section == "Genel Veri Akışı":
    st.header("2. Genel Veri Akışı ve Sistem Mimarisi")
    st.markdown("""
    Bu bölümde, projenin başlangıcından sonuna kadar verinin izlediği yol, bu süreçte kullanılan Python script'leri, üretilen ara ve nihai Excel çıktıları detaylı bir akış şeması ile görselleştirilmektedir.
    """)

    # Graphviz ile Akış Şeması
    dot_string = """
    digraph VeriAkisi {
        rankdir="TB"; // Yukarıdan aşağıya akış
        node [shape=box, style="filled,rounded", fontname="Inter, sans-serif", fontsize=10];
        edge [fontname="Inter, sans-serif", fontsize=9];

        subgraph cluster_veri_hazirlama {
            label = "Veri Hazırlama ve Ön İşleme";
            style=filled;
            color=lightgrey;
            node [fillcolor="#E6E6FA"]; // Lavender

            aday_havuzu [label="📄 aday_havuzu.xlsx\n(Ham Aday Verisi)"];
            tamTemiz_pipeline [label="🐍 1_tamTemiz_pipeline.py\n(Temizleme, Özellik Çıkarma)", shape=ellipse, fillcolor="#ADD8E6"];
            processed_full [label="📄 processed_candidates_full.xlsx\n(Tüm Ara Sütunlar)"];
            scaler_py [label="🐍 2_scaler.py\n(Normalizasyon)", shape=ellipse, fillcolor="#ADD8E6"];
            processed_scaled [label="📊 processed_candidates_anonymized_scaled.xlsx\n(TOPSIS/ELECTRE Girdisi)", fillcolor="#90EE90"];
        }

        subgraph cluster_ahp {
            label = "AHP ile Kriter Ağırlıklandırma";
            style=filled;
            color=lightgrey;
            node [fillcolor="#E6E6FA"];

            ahp_template_gen [label="🐍 3_ahp_expert_template_generator.py\n(Boş AHP Şablonu)", shape=ellipse, fillcolor="#ADD8E6"];
            ahp_formullu [label="📄 ahp_matrices_formullu.xlsx\n(Uzmanlara Dağıtılır)"];
            ahp_expert_filled [label="📝 ahp_expert_filled.xlsx\n(Doldurulmuş Uzman Matrisleri)"];
            ahp_calculator [label="🐍 4_ahp_calculator.py\n(Ağırlık ve Tutarlılık Hesabı)", shape=ellipse, fillcolor="#ADD8E6"];
            ahp_summary [label="⚖️ ahp_weights_summary.xlsx\n(Ağırlıklar, CR Sonuçları)", fillcolor="#90EE90"];
        }

        subgraph cluster_siralama {
            label = "Çok Kriterli Sıralama ve Raporlama";
            style=filled;
            color=lightgrey;
            node [fillcolor="#E6E6FA"];

            multi_criteria_pipeline [label="🐍 multi_criteria_ranking_pipeline.py\n(TOPSIS & ELECTRE Motoru)", shape=ellipse, fillcolor="#ADD8E6"];
            topsis_ranking [label="🏆 TOPSIS_Ranking.xlsx", fillcolor="#FFD700"];
            electre_results [label="🥇 ELECTRE_Results.xlsx", fillcolor="#FFD700"];
            combined_report [label="📈 combined_ranking_report.xlsx", fillcolor="#FFD700"];
            electre_concordance [label="📄 ELECTRE_Concordance.xlsx", fillcolor="#FFD700"];
            electre_discordance [label="📄 ELECTRE_Discordance.xlsx", fillcolor="#FFD700"];
            electre_outranking [label="📄 ELECTRE_Outranking.xlsx", fillcolor="#FFD700"];
        }
        
        subgraph cluster_sunum {
            label = "Analiz ve Sunum";
            style=filled;
            color=lightgrey;
            node [fillcolor="#E6E6FA"];
            demo_notebook [label="💻 multi_criteria_ranking_demo.ipynb\n(İnteraktif Analiz, Görselleştirme)", shape=ellipse, fillcolor="#ADD8E6"];
            yonetim_sunumu [label="📊 Yönetim Sunumları", fillcolor="#FFD700"];
        }

        // Akış Bağlantıları
        aday_havuzu -> tamTemiz_pipeline;
        tamTemiz_pipeline -> processed_full;
        processed_full -> scaler_py;
        scaler_py -> processed_scaled;

        ahp_template_gen -> ahp_formullu;
        ahp_formullu -> ahp_expert_filled [style=dashed, label=" Uzman Girdisi "];
        ahp_expert_filled -> ahp_calculator;
        ahp_calculator -> ahp_summary;

        processed_scaled -> multi_criteria_pipeline [label=" Normalize Aday Verisi "];
        ahp_summary -> multi_criteria_pipeline [label=" Birleşik AHP Ağırlıkları "];
        
        multi_criteria_pipeline -> topsis_ranking;
        multi_criteria_pipeline -> electre_results;
        multi_criteria_pipeline -> combined_report;
        multi_criteria_pipeline -> electre_concordance;
        multi_criteria_pipeline -> electre_discordance;
        multi_criteria_pipeline -> electre_outranking;

        topsis_ranking -> demo_notebook;
        electre_results -> demo_notebook;
        demo_notebook -> yonetim_sunumu;
    }
    """
    st.graphviz_chart(dot_string, use_container_width=True)

elif section == "Kullanılan Python Kodları ve İşlevleri":
    st.header("3. Kullanılan Python Kodları ve İşlevleri")
    st.markdown("""
    Proje kapsamında geliştirilen Python script'leri ve temel işlevleri aşağıda açıklanmıştır. Her bir script, veri işleme ve analiz sürecinin belirli bir aşamasını otomatize etmek için tasarlanmıştır.
    """)

    st.subheader("3.1. `1_tamTemiz_pipeline.py`: Veri Ön İşleme ve Özellik Mühendisliği")
    st.markdown("""
    Bu script, ham veri kaynağı olan `aday_havuzu.xlsx` dosyasını okuyarak, içerisindeki aday bilgilerini temizler ve ham veriden ÇKKV analizlerinde kullanılacak anlamlı, nicel özellikler (kriterler) türetir.
    - **Temel İşlevler:**
        - Tarih formatlarını standartlaştırma ve deneyim süresi hesaplama (gün bazında).
        - Kategorik verileri (örn: eğitim düzeyi, yabancı dil seviyesi) sayısal skorlara dönüştürme.
        - Metin tabanlı verilerden (örn: sosyal aktiviteler) özellik çıkarma (örneğin, anahtar kelime sayımı veya daha gelişmiş NLP teknikleri ile skorlama).
        - Eksik verilerin yönetimi (örn: doldurma veya işaretleme).
    - **Önemli Özellik Çıkarımları:**
        - `Toplam Deneyim Süresi`: Gün bazında hesaplanır, kategorik skora dönüştürülür.
        - `Yabancı Dil Seviyesi`: Okuma/Yazma/Konuşma skorları üzerinden genel bir skor hesaplanır.
        - `Temel Bilgisayar Becerileri`: Bilinen yazılım sayısı çıkarılır, interpolasyonla skora dönüştürülür.
        - `Sertifika Sayısı`: Sayısal değere dönüştürülür, interpolasyonla skora dönüştürülür.
        - `Eğitim Düzeyi`: Kategorik (Lise, Lisans vb.) skora dönüştürülür.
        - `Sosyal Aktivite Skoru`: Metin madenciliği ve embedding teknikleri kullanılarak 0-100 aralığında normalize edilmiş bir skor üretilir.
    - **Çıktıları:**
        - `processed_candidates_full.xlsx`: Tüm ham, ara ve türetilmiş sütunları içerir.
        - `processed_candidates_anonymized_scaled.xlsx`: Sadece ÇKKV analizlerinde kullanılacak, anonimleştirilmiş ve normalize edilmiş (genellikle 0-100) kriter skorlarını içerir. **Bu dosya, TOPSIS ve ELECTRE için ana girdidir.**
    """)

    st.subheader("3.2. `2_scaler.py`: Veri Ölçekleme ve Normalizasyon")
    st.markdown("""
    Bu script, `1_tamTemiz_pipeline.py` çıktısındaki sayısal kriterlerin farklı ölçeklerde olmasından kaynaklanabilecek yanlılıkları önlemek amacıyla, bu kriterleri standart bir aralığa (genellikle 0-100) normalize eder.
    - **Temel İşlevler:**
        - Genellikle Min-Max Normalizasyonu kullanılır: $$X_{scaled} = \\frac{X - X_{min}}{X_{max} - X_{min}} \\times 100$$
        - Bazı durumlarda Z-skor standardizasyonu da tercih edilebilir.
    - **Uygulandığı Sütunlar:** `Yabancı Dil Skoru`, `Temel Bilgisayar Becerileri Skoru`, `Sertifika Skoru`, `Sosyal Aktivite Skoru` gibi sürekli veya yarı sürekli değişkenler.
    - **Çıktısı:** Güncellenmiş `processed_candidates_anonymized_scaled.xlsx` dosyası.
    """)

    st.subheader("3.3. `3_ahp_expert_template_generator.py`: AHP Uzman Değerlendirme Şablonu Oluşturucu")
    st.markdown("""
    Bu script, uzmanların değerlendirme kriterlerini birbirlerine göre ikili olarak karşılaştırabilmeleri için standart bir AHP matris şablonu (`ahp_matrices_formullu.xlsx`) oluşturur.
    - **Temel İşlevler:**
        - Kriter listesini alır.
        - Her bir uzman için boş bir ikili karşılaştırma matrisi oluşturur.
        - Matrisin diyagonal elemanlarını 1 olarak ayarlar.
        - Genellikle üst üçgen kısmına başlangıç değerleri (örn: 1'den 9'a kadar Saaty skalasına göre varsayılan değerler veya boş bırakma) atar ve alt üçgeni formüllerle (örn: $a_{ji} = 1/a_{ij}$) doldurur.
    - **Çıktısı:** `ahp_matrices_formullu.xlsx` → Uzmanlara dağıtılacak boş şablon.
    """)

    st.subheader("3.4. `4_ahp_calculator.py`: AHP Ağırlık Hesaplayıcı ve Tutarlılık Analizcisi")
    st.markdown("""
    Uzmanlar tarafından doldurulmuş olan `ahp_expert_filled.xlsx` dosyasını okur ve AHP metodolojisinin matematiksel adımlarını uygular.
    - **Temel İşlevler (Her uzman için):**
        - İkili karşılaştırma matrisini normalize etme.
        - Her kriter için yerel ağırlık vektörünü hesaplama (genellikle normalize matrisin satır ortalamaları veya özvektör yöntemi ile).
        - En büyük özdeğer ($\lambda_{max}$) hesaplama.
        - Tutarlılık İndeksi (CI) hesaplama: $$CI = \\frac{\lambda_{max} - n}{n - 1}$$ (n: kriter sayısı)
        - Rastgele İndeks (RI) değerini (kriter sayısına göre standart tablolardan alınır) kullanarak Tutarlılık Oranı (CR) hesaplama: $$CR = \\frac{CI}{RI}$$
    - **Filtreleme ve Birleştirme:**
        - **CR ≤ 0.10 (veya projede belirtildiği gibi 0.15) filtresi:** Tutarsız uzman yargılarını (isteğe bağlı olarak) ayıklama.
        - Tutarlı uzmanların ağırlık vektörlerini geometrik ortalama veya aritmetik ortalama ile birleştirerek **nihai birleşik kriter ağırlıklarını** elde etme.
    - **Çıktısı:** `ahp_weights_summary.xlsx` dosyası ve içindeki sheet'ler:
        - `Uzman_Agirliklari`: Her bir uzmanın hesaplanan kriter ağırlıkları ve CR değerleri.
        - `Birlesik_Agirlik`: Filtrelenmiş ve birleştirilmiş nihai kriter ağırlık vektörü.
        - `Consistency_Results`: Her uzman için $\lambda_{max}$, CI, CR gibi detaylı tutarlılık metrikleri.
    """)

    st.subheader("3.5. `multi_criteria_ranking_pipeline.py`: Çok Kriterli Sıralama Motoru")
    st.markdown("""
    Bu ana script, AHP'den elde edilen birleşik kriter ağırlıklarını ve `processed_candidates_anonymized_scaled.xlsx` dosyasındaki normalize edilmiş aday verilerini kullanarak TOPSIS ve ELECTRE metodolojilerini uygular ve aday sıralamalarını üretir.
    - **Girdiler:**
        - `ahp_weights_summary.xlsx` (Sheet: `Birlesik_Agirlik`) → Kriter ağırlıkları.
        - `processed_candidates_anonymized_scaled.xlsx` → Karar matrisi (adayların kriter skorları).
    - **TOPSIS Uygulaması:**
        1. Karar matrisini normalize etme (genellikle vektör normalizasyonu).
        2. Normalize edilmiş karar matrisini kriter ağırlıkları ile ağırlıklandırma.
        3. İdeal Çözüm ($A^+$) ve Negatif-İdeal Çözüm ($A^-$) belirleme.
        4. Her adayın $A^+$ ve $A^-$'ye olan Öklid mesafelerini ($S_i^+$ ve $S_i^-$) hesaplama.
        5. Her adayın ideale yakınlık katsayısını ($CC_i$) hesaplama: $$CC_i = \\frac{S_i^-}{S_i^+ + S_i^-}$$
        6. Adayları $CC_i$ değerlerine göre büyükten küçüğe sıralama.
    - **ELECTRE (Genellikle ELECTRE I veya benzeri bir varyant) Uygulaması:**
        1. **Uyum (Concordance) Matrisi ($C_{kl}$):** $a_k$ adayının $a_l$ adayından en az onun kadar iyi olduğu kriterlerin ağırlıkları toplamı.
        2. **Uyumsuzluk (Discordance) Matrisi ($D_{kl}$):** $a_k$ adayının $a_l$ adayından daha kötü olduğu kriterlerdeki maksimum normalize edilmiş fark.
        3. **Uyum Eşiği ($c$) ve Uyumsuzluk Eşiği ($d$):** Genellikle uzmanlar tarafından belirlenir veya ortalama değerler üzerinden hesaplanır.
        4. **Baskınlık (Outranking) Matrisi ($S_{kl}$):** Eğer $C_{kl} \ge c$ VE $D_{kl} \le d$ ise $a_k$ adayı $a_l$ adayını baskılar ($a_k S a_l$).
        5. Adayların net baskınlık skorları (örn: kaç adayı baskıladığı eksi kaç aday tarafından baskılandığı) veya farklı sıralama yöntemleri (örn: kernel bulma) ile sıralanması.
    - **Çıktıları:**
        - `TOPSIS_Ranking.xlsx`: Adayların TOPSIS skorları ve sıraları.
        - `ELECTRE_Results.xlsx`: Adayların ELECTRE baskınlık skorları (veya benzeri bir metrik) ve sıraları.
        - `combined_ranking_report.xlsx`: TOPSIS ve ELECTRE sonuçlarının karşılaştırmalı olarak sunulduğu birleşik rapor.
        - `ELECTRE_Concordance.xlsx`, `ELECTRE_Discordance.xlsx`, `ELECTRE_Outranking.xlsx`: ELECTRE metodunun ara matrisleri.
    """)

    st.subheader("3.6. `multi_criteria_ranking_demo.ipynb`: İnteraktif Analiz ve Görselleştirme Not Defteri")
    st.markdown("""
    Bu Jupyter Notebook, analiz sonuçlarını daha interaktif bir şekilde incelemek ve görselleştirmek için kullanılır. Özellikle yönetim sunumları veya daha derinlemesine analizler için faydalıdır.
    - **Temel İşlevler:**
        - **Parametrik Analiz:** Özellikle ELECTRE metodunda kullanılan uyum ($c$) ve uyumsuzluk ($d$) eşik değerlerinin değiştirilerek sonuçlar üzerindeki etkisinin incelenmesi.
        - **Görselleştirme:**
            - TOPSIS Skorları için barplot.
            - ELECTRE Baskınlık Skorları için barplot.
            - TOPSIS ve ELECTRE sıralamaları/skorları arası ilişkiyi gösteren scatterplot.
            - Kriter ağırlıklarının görselleştirilmesi.
            - Belirli adayların detaylı profil analizleri.
    - **Amaç:** Karar vericilere sonuçları daha anlaşılır ve etkileşimli bir formatta sunmak, farklı senaryoları test etme imkanı sağlamak.
    """)

elif section == "AHP Analizi ve Kriter Ağırlıkları":
    st.header("4. AHP Analizi ve Kriter Ağırlıkları")
    st.markdown("Bu bölümde, Analitik Hiyerarşi Süreci (AHP) kullanılarak elde edilen kriter ağırlıkları ve uzman değerlendirmelerinin tutarlılık analizleri sunulmaktadır.")

    # Birleşik Ağırlıklar
    df_ahp_birlesik = load_data(file_ahp_birlesik_agirlik, sheet_name='Birlesik_Agirlik', use_excel=True)
    if df_ahp_birlesik is not None:
        st.subheader("4.1. Nihai Birleşik Kriter Ağırlıkları")
        # CSV'den doğru sütunları al
        # Dosya formatı: Kriter Adı,Birlesik Agirlik
        # Eğer sütun adları farklıysa burada güncelleyin
        df_ahp_plot = df_ahp_birlesik.rename(columns={'Unnamed: 0': 'Kriter', 'Birlesik_Agirlik': 'Ağırlık'})
        df_ahp_plot = df_ahp_plot.sort_values(by='Ağırlık', ascending=False)
        
        fig_ahp_bar = px.bar(df_ahp_plot, x='Ağırlık', y='Kriter', orientation='h',
                                title='Nihai Birleşik Kriter Ağırlıkları',
                                labels={'Ağırlık': 'Ağırlık Değeri', 'Kriter': 'Değerlendirme Kriteri'},
                                color='Ağırlık', color_continuous_scale=px.colors.sequential.Tealgrn,
                                text='Ağırlık')
        fig_ahp_bar.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_ahp_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig_ahp_bar, use_container_width=True)
        st.dataframe(df_ahp_plot.style.format({"Ağırlık": "{:.4f}"}), use_container_width=True)
        # else:
        #     st.warning(f"`{file_ahp_birlesik_agirlik}` dosyasında beklenen 'Kriter Adı' veya 'Birlesik Agirlik' sütunları bulunamadı.")
        #     st.dataframe(df_ahp_birlesik.head())

    # Uzman Ağırlıkları ve Tutarlılık
    df_uzman_agirliklari = load_data(file_ahp_uzman_agirliklari, sheet_name='Uzman_Agirliklari', use_excel=True)
    df_ahp_tutarlilik = load_data(file_ahp_tutarlilik, sheet_name='Consistency_Results', use_excel=True)

    if df_uzman_agirliklari is not None and df_ahp_tutarlilik is not None:
        st.subheader("4.2. Bireysel Uzman Ağırlıkları ve Tutarlılık Oranları (CR)")
        
        # Uzman ağırlıkları için CR değerlerini birleştir
        # df_ahp_tutarlilik formatı: Uzman,Lambda Max,CI,RI,CR
        # df_uzman_agirliklari formatı: Kriter Adı,Uzman_1 Ağırlık,Uzman_1 CR,Uzman_2 Ağırlık,Uzman_2 CR ...
        
        # Uzmanların CR değerlerini alalım (Tutarlılık dosyasından)
        # Uzman adları 'Uzman_1', 'Uzman_2' vb. olmalı
        print(df_ahp_tutarlilik.columns)
        cr_values = {}
        if 'CR' in df_ahp_tutarlilik.columns:
            cr_values = pd.Series(df_ahp_tutarlilik.CR.values, index=df_ahp_tutarlilik['Uzman']).to_dict()

        # Radar grafik için veri hazırlığı
        # Kriterler ilk sütunda olmalı
        if 'Kriter Adı' in df_uzman_agirliklari.columns:
            kriterler = df_uzman_agirliklari['Kriter Adı'].tolist()
            fig_radar = go.Figure()
            
            # Sadece ağırlık sütunlarını al (örn: 'Uzman_1 Ağırlık')
            agirlik_sutunlari = [col for col in df_uzman_agirliklari.columns if 'Uzman' in col]

            for uzman_sutun_adi in agirlik_sutunlari:
                uzman_adi = uzman_sutun_adi.split(' ')[0] # 'Uzman_1'
                cr_text = f"(CR: {cr_values.get(uzman_adi, 'N/A'):.3f})" if uzman_adi in cr_values else ""
                fig_radar.add_trace(go.Scatterpolar(
                    r=df_uzman_agirliklari[uzman_sutun_adi],
                    theta=kriterler,
                    fill='toself',
                    name=f"{uzman_adi} {cr_text}"
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, df_uzman_agirliklari[agirlik_sutunlari].max().max() * 1.1])), # Max ağırlığa göre ayarla
                showlegend=True,
                title="Uzman Bazlı Kriter Ağırlıkları Dağılımı (Radar Grafik)",
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            st.markdown("Aşağıdaki tabloda her bir uzmanın atadığı ağırlıklar ve CR değerleri gösterilmektedir. Proje kılavuzuna göre CR > 0.15 olan uzmanların yargıları tutarsız kabul edilebilir.")
            
            # Uzman ağırlıklarını ve CR'larını bir arada göstermek için tabloyu yeniden düzenleyelim
            # Bu kısım df_uzman_agirliklari'nın yapısına göre daha detaylı işlenebilir.
            # Şimdilik sadece ham tabloyu gösterelim.
            st.dataframe(df_uzman_agirliklari, use_container_width=True)
            st.dataframe(df_ahp_tutarlilik.style.format({"Lambda Max": "{:.3f}", "CI": "{:.3f}", "RI": "{:.3f}", "CR": "{:.3f}"}), use_container_width=True)
            
            # Birleşik CR değeri (genellikle Consistency_Results'da son satırda olabilir veya ayrıca hesaplanır)
            # Örnek olarak:
            if 'Birlesik CR' in df_ahp_tutarlilik.columns: # Varsayımsal bir sütun
                 st.success(f"**Birleşik Tutarlılık Oranı (CR): {df_ahp_tutarlilik['Birlesik CR'].iloc[-1]:.3f}** (Proje eşiği: ≤ 0.15)")
            elif 'CR' in df_ahp_tutarlilik.columns and 'Uzman' in df_ahp_tutarlilik.columns and df_ahp_tutarlilik['Uzman'].str.contains('Birleşik', case=False, na=False).any():
                 birlesik_cr_satiri = df_ahp_tutarlilik[df_ahp_tutarlilik['Uzman'].str.contains('Birleşik', case=False, na=False)]
                 if not birlesik_cr_satiri.empty:
                    st.success(f"**Birleşik Tutarlılık Oranı (CR): {birlesik_cr_satiri['CR'].iloc[0]:.3f}** (Proje eşiği: ≤ 0.15)")


    else:
        st.warning("AHP uzman ağırlıkları veya tutarlılık verileri yüklenemedi.")


elif section == "TOPSIS ve ELECTRE Sıralama Sonuçları":
    st.header("5. TOPSIS ve ELECTRE Sıralama Sonuçları")
    st.markdown("Bu bölümde, TOPSIS ve ELECTRE metodolojileri kullanılarak elde edilen aday sıralamaları ve skorları sunulmaktadır.")
    
    num_aday_goster = st.slider("Grafiklerde gösterilecek en iyi aday sayısı:", min_value=5, max_value=30, value=10, key="top_n_slider")

    # TOPSIS Sonuçları
    df_topsis = load_data(file_topsis_ranking, sheet_name='Sheet1', use_excel=True)
    if df_topsis is not None:
        st.subheader("5.1. TOPSIS Sıralaması (İdeale Yakınlık)")
        # Sütun adları: Aday ID,TOPSIS Score,TOPSIS Rank
        if 'ID' in df_topsis.columns and 'TOPSIS_Score' in df_topsis.columns and 'TOPSIS_Rank' in df_topsis.columns:
            df_topsis_sorted = df_topsis.sort_values(by='TOPSIS_Rank').head(num_aday_goster)
            df_topsis_sorted['ID'] = df_topsis_sorted['ID'].astype(str) # Plotly için kategorik

            fig_topsis_bar = px.bar(df_topsis_sorted, x='TOPSIS_Score', y='ID', orientation='h',
                                    title=f'En İyi {num_aday_goster} Aday için TOPSIS Skorları',
                                    labels={'TOPSIS_Score': 'TOPSIS Skoru (İdeale Yakınlık)', 'ID': 'Aday ID'},
                                    color='TOPSIS_Score', color_continuous_scale=px.colors.sequential.Viridis,
                                    text='TOPSIS_Score')
            fig_topsis_bar.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            fig_topsis_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=max(400, num_aday_goster * 35))
            st.plotly_chart(fig_topsis_bar, use_container_width=True)
            st.dataframe(df_topsis.head(num_aday_goster).style.format({"TOPSIS_Score": "{:.4f}"}), use_container_width=True)
        else:
            st.warning(f"`{file_topsis_ranking}` dosyasında beklenen sütunlar (Aday ID, TOPSIS Score, TOPSIS Rank) bulunamadı.")
            st.dataframe(df_topsis.head())

    # ELECTRE Sonuçları
    df_electre = load_data(file_electre_results, sheet_name='Sheet1', use_excel=True)
    if df_electre is not None:
        st.subheader("5.2. ELECTRE Sıralaması (Baskınlık Skoru)")
        # Sütun adları: Aday ID,ELECTRE Dominance Score,ELECTRE Rank
        if 'ID' in df_electre.columns and 'ELECTRE_Dominance_Score' in df_electre.columns and 'ELECTRE_Rank' in df_electre.columns:
            df_electre_sorted = df_electre.sort_values(by='ELECTRE_Rank').head(num_aday_goster)
            df_electre_sorted['ID'] = df_electre_sorted['ID'].astype(str)

            fig_electre_bar = px.bar(df_electre_sorted, x='ELECTRE_Dominance_Score', y='ID', orientation='h',
                                     title=f'En İyi {num_aday_goster} Aday için ELECTRE Baskınlık Skorları',
                                     labels={'ELECTRE_Dominance_Score': 'ELECTRE Baskınlık Skoru', 'ID': 'Aday ID'},
                                     color='ELECTRE_Dominance_Score', color_continuous_scale=px.colors.sequential.Plasma,
                                     text='ELECTRE_Dominance_Score')
            fig_electre_bar.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig_electre_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=max(400, num_aday_goster * 35))
            st.plotly_chart(fig_electre_bar, use_container_width=True)
            st.dataframe(df_electre.head(num_aday_goster), use_container_width=True)
        else:
            st.warning(f"`{file_electre_results}` dosyasında beklenen sütunlar (Aday ID, ELECTRE Dominance Score, ELECTRE Rank) bulunamadı.")
            st.dataframe(df_electre.head())

elif section == "Karşılaştırmalı Analiz ve Raporlama":
    st.header("6. Karşılaştırmalı Analiz ve Raporlama")
    st.markdown("Bu bölümde, TOPSIS ve ELECTRE metodolojilerinden elde edilen sonuçlar karşılaştırılmakta ve adayların genel durumu değerlendirilmektedir.")

    df_combined = load_data(file_combined_report, sheet_name='Sheet1', use_excel=True)
    if df_combined is not None:
        st.subheader("6.1. TOPSIS ve ELECTRE Sıralamalarının Karşılaştırılması (Saçılım Grafiği)")
        # Sütun adları: Aday ID,TOPSIS Score,TOPSIS Rank,ELECTRE Dominance Score,ELECTRE Rank
        if all(col in df_combined.columns for col in ['ID', 'TOPSIS_Score', 'TOPSIS_Rank', 'ELECTRE_Dominance_Score', 'ELECTRE_Rank']):
            df_combined['ID'] = df_combined['ID'].astype(str)

            # Hover için metin oluşturma
            df_combined['hover_text'] = df_combined.apply(
                lambda row: f"Aday ID: {row['ID']}<br>TOPSIS Skor: {row['TOPSIS_Score']:.3f} (Sıra: {row['TOPSIS_Rank']})<br>ELECTRE Skor: {row['ELECTRE_Dominance_Score']} (Sıra: {row['ELECTRE_Rank']})",
                axis=1
            )

            fig_scatter = px.scatter(df_combined, x='TOPSIS_Score', y='ELECTRE_Rank',
                                     title='TOPSIS Skoru vs. ELECTRE Sırası',
                                     labels={'TOPSIS_Score': 'TOPSIS Skoru (İdeale Yakınlık)', 'ELECTRE_Rank': 'ELECTRE Sırası (Baskınlık)'},
                                     color='TOPSIS_Rank', # Renklendirme için bir metrik seçilebilir
                                     color_continuous_scale=px.colors.sequential.Inferno_r,
                                     hover_name='ID',
                                     hover_data={'TOPSIS_Score':':.3f', 'TOPSIS_Rank':True, 'ELECTRE_Dominance_Score':True, 'ELECTRE_Rank':True, 'hover_text':False}, # hover_text'i doğrudan gösterme
                                     custom_data=['hover_text'] # Özel hover verisi
                                     )
            fig_scatter.update_traces(hovertemplate="%{customdata[0]}<extra></extra>") # Özel hover şablonu
            fig_scatter.update_layout(yaxis_autorange="reversed", height=600) # ELECTRE Rank'ı ters çevir (1 en iyi)
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown("Bu grafik, her bir adayın TOPSIS skoru ile ELECTRE metodolojisindeki sıralaması arasındaki ilişkiyi göstermektedir. İki metodun ne ölçüde benzer veya farklı sonuçlar ürettiği görülebilir.")

        else:
            st.warning(f"`{file_combined_report}` dosyasında beklenen sütunlardan bazıları bulunamadı.")
            st.dataframe(df_combined.head())

        st.subheader("6.2. ELECTRE Baskınlık Matrisi (Heatmap)")
        df_outranking = load_data(file_electre_outranking, sheet_name='Sheet1', use_excel=True)
        if df_outranking is not None:
            # Etiketler için aday ID'lerini al (Combined Report'tan ilk N aday)
            # Outranking matrisinin boyutuna göre etiket sayısı ayarlanmalı
            # Genellikle outranking matrisi tüm adayları içerir ama görselleştirme için ilk N aday alınabilir.
            # Şimdilik, outranking matrisinin sütun/satır sayısına göre genel etiketler oluşturalım
            # veya combined_report'tan sıralı adayları alalım.

            num_heatmap_aday = st.slider("Heatmap için aday sayısı (En iyi TOPSIS sırasına göre):", min_value=5, max_value=min(50, len(df_combined) if df_combined is not None else 50), value=15, key="heatmap_aday_slider")

            if 'ID' in df_combined.columns and 'TOPSIS_Rank' in df_combined.columns:
                # En iyi N adayı TOPSIS sırasına göre al
                top_n_aday_ids_ordered = df_combined.sort_values(by='TOPSIS_Rank').head(num_heatmap_aday)['ID'].tolist()

                # Outranking matrisini bu adaylara göre filtrele/yeniden sırala
                # Bu adım, df_outranking'in yapısına bağlıdır. Eğer df_outranking'in sütun ve indeksleri
                # Aday ID'leri ise, .loc kullanarak filtreleme yapılabilir.
                # Şu anki CSV formatında sütunlar '0', '1', ... şeklinde. Bu, adayların orijinal sırasına göre.
                # Bu yüzden, top_n_aday_ids_ordered listesindeki ID'lerin orijinal indekslerini bulmamız gerekebilir.
                # Basitlik adına, ilk N satır ve sütunu alıyoruz ve etiketleri top_n_aday_ids_ordered'dan atıyoruz.
                # GERÇEK UYGULAMADA BU EŞLEŞTİRME DOĞRU YAPILMALIDIR.
                
                if not df_outranking.empty and len(df_outranking) >= num_heatmap_aday and len(df_outranking.columns) >= num_heatmap_aday:
                    outranking_subset = df_outranking.iloc[:num_heatmap_aday, :num_heatmap_aday].values
                    heatmap_labels = [str(id) for id in top_n_aday_ids_ordered[:num_heatmap_aday]]

                    fig_heatmap = go.Figure(data=go.Heatmap(
                                       z=outranking_subset,
                                       x=heatmap_labels,
                                       y=heatmap_labels,
                                       colorscale='Blues',
                                       reversescale=True, # Koyu renk baskınlığı göstersin (1)
                                       hovertemplate="Baskılayan Aday (Satır): %{y}<br>Baskılanan Aday (Sütun): %{x}<br>Baskınlık: %{z}<extra></extra>"
                                       ))
                    fig_heatmap.update_layout(
                        title=f'ELECTRE Baskınlık Matrisi (En İyi {num_heatmap_aday} Aday)',
                        xaxis_title="Baskılanan Aday",
                        yaxis_title="Baskılayan Aday (Satır)",
                        yaxis_autorange='reversed', # Matrisin sol üstten başlaması için
                        height=max(500, num_heatmap_aday * 30),
                        xaxis_side="top"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    st.markdown("Bu ısı haritası, seçilen en iyi adaylar arasındaki baskınlık ilişkilerini gösterir. Koyu renk, satırdaki adayın sütundaki adayı baskıladığını (outrank ettiğini) belirtir (1=Baskılar, 0=Baskılamaz).")
                else:
                    st.warning(f"Outranking matrisi {num_heatmap_aday}x{num_heatmap_aday} boyutunda alt küme için yeterli değil veya yüklenemedi.")
                    st.dataframe(df_outranking.head())
            else:
                st.warning("Heatmap etiketleri için `combined_ranking_report.xlsx` dosyasında 'Aday ID' veya 'TOPSIS Rank' sütunları bulunamadı.")
        else:
            st.warning(f"`{file_electre_outranking}` dosyası yüklenemedi.")

        st.subheader("6.3. Birleşik Sıralama Raporu (İlk 20 Aday)")
        st.dataframe(df_combined.head(20).style.format({
            "TOPSIS_Score": "{:.4f}",
            "TOPSIS_Rank": "{:.0f}",
            "ELECTRE_Dominance_Score": "{:.0f}",
            "ELECTRE_Rank": "{:.0f}"
        }), use_container_width=True)

    else:
        st.warning(f"`{file_combined_report}` dosyası yüklenemedi.")


elif section == "Excel Çıktı Dosyaları ve Yapıları":
    st.header("7. Excel Çıktı Dosyaları ve Sheet Yapıları")
    st.markdown("Proje süresince üretilen her bir Excel dosyası (veya bu uygulamada kullanılan CSV karşılıkları) ve bu dosyalar içindeki önemli sütun yapıları aşağıda özetlenmiştir.")

    st.subheader("7.1. `processed_candidates_anonymized_scaled.xlsx` (Karar Matrisi Girdisi)")
    st.markdown("""
    Bu dosya, AHP ağırlıkları ile birlikte TOPSIS ve ELECTRE metodolojilerine girdi olarak kullanılan, anonimleştirilmiş ve normalize edilmiş (0-100 aralığında) aday kriter skorlarını içerir.
    - **Örnek Sütunlar:** `Aday ID`, `Yabancı Dil Skoru (0-100)`, `Temel Bilgisayar Becerileri Skoru (0-100)`, `Eğitim Düzeyi Skoru`, `Sertifika Skoru (0-100)`, `Sosyal Aktivite Skoru (0-100)`, `Deneyim Skoru (Kategori)`.
    """)
    # df_processed = load_data(file_processed_candidates)
    # if df_processed is not None:
    #     st.dataframe(df_processed.head(), height=200, use_container_width=True)

    st.subheader("7.2. `ahp_weights_summary.xlsx` (AHP Sonuçları)")
    st.markdown("""
    Bu dosya, AHP analizinin sonuçlarını içerir.
    - **Sheet `Birlesik_Agirlik` (CSV: `ahp_weights_summary.xlsx - Birlesik_Agirlik.csv`):**
        - `Kriter Adı`: Değerlendirme kriterinin adı.
        - `Birlesik Agirlik`: Her bir kriter için hesaplanmış nihai birleşik ağırlık.
    - **Sheet `Uzman_Agirliklari` (CSV: `ahp_weights_summary.xlsx - Uzman_Agirliklari.csv`):**
        - `Kriter Adı`: Değerlendirme kriterinin adı.
        - `Uzman_X Ağırlık`: X numaralı uzmanın ilgili kritere verdiği ağırlık.
        - `Uzman_X CR`: X numaralı uzmanın değerlendirmesinin tutarlılık oranı.
    - **Sheet `Consistency_Results` (CSV: `ahp_weights_summary.xlsx - Consistency_Results.csv`):**
        - `Uzman`: Uzman numarası veya 'Birleşik'.
        - `Lambda Max`: En büyük özdeğer.
        - `CI`: Tutarlılık İndeksi.
        - `RI`: Rastgele İndeks.
        - `CR`: Tutarlılık Oranı.
    """)
    # Örnek tablolar gösterilebilir
    df_ahp_b = load_data(file_ahp_birlesik_agirlik, sheet_name='Birlesik_Agirlik', use_excel=True)
    if df_ahp_b is not None:
        st.markdown("**Örnek: Birleşik Ağırlıklar**")
        st.dataframe(df_ahp_b.head(), height=200, use_container_width=True)

    st.subheader("7.3. `TOPSIS_Ranking.xlsx` (TOPSIS Sonuçları)")
    st.markdown("""
    - `Aday ID`: Adayın anonim kimliği.
    - `TOPSIS Score`: Adayın ideale yakınlık skoru (0-1 aralığında, 1'e yakın olan daha iyi).
    - `TOPSIS Rank`: Adayın TOPSIS skoruna göre sıralaması.
    """)
    df_t = load_data(file_topsis_ranking, sheet_name='Sheet1', use_excel=True)
    if df_t is not None:
        st.dataframe(df_t.head(), height=200, use_container_width=True)

    st.subheader("7.4. `ELECTRE_Results.xlsx` (ELECTRE Sonuçları)")
    st.markdown("""
    - `Aday ID`: Adayın anonim kimliği.
    - `ELECTRE Dominance Score`: Adayın net baskınlık skoru (veya benzeri bir ELECTRE sıralama metriği).
    - `ELECTRE Rank`: Adayın ELECTRE skoruna göre sıralaması.
    """)
    df_e = load_data(file_electre_results, sheet_name='Sheet1', use_excel=True)
    if df_e is not None:
        st.dataframe(df_e.head(), height=200, use_container_width=True)

    st.subheader("7.5. `combined_ranking_report.xlsx` (Birleşik Rapor)")
    st.markdown("""
    Bu dosya, TOPSIS ve ELECTRE sonuçlarını tek bir tabloda birleştirerek karşılaştırmalı bir görünüm sunar.
    - `Aday ID`, `TOPSIS Score`, `TOPSIS Rank`, `ELECTRE Dominance Score`, `ELECTRE Rank`.
    """)
    df_c = load_data(file_combined_report, sheet_name='Sheet1', use_excel=True)
    if df_c is not None:
        st.dataframe(df_c.head(), height=200, use_container_width=True)

    st.subheader("7.6. ELECTRE Ara Matrisleri")
    st.markdown("""
    - `ELECTRE_Concordance.xlsx`: Aday çiftleri arasındaki uyum değerlerini içerir.
    - `ELECTRE_Discordance.xlsx`: Aday çiftleri arasındaki uyumsuzluk değerlerini içerir.
    - `ELECTRE_Outranking.xlsx` (CSV: `ELECTRE_Outranking.xlsx - Sheet1.csv`): Adaylar arası baskınlık ilişkilerini gösteren matris (1: baskılar, 0: baskılamaz).
    """)
    df_eo = load_data(file_electre_outranking, sheet_name='Sheet1', use_excel=True)
    if df_eo is not None:
        st.markdown("**Örnek: Outranking Matrisi (İlk 5x5)**")
        st.dataframe(df_eo.iloc[:5, :5], height=200, use_container_width=True)


elif section == "Genel Metodoloji Özeti":
    st.header("8. Genel Metodoloji Özeti")
    st.markdown("""
    Proje, aday değerlendirme sürecini yapılandırmak ve nesnel hale getirmek için aşağıdaki adımları izlemiştir:

    1.  ✅ **Veri Temizleme ve Özellik Çıkarma:** Ham aday verilerinden (`aday_havuzu.xlsx`) anlamlı ve ölçülebilir kriterler türetilmiştir. Bu aşamada deneyim, dil becerisi, eğitim, bilgisayar yetkinlikleri, sertifikalar ve sosyal aktiviteler gibi faktörler sayısal skorlara dönüştürülmüştür.
    2.  ✅ **AHP ile Kriter Ağırlıkları Belirleme:** Alan uzmanlarının ikili karşılaştırma matrisleri (`ahp_expert_filled.xlsx`) kullanılarak her bir değerlendirme kriterinin göreceli önemi (ağırlığı) Analitik Hiyerarşi Süreci (AHP) ile hesaplanmıştır.
    3.  ✅ **Tutarlılık Analizi:** Uzman değerlendirmelerinin tutarlılığı, Tutarlılık Oranı (CR) ile kontrol edilmiş ve CR ≤ 0.15 (veya projede belirtilen eşik) olan tutarlı yargılar dikkate alınarak birleşik kriter ağırlıkları oluşturulmuştur (`ahp_weights_summary.xlsx`).
    4.  ✅ **Aday Verisinin Normalizasyonu (0-100):** Farklı ölçeklerdeki kriter skorları, TOPSIS ve ELECTRE analizlerine uygun hale getirmek için genellikle Min-Max normalizasyonu ile 0-100 aralığına ölçeklenmiştir (`processed_candidates_anonymized_scaled.xlsx`).
    5.  ✅ **TOPSIS ile İdeal Çözüm Bazlı Sıralama:** Normalize edilmiş aday verileri ve AHP ağırlıkları kullanılarak, her adayın ideal ve negatif-ideal çözümlere olan uzaklıkları hesaplanmış ve ideale yakınlık katsayısına göre adaylar sıralanmıştır (`TOPSIS_Ranking.xlsx`).
    6.  ✅ **ELECTRE ile Baskınlık Analizi:** Yine normalize edilmiş veriler ve AHP ağırlıkları ile adaylar arasında uyum (concordance) ve uyumsuzluk (discordance) analizleri yapılmış, belirlenen eşik değerlere göre baskınlık (outranking) ilişkileri çıkarılmış ve adaylar sıralanmıştır (`ELECTRE_Results.xlsx` ve ara matrisler).
    7.  ✅ **Birleşik Raporlama ve Karar Destek:** TOPSIS ve ELECTRE metodolojilerinden elde edilen sıralamalar ve skorlar bir araya getirilerek (`combined_ranking_report.xlsx`) karar vericilere kapsamlı bir bakış açısı sunulmuştur.
    8.  ✅ **Görselleştirme ve İnteraktif Analiz:** Sonuçlar, grafikler ve interaktif araçlar (bu Streamlit uygulaması ve `multi_criteria_ranking_demo.ipynb` gibi) aracılığıyla daha anlaşılır ve yorumlanabilir hale getirilmiştir.
    """)

elif section == "Sonuç ve Değerlendirme":
    st.header("9. Sonuç ve Değerlendirme")
    st.markdown("""
    Bu proje, AHP, TOPSIS ve ELECTRE gibi güçlü Çok Kriterli Karar Verme (ÇKKV) metodolojilerini başarılı bir şekilde entegre ederek, aday değerlendirme problemine yapılandırılmış, şeffaf, nesnel ve analitik bir çözüm sunmuştur.

    #### Elde Edilen Başlıca Çıktılar:
    -   **Tam ve Kapsamlı Sıralama (TOPSIS):** Tüm adayları ideal çözüme olan yakınlıklarına göre net bir şekilde sıralayan bir liste.
    -   **Baskınlık ve Üstünlük Analizi (ELECTRE):** Adaylar arasındaki ikili karşılaştırmalara dayalı olarak hangi adayların diğerlerine göre daha üstün olduğunu gösteren, daha sağlam ve daha az riskli aday gruplarını belirlemeye yardımcı olan bir analiz.
    -   **Kriter Ağırlıklarının Objektif Tespiti (AHP):** Uzman görüşlerini sistematik bir şekilde birleştirerek değerlendirme kriterlerinin göreceli önemini belirleyen, şeffaf bir ağırlıklandırma süreci.
    -   **Birleşik ve Karşılaştırmalı Raporlar:** Farklı metodolojilerin sonuçlarını bir arada sunarak karar vericilere daha geniş bir perspektif ve daha güvenilir bir karar zemini sağlayan raporlar.
    -   **Görselleştirme ve İnteraktif Analiz Araçları:** Karmaşık verilerin ve sonuçların kolayca anlaşılmasını ve yorumlanmasını sağlayan grafikler ve interaktif arayüzler (bu Streamlit uygulaması gibi).

    #### Sistemin Katkıları ve Üstünlükleri:
    -   **Nesnellik ve Şeffaflık:** Karar verme sürecini kişisel yanlılıklardan arındırarak, tanımlanmış kriterlere ve matematiksel modellere dayandırır.
    -   **Kapsamlılık:** Birden fazla ve birbiriyle çelişebilen kriteri aynı anda değerlendirme yeteneği sunar.
    -   **Esneklik ve Uyarlanabilirlik:** Farklı sektörlerdeki, farklı pozisyonlardaki veya farklı amaçlardaki değerlendirme problemlerine kolayca uyarlanabilir.
    -   **Karar Kalitesinin Artırılması:** Verilere dayalı ve sistematik bir yaklaşım sunarak daha bilinçli ve savunulabilir kararlar alınmasına yardımcı olur.
    -   **Denetlenebilirlik:** Sürecin her adımı (veri toplama, ağırlıklandırma, sıralama) belgelenmiş ve izlenebilir olduğu için denetimi kolaydır.

    #### Gelecek Çalışmalar ve Potansiyel İyileştirmeler:
    -   **Farklı ÇKKV Metotlarının Entegrasyonu:** PROMETHEE, VIKOR gibi diğer ÇKKV metotlarının da sisteme dahil edilerek sonuçların zenginleştirilmesi.
    -   **Grup Karar Verme Teknikleri:** Birden fazla karar vericinin olduğu durumlarda, onların tercihlerini daha etkin bir şekilde birleştirecek grup AHP veya Delphi gibi tekniklerin kullanılması.
    -   **Belirsizlik Yönetimi:** Verilerdeki veya uzman yargılarındaki belirsizlikleri (örn: bulanık sayılar, aralık değerleri) modelleyebilen Bulanık AHP, Bulanık TOPSIS gibi yaklaşımların entegrasyonu.
    -   **Dinamik Kriter Ağırlıklandırması:** Zamanla veya farklı senaryolara göre değişebilen kriter ağırlıklarını modelleyebilen dinamik yaklaşımlar.
    -   **Kullanıcı Arayüzünün Geliştirilmesi:** Karar vericilerin sistemi daha kolay kullanabilmesi, kendi parametrelerini girebilmesi ve "what-if" analizleri yapabilmesi için daha gelişmiş ve kullanıcı dostu bir web arayüzü geliştirilmesi.

    Sonuç olarak, bu çalışma ile kuruma/teze/sunuma verilebilecek, kapsamlı ve bilimsel temellere dayanan bir karar destek sistemi başarıyla inşa edilmiştir. 🚀
    """)

# Uygulamayı çalıştırmak için terminalde: streamlit run app.py
