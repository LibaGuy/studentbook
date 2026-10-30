#!/usr/bin/env python3
"""
Master Builder for Clinical Orthopedic Reference Manual
Compiles all Hebrew-English chapters into a fully responsive, mobile-optimized HTML reader.
Features:
- Mobile-first responsive design with off-canvas TOC drawer on phones & tablets.
- Sticky mobile top app bar with hamburger menu, dark/light toggle and quick navigation.
- Smooth horizontal scrolling wrappers on all markdown tables with scroll indicators.
- Non-overflowing pre/code ASCII diagrams with font scaling.
- Single author credit in the top hero header and sidebar header (0 repeated author lines in chapter bodies).
- Instant client-side search across all chapters.
- Dark / Light mode toggle with local storage persistence.
- Floating back-to-top button.
"""

import os
import glob
import re
from markdown_it import MarkdownIt

BASE_DIR = r"c:\Users\guyli\MedicalWriter"
CHAPTERS_DIR = os.path.join(BASE_DIR, "med5_chapters")
OUTPUT_HTML = os.path.join(BASE_DIR, "Orthopedic_Surgery_5th_Year_Clerkship_Textbook.html")
OUTPUT_INDEX = os.path.join(BASE_DIR, "med5_index.html")

CHAPTER_CONFIG = [
    {"num": 1, "id": "01_Introduction_and_Diagnostics", "title": "פרק 1: מבוא, דימות ואנטומיה יישומית", "short": "מבוא ודימות"},
    {"num": 2, "id": "02_Physical_Examination", "title": "פרק 2: אנמנזה ובדיקה גופנית ממוקדת", "short": "הבדיקה הגופנית"},
    {"num": 3, "id": "03_Pediatric_Orthopaedics", "title": "פרק 3: אורתופדיה ילדים", "short": "אורתופדיה ילדים"},
    {"num": 4, "id": "04_Joint_Arthroplasty", "title": "פרק 4: החלפות מפרקים בירך ובברך", "short": "החלפות מפרקים"},
    {"num": 5, "id": "05_Orthopaedic_Trauma", "title": "פרק 5: טראומה אורתופדית ושברים", "short": "טראומה ושברים"},
    {"num": 6, "id": "06_Casting_and_External_Fixation", "title": "פרק 6: עקרונות קיבוע בגבס וקיבוע חיצוני", "short": "גבס וקיבוע חיצוני"},
    {"num": 7, "id": "07_Shoulder_Pathologies", "title": "פרק 7: פתולוגיות כתף ואי-יציבות", "short": "פתולוגיות כתף"},
    {"num": 8, "id": "08_Hand_and_Distal_Upper_Extremity", "title": "פרק 8: שברי רדיוס וכף יד רחיקנית", "short": "כף יד ורדיוס"},
    {"num": 9, "id": "09_Spine_Disorders", "title": "פרק 9: עמוד שדרה וחירום נוירולוגי", "short": "עמוד שדרה"},
    {"num": 10, "id": "10_Foot_and_Ankle", "title": "פרק 10: כף רגל סוכרתית ועיוותים", "short": "כף רגל וקרסול"},
    {"num": 11, "id": "11_Sports_Medicine", "title": "פרק 11: אורתופדית ספורט ופציעות ברך", "short": "אורתופדית ספורט"},
    {"num": 12, "id": "12_Patient_Rights_and_Legal_Aspects", "title": "פרק 12: חוק זכויות החולה, אפוטרופסות והיבטים משפטיים באורתופדיה", "short": "זכויות החולה ומשפט"},
]

def load_markdown_chapters():
    md = MarkdownIt().enable('table')
    chapters_data = []
    total_words = 0

    for cfg in CHAPTER_CONFIG:
        folder = os.path.join(CHAPTERS_DIR, cfg["id"])
        if not os.path.exists(folder):
            continue
        md_files = glob.glob(os.path.join(folder, "*.md"))
        if not md_files:
            continue
        
        md_file = md_files[0]
        with open(md_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        words = len(raw_text.split())
        total_words += words

        # 1. Ensure no images are present in HTML - clean text & ASCII only
        clean_text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', raw_text)
        
        # 2. Strip any status summary / picture of situation if present
        clean_text = re.sub(r'###\s*סיכום תמונת מצב.*$', '', clean_text, flags=re.DOTALL)
        
        # 3. Strip author credit from individual chapter bodies
        clean_text = re.sub(r'\*\*עורך ומחבר ראשי:\*\*.*?\n+', '', clean_text)
        
        # 4. Strip duplicate leading H1 and H2 chapter headers (already in chapter card header)
        clean_text = re.sub(r'^#\s*פרק\s*\d+:.*?\n+', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'^##\s*(Master Clinical|Clinical & Applied).*?\n+', '', clean_text, flags=re.MULTILINE)

        html_body = md.render(clean_text)

        # 5. Wrap every table in a responsive scrolling container with scroll hint
        html_body = re.sub(
            r'(<table\b[^>]*>.*?</table>)',
            r'<div class="table-responsive"><div class="table-scroll-hint">⟵ ניתן לגלול אופקית לצפייה בטבלה המלאה ⟶</div>\1</div>',
            html_body,
            flags=re.DOTALL
        )

        chapters_data.append({
            "num": cfg["num"],
            "id": cfg["id"],
            "title": cfg["title"],
            "short": cfg["short"],
            "words": words,
            "html": html_body
        })

    return chapters_data, total_words

def generate_html(chapters, total_words):
    toc_links = []
    sections_html = []
    total_ch = len(chapters)

    for ch in chapters:
        toc_links.append(f"""
            <a href="#ch-{ch['num']}" class="toc-item" data-ch="{ch['num']}" onclick="onTocItemClick(event, {ch['num']})">
                <span class="toc-badge">{ch['num']}</span>
                <span class="toc-title">{ch['short']}</span>
            </a>
        """)
        sections_html.append(f"""
            <article id="ch-{ch['num']}" class="chapter-card">
                <div class="chapter-header">
                    <span class="chapter-num-badge">פרק {ch['num']} מתוך {total_ch}</span>
                    <h2 class="chapter-main-title">{ch['title']}</h2>
                    <div class="chapter-meta">עיגון ספרותי ומשפטי: חוק זכויות החולה, חוק הכשרות המשפטית, Campbell 14th, Rockwood 10th, Miller 8th</div>
                </div>
                <div class="chapter-content">
                    {ch['html']}
                </div>
            </article>
        """)

    toc_str = "\n".join(toc_links)
    content_str = "\n".join(sections_html)

    html_template = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>ספר לימוד וסיכומים קליניים באורתופדיה | ד"ר גיא ליבה</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --primary-light: #e0f2fe;
            --accent: #0ea5e9;
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --border: #e2e8f0;
            --sidebar-bg: #0f172a;
            --sidebar-text: #f1f5f9;
            --code-bg: #f1f5f9;
            --callout-bg: #f0fdf4;
            --callout-border: #16a34a;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06);
            --header-height: 56px;
        }}

        [data-theme="dark"] {{
            --primary: #38bdf8;
            --primary-dark: #0284c7;
            --primary-light: #082f49;
            --bg-body: #0b1120;
            --bg-card: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --sidebar-bg: #020617;
            --sidebar-text: #e2e8f0;
            --code-bg: #0f172a;
            --callout-bg: #064e3b;
            --callout-border: #10b981;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.35);
        }}

        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            scroll-behavior: smooth;
            -webkit-text-size-adjust: 100%;
        }}

        body {{
            font-family: 'Assistant', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.75;
            font-size: 17px;
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
            width: 100%;
        }}

        /* Mobile Sticky Top App Bar */
        .mobile-top-bar {{
            display: none;
            position: sticky;
            top: 0;
            right: 0;
            left: 0;
            height: var(--header-height);
            background-color: var(--sidebar-bg);
            color: #ffffff;
            z-index: 1100;
            padding: 0 16px;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .mobile-menu-btn {{
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.2);
            color: #ffffff;
            padding: 7px 12px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 700;
            font-family: inherit;
        }}

        .mobile-menu-btn:active {{
            background: rgba(56, 189, 248, 0.25);
        }}

        .mobile-brand {{
            font-size: 16px;
            font-weight: 800;
            color: #38bdf8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding: 0 8px;
        }}

        .mobile-theme-btn {{
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.2);
            color: #ffffff;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 16px;
        }}

        /* Sidebar Backdrop Overlay on Mobile */
        .sidebar-backdrop {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.65);
            z-index: 1150;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            backdrop-filter: blur(2px);
        }}

        .sidebar-backdrop.active {{
            display: block;
            opacity: 1;
            pointer-events: auto;
        }}

        /* Sidebar Navigation */
        .sidebar {{
            width: 310px;
            background-color: var(--sidebar-bg);
            color: var(--sidebar-text);
            position: fixed;
            top: 0;
            bottom: 0;
            right: 0;
            display: flex;
            flex-direction: column;
            border-left: 1px solid var(--border);
            z-index: 1200;
            box-shadow: -4px 0 12px rgba(0,0,0,0.15);
            transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .sidebar-header {{
            padding: 22px 18px 18px 18px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .sidebar-header-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }}

        .sidebar-header h1 {{
            font-size: 18px;
            font-weight: 800;
            color: #38bdf8;
            line-height: 1.3;
        }}

        .sidebar-close-btn {{
            display: none;
            background: rgba(255,255,255,0.1);
            border: none;
            color: #cbd5e1;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            align-items: center;
            justify-content: center;
        }}

        .sidebar-close-btn:active {{
            background: rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }}

        .sidebar-header .author {{
            font-size: 13px;
            color: #94a3b8;
            font-weight: 600;
        }}

        .search-box {{
            padding: 12px 16px;
            background-color: rgba(255,255,255,0.03);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }}

        .search-input {{
            width: 100%;
            padding: 9px 13px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background-color: rgba(255,255,255,0.06);
            color: #ffffff;
            font-size: 14px;
            outline: none;
            direction: rtl;
            font-family: inherit;
        }}

        .search-input:focus {{
            border-color: #38bdf8;
            background-color: rgba(255,255,255,0.1);
        }}

        .toc-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px 8px;
            -webkit-overflow-scrolling: touch;
        }}

        .toc-item {{
            display: flex;
            align-items: center;
            padding: 10px 12px;
            color: #cbd5e1;
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
            font-size: 14.5px;
            font-weight: 600;
        }}

        .toc-item:hover, .toc-item.active {{
            background-color: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
        }}

        .toc-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 24px;
            height: 24px;
            border-radius: 6px;
            background-color: rgba(255,255,255,0.1);
            font-size: 12px;
            margin-left: 10px;
            color: #38bdf8;
            font-weight: 700;
        }}

        .toc-title {{
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .sidebar-footer {{
            padding: 12px 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }}

        .theme-btn {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #ffffff;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            font-family: inherit;
        }}

        /* Main Content Area */
        .main-wrapper {{
            margin-right: 310px;
            flex: 1;
            padding: 40px 48px;
            max-width: 1180px;
            width: calc(100% - 310px);
            overflow-x: hidden;
        }}

        /* Top Hero Section (Single Author Credit Here) */
        .top-hero {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            padding: 36px 40px;
            border-radius: 16px;
            box-shadow: var(--shadow);
            margin-bottom: 40px;
        }}

        .hero-top-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: 0.3px;
        }}

        .top-hero h1 {{
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 14px;
            line-height: 1.3;
        }}

        .hero-author-card {{
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 10px;
            padding: 12px 18px;
            margin-bottom: 18px;
            display: inline-block;
        }}

        .hero-author-role {{
            font-size: 11.5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #e0f2fe;
            font-weight: 700;
            margin-bottom: 2px;
        }}

        .hero-author-name {{
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
        }}

        .hero-author-sub {{
            font-size: 13px;
            color: #bae6fd;
            font-weight: 600;
        }}

        .hero-desc {{
            font-size: 16.5px;
            opacity: 0.95;
            margin-bottom: 18px;
            line-height: 1.6;
        }}

        .hero-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .hero-badge {{
            background: rgba(255,255,255,0.18);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12.5px;
            font-weight: 700;
        }}

        /* Chapter Cards */
        .chapter-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 38px 44px;
            margin-bottom: 42px;
            box-shadow: var(--shadow);
            scroll-margin-top: 24px;
            width: 100%;
            overflow-x: hidden;
        }}

        .chapter-header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 18px;
            margin-bottom: 26px;
        }}

        .chapter-num-badge {{
            display: inline-block;
            background-color: var(--primary-light);
            color: var(--primary-dark);
            font-weight: 800;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 8px;
        }}

        [data-theme="dark"] .chapter-num-badge {{
            background-color: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
        }}

        .chapter-main-title {{
            font-size: 24px;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 6px;
            line-height: 1.35;
        }}

        .chapter-meta {{
            font-size: 13.5px;
            color: var(--text-muted);
            font-weight: 600;
        }}

        /* Chapter Typography */
        .chapter-content h2 {{
            font-size: 21px;
            font-weight: 800;
            color: var(--primary);
            margin-top: 32px;
            margin-bottom: 14px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
            line-height: 1.4;
        }}

        .chapter-content h3 {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-main);
            margin-top: 24px;
            margin-bottom: 10px;
            line-height: 1.4;
        }}

        .chapter-content h4 {{
            font-size: 16px;
            font-weight: 700;
            color: var(--primary-dark);
            margin-top: 18px;
            margin-bottom: 8px;
        }}

        [data-theme="dark"] .chapter-content h4 {{
            color: #38bdf8;
        }}

        .chapter-content p {{
            margin-bottom: 16px;
            text-align: justify;
            word-wrap: break-word;
        }}

        .chapter-content ul, .chapter-content ol {{
            margin-bottom: 18px;
            padding-right: 22px;
        }}

        .chapter-content li {{
            margin-bottom: 6px;
        }}

        .chapter-content hr {{
            border: 0;
            border-top: 1px solid var(--border);
            margin: 26px 0;
        }}

        /* Responsive Table Container with Horizontal Scroll */
        .table-responsive {{
            width: 100%;
            max-width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 20px 0 26px 0;
            border-radius: 10px;
            border: 1px solid var(--border);
            background-color: var(--bg-card);
            box-shadow: var(--shadow);
            position: relative;
        }}

        .table-scroll-hint {{
            font-size: 11.5px;
            color: var(--primary);
            background-color: var(--primary-light);
            padding: 5px 12px;
            text-align: center;
            font-weight: 700;
            border-bottom: 1px solid var(--border);
            user-select: none;
            letter-spacing: 0.2px;
        }}

        [data-theme="dark"] .table-scroll-hint {{
            background-color: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
        }}

        .table-responsive table {{
            width: 100%;
            min-width: 580px;
            border-collapse: collapse;
            margin: 0;
            border: none;
            table-layout: auto;
        }}

        .table-responsive th,
        .table-responsive td {{
            padding: 11px 14px;
            text-align: right;
            border: 1px solid var(--border);
            vertical-align: top;
            font-size: 14px;
            line-height: 1.5;
            white-space: normal;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}

        .table-responsive th {{
            background-color: var(--primary-light);
            color: var(--primary-dark);
            font-weight: 700;
            font-size: 13.5px;
            white-space: nowrap;
        }}

        [data-theme="dark"] .table-responsive th {{
            background-color: #0c2d48;
            color: #38bdf8;
        }}

        .table-responsive tr:nth-child(even) td {{
            background-color: rgba(0,0,0,0.015);
        }}

        [data-theme="dark"] .table-responsive tr:nth-child(even) td {{
            background-color: rgba(255,255,255,0.02);
        }}

        /* Code / ASCII Diagrams */
        pre {{
            background-color: var(--code-bg);
            color: var(--text-main);
            padding: 16px 18px;
            border-radius: 10px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            direction: ltr;
            text-align: left;
            font-family: 'Fira Code', Consolas, 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.45;
            margin: 20px 0;
            border: 1px solid var(--border);
            max-width: 100%;
            white-space: pre;
        }}

        /* Blockquotes / Alerts */
        blockquote {{
            margin: 20px 0;
            padding: 14px 18px;
            background-color: var(--callout-bg);
            border-right: 4px solid var(--callout-border);
            border-radius: 8px;
            font-size: 15px;
            color: var(--text-main);
        }}

        [data-theme="dark"] blockquote {{
            background-color: rgba(6, 78, 59, 0.35);
            border-right-color: #10b981;
        }}

        /* Floating Back to Top Button */
        .back-to-top {{
            position: fixed;
            bottom: 24px;
            left: 24px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background-color: var(--primary);
            color: #ffffff;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: all 0.25s ease;
        }}

        .back-to-top.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        .back-to-top:hover {{
            background-color: var(--primary-dark);
            transform: translateY(-2px);
        }}

        /* ========================================================
           RESPONSIVE MOBILE BREAKPOINTS (Phones & Tablets)
           ======================================================== */
        @media (max-width: 992px) {{
            body {{
                font-size: 15.5px;
                display: block;
            }}

            .mobile-top-bar {{
                display: flex;
            }}

            /* Off-Canvas Drawer Sidebar */
            .sidebar {{
                right: -320px;
                width: 300px;
                max-width: 85vw;
                box-shadow: -8px 0 24px rgba(0,0,0,0.45);
            }}

            .sidebar.open {{
                right: 0;
            }}

            .sidebar-close-btn {{
                display: inline-flex;
            }}

            .main-wrapper {{
                margin-right: 0;
                width: 100%;
                max-width: 100%;
                padding: 16px 14px;
            }}

            .top-hero {{
                padding: 24px 20px;
                margin-bottom: 24px;
                border-radius: 14px;
            }}

            .top-hero h1 {{
                font-size: 22px;
                margin-bottom: 12px;
            }}

            .hero-author-card {{
                padding: 10px 14px;
                margin-bottom: 14px;
                width: 100%;
            }}

            .hero-author-name {{
                font-size: 16px;
            }}

            .hero-author-sub {{
                font-size: 12.5px;
            }}

            .hero-desc {{
                font-size: 14.5px;
                margin-bottom: 14px;
            }}

            .hero-badge {{
                font-size: 11.5px;
                padding: 4px 10px;
            }}

            .chapter-card {{
                padding: 22px 16px;
                margin-bottom: 26px;
                border-radius: 12px;
                scroll-margin-top: calc(var(--header-height) + 16px);
            }}

            .chapter-header {{
                padding-bottom: 14px;
                margin-bottom: 20px;
            }}

            .chapter-main-title {{
                font-size: 20px;
                line-height: 1.35;
            }}

            .chapter-content h2 {{
                font-size: 18px;
                margin-top: 26px;
                margin-bottom: 12px;
            }}

            .chapter-content h3 {{
                font-size: 16.5px;
                margin-top: 20px;
                margin-bottom: 8px;
            }}

            .chapter-content h4 {{
                font-size: 15px;
            }}

            pre {{
                font-size: 11.5px;
                padding: 12px 14px;
                line-height: 1.4;
                margin: 16px 0;
            }}

            .table-responsive th,
            .table-responsive td {{
                padding: 8px 10px;
                font-size: 13px;
            }}

            blockquote {{
                padding: 12px 14px;
                font-size: 14px;
                margin: 16px 0;
            }}

            .back-to-top {{
                bottom: 18px;
                left: 18px;
                width: 40px;
                height: 40px;
                font-size: 16px;
            }}
        }}

        @media (max-width: 480px) {{
            .main-wrapper {{
                padding: 12px 10px;
            }}

            .chapter-card {{
                padding: 18px 12px;
                margin-bottom: 20px;
            }}

            .chapter-main-title {{
                font-size: 19px;
            }}

            pre {{
                font-size: 10.5px;
                padding: 10px 10px;
            }}

            .table-responsive th,
            .table-responsive td {{
                padding: 7px 8px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Mobile Sticky Top App Bar -->
    <header class="mobile-top-bar">
        <button class="mobile-menu-btn" onclick="toggleSidebar()" aria-label="פתח תוכן עניינים">
            <span>☰</span>
            <span>פרקים</span>
        </button>
        <div class="mobile-brand">ספר אורתופדיה קלינית</div>
        <button class="mobile-theme-btn" onclick="toggleTheme()" aria-label="החלף מצב תצוגה">
            🌓
        </button>
    </header>

    <!-- Backdrop for Mobile Drawer -->
    <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeSidebar()"></div>

    <!-- Sidebar Navigation Drawer -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-header-top">
                <h1>ספר אורתופדיה קלינית</h1>
                <button class="sidebar-close-btn" onclick="closeSidebar()" aria-label="סגור תוכן עניינים">✕</button>
            </div>
            <div class="author">ד"ר גיא ליבה | מתמחה באורתופדיה, מדריך קליני</div>
        </div>
        <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="חיפוש מהיר בספר..." onkeyup="filterChapters()">
        </div>
        <nav class="toc-list" id="tocList">
            {toc_str}
        </nav>
        <div class="sidebar-footer">
            <span>סה"כ: {total_ch} פרקים</span>
            <button class="theme-btn" onclick="toggleTheme()">מצב כהה / בהיר</button>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-wrapper">
        <header class="top-hero">
            <div class="hero-top-badge">מהדורה קלינית מעודכנת</div>
            <h1>ספר לימוד וסיכומים קליניים באורתופדיה</h1>
            <div class="hero-author-card">
                <div class="hero-author-role">עורך ומחבר ראשי</div>
                <div class="hero-author-name">ד"ר גיא ליבה (Dr. Guy Liba, M.D.)</div>
                <div class="hero-author-sub">מתמחה בכירורגיה אורתופדית, מדריך קליני</div>
            </div>
            <p class="hero-desc">מדריך סמכותי ומעמיק לעבודה קלינית במחלקה, סבבים ותורנויות במלר"ד. מבוסס על ספרי היסוד הבינלאומיים המובילים ודיני מדינת ישראל.</p>
            <div class="hero-badges">
                <span class="hero-badge">Campbell's Operative Orthopaedics 14th Ed.</span>
                <span class="hero-badge">Rockwood and Green's 10th Ed.</span>
                <span class="hero-badge">Miller's Review of Orthopaedics 8th Ed.</span>
                <span class="hero-badge">חוק זכויות החולה ואפוטרופסות</span>
            </div>
        </header>

        {content_str}
    </main>

    <!-- Floating Back to Top Button -->
    <button id="backToTopBtn" class="back-to-top" onclick="scrollToTop()" title="חזרה לראש הספר" aria-label="חזרה לראש הספר">
        ↑
    </button>

    <script>
        // Sidebar Drawer Toggle for Mobile
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('sidebarBackdrop');
            const isOpen = sidebar.classList.contains('open');
            if (isOpen) {{
                closeSidebar();
            }} else {{
                openSidebar();
            }}
        }}

        function openSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('sidebarBackdrop');
            sidebar.classList.add('open');
            backdrop.classList.add('active');
            document.body.style.overflowY = 'hidden';
        }}

        function closeSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const backdrop = document.getElementById('sidebarBackdrop');
            sidebar.classList.remove('open');
            backdrop.classList.remove('active');
            document.body.style.overflowY = '';
        }}

        // When a chapter link in TOC is clicked
        function onTocItemClick(event, chNum) {{
            if (window.innerWidth <= 992) {{
                closeSidebar();
            }}
        }}

        // Theme Toggle
        function toggleTheme() {{
            const current = document.body.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', target);
            localStorage.setItem('med5_theme', target);
        }}

        // Restore Theme Preference
        const savedTheme = localStorage.getItem('med5_theme');
        if (savedTheme) {{
            document.body.setAttribute('data-theme', savedTheme);
        }}

        // Client-side Instant Filter
        function filterChapters() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const items = document.querySelectorAll('.toc-item');
            const articles = document.querySelectorAll('.chapter-card');

            items.forEach((item, idx) => {{
                const text = item.innerText.toLowerCase();
                const card = articles[idx];
                const cardText = card.innerText.toLowerCase();
                if (!query || text.includes(query) || cardText.includes(query)) {{
                    item.style.display = 'flex';
                    card.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                    card.style.display = 'none';
                }}
            }});
        }}

        // Scroll to Top
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // Show/Hide Back to Top Button
        const backToTopBtn = document.getElementById('backToTopBtn');
        window.addEventListener('scroll', () => {{
            if (window.scrollY > 350) {{
                backToTopBtn.classList.add('visible');
            }} else {{
                backToTopBtn.classList.remove('visible');
            }}
        }}, {{ passive: true }});
    </script>
</body>
</html>
"""
    return html_template

def main():
    print("Compiling Modern Responsive Orthopedic Textbook Web Edition...")
    chapters, total_words = load_markdown_chapters()
    print(f"Loaded {len(chapters)} authored chapters ({total_words:,} words total).")
    
    html_out = generate_html(chapters, total_words)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_out)
    with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
        f.write(html_out)
        
    print(f"Successfully generated standalone HTML reader:")
    print(f"  -> {OUTPUT_HTML} ({len(html_out):,} bytes)")
    print(f"  -> {OUTPUT_INDEX}")

if __name__ == "__main__":
    main()
