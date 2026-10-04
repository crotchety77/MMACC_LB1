# -*- coding: utf-8 -*-
"""
Динамический генератор чистового отчёта по Лабораторной работе №1
в формате Microsoft Word (.docx).

Скрипт автоматически считывает исходные суждения экспертов из input.txt
(или указанного файла), производит строгий математический расчёт всеми методами
ядра expert_estimate и формирует готовый академический документ со всеми таблицами,
формулами, динамическими сравнительными выводами и приложениями с кодом.
"""

import sys
from pathlib import Path
from statistics import median
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from expert_estimate.transform import transform_data, get_objects
from expert_estimate.stats import (
    get_ranks_sum, get_ranks_average, get_ranks_median,
    get_ranking_by_average, get_ranking_by_median
)
from expert_estimate.relations import get_binary_relations, build_distance_matrix
from expert_estimate.kemeny import (
    get_preference_vectors, build_loss_matrix, solve_assignment,
    get_all_assignment_optima, get_all_kemeny_medians_bruteforce,
    get_kemeny_medians_by_experts, kemeny_total_distance
)

BASE_DIR = Path(r"c:\Users\Foxi8\OneDrive\Рабочий стол\ММАСС_ЛБ1")
OUTPUT_DOCX = BASE_DIR / "Лабораторная_работа_1_Экспертные_оценки.docx"


def set_cell_background(cell, fill_hex):
    """Устанавливает цвет фона ячейки таблицы."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Устанавливает внутренние отступы ячейки."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="A0AEC0", sz="6", val="single"):
    """Устанавливает академические границы таблицы."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table(table, col_widths, col_alignments, header_bg="EAEFF5", monospace_cols=None):
    """Форматирует таблицу: ширины колонок, выравнивание, запрет разрыва строк."""
    if monospace_cols is None:
        monospace_cols = set()
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="A0AEC0", sz="6", val="single")

    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for j, cell in enumerate(row.cells):
            cell.width = col_widths[j]
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

            if i == 0:
                set_cell_background(cell, header_bg)

            align = col_alignments[j]
            for p in cell.paragraphs:
                p.alignment = align
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                for run in p.runs:
                    if j in monospace_cols and i > 0:
                        run.font.name = "Consolas"
                        run.font.size = Pt(9.5)
                    else:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(10.5)
                    if i == 0:
                        run.font.bold = True


def add_page_number(run):
    """Добавляет динамический номер страницы."""
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    run._r.append(fldSimple)


def load_input_data(file_path: Path):
    """Считывает текстовый файл экспертных ранжирований."""
    text = file_path.read_text(encoding="utf-8").strip()
    raw_lines = [line.strip().split() for line in text.splitlines() if line.strip()]
    raw_table = {i + 1: items for i, items in enumerate(raw_lines)}
    return raw_table


def format_ranking_str(ranking_list):
    """Преобразует список объектов в читаемый вид a1 ≻ a2 ≻ a3."""
    return " ≻ ".join(ranking_list)


def format_matrix_brackets(matrix_named, rows, cols):
    """Преобразует NamedMatrix в красивое моноширинное текстовое матричное представление."""
    lines = []
    for r in rows:
        vals = "  ".join(str(matrix_named[r, c]) for c in cols)
        lines.append(f"[ {vals} ]")
    return "\n".join(lines)


def build_report(input_file: Path = BASE_DIR / "input.txt"):
    print(f"Считывание данных из: {input_file}")
    raw_table = load_input_data(input_file)
    table = transform_data(raw_table)
    objects = get_objects(table)
    m_experts = len(table)
    n_objects = len(objects)

    print(f"Количество экспертов: {m_experts}, количество альтернатив: {n_objects}")
    print(f"Объекты: {objects}")

    # =========================================================================
    # ВЫЧИСЛЕНИЯ ВСЕХ МЕТОДОВ ЧЕРЕЗ EXPERT_ESTIMATE
    # =========================================================================
    # 1. Средние арифметические ранги
    ranks_sum = get_ranks_sum(table)
    ranks_avg = get_ranks_average(ranks_sum, m_experts)
    avg_ranking = get_ranking_by_average(table)

    # 2. Медианные ранги и вариационные ряды
    ranks_by_obj = {}
    for ranks in table.values():
        for obj, r in ranks.items():
            ranks_by_obj.setdefault(obj, []).append(r)
    var_series = {obj: sorted(ranks_by_obj[obj]) for obj in objects}
    ranks_med = get_ranks_median(table)
    med_ranking = get_ranking_by_median(table)

    # 3. Бинарные отношения и расстояния Кемени
    bin_rels = get_binary_relations(table, objects)
    dist_matrix = build_distance_matrix(bin_rels)
    sums_dist = {r: sum(dist_matrix[r, c] for c in dist_matrix.cols) for r in dist_matrix.rows}
    min_dist_val = min(sums_dist.values())
    best_experts = get_kemeny_medians_by_experts(dist_matrix)

    # 4. Векторы предпочтений и матрица потерь
    pvs = get_preference_vectors(table, objects)
    loss = build_loss_matrix(pvs, objects)

    # 5. Задача о назначениях
    assign_orders, min_assign_loss = get_all_assignment_optima(loss, objects)
    assign_sol_places, _ = solve_assignment(loss, objects)

    # 6. Истинная медиана Кемени (полный перебор)
    kemeny_orders, min_kemeny_dist = get_all_kemeny_medians_bruteforce(bin_rels, objects)

    # Расстояния Кемени для решений задачи назначений
    assign_kemeny_dists = [kemeny_total_distance(order, bin_rels, objects) for order in assign_orders]

    # Создание документа Word
    doc = docx.Document()

    # Поля страницы ГОСТ: левое 3.0 см, правое 1.5 см, верхнее 2.0 см, нижнее 2.0 см
    for section in doc.sections:
        section.top_margin = docx.shared.Cm(2.0)
        section.bottom_margin = docx.shared.Cm(2.0)
        section.left_margin = docx.shared.Cm(3.0)
        section.right_margin = docx.shared.Cm(1.5)
        section.different_first_page_header_footer = True

        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f_run = f_p.add_run()
        f_run.font.name = "Times New Roman"
        f_run.font.size = Pt(11)
        f_run.font.color.rgb = RGBColor(100, 100, 100)
        add_page_number(f_run)

    # Базовые стили
    style_normal = doc.styles["Normal"]
    style_normal.font.name = "Times New Roman"
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(20, 20, 20)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(4)

    h1_style = doc.styles["Heading 1"]
    h1_style.font.name = "Times New Roman"
    h1_style.font.size = Pt(14)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(15, 23, 42)
    h1_style.paragraph_format.space_before = Pt(14)
    h1_style.paragraph_format.space_after = Pt(6)
    h1_style.paragraph_format.first_line_indent = 0
    h1_style.paragraph_format.keep_with_next = True

    h2_style = doc.styles["Heading 2"]
    h2_style.font.name = "Times New Roman"
    h2_style.font.size = Pt(12.5)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(30, 41, 59)
    h2_style.paragraph_format.space_before = Pt(10)
    h2_style.paragraph_format.space_after = Pt(4)
    h2_style.paragraph_format.first_line_indent = 0
    h2_style.paragraph_format.keep_with_next = True

    def add_p(text="", first_indent=1.25, space_before=0, space_after=4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.first_line_indent = docx.shared.Cm(first_indent) if first_indent else 0
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if text:
            run = p.add_run(text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.bold = bold
            run.font.italic = italic
        return p

    def add_h1(text):
        p = doc.add_heading(text, level=1)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        return p

    def add_h2(text):
        p = doc.add_heading(text, level=2)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        return p

    def add_table_title(title_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_formula(formula_text, formula_num=""):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = 0
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(formula_text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.font.italic = True
        if formula_num:
            run_num = p.add_run(f"\t\t({formula_num})")
            run_num.font.name = "Times New Roman"
            run_num.font.size = Pt(12)
            run_num.font.italic = False
        return p

    # =========================================================================
    # 1. ТИТУЛЬНЫЙ ЛИСТ
    # =========================================================================
    p_top = add_p("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", first_indent=0, space_before=10, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    p_top.runs[0].font.size = Pt(10)
    p_univ = add_p("[Наименование высшего учебного заведения / университета]", first_indent=0, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_univ.runs[0].font.size = Pt(10)
    p_inst = add_p("Институт / Факультет: ________________________________________________", first_indent=0, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_inst.runs[0].font.size = Pt(10)
    p_dep = add_p("Кафедра: ___________________________________________________________", first_indent=0, space_before=0, space_after=40, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_dep.runs[0].font.size = Pt(10)

    p_dis = add_p("Дисциплина: «Математические методы анализа сложных систем»", first_indent=0, space_before=20, space_after=15, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    p_dis.runs[0].font.size = Pt(12)

    p_title = add_p("ОТЧЁТ ПО ЛАБОРАТОРНОЙ РАБОТЕ № 1", first_indent=0, space_before=15, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    p_title.runs[0].font.size = Pt(16)

    p_sub = add_p("«Исследование сложных систем методом экспертных оценок»", first_indent=0, space_before=0, space_after=120, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    p_sub.runs[0].font.size = Pt(14)

    p_sign1 = add_p("Выполнил:", first_indent=8.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    p_sign2 = add_p("Студент группы: __________________", first_indent=8.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
    p_sign3 = add_p("Ф.И.О.: __________________________", first_indent=8.5, space_before=0, space_after=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    p_sign4 = add_p("Проверил:", first_indent=8.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    p_sign5 = add_p("Должность, звание: _______________", first_indent=8.5, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.LEFT)
    p_sign6 = add_p("Ф.И.О.: __________________________", first_indent=8.5, space_before=0, space_after=90, align=WD_ALIGN_PARAGRAPH.LEFT)

    p_city = add_p("г. ___________________ — 2026 г.", first_indent=0, space_before=30, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    p_city.runs[0].font.size = Pt(11)

    doc.add_page_break()

    # =========================================================================
    # 2. ОГЛАВЛЕНИЕ И ВВЕДЕНИЕ
    # =========================================================================
    add_h1("ОГЛАВЛЕНИЕ")
    toc_lines = [
        ("ВВЕДЕНИЕ И ПОСТАНОВКА ЗАДАЧИ", "3"),
        ("1. ТЕОРЕТИЧЕСКИЕ СВЕДЕНИЯ", "4"),
        ("   1.1. Экспертное оценивание, понятие ранга и групповое упорядочение", "4"),
        ("   1.2. Метод средних арифметических рангов", "4"),
        ("   1.3. Метод медианных рангов", "5"),
        ("   1.4. Метод медианы Кемени на бинарных отношениях", "5"),
        ("   1.5. Расстояние Кемени и его связь с числом попарных инверсий", "6"),
        ("   1.6. Векторы предпочтений и позиционная L1-матрица потерь", "6"),
        ("   1.7. Задача о назначениях", "7"),
        ("   1.8. Поиск истинной медианы Кемени полным перебором перестановок", "7"),
        ("2. ИСХОДНЫЕ ДАННЫЕ", "8"),
        ("3. РЕЗУЛЬТАТЫ ОБРАБОТКИ ЭКСПЕРТНЫХ ОЦЕНОК", "9"),
        ("   3.1. Расчёт средних арифметических рангов", "9"),
        ("   3.2. Расчёт медианных рангов", "10"),
        ("   3.3. Матрицы бинарных отношений экспертов", "11"),
        ("   3.4. Матрица попарных расстояний Кемени и медианы среди экспертов", "12"),
        ("   3.5. Векторы предпочтений и матрица потерь", "13"),
        ("   3.6. Решение задачи о назначениях", "14"),
        ("   3.7. Поиск истинной медианы Кемени на полном множестве перестановок", "15"),
        ("4. СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТОДОВ", "16"),
        ("   4.1. Сопоставление полученных результатов", "16"),
        ("   4.2. Анализ различия целевых функций задачи о назначениях и медианы Кемени", "17"),
        ("   4.3. Содержательная интерпретация группового выбора", "18"),
        ("5. ЗАКЛЮЧЕНИЕ", "19"),
        ("ПРИЛОЖЕНИЕ. ИСХОДНЫЙ КОД ПРОГРАММЫ", "20"),
    ]
    for title, pg in toc_lines:
        p_t = add_p(first_indent=0, space_before=1, space_after=2)
        r1 = p_t.add_run(title)
        r1.font.size = Pt(11)
        dots_count = max(5, 68 - len(title))
        r_dots = p_t.add_run(f"  {'.' * dots_count}  ")
        r_dots.font.color.rgb = RGBColor(160, 160, 160)
        r2 = p_t.add_run(pg)
        r2.font.size = Pt(11)
        r2.font.bold = True

    add_h1("ВВЕДЕНИЕ И ПОСТАНОВКА ЗАДАЧИ")
    add_p(
        "Цель лабораторной работы: изучить основные математические методы агрегирования результатов "
        "экспертного опроса при анализе сложных систем и разработать программный комплекс для обработки "
        "ранжирований следующими классическими методами:"
    )
    add_p("• метод средних арифметических рангов;", first_indent=1.5, space_before=1, space_after=1)
    add_p("• метод медианных рангов;", first_indent=1.5, space_before=1, space_after=1)
    add_p(
        "• метод медианы Кемени (с вычислением как на множестве мнений экспертов, так и на полном множестве "
        "всех возможных строгих ранжирований методом перебора перестановок);",
        first_indent=1.5, space_before=1, space_after=1
    )
    add_p("• оптимизационный метод на основе векторов предпочтений через решение задачи о назначениях.", first_indent=1.5, space_before=1, space_after=3)

    add_p("В соответствии со спецификацией задания в отчёте приводятся:")
    add_p("1) матрицы бинарных отношений для каждого эксперта комиссии;", first_indent=1.5, space_after=1)
    add_p("2) матрица попарных расстояний между ранжировками экспертов и суммы расстояний по строкам;", first_indent=1.5, space_after=1)
    add_p("3) векторы предпочтений для каждого эксперта;", first_indent=1.5, space_after=1)
    add_p("4) матрица потерь и постановка оптимизационной задачи о назначениях;", first_indent=1.5, space_after=1)
    add_p("5) матрица оптимальных назначений и полученные порядки предпочтений;", first_indent=1.5, space_after=1)
    add_p("6) все глобальные оптимумы медианы Кемени на полном множестве перестановок;", first_indent=1.5, space_after=1)
    add_p("7) глубокий сравнительный анализ результатов всех методов и содержательная интерпретация группового выбора.", first_indent=1.5, space_after=4)

    doc.add_page_break()

    # =========================================================================
    # 3. ТЕОРЕТИЧЕСКИЕ СВЕДЕНИЯ
    # =========================================================================
    add_h1("1. ТЕОРЕТИЧЕСКИЕ СВЕДЕНИЯ")

    add_h2("1.1. Экспертное оценивание, понятие ранга и групповое упорядочение")
    add_p(
        "Экспертное оценивание представляет собой формализованную процедуру получения обобщённых оценок "
        "сложных систем на основе суждений группы квалифицированных специалистов (экспертов). "
        "Пусть исследуется совокупность из n альтернативных объектов A = {a₁, a₂, ..., aₙ}. "
        f"Группа состоит из m = {m_experts} независимых экспертов E = {{E₁, ..., E_{{{m_experts}}}}}. "
        "Каждый эксперт упорядочивает совокупность объектов в порядке убывания их приоритета. "
        "Результатом упорядочения k-м экспертом является вектор рангов rₖ = (r_{k1}, ..., r_{kn}). "
        "В соответствии с общепринятым соглашением, ранг 1 присваивается наилучшему (наиболее предпочтительному) объекту, "
        "а ранг n — наихудшему объекту. Следовательно, r_{ki} < r_{kj} означает, что для эксперта k объект aᵢ строго предпочтительнее aⱼ."
    )

    add_h2("1.2. Метод средних арифметических рангов")
    add_p(
        "В методе средних рангов порядковые номера трактуются как балльные оценки. Для каждого объекта aᵢ вычисляется суммарный балл:"
    )
    add_formula("S_i = ∑_{k=1}^{m} r_{ki}", "1")
    add_p("и средний арифметический ранг:")
    add_formula("r̄_i = S_i / m = (1 / m) ∑_{k=1}^{m} r_{ki}", "2")
    add_p(
        "Итоговое коллективное упорядочение строится по возрастанию r̄_i (наименьший средний ранг соответствует 1-му итоговому месту). "
        "При равенстве средних рангов объектам присваиваются связанные места."
    )

    add_h2("1.3. Метод медианных рангов")
    add_p(
        "Для каждого объекта aᵢ строится вариационный ряд рангов r_{(1)i} ≤ r_{(2)i} ≤ ... ≤ r_{(m)i}. "
        "Медианный ранг Me_i определяется как квантиль порядка 0.5:"
    )
    if m_experts % 2 != 0:
        med_idx = (m_experts + 1) // 2
        add_formula(f"Me_i = r_{{({med_idx})i}},   поскольку m = {m_experts} (нечётное число)", "3")
        add_p(
            f"Для нечётного числа экспертов (m = {m_experts}) медианный ранг равен рангу центрального ({med_idx}-го) члена "
            "вариационного ряда и всегда принимает целочисленное значение."
        )
    else:
        k1 = m_experts // 2
        k2 = k1 + 1
        add_formula(f"Me_i = (r_{{({k1})i}} + r_{{({k2})i}}) / 2,   поскольку m = {m_experts} (чётное число)", "3")
        add_p(
            f"Для чётного числа экспертов (m = {m_experts}) медиана вычисляется как среднее арифметическое "
            f"{k1}-го и {k2}-го членов упорядоченного ряда оценок."
        )

    add_h2("1.4. Метод медианы Кемени на бинарных отношениях")
    add_p(
        "В аксиоматической теории Кемени — Снелла каждое строгое ранжирование эксперта k представляется "
        "бинарной матрицей нестрогого предпочтения Aₖ = (x^{(k)}_{ij}) размера n × n, где элементы задаются правилом:"
    )
    add_formula("x^{(k)}_{ij} = 1, если r_{ki} ≥ r_{kj};    x^{(k)}_{ij} = 0, если r_{ki} < r_{kj}", "4")
    add_p(
        "Диагональные элементы всегда равны единице (x^{(k)}_{ii} = 1). Элемент x_{ij} = 0 означает, что объект aᵢ строго лучше объекта aⱼ, "
        "а x_{ij} = 1 — что объект aᵢ уступает или равен объекту aⱼ."
    )

    add_h2("1.5. Расстояние Кемени и его связь с числом попарных инверсий")
    add_p("Расстояние между ранжированиями A и B определяется суммой поэлементных модулей разностей:")
    add_formula("d(A, B) = ∑_{i=1}^{n} ∑_{j=1}^{n} |a_{ij} - b_{ij}|", "5")
    add_p(
        "На главной диагонали |a_{ii} - b_{ii}| = |1 - 1| = 0 (диагональ не вносит вклада). "
        "Для любой пары объектов (aᵢ, aⱼ), если порядок их взаимного предпочтения у экспертов различен, "
        "в ячейке (i, j) разность равна 1, и в ячейке (j, i) разность также равна 1 (|0 - 1| + |1 - 0| = 2). "
        "Следовательно, реализованное расстояние строго равно удвоенному числу инверсий I(A, B):"
    )
    add_formula("d(A, B) = 2 · I(A, B)", "6")
    add_p(
        "где I(A, B) — число несогласованных пар альтернатив (число инверсий перестановки). "
        "Оно не является коэффициентом корреляции Кендалла τ (который нормируется на интервал [-1; 1]), "
        "а представляет собой абсолютную дискретную метрику расстояния на перестановках."
    )

    add_h2("1.6. Векторы предпочтений и позиционная L1-матрица потерь")
    add_p("Для каждого эксперта строится вектор предпочтений π^{(k)}, координата πᵢ^{(k)} которого равна числу объектов, лучших aᵢ:")
    add_formula("π_i^{(k)} = ∑_{j ≠ i} 𝕀(r_{kj} < r_{ki}) = r_{ki} - 1", "7")
    add_p(
        "На основе векторов предпочтений строится матрица потерь R = (r_{ij}) размера n × n, где r_{ij} отражает суммарный "
        "позиционный штраф за назначение объекта aᵢ на j-е итоговое место:"
    )
    add_formula("r_{ij} = ∑_{k=1}^{m} |(j - 1) - π_i^{(k)}|", "8")

    add_h2("1.7. Задача о назначениях")
    add_p("Оптимизационная модель минимизации позиционных потерь имеет вид задачи о назначениях:")
    add_formula("Φ_{Assign}(X) = ∑_{i=1}^{n} ∑_{j=1}^{n} r_{ij} X_{ij} → min", "9")
    add_formula("∑_{j=1}^{n} X_{ij} = 1,   ∑_{i=1}^{n} X_{ij} = 1,   X_{ij} ∈ {0, 1}", "10")

    add_h2("1.8. Поиск истинной медианы Кемени полным перебором перестановок")
    add_p(
        "Истинной медианой Кемени называется строгое ранжирование R*, минимизирующее сумму попарных расстояний Кемени "
        "до всех экспертов на множестве всех n! перестановок 𝒫ₙ:"
    )
    add_formula("R* = argmin_{R ∈ 𝒫_n} Φ_{Kemeny}(R) = argmin_{R ∈ 𝒫_n} ∑_{k=1}^{m} d(R, R_k)", "11")

    doc.add_page_break()

    # =========================================================================
    # 4. ИСХОДНЫЕ ДАННЫЕ
    # =========================================================================
    add_h1("2. ИСХОДНЫЕ ДАННЫЕ")
    add_p(
        f"В исследуемом варианте экспертная комиссия состоит из m = {m_experts} экспертов, "
        f"оценивающих совокупность из n = {n_objects} альтернативных проектов A = {{{', '.join(objects)}}}. "
        "Исходные протоколы ранжирования приведены в таблице 1."
    )

    add_table_title("Таблица 1 — Исходные протоколы ранжирования экспертов")
    t1 = doc.add_table(rows=m_experts + 1, cols=3)
    t1_headers = ["Обозначение эксперта", "Порядковое суждение эксперта (от лучшего к худшему)", "Текстовый вектор"]
    for j, h in enumerate(t1_headers):
        t1.rows[0].cells[j].paragraphs[0].text = h
    for i in range(1, m_experts + 1):
        raw_seq = raw_table[i]
        t1.rows[i].cells[0].paragraphs[0].text = f"Эксперт Э_{i}"
        t1.rows[i].cells[1].paragraphs[0].text = format_ranking_str(raw_seq)
        t1.rows[i].cells[2].paragraphs[0].text = " ".join(raw_seq)
    format_table(t1, [docx.shared.Cm(4.0), docx.shared.Cm(8.0), docx.shared.Cm(4.5)],
                 [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER])

    add_p(
        "На основе индивидуальных суждений строится матрица рангов объектов «Эксперт × Объект», "
        "где наивысший приоритет имеет ранг 1 (таблица 2)."
    )

    add_table_title("Таблица 2 — Матрица рангов объектов (r_ki)")
    t2 = doc.add_table(rows=m_experts + 1, cols=n_objects + 1)
    t2.rows[0].cells[0].paragraphs[0].text = "Эксперт"
    for j, obj in enumerate(objects, start=1):
        t2.rows[0].cells[j].paragraphs[0].text = obj
    for i in range(1, m_experts + 1):
        t2.rows[i].cells[0].paragraphs[0].text = f"Э_{i}"
        for j, obj in enumerate(objects, start=1):
            t2.rows[i].cells[j].paragraphs[0].text = str(table[i][obj])
    col_w = docx.shared.Cm(13.0 / n_objects)
    format_table(t2, [docx.shared.Cm(3.5)] + [col_w] * n_objects,
                 [WD_ALIGN_PARAGRAPH.CENTER] * (n_objects + 1))

    doc.add_page_break()

    # =========================================================================
    # 5. РЕЗУЛЬТАТЫ ОБРАБОТКИ
    # =========================================================================
    add_h1("3. РЕЗУЛЬТАТЫ ОБРАБОТКИ ЭКСПЕРТНЫХ ОЦЕНОК")

    add_h2("3.1. Расчёт средних арифметических рангов")
    add_p("По формулам (1) и (2) вычислены суммы рангов Sᵢ и средние ранги r̄ᵢ (таблица 3).")

    add_table_title("Таблица 3 — Результаты ранжирования методом средних арифметических рангов")
    t3 = doc.add_table(rows=n_objects + 1, cols=5)
    t3_headers = ["Объект", "Сумма рангов Sᵢ", "Формула усреднения", "Средний ранг r̄ᵢ", "Итоговое место"]
    for j, h in enumerate(t3_headers):
        t3.rows[0].cells[j].paragraphs[0].text = h
    for idx, (p_place, obj, r_val) in enumerate(avg_ranking, start=1):
        t3.rows[idx].cells[0].paragraphs[0].text = obj
        t3.rows[idx].cells[1].paragraphs[0].text = str(ranks_sum[obj])
        t3.rows[idx].cells[2].paragraphs[0].text = f"{ranks_sum[obj]} / {m_experts}"
        t3.rows[idx].cells[3].paragraphs[0].text = f"{r_val:.2f}"
        t3.rows[idx].cells[4].paragraphs[0].text = str(p_place)
    format_table(t3, [docx.shared.Cm(2.5), docx.shared.Cm(3.5), docx.shared.Cm(3.5), docx.shared.Cm(3.5), docx.shared.Cm(3.5)],
                 [WD_ALIGN_PARAGRAPH.CENTER] * 5)

    avg_order_str = " ≻ ".join(obj for _, obj, _ in avg_ranking)
    add_p(f"Результирующий порядок по методу средних арифметических рангов: {avg_order_str}.")

    add_h2("3.2. Расчёт медианных рангов")
    add_p("Для каждого объекта построен вариационный ряд и вычислен медианный ранг (таблица 4).")

    add_table_title("Таблица 4 — Результаты ранжирования методом медианных рангов")
    t4 = doc.add_table(rows=n_objects + 1, cols=5)
    t4_headers = ["Объект", "Вариационный ряд рангов", "Расчёт медианы", "Медианный ранг Me_i", "Итоговое место"]
    for j, h in enumerate(t4_headers):
        t4.rows[0].cells[j].paragraphs[0].text = h
    for idx, (p_place, obj, med_val) in enumerate(med_ranking, start=1):
        v_list = var_series[obj]
        v_str = "(" + ", ".join(map(str, v_list)) + ")"
        if m_experts % 2 != 0:
            calc_str = f"r_({(m_experts+1)//2}) = {v_list[(m_experts-1)//2]}"
        else:
            k1 = m_experts // 2 - 1
            calc_str = f"({v_list[k1]} + {v_list[k1+1]}) / 2"
        t4.rows[idx].cells[0].paragraphs[0].text = obj
        t4.rows[idx].cells[1].paragraphs[0].text = v_str
        t4.rows[idx].cells[2].paragraphs[0].text = calc_str
        t4.rows[idx].cells[3].paragraphs[0].text = f"{med_val:.2f}"
        t4.rows[idx].cells[4].paragraphs[0].text = str(p_place)
    format_table(t4, [docx.shared.Cm(2.5), docx.shared.Cm(4.5), docx.shared.Cm(3.5), docx.shared.Cm(3.0), docx.shared.Cm(3.0)],
                 [WD_ALIGN_PARAGRAPH.CENTER] * 5)

    med_order_str = " ≻ ".join(obj for _, obj, _ in med_ranking)
    add_p(f"Результирующий порядок по методу медианных рангов: {med_order_str}.")

    doc.add_page_break()

    # =========================================================================
    # 6. БИНАРНЫЕ ОТНОШЕНИЯ И КЕМЕНИ
    # =========================================================================
    add_h2("3.3. Матрицы бинарных отношений экспертов")
    add_p(
        "На основе формулы (4) сформированы матрицы отношений нестрогого предпочтения Aₖ размера n × n. "
        "Диагональные элементы равны 1, x_{ij} = 0 означает строгое доминирование aᵢ над aⱼ (таблица 5)."
    )

    add_table_title(f"Таблица 5 — Матрицы бинарных отношений экспертов A₁–A_{m_experts}")
    t5 = doc.add_table(rows=m_experts + 1, cols=3)
    t5_headers = ["Эксперт", "Ранжирование эксперта", f"Матрица отношений Aₖ ({n_objects} × {n_objects})"]
    for j, h in enumerate(t5_headers):
        t5.rows[0].cells[j].paragraphs[0].text = h
    for i in range(1, m_experts + 1):
        t5.rows[i].cells[0].paragraphs[0].text = f"Эксперт Э_{i}"
        t5.rows[i].cells[1].paragraphs[0].text = format_ranking_str(raw_table[i])
        t5.rows[i].cells[2].paragraphs[0].text = format_matrix_brackets(bin_rels[i], objects, objects)
    format_table(t5, [docx.shared.Cm(3.0), docx.shared.Cm(6.0), docx.shared.Cm(7.5)],
                 [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER],
                 monospace_cols={2})

    add_h2("3.4. Матрица попарных расстояний Кемени и медианы среди экспертов")
    add_p(
        f"По формуле (5) рассчитана матрица попарных расстояний D размера {m_experts} × {m_experts}. "
        "Для каждого эксперта вычислена сумма расстояний по строке S_k (таблица 6)."
    )

    add_table_title("Таблица 6 — Матрица попарных расстояний Кемени D и суммы строк S_k")
    t6 = doc.add_table(rows=m_experts + 1, cols=m_experts + 2)
    t6.rows[0].cells[0].paragraphs[0].text = "Эксперт"
    for j in range(1, m_experts + 1):
        t6.rows[0].cells[j].paragraphs[0].text = f"Э_{j}"
    t6.rows[0].cells[m_experts + 1].paragraphs[0].text = "Сумма строки S_k"

    for i in range(1, m_experts + 1):
        t6.rows[i].cells[0].paragraphs[0].text = f"Э_{i}"
        for j in range(1, m_experts + 1):
            t6.rows[i].cells[j].paragraphs[0].text = str(dist_matrix[str(i), str(j)])
        is_best = str(i) in best_experts
        best_mark = "  (минимум)" if is_best else ""
        t6.rows[i].cells[m_experts + 1].paragraphs[0].text = f"{sums_dist[str(i)]}{best_mark}"

    col_d_w = docx.shared.Cm(11.0 / m_experts)
    format_table(t6, [docx.shared.Cm(2.2)] + [col_d_w] * m_experts + [docx.shared.Cm(3.3)],
                 [WD_ALIGN_PARAGRAPH.CENTER] * (m_experts + 2))

    best_exps_str = ", ".join(f"Э_{k}" for k in best_experts)
    add_p(
        f"Минимальная сумма попарных расстояний на выборке экспертов составляет S_min = {min_dist_val} "
        f"и достигается на эксперте(-ах): {best_exps_str}. "
        "Данные ранжирования являются медианами на множестве предложенных экспертных мнений."
    )

    doc.add_page_break()

    # =========================================================================
    # 7. ВЕКТОРЫ ПРЕДПОЧТЕНИЙ И МАТРИЦА ПОТЕРЬ
    # =========================================================================
    add_h2("3.5. Векторы предпочтений и матрица потерь")
    add_p("По формуле (7) построены векторы предпочтений π^{(k)} (таблица 7).")

    add_table_title("Таблица 7 — Векторы предпочтений экспертов π^(k)")
    t7 = doc.add_table(rows=m_experts + 1, cols=n_objects + 1)
    t7.rows[0].cells[0].paragraphs[0].text = "Эксперт"
    for j, obj in enumerate(objects, start=1):
        t7.rows[0].cells[j].paragraphs[0].text = obj
    for i in range(1, m_experts + 1):
        t7.rows[i].cells[0].paragraphs[0].text = f"Э_{i}"
        for j, obj in enumerate(objects, start=1):
            t7.rows[i].cells[j].paragraphs[0].text = str(pvs[i][obj])
    format_table(t7, [docx.shared.Cm(3.5)] + [col_w] * n_objects,
                 [WD_ALIGN_PARAGRAPH.CENTER] * (n_objects + 1))

    add_p("На основе векторов предпочтений формируется матрица потерь r_{ij} (таблица 8).")

    add_table_title("Таблица 8 — Матрица позиционных потерь r_ij")
    t8 = doc.add_table(rows=n_objects + 1, cols=n_objects + 1)
    t8.rows[0].cells[0].paragraphs[0].text = "Объект \\ Место"
    for j in range(1, n_objects + 1):
        t8.rows[0].cells[j].paragraphs[0].text = f"Место {j}"
    for i, obj in enumerate(objects, start=1):
        t8.rows[i].cells[0].paragraphs[0].text = obj
        for j in range(1, n_objects + 1):
            t8.rows[i].cells[j].paragraphs[0].text = str(loss[obj, str(j)])
    format_table(t8, [docx.shared.Cm(3.5)] + [col_w] * n_objects,
                 [WD_ALIGN_PARAGRAPH.CENTER] * (n_objects + 1))

    first_obj = objects[0]
    calc_terms = [f"|0 - {pvs[k][first_obj]}|" for k in range(1, m_experts + 1)]
    calc_vals = [abs(0 - pvs[k][first_obj]) for k in range(1, m_experts + 1)]
    add_p(f"Пример ручного расчёта ячейки r_{{1,1}} (штраф за назначение объекта {first_obj} на 1-е место):")
    add_formula(
        f"r_{{1,1}} = ∑_{{k=1}}^{{{m_experts}}} |(1 - 1) - π_{{{first_obj}}}^{{(k)}}| = "
        f"{' + '.join(calc_terms)} = {' + '.join(map(str, calc_vals))} = {loss[first_obj, '1']}", "12"
    )

    add_h2("3.6. Решение задачи о назначениях")
    add_p(
        f"Решение оптимизационной задачи о назначениях с матрицей r_{{ij}} обеспечивает минимум целевой функции "
        f"Φ_{{Assign}} = {min_assign_loss}. Найдено оптимальных решений: {len(assign_orders)}. "
        "Одно из решений задаётся матрицей назначений X (таблица 9)."
    )

    add_table_title("Таблица 9 — Оптимальная матрица назначений X")
    t9 = doc.add_table(rows=n_objects + 1, cols=n_objects + 1)
    t9.rows[0].cells[0].paragraphs[0].text = "Объект \\ Место"
    for j in range(1, n_objects + 1):
        t9.rows[0].cells[j].paragraphs[0].text = f"Место {j}"
    for i, obj in enumerate(objects, start=1):
        t9.rows[i].cells[0].paragraphs[0].text = obj
        assigned_place = assign_sol_places[obj]
        for j in range(1, n_objects + 1):
            t9.rows[i].cells[j].paragraphs[0].text = "1" if j == assigned_place else "0"
    format_table(t9, [docx.shared.Cm(3.5)] + [col_w] * n_objects,
                 [WD_ALIGN_PARAGRAPH.CENTER] * (n_objects + 1))

    add_p("Оптимальные решения задачи о назначениях:")
    for idx, (ord_list, d_val) in enumerate(zip(assign_orders, assign_kemeny_dists), start=1):
        add_p(
            f"{idx}. {format_ranking_str(ord_list)}   "
            f"(целевая функция назначений Φ_{{Assign}} = {min_assign_loss}, истинное расстояние Кемени Σ d = {d_val});",
            first_indent=1.5, space_after=2
        )

    doc.add_page_break()

    # =========================================================================
    # 8. ПОЛНЫЙ ПЕРЕБОР КЕМЕНИ
    # =========================================================================
    add_h2("3.7. Поиск истинной медианы Кемени на полном множестве перестановок")
    add_p(
        f"Полный перебор всех {n_objects}! = 120 перестановок обеспечивает нахождение глобального минимума "
        "суммы попарных расстояний Кемени:"
    )
    add_formula(f"min_{{R ∈ 𝒫_{n_objects}}} Φ_{{Kemeny}}(R) = min ∑_{{k=1}}^{{{m_experts}}} d(R, R_k) = {min_kemeny_dist}", "13")
    add_p(f"Число найденных глобальных медиан Кемени: {len(kemeny_orders)}.")
    for idx, km_ord in enumerate(kemeny_orders, start=1):
        add_p(f"{idx}. {format_ranking_str(km_ord)}   (сумма расстояний Кемени Σ d = {min_kemeny_dist});", first_indent=1.5, space_after=2)

    # =========================================================================
    # 9. СРАВНИТЕЛЬНЫЙ АНАЛИЗ
    # =========================================================================
    add_h1("4. СРАВНИТЕЛЬНЫЙ АНАЛИЗ МЕТОДОВ")

    add_h2("4.1. Сопоставление полученных результатов")
    add_p("Сведём результаты расчёта всеми исследованными методами в единую сравнительную таблицу (таблица 10).")

    add_table_title("Таблица 10 — Сводная таблица результатов агрегирования мнений экспертов")
    t10 = doc.add_table(rows=6, cols=3)
    t10_headers = ["Метод агрегирования", "Оптимизируемый критерий / целевая функция", "Полученный результат ранжирования"]
    for j, h in enumerate(t10_headers):
        t10.rows[0].cells[j].paragraphs[0].text = h

    t10_rows_data = [
        ("Средние арифметические ранги", "r̄ᵢ = (1/m) ∑ r_{ki} → min", f"{avg_order_str}\n(ранги от наименьшего к наибольшему)"),
        ("Медианные ранги", "Me_i = median(r_{ki}) → min", f"{med_order_str}\n(робастное медианное упорядочение)"),
        (
            "Медиана среди мнений экспертов",
            "S_k = ∑_{l=1}^{m} D_{kl} → min",
            f"Эксперт(-ы) {best_exps_str} (S_min = {min_dist_val}):\n" +
            "\n".join(f"Э_{k}: {format_ranking_str(raw_table[int(k)])}" for k in best_experts)
        ),
        (
            "Позиционная задача о назначениях",
            "Φ_{Assign} = ∑ r_{ij} X_{ij} → min",
            f"Минимум позиционных потерь: {min_assign_loss}\n"
            f"Решений: {len(assign_orders)}\n"
            f"Например: {format_ranking_str(assign_orders[0])}\n"
            f"(расстояние Кемени Σ d = {assign_kemeny_dists[0]})"
        ),
        (
            "Истинная медиана Кемени (полный перебор)",
            f"Φ_{{Kemeny}} = ∑ d(R, R_k) → min на 𝒫_{n_objects}",
            f"Минимум истинного расстояния: {min_kemeny_dist}\n"
            f"Число глобальных оптимумов: {len(kemeny_orders)}\n"
            f"Оптимум: {format_ranking_str(kemeny_orders[0])}"
        ),
    ]

    for idx, (m_name, m_crit, m_res) in enumerate(t10_rows_data, start=1):
        t10.rows[idx].cells[0].paragraphs[0].text = m_name
        t10.rows[idx].cells[1].paragraphs[0].text = m_crit
        t10.rows[idx].cells[2].paragraphs[0].text = m_res
    format_table(t10, [docx.shared.Cm(4.5), docx.shared.Cm(5.0), docx.shared.Cm(7.0)],
                 [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    add_h2("4.2. Анализ различия целевых функций задачи о назначениях и медианы Кемени")
    add_p(
        f"Ключевым теоретическим выводом проведённого исследования является различие минимумов целевых функций: "
        f"значение {min_assign_loss} получено для задачи о назначениях, а значение {min_kemeny_dist} — для медианы Кемени. "
        "Эти величины представляют собой минимумы принципиально разных критериев:"
    )
    add_p(
        f"1. Значение {min_assign_loss} получено минимизацией позиционной L1-функции потерь (формула 9). "
        "Оно оценивает суммарное отклонение координатных номеров в пространстве векторов предпочтений π.",
        first_indent=1.5, space_after=2
    )
    add_p(
        f"2. Значение {min_kemeny_dist} получено минимизацией суммы попарных расстояний Кемени — Снелла (формула 11), "
        "определённых на графах бинарных отношений через число попарных инверсий.",
        first_indent=1.5, space_after=2
    )

    # Проверка совпадения решений
    assign_set = {tuple(o) for o in assign_orders}
    kemeny_set = {tuple(o) for o in kemeny_orders}
    intersection = assign_set.intersection(kemeny_set)

    if intersection:
        add_p(
            f"В исследуемом варианте решение задачи о назначениях строго вошло в множество глобальных медиан Кемени, "
            f"что свидетельствует о высокой степени взаимной согласованности позиционной шкалы и попарных предпочтений."
        )
    else:
        first_assign = assign_orders[0]
        first_kemeny = kemeny_orders[0]
        d_assign_kemeny = assign_kemeny_dists[0]
        add_p(
            f"В исследуемом варианте оптимальное решение задачи о назначениях ({format_ranking_str(first_assign)}) "
            f"не совпадает с истинной медианой Кемени ({format_ranking_str(first_kemeny)}). "
            f"Сумма расстояний Кемени для порядка задачи о назначениях составляет {d_assign_kemeny}, что строго больше "
            f"глобального минимума {min_kemeny_dist}. "
            "Это наглядно иллюстрирует теоретическое свойство: задача о назначениях с позиционной матрицей потерь "
            "сглаживает циклические противоречия и оптимизирует другой функционал, не гарантируя глобального оптимума Кемени."
        )

    add_h2("4.3. Содержательная интерпретация группового выбора")
    # Анализ кластеризации в оптимумах Кемени
    top_candidates = [ord_list[0] for ord_list in kemeny_orders]
    bottom_candidates = [ord_list[-1] for ord_list in kemeny_orders]
    unique_top = sorted(list(set(top_candidates)))
    unique_bottom = sorted(list(set(bottom_candidates)))

    add_p(
        f"Анализ глобальных оптимумов Кемени показывает структуру коллективного приоритета: "
        f"наиболее предпочтительной(-ыми) альтернативой(-ами) на 1-м месте выступает(-ют) {', '.join(unique_top)}, "
        f"в то время как наименее предпочтительной на последнем месте однозначно признаётся {', '.join(unique_bottom)}. "
        "Результаты экспертного оценивания показывают устойчивое согласованное разделение альтернатив, "
        "а имеющиеся локальные различия между методами отражают специфику оптимизируемых математических шкал."
    )

    doc.add_page_break()

    # =========================================================================
    # 10. ЗАКЛЮЧЕНИЕ
    # =========================================================================
    add_h1("5. ЗАКЛЮЧЕНИЕ")
    add_p(
        "В ходе лабораторной работы были всесторонне исследованы основные методы обработки экспертных оценок "
        "в задачах системного анализа. Реализованный программный комплекс позволил автоматизировать расчёты "
        "методами средних арифметических рангов, медианных рангов, построить структуры бинарных отношений, "
        "определить матрицу расстояний Кемени, векторы предпочтений, матрицу позиционных потерь, "
        "решить оптимизационную задачу о назначениях и выполнить полный перебор множества перестановок."
    )
    add_p("Основные выводы по результатам работы:")
    add_p(
        f"1. Метод средних арифметических рангов сформировал порядок {avg_order_str} с лидером {avg_ranking[0][1]} "
        f"(средний ранг {avg_ranking[0][2]:.2f}). Метод чувствителен к балльной шкале и прост в расчёте.",
        first_indent=1.5, space_after=2
    )
    add_p(
        f"2. Метод медианных рангов дал порядок {med_order_str}, выделив в качестве фаворита {med_ranking[0][1]} "
        f"(медианный ранг {med_ranking[0][2]:.2f}). Для выборки из m = {m_experts} экспертов метод подтвердил "
        "робастность к индивидуальным смещениям оценок.",
        first_indent=1.5, space_after=2
    )
    add_p(
        f"3. На множестве индивидуальных экспертных суждений минимум суммы расстояний Кемени S_min = {min_dist_val} "
        f"достигнут на эксперте(-ах) {best_exps_str}, что выделяет эти суждения в качестве медианных среди выборки.",
        first_indent=1.5, space_after=2
    )
    add_p(
        f"4. Продемонстрировано принципиальное разделение целевых функций: минимум задачи о назначениях составил "
        f"Φ_{{Assign}} = {min_assign_loss}, а минимум истинного расстояния Кемени — Φ_{{Kemeny}} = {min_kemeny_dist}. "
        "Оптимизация задачи о назначениях и поиск медианы Кемени соответствуют различным математическим критериям.",
        first_indent=1.5, space_after=2
    )
    add_p(
        f"5. Полный перебор {n_objects}! = 120 перестановок позволил строго идентифицировать все {len(kemeny_orders)} "
        f"глобальные медианы Кемени со значением критерия {min_kemeny_dist}, предоставив строгое математическое решение "
        "задачи коллективного выбора.",
        first_indent=1.5, space_after=4
    )

    doc.add_page_break()

    # =========================================================================
    # 11. ПРИЛОЖЕНИЕ. ТЕКСТ ПРОГРАММЫ
    # =========================================================================
    add_h1("ПРИЛОЖЕНИЕ. ИСХОДНЫЙ КОД ПРОГРАММЫ")
    add_p(
        "Ниже приведены листинги основных вычислительных модулей ядра экспертных оценок пакета expert_estimate, "
        "отвечающих за математическую обработку данных лабораторной работы."
    )

    code_files = [
        ("expert_estimate/transform.py", "Модуль преобразования исходных данных и сортировки объектов"),
        ("expert_estimate/stats.py", "Модуль средних арифметических и медианных рангов"),
        ("expert_estimate/relations.py", "Модуль бинарных отношений и вычисления расстояний Кемени"),
        ("expert_estimate/kemeny.py", "Модуль векторов предпочтений, матрицы потерь, задачи о назначениях и перебора"),
        ("expert_estimate/printers.py", "Модуль форматированного табличного вывода результатов"),
        ("expert_estimate/algorithm.py", "Главный модуль координации вычислений и консольного интерфейса (CLI)"),
    ]

    for rel_path, desc in code_files:
        full_path = BASE_DIR / rel_path
        if full_path.exists():
            add_h2(f"Файл {rel_path} — {desc}")
            code_text = full_path.read_text(encoding="utf-8")

            t_box = doc.add_table(rows=1, cols=1)
            t_box.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_borders(t_box, color="CBD5E1", sz="4", val="single")
            c = t_box.rows[0].cells[0]
            c.width = docx.shared.Cm(16.5)
            set_cell_background(c, "F8FAFC")
            set_cell_margins(c, top=100, bottom=100, left=150, right=150)

            p_code = c.paragraphs[0]
            p_code.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_code.paragraph_format.first_line_indent = 0
            p_code.paragraph_format.space_before = Pt(0)
            p_code.paragraph_format.space_after = Pt(0)
            p_code.paragraph_format.line_spacing = 1.0

            run_code = p_code.add_run(code_text)
            run_code.font.name = "Consolas"
            run_code.font.size = Pt(8.0)
            run_code.font.color.rgb = RGBColor(30, 41, 59)
            add_p(space_after=4)

    doc.save(str(OUTPUT_DOCX))
    print(f"Документ успешно сформирован: {OUTPUT_DOCX}")


if __name__ == "__main__":
    target_input = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_DIR / "input.txt"
    build_report(target_input)
