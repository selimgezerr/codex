# Masaüstü Müşteri ve Proje Yöneticisi

Bu depo, müşterilerinizi, projelerinizi ve yapılacak işlerinizi yönetmek için basit bir Tkinter uygulaması içerir.

## Özellikler

- Telefon, e-posta, hosting ve domain bitiş tarihleriyle müşteri ekleme, düzenleme ve silme
- Müşterilere ait projeleri ekleme, düzenleme ve silme
- Yapılacak listesi oluşturma, düzenleme ve görevleri tamamlama
- Müşteri listesinden WhatsApp ile hızlı mesaj gönderebilme
- Hosting ve domain bitiş tarihlerine kalan günlerin listede gösterilmesi
- Müşteri ve projeleri CSV olarak dışa aktarabilme
- Müşteri listesinde arama yapabilme
- Görevleri ve bitiş tarihlerini CSV'ye kaydedebilme
- Proje detaylarını görmek için listede çift tıklama
- Tamamlanan görevleri gizleyebilme ve topluca silebilme
- Uzun listeler için kaydırma çubukları

Veriler `app.db` isimli yerel SQLite veritabanında saklanır.

CSV tuşlarıyla verilerinizi yedekleyebilir ve arama kutusu sayesinde müşteri listesinde filtreleme yapabilirsiniz.
Tarih alanları hatalı girildiğinde uygulama sizi bilgilendirir.

## Gereksinimler

- Python 3.x (Tkinter standart Python ile gelir)
- PyInstaller

## Çalıştırma

```bash
python app.py
```

Uygulama açıldığında müşterilerinizi, projelerinizi ve yapılacak işlerinizi yönetebilirsiniz.

## EXE Oluşturma

Uygulamayı tek bir dosya olarak derlemek için [PyInstaller](https://pyinstaller.org/) kullanabilirsiniz. Önce PyInstaller'ı kurun:

```bash
pip install -r requirements.txt
```

Ardından Windows komut satırında `build_exe.bat` dosyasını çalıştırarak uygulamayı paketleyebilirsiniz:

```bash
pyinstaller --noconsole --onefile app.py
```

`dist/app.exe` altında oluşan dosyayı Windows 10 veya 11 üzerinde doğrudan çalıştırabilirsiniz.
