# HCNET PowerPoint Template

[hcnet.co.jp](https://www.hcnet.co.jp/) сайтын өнгө, дизайныг суурилсан PowerPoint загвар.

## Файл

| Файл | Тайлбар |
|------|---------|
| `HCNET_PowerPoint_Template.pptx` | Бэлэн PowerPoint загвар (9 слайд) |

## Өнгийн палитр (албан ёсны сайтаас)

| Нэр | HEX | Хэрэглээ |
|-----|-----|----------|
| Primary Green | `#008C41` | Гарчиг, товч, гол элемент |
| Accent Green | `#00C05B` | Тод акцент, зураас |
| Dark Green | `#24593D` | Footer, харанхуй хэсэг |
| Light BG | `#E5F9EE` | Зөөлөн дэвсгэр |
| Text | `#333333` | Үндсэн текст |
| Background | `#F8F8F8` | Слайдын дэвсгэр |

## Слайдын бүтэц

1. **Тitle** — Үндсэн гарчиг (表紙)
2. **Section** — Хэсгийн заагч
3. **Content** — Жагсаалт / bullet points
4. **Two Column** — 2 багана
5. **Image + Text** — Зураг + текст
6. **Table** — Хүснэгт
7. **Quote** — Ишлэл / highlight
8. **Thank You** — Төгсгөл
9. **Guide** — Загварын заавар + өнгийн палитр

## MS Office 365-д хэрхэн ашиглах

### 1. Файлыг нээх

1. `HCNET_PowerPoint_Template.pptx` файлыг татаж авна
2. PowerPoint (Office 365) дээр нээнэ

### 2. Шинэ презентаци үүсгэх

1. Хэрэгтэй слайдыг **хуулна** (Ctrl+C → Ctrl+V)
2. Текстийг өөрийн агуулгаар солино
3. Хэрэггүй слайдыг устгана

### 3. Загвар болгон хадгалах (сонголт)

1. **Файл** → **另存为 / Save As**
2. Файлын төрөл: **PowerPoint Template (*.potx)**
3. Дараагийн удаа `.potx`-оос шинэ файл үүсгэнэ

### 4. OneDrive / SharePoint

Office 365 ашиглаж байгаа бол OneDrive дээр хадгалаад багийнхантай хуваалцана.

## Дахин үүсгэх (хөгжүүлэгчид)

```bash
pip install python-pptx
python scripts/generate_hcnet_ppt_template.py
```

## Анхаарах зүйл

- Энэ загвар нь HCNET сайтын **өнгө, загвар**-д суурилсан **загварчилсан** template юм.
- Албан ёсны HCNET лого нь оруулаагүй — шаардлагатай бол [hcnet.co.jp](https://www.hcnet.co.jp/)-ийн албан ёсны лого ашиглана уу.
- Фont: **Yu Gothic** (Windows), **Noto Sans JP** (Mac) — япон текстэд тохиромжтой.
