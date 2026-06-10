# HCNET PowerPoint Template

[hcnet.co.jp](https://www.hcnet.co.jp/) сайтын өнгө, дизайныг суурилсан PowerPoint загвар.

## Файлууд

| Файл | Тайлбар |
|------|---------|
| `HCNET_PowerPoint_Template.pptx` | Бэлэн презентаци (16 слайд) |
| `HCNET_PowerPoint_Template.potx` | **Office 365 template** — шинэ файл үүсгэхэд ашиглана |
| `assets/hcnet_logo.jpg` | Албан ёсны HCNET лого |
| `assets/hcnet_footer_logo.png` | Footer лого |

## Слайдын бүтэц (16)

| № | Төрөл | Зориулалт |
|---|--------|-----------|
| 1 | Title | Үндсэн гарчиг (лого орсон) |
| 2 | Section | Хэсгийн заагч |
| 3 | Agenda | Агуулгын жагсаалт |
| 4 | Content | Bullet points |
| 5 | Two Column | 2 багана |
| 6 | Three Column | 3 багана |
| 7 | Image + Text | Зураг + текст |
| 8 | Process | Алхам алхмаар процесс |
| 9 | KPI | Тоо, статистик |
| 10 | Comparison | Before / After |
| 11 | Team | Баг / профайл |
| 12 | Table | Хүснэгт |
| 13 | Quote | Ишлэл / highlight |
| 14 | Contact | Холбоо барих / Q&A |
| 15 | Thank You | Төгсгөл (лого орсон) |
| 16 | Guide | Загварын заавар |

## Өнгийн палитр

| Өнгө | HEX |
|------|-----|
| Primary Green | `#008C41` |
| Accent Green | `#00C05B` |
| Dark Green | `#24593D` |
| Light BG | `#E5F9EE` |
| Text | `#333333` |
| Background | `#F8F8F8` |

## MS Office 365-д хэрхэн ашиглах

### .potx template ашиглах (зөвлөмж)

1. `HCNET_PowerPoint_Template.potx` файлыг татаж авна
2. Файл дээр **давхар дарж** PowerPoint-оор нээнэ
3. Office 365 автоматаар **шинэ презентаци** үүсгэнэ
4. Хэрэгтэй слайдыг хуулж, текстийг солино

### .pptx ашиглах

1. `HCNET_PowerPoint_Template.pptx` нээнэ
2. Хэрэгтэй слайдыг хуулна (Ctrl+C → Ctrl+V)
3. Хэрэггүй слайдыг устгана

### OneDrive / SharePoint

Office 365 ашиглаж байгаа бол `.potx` файлыг OneDrive дээр хадгалаад багийнхантай хуваалцана.

## Дахин үүсгэх

```bash
pip install python-pptx
python scripts/generate_hcnet_ppt_template.py
```

## Анхаарах зүйл

- Лого нь [hcnet.co.jp](https://www.hcnet.co.jp/) албан ёсны сайтаас авсан
- Font: **Yu Gothic** (Windows), **Noto Sans JP** (Mac)
