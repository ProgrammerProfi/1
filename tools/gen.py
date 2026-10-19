"""Генераторы задач ЕГЭ по информатике.

Каждый генератор берёт random.Random и возвращает dict:
  statement : HTML условия
  steps     : список HTML-абзацев разбора с конкретными числами
  code      : программа на Python, которая печатает ответ
  answer    : строка ответа (ровно то, что печатает code)
  title     : короткий заголовок для <title>

Ответ генератор считает своим способом, а code потом отдельно запускается
в verify.py; задачи, где они разошлись, в сайт не попадают.
"""
import math
import re
import itertools
import fnmatch
import ipaddress
from functools import lru_cache


def H(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- №5
def gen_5(rng):
    kind = rng.choice(["parity_n", "ones_twice", "div3"])
    if kind == "parity_n":
        pe = rng.choice(["10", "01", "11", "00"])
        po = rng.choice([p for p in ["10", "01", "11", "00"] if p != pe])
        rule = (f"если N чётное, то к двоичной записи справа дописываются цифры <b>{pe}</b>, "
                f"а если нечётное — цифры <b>{po}</b>")

        def R(n):
            b = bin(n)[2:]
            return int(b + (pe if n % 2 == 0 else po), 2)
        code_rule = (f"    b = bin(n)[2:]\n"
                     f"    b += '{pe}' if n % 2 == 0 else '{po}'\n")
    elif kind == "ones_twice":
        rule = ("к двоичной записи справа дописывается остаток от деления суммы её цифр на 2; "
                "затем эта операция повторяется ещё раз для получившейся записи")

        def R(n):
            b = bin(n)[2:]
            for _ in range(2):
                b += str(b.count("1") % 2)
            return int(b, 2)
        code_rule = ("    b = bin(n)[2:]\n"
                     "    for _ in range(2):\n"
                     "        b += str(b.count('1') % 2)\n")
    else:
        rule = ("если N делится на 3, то к двоичной записи справа дописываются три её последние цифры; "
                "иначе справа дописывается двоичная запись числа 3·(N mod 3)")

        def R(n):
            b = bin(n)[2:]
            b += b[-3:] if n % 3 == 0 else bin(n % 3 * 3)[2:]
            return int(b, 2)
        code_rule = ("    b = bin(n)[2:]\n"
                     "    b += b[-3:] if n % 3 == 0 else bin(n % 3 * 3)[2:]\n")

    q = rng.choice(["minN", "minR"])
    X = rng.randint(40, 400) if kind != "div3" else rng.randint(60, 500)
    if q == "minN":
        ans = next(n for n in range(4, 10000) if R(n) > X)
        ask = f"Укажите <b>минимальное</b> число N, после обработки которого с помощью этого алгоритма получается число R, большее {X}."
        loop = (f"for n in range(4, 10000):\n    if R(n) > {X}:\n        print(n)\n        break\n")
        last = f"Перебираем N по возрастанию и останавливаемся на первом, для которого R(N) > {X}."
    else:
        ans = min(R(n) for n in range(4, 10000) if R(n) > X)
        ask = f"Укажите <b>минимальное</b> число R, большее {X}, которое может быть получено с помощью этого алгоритма."
        loop = (f"print(min(R(n) for n in range(4, 10000) if R(n) > {X}))\n")
        last = (f"Здесь важно перебрать все N, а не остановиться на первом подходящем: R растёт с N не монотонно, "
                f"поэтому берём минимум из всех R(N) > {X}.")
    statement = (
        "<p>На вход алгоритма подаётся натуральное число N (N ≥ 4). Алгоритм строит по нему новое число R следующим образом.</p>"
        "<ol><li>Строится двоичная запись числа N.</li>"
        f"<li>Далее эта запись обрабатывается по правилу: {rule}.</li>"
        "<li>Полученная таким образом запись является двоичной записью искомого числа R.</li></ol>"
        f"<p>{ask} В ответе запишите это число в десятичной системе счисления.</p>")
    code = "def R(n):\n" + code_rule + "    return int(b, 2)\n\n\n" + loop
    steps = [
        "Задачи №5 решаются прямым моделированием. Пишем функцию R(n), которая делает ровно то, что написано в условии, "
        "и перебираем N. Руками это делать долго и легко ошибиться в одном разряде.",
        "Двоичную запись удобно держать строкой: <code>bin(n)[2:]</code> даёт её без префикса <code>0b</code>, "
        "дописывание справа — это конкатенация, а обратно в число переводит <code>int(b, 2)</code>.",
        last,
        f"Ответ: <b>{ans}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(ans),
                title=f"R больше {X}")


# ---------------------------------------------------------------- №7
def gen_7(rng):
    if rng.random() < 0.5:
        k = rng.choice([4, 8, 10, 12, 16, 24])
        w, h = rng.choice([(640, 480), (800, 600), (1024, 768), (1280, 720), (1920, 1080), (1600, 1200)])
        period = rng.choice([5, 10, 15, 20, 30, 60])
        hours = rng.choice([1, 2, 3, 4, 6, 8, 12, 24])
        cnt = hours * 3600 // period
        bits = w * h * k * cnt
        ans = math.ceil(bits / 8 / 2**20)
        statement = (
            f"<p>Автоматическая фотокамера каждые {period} с создаёт растровое изображение, содержащее до {2**k} цветов. "
            f"Размер изображения — {w}×{h} пикселей. Все полученные изображения и коды пикселей внутри одного изображения "
            "записываются подряд, никакая дополнительная информация не сохраняется, данные не сжимаются.</p>"
            f"<p>Сколько Мбайт нужно выделить для хранения всех изображений, полученных за {hours} ч? "
            "В ответе укажите только целое число — минимально достаточный объём.</p>")
        code = (f"import math\n\nk = {k}  # бит на пиксель: 2**{k} = {2**k} цветов\n"
                f"img_bits = {w} * {h} * k\ncount = {hours} * 3600 // {period}\n"
                f"print(math.ceil(img_bits * count / 8 / 2**20))\n")
        steps = [
            f"{2**k} цветов = 2<sup>{k}</sup>, значит на один пиксель уходит {k} бит.",
            f"Одно изображение: {w}·{h}·{k} = {w*h*k} бит.",
            f"За {hours} ч камера делает {hours}·3600 / {period} = {cnt} снимков.",
            f"Всего {bits} бит = {bits/8/2**20:.4f} Мбайт. Округляем вверх, потому что в меньший объём данные не влезут.",
            f"Ответ: <b>{ans}</b>.",
        ]
        title = f"фотокамера {w}×{h}, {2**k} цветов"
    else:
        ch = rng.choice([1, 2, 4])
        khz = rng.choice([16, 22, 32, 44, 48, 64])
        depth = rng.choice([8, 16, 24, 32])
        minutes = rng.choice([1, 2, 3, 4, 5, 6, 8, 10])
        bits = ch * khz * 1000 * depth * minutes * 60
        mb = bits / 8 / 2**20
        ans = round(mb)
        if abs(mb - ans) > 0.45:
            return None
        chn = {1: "моно (одноканальная)", 2: "стерео (двухканальная)", 4: "квадро (четырёхканальная)"}[ch]
        statement = (
            f"<p>Производится {chn} звукозапись с частотой дискретизации {khz} кГц и глубиной кодирования {depth} бит. "
            f"Запись длится {minutes} мин, её результаты записываются в файл, сжатие данных не производится.</p>"
            "<p>Определите размер полученного файла в мегабайтах. "
            "В ответе укажите ближайшее целое число мегабайт.</p>")
        code = (f"bits = {ch} * {khz} * 1000 * {depth} * {minutes} * 60\nprint(round(bits / 8 / 2**20))\n")
        steps = [
            "Объём звука = каналы · частота · глубина · время. Частоту переводим в герцы: 1 кГц = 1000 Гц, время — в секунды.",
            f"{ch}·{khz*1000}·{depth}·{minutes*60} = {bits} бит.",
            f"В мегабайтах: {bits} / 8 / 2<sup>20</sup> ≈ {mb:.3f}.",
            f"Ответ: <b>{ans}</b>.",
        ]
        title = f"звукозапись {khz} кГц, {depth} бит, {minutes} мин"
    return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=title)


# ---------------------------------------------------------------- №8
VOWELS = set("АЕЁИОУЫЭЮЯ")


def gen_8(rng):
    pool = list("АБВГДЕИКЛМНОПРСТУ")
    n = rng.randint(5, 7)
    letters = sorted(rng.sample(pool, n), key=lambda c: "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ".index(c))
    vow = [c for c in letters if c in VOWELS]
    con = [c for c in letters if c not in VOWELS]
    if len(vow) < 1 or len(con) < 2:
        return None
    L = rng.randint(5, 6) if n <= 6 else 5
    kind = rng.choice(["count", "count_once", "position"])
    s = "".join(letters)
    words = list(itertools.product(letters, repeat=L))
    if kind == "count":
        def ok(w):
            if w[0] in VOWELS:
                return False
            return all(not (w[i] in VOWELS and w[i + 1] in VOWELS) for i in range(L - 1))
        ans = sum(1 for w in words if ok(w))
        cond = "не начинаются с гласной буквы и не содержат двух гласных, стоящих рядом"
        code = (f"from itertools import product\n\nvowels = set('{''.join(vow)}')\ncnt = 0\n"
                f"for w in product('{s}', repeat={L}):\n"
                "    if w[0] in vowels:\n        continue\n"
                f"    if any(w[i] in vowels and w[i + 1] in vowels for i in range({L} - 1)):\n        continue\n"
                "    cnt += 1\nprint(cnt)\n")
        title = f"слова из букв {s} без двух гласных подряд"
    elif kind == "count_once":
        x = rng.choice(letters)
        y = rng.choice([c for c in letters if c != x])
        ans = sum(1 for w in words if w.count(x) == 1 and w[-1] != y)
        cond = f"содержат ровно одну букву {x} и не заканчиваются буквой {y}"
        code = (f"from itertools import product\n\ncnt = 0\nfor w in product('{s}', repeat={L}):\n"
                f"    if w.count('{x}') == 1 and w[-1] != '{y}':\n        cnt += 1\nprint(cnt)\n")
        title = f"ровно одна {x}, не на {y}"
    else:
        if L > n:
            return None
        x = rng.choice(con)
        ans = next(i for i, w in enumerate(words, 1) if w[0] == x and len(set(w)) == L)
        statement = (
            f"<p>Все {L}-буквенные слова, составленные из букв {', '.join(letters)}, записаны в алфавитном порядке и пронумерованы, "
            "начиная с 1. Буквы в словах могут повторяться.</p>"
            f"<p>Под каким номером в этом списке стоит первое слово, которое начинается с буквы {x} и в котором нет повторяющихся букв?</p>")
        code = (f"from itertools import product\n\nfor i, w in enumerate(product('{s}', repeat={L}), 1):\n"
                f"    if w[0] == '{x}' and len(set(w)) == {L}:\n        print(i)\n        break\n")
        steps = [
            "<code>itertools.product</code> перебирает слова ровно в алфавитном порядке, если буквы в строке отсортированы. "
            f"Строка «{s}» уже упорядочена, так что номер слова = номер итерации.",
            f"Нумерация начинается с 1, поэтому <code>enumerate(..., 1)</code>. Условие «нет повторов» проверяем как <code>len(set(w)) == {L}</code>.",
            "Аналитически тоже можно: каждая позиция — разряд в системе счисления с основанием "
            f"{n}, но с условием «без повторов» перебор надёжнее.",
            f"Ответ: <b>{ans}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(ans),
                    title=f"номер первого слова на {x} без повторов")
    statement = (
        f"<p>Петя составляет {L}-буквенные слова из букв {', '.join(letters)}. Каждая буква может входить в слово любое количество раз "
        "или не входить совсем. Словом считается любая допустимая последовательность букв, не обязательно осмысленная.</p>"
        f"<p>Сколько существует таких слов, которые {cond}?</p>")
    steps = [
        f"Всего слов {n}<sup>{L}</sup> = {n**L}, перебрать их все — мгновенно. Поэтому решаем перебором через <code>itertools.product</code> и просто проверяем условие.",
        ("Гласные среди наших букв: " + ", ".join(vow) + ". ") if kind == "count" else
        "Ровно одно вхождение проверяем через <code>w.count(...) == 1</code>, последнюю букву — через <code>w[-1]</code>.",
        "Формулой тоже можно, но там легко пропустить случай. Перебор не ошибается.",
        f"Ответ: <b>{ans}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=title)


# ---------------------------------------------------------------- №11
def gen_11(rng):
    L = rng.randint(7, 25)
    M = rng.randint(10, 3000)
    K = rng.choice([20, 25, 30, 40, 50, 60, 80, 100, 128, 200, 256, 500, 1024])
    bits = math.ceil(math.log2(M))
    pw = math.ceil(L * bits / 8)
    extra = rng.randint(4, 40)
    V = K * (pw + extra)
    alph = ("26 строчных латинских букв, 26 заглавных латинских букв и 10 десятичных цифр" if M == 62 else
            f"набор из {M} различных символов")
    statement = (
        f"<p>При регистрации в компьютерной системе каждому пользователю выдаётся пароль, состоящий из {L} символов. "
        f"Для пароля используется {alph}. В базе данных для хранения каждого пароля отведено одинаковое и минимально возможное целое число байт. "
        "При этом используют посимвольное кодирование паролей, все символы кодируют одинаковым и минимально возможным количеством бит.</p>"
        "<p>Кроме собственно пароля, для каждого пользователя в системе хранятся дополнительные сведения, для чего отведено одинаковое для всех "
        f"пользователей целое число байт. Для хранения сведений о {K} пользователях потребовалось {V} байт.</p>"
        "<p>Сколько байт выделено для хранения дополнительных сведений об одном пользователе? В ответе запишите только целое число.</p>")
    code = (f"import math\n\nbits = math.ceil(math.log2({M}))      # бит на символ\n"
            f"pw = math.ceil({L} * bits / 8)          # байт на пароль\n"
            f"per_user = {V} // {K}\nprint(per_user - pw)\n")
    steps = [
        f"Минимальное число бит на символ i — такое, что 2<sup>i</sup> ≥ {M}. Это i = {bits} (2<sup>{bits}</sup> = {2**bits}"
        + (f", а 2<sup>{bits-1}</sup> = {2**(bits-1)} уже мало" if bits > 1 else "") + ").",
        f"Пароль: {L}·{bits} = {L*bits} бит. Округляем до целых байт вверх: ⌈{L*bits}/8⌉ = {pw} байт. "
        "Типичная ошибка — сначала посчитать весь объём в битах на всех пользователей и только потом делить; округление идёт для каждого пароля отдельно.",
        f"На одного пользователя: {V} / {K} = {V//K} байт.",
        f"Доп. сведения: {V//K} − {pw} = {extra}.",
        f"Ответ: <b>{extra}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(extra),
                title=f"пароль из {L} символов, алфавит {M}")


# ---------------------------------------------------------------- №12
def gen_12(rng):
    a, b = rng.sample("123456789", 2)
    k1, k2 = rng.choice([(3, 2), (2, 3), (3, 3), (4, 2), (2, 4), (4, 3)])
    m1 = rng.randint(1, k1 - 1)
    m2 = rng.randint(1, k2 - 1)
    p1, r1, p2, r2 = a * k1, b * m1, b * k2, a * m2
    start_d = a

    def run(n):
        s = start_d * n
        while p1 in s or p2 in s:
            if p1 in s:
                s = s.replace(p1, r1, 1)
            else:
                s = s.replace(p2, r2, 1)
        return s
    kind = rng.choice(["string", "maxsum"])
    prog = (f"НАЧАЛО\nПОКА нашлось({p1}) ИЛИ нашлось({p2})\n"
            f"  ЕСЛИ нашлось({p1})\n    ТО заменить({p1}, {r1})\n    ИНАЧЕ заменить({p2}, {r2})\n"
            "  КОНЕЦ ЕСЛИ\nКОНЕЦ ПОКА\nКОНЕЦ")
    intro = ("<p>Исполнитель Редактор получает на вход строку цифр и преобразовывает её. Команда <b>заменить(v, w)</b> заменяет в строке "
             "первое слева вхождение цепочки v на цепочку w; команда <b>нашлось(v)</b> проверяет, встречается ли цепочка v в строке.</p>")
    fn = ("def run(s):\n"
          f"    while '{p1}' in s or '{p2}' in s:\n"
          f"        if '{p1}' in s:\n            s = s.replace('{p1}', '{r1}', 1)\n"
          f"        else:\n            s = s.replace('{p2}', '{r2}', 1)\n"
          "    return s\n\n\n")
    if kind == "string":
        n = rng.randint(40, 200)
        res = run(n)
        if len(res) > 12:
            return None
        statement = intro + (f"<p>Какая строка получится в результате применения приведённой ниже программы к строке, "
                             f"состоящей из {n} идущих подряд цифр {start_d}?</p><pre class=prog>{H(prog)}</pre>")
        code = fn + f"print(run('{start_d}' * {n}))\n"
        ans = res
        steps = [
            "Редактор — это ровно <code>str.replace(..., 1)</code>: замена только первого вхождения. Без третьего аргумента Python заменит все вхождения сразу, и ответ может разойтись.",
            f"Каждая замена укорачивает строку ({k1}→{m1} и {k2}→{m2} символов), поэтому цикл гарантированно закончится.",
            f"Моделируем на строке из {n} цифр {start_d} и печатаем результат.",
            f"Ответ: <b>{ans}</b>.",
        ]
        title = f"{n} цифр {start_d}, замены {p1}→{r1}, {p2}→{r2}"
    else:
        lo, hi = rng.choice([(10, 100), (20, 150), (30, 200)])
        best = max(range(lo, hi + 1), key=lambda n: (sum(map(int, run(n))), n))
        statement = intro + (f"<p>На вход приведённой ниже программе поступает строка, состоящая из n цифр {start_d} ({lo} ≤ n ≤ {hi}). "
                             "Определите <b>наибольшее</b> значение n, при котором сумма цифр в строке, получившейся в результате "
                             f"выполнения программы, максимальна.</p><pre class=prog>{H(prog)}</pre>")
        code = fn + (f"best = max(range({lo}, {hi + 1}), key=lambda n: (sum(map(int, run('{start_d}' * n))), n))\nprint(best)\n")
        ans = best
        steps = [
            "Перебираем все n из диапазона и для каждого моделируем программу через <code>str.replace(..., 1)</code> — это и есть «первое вхождение».",
            "Ключ сортировки — пара (сумма цифр, n): при равной максимальной сумме выиграет большее n, как и требует условие.",
            "Искать закономерность руками можно (результат периодичен по n), но на экзамене перебор быстрее и надёжнее.",
            f"Ответ: <b>{ans}</b>.",
        ]
        title = f"наибольшее n с максимальной суммой, {p1}→{r1}"
    return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=title)


# ---------------------------------------------------------------- №13
def gen_13(rng):
    kind = rng.choice(["masks", "ones"])
    if kind == "masks":
        pref = rng.randint(16, 28)
        net = ipaddress.ip_network(f"{rng.randint(10, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}/{pref}", strict=False)
        hosts = list(net.hosts())
        if not hosts:
            return None
        ip = rng.choice(hosts)
        cnt = 0
        for p in range(0, 33):
            n2 = ipaddress.ip_network(f"{ip}/{p}", strict=False)
            if n2.network_address == net.network_address and ip != n2.network_address and ip != n2.broadcast_address:
                cnt += 1
        statement = (
            "<p>В терминологии сетей TCP/IP маской сети называют двоичное число, которое показывает, какая часть IP-адреса узла относится к адресу сети, "
            "а какая — к адресу узла в этой сети. Адрес сети получается в результате поразрядной конъюнкции IP-адреса узла и маски.</p>"
            f"<p>Узел с IP-адресом <b>{ip}</b> находится в сети с адресом <b>{net.network_address}</b>. "
            "Для скольких различных значений маски это возможно? Учтите, что адрес узла не может совпадать с адресом сети и с широковещательным адресом.</p>")
        code = ("from ipaddress import ip_network\n\ncnt = 0\nfor p in range(33):\n"
                f"    net = ip_network('{ip}/' + str(p), strict=False)\n"
                f"    if str(net.network_address) == '{net.network_address}' and '{ip}' not in (str(net.network_address), str(net.broadcast_address)):\n"
                "        cnt += 1\nprint(cnt)\n")
        steps = [
            "Маска однозначно задаётся длиной префикса p от 0 до 32. Для каждого p считаем адрес сети и проверяем, совпадает ли он с данным.",
            "Модуль <code>ipaddress</code> делает побитовое И сам: <code>ip_network('адрес/p', strict=False)</code> обнуляет хостовую часть.",
            "Дополнительно отбрасываем маски, при которых узел оказывается адресом сети или широковещательным адресом (это бывает при самых длинных масках).",
            f"Ответ: <b>{cnt}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(cnt),
                    title=f"маски для узла {ip}")
    pref = rng.randint(17, 26)
    net = ipaddress.ip_network(f"{rng.randint(10, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.0/{pref}", strict=False)
    d = rng.choice([2, 3, 4, 5])
    neg = rng.random() < 0.5
    cnt = sum(1 for a in net if ((bin(int(a)).count("1") % d != 0) if neg else (bin(int(a)).count("1") % d == 0)))
    cond = f"{'не ' if neg else ''}кратно {d}"
    statement = (
        "<p>Сеть задана IP-адресом и маской. Адрес сети получается поразрядной конъюнкцией IP-адреса любого узла этой сети и маски.</p>"
        f"<p>Сеть задана адресом <b>{net.network_address}</b> и маской <b>{net.netmask}</b>. "
        f"Сколько в этой сети IP-адресов, для которых количество единиц в двоичной записи IP-адреса {cond}? "
        "В ответе укажите только число.</p>")
    code = (f"from ipaddress import ip_network\n\ncnt = 0\nfor a in ip_network('{net.network_address}/{net.netmask}'):\n"
            f"    if bin(int(a)).count('1') % {d} {'!=' if neg else '=='} 0:\n        cnt += 1\nprint(cnt)\n")
    steps = [
        f"Маска {net.netmask} — это /{pref}, в сети 2<sup>{32-pref}</sup> = {net.num_addresses} адресов. Перебрать их все — мгновенно.",
        "Итерация по <code>ip_network</code> выдаёт все адреса сети, включая адрес сети и широковещательный — условие говорит «IP-адресов в сети», поэтому их учитываем.",
        "<code>int(a)</code> переводит адрес в 32-битное число, дальше считаем единицы через <code>bin(...).count('1')</code>.",
        f"Ответ: <b>{cnt}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(cnt),
                title=f"сеть {net.network_address}/{pref}, единицы {cond}")


# ---------------------------------------------------------------- №14
DIG = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gen_14(rng):
    kind = rng.choice(["count_digit", "unknown_digit"])
    if kind == "count_digit":
        q = rng.choice([2, 3, 4, 5, 6, 7, 8, 9])
        A = rng.choice([x for x in [2, 3, 4, 5, 6, 7, 8, 9, 16, 25, 27, 36, 49] if x != q])
        x = rng.randint(100, 2030)
        y = rng.randint(50, x - 10)
        B = rng.randint(5, 3000)
        v = A**x + A**y - B
        d = rng.randrange(q)
        s = []
        t = v
        while t:
            s.append(t % q)
            t //= q
        ans = s.count(d)
        statement = (f"<p>Значение арифметического выражения {A}<sup>{x}</sup> + {A}<sup>{y}</sup> − {B} записали в системе счисления "
                     f"с основанием {q}. Сколько цифр {d} содержится в этой записи?</p>")
        code = (f"v = {A}**{x} + {A}**{y} - {B}\ncnt = 0\nwhile v:\n    cnt += v % {q} == {d}\n    v //= {q}\nprint(cnt)\n")
        steps = [
            "Python работает с длинными целыми без ограничений, так что считаем значение выражения напрямую.",
            f"Дальше обычный перевод в систему с основанием {q}: берём остаток от деления на {q} (очередная цифра справа) и делим нацело.",
            "Аналитический путь (через то, как выглядит в записи степень основания минус число) полезен, когда основание выражения — степень q. Но он требует аккуратности, а код даёт ответ сразу.",
            f"Ответ: <b>{ans}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(ans),
                    title=f"цифры {d} в записи {A}^{x}+{A}^{y}−{B} по основанию {q}")
    q = rng.choice([11, 12, 13, 14, 15, 16, 17, 19])
    M = rng.choice([7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53])
    a = "".join(rng.choice(DIG[:q]) for _ in range(rng.randint(3, 4)))
    b = "".join(rng.choice(DIG[:q]) for _ in range(rng.randint(3, 4)))
    pa = rng.randrange(len(a) + 1)
    pb = rng.randrange(len(b) + 1)
    A = a[:pa] + "x" + a[pa:]
    Bs = b[:pb] + "x" + b[pb:]
    if A[0] == "x" or Bs[0] == "x" or A[0] == "0" or Bs[0] == "0":
        return None
    sol = None
    for xd in range(q):
        c = DIG[xd]
        val = int(A.replace("x", c), q) + int(Bs.replace("x", c), q)
        if val % M == 0:
            sol = val // M
            break
    if sol is None:
        return None
    statement = (f"<p>Операнды арифметического выражения записаны в системе счисления с основанием {q}:</p>"
                 f"<p class=formula>{A}<sub>{q}</sub> + {Bs}<sub>{q}</sub></p>"
                 f"<p>В записи чисел переменной x обозначена неизвестная цифра из алфавита {q}-ричной системы счисления. "
                 f"Определите наименьшее значение x, при котором значение данного арифметического выражения кратно {M}. "
                 f"Для найденного значения x вычислите частное от деления значения арифметического выражения на {M} и укажите его в ответе "
                 "в десятичной системе счисления.</p>")
    code = (f"alphabet = '{DIG[:q]}'\nfor x in alphabet:\n"
            f"    v = int('{A}'.replace('x', x), {q}) + int('{Bs}'.replace('x', x), {q})\n"
            f"    if v % {M} == 0:\n        print(v // {M})\n        break\n")
    steps = [
        f"x — одна цифра {q}-ричной системы, вариантов всего {q}. Перебираем их по возрастанию.",
        f"<code>int(строка, {q})</code> сам переводит запись в десятичное число; цифры больше 9 он понимает как буквы A, B, C…",
        f"Как только сумма разделилась на {M}, печатаем частное и выходим: первый найденный x и есть наименьший.",
        f"Ответ: <b>{sol}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(sol),
                title=f"{A}_{q} + {Bs}_{q} кратно {M}")


# ---------------------------------------------------------------- №15
def gen_15(rng):
    kind = rng.choice(["del_max", "del_min", "seg"])
    if kind in ("del_max", "del_min"):
        a, b = rng.sample(range(2, 40), 2)
        if kind == "del_max":
            f = "¬ДЕЛ(x, A) → (ДЕЛ(x, %d) → ¬ДЕЛ(x, %d))" % (a, b)

            def F(x, A):
                return (x % A == 0) or not ((x % a == 0) and (x % b == 0))
            cand = range(1, 2000)
            good = [A for A in cand if all(F(x, A) for x in range(1, 5000))]
            ans = max(good)
            q = "наибольшего"
            pyf = f"(x % A == 0) or not (x % {a} == 0 and x % {b} == 0)"
            loop = "print(max(A for A in range(1, 2000) if all(f(x, A) for x in range(1, 5000))))\n"
            idea = (f"Импликация p → q ложна только при p = 1, q = 0. Формула ложна, когда x не делится на A, но делится и на {a}, и на {b}. "
                    f"Значит, каждое число, делящееся на {a} и {b} (то есть кратное НОК = {math.lcm(a, b)}), обязано делиться на A. "
                    f"Наибольшее такое A — сам НОК({a}, {b}) = {math.lcm(a, b)}.")
        else:
            f = "ДЕЛ(x, A) → (¬ДЕЛ(x, %d) → ДЕЛ(x, %d))" % (a, b)

            def F(x, A):
                return (not x % A == 0) or (x % a == 0) or (x % b == 0)
            good = [A for A in range(1, 2000) if all(F(x, A) for x in range(1, 5000))]
            ans = min(good)
            q = "наименьшего"
            pyf = f"(x % A != 0) or (x % {a} == 0) or (x % {b} == 0)"
            loop = "print(min(A for A in range(1, 2000) if all(f(x, A) for x in range(1, 5000))))\n"
            idea = (f"Формула равносильна ¬ДЕЛ(x, A) ∨ ДЕЛ(x, {a}) ∨ ДЕЛ(x, {b}). Она должна быть истинна для каждого x, в том числе для x = A. "
                    f"Значит, A само должно делиться на {a} или на {b}; тогда и все его кратные тоже. Наименьшее такое A — {min(a, b)}.")
        statement = ("<p>Обозначим через ДЕЛ(n, m) утверждение «натуральное число n делится без остатка на натуральное число m».</p>"
                     f"<p>Для какого {q} натурального числа A формула</p><p class=formula>{f}</p>"
                     "<p>тождественно истинна (то есть принимает значение 1 при любом натуральном значении переменной x)?</p>")
        code = (f"def f(x, A):\n    return {pyf}\n\n\n" + loop)
        steps = [
            "Решаем перебором: для каждого кандидата A проверяем формулу на большом отрезке x. Если нашёлся x, где формула ложна, A не подходит.",
            "Импликацию p → q в Python пишем как <code>(not p) or q</code>, а ДЕЛ(x, m) — как <code>x % m == 0</code>.",
            idea,
            "Почему хватает x до 5000: все делимости здесь периодичны с периодом НОК(A, " + f"{a}, {b}), и для подходящих A этот период укладывается в диапазон. "
            "Если сомневаешься, увеличь границу и убедись, что ответ не поменялся.",
            f"Ответ: <b>{ans}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=f"ДЕЛ, {a} и {b}")
    p1 = rng.randint(5, 40)
    p2 = p1 + rng.randint(10, 40)
    q1 = rng.randint(p1 - 10, p2 - 5)
    q2 = q1 + rng.randint(10, 40)
    E = sorted({p1, p2, q1, q2})
    # (x∈P) → ((x∈Q ∧ ¬(x∈A)) → ¬(x∈P))  ⇔  ¬P ∨ ¬Q ∨ A ; A must cover P∩Q
    pts = sorted(set([e for e in E] + [(E[i] + E[i + 1]) / 2 for i in range(len(E) - 1)] + [E[0] - 1, E[-1] + 1]))

    def F(x, l, r):
        P = p1 <= x <= p2
        Q = q1 <= x <= q2
        A = l <= x <= r
        return (not P) or (not (Q and not A)) or (not P)
    best = None
    for l in E:
        for r in E:
            if l <= r and all(F(x, l, r) for x in pts):
                if best is None or r - l < best:
                    best = r - l
    if best is None or best == 0:
        return None
    statement = (f"<p>На числовой прямой даны два отрезка: P = [{p1}; {p2}] и Q = [{q1}; {q2}]. "
                 "Укажите наименьшую возможную длину такого отрезка A, что формула</p>"
                 "<p class=formula>(x ∈ P) → (((x ∈ Q) ∧ ¬(x ∈ A)) → ¬(x ∈ P))</p>"
                 "<p>тождественно истинна, то есть принимает значение 1 при любом значении переменной x.</p>")
    code = (f"E = {E}\n"
            "pts = E + [(E[i] + E[i + 1]) / 2 for i in range(len(E) - 1)] + [E[0] - 1, E[-1] + 1]\n\n\n"
            "def f(x, l, r):\n"
            f"    P = {p1} <= x <= {p2}\n    Q = {q1} <= x <= {q2}\n    A = l <= x <= r\n"
            "    return (not P) or (not (Q and not A)) or (not P)\n\n\n"
            "print(min(r - l for l in E for r in E if l <= r and all(f(x, l, r) for x in pts)))\n")
    lo, hi = max(p1, q1), min(p2, q2)
    steps = [
        "Раскрываем импликации: p → q = ¬p ∨ q. Получается ¬P ∨ ¬(Q ∧ ¬A) ∨ ¬P = ¬P ∨ ¬Q ∨ A.",
        f"Ложной формула может быть только там, где x ∈ P и x ∈ Q одновременно, то есть на пересечении [{lo}; {hi}]. Там обязано выполняться x ∈ A.",
        f"Значит, A должен накрыть пересечение, и минимальный такой отрезок — оно само. Длина {hi} − {lo} = {hi - lo}.",
        "Код проверяет то же перебором. Концы A берём только из концов P и Q, а x проверяем в самих концах и серединах между ними: истинность формулы меняется только в этих точках.",
        f"Ответ: <b>{best}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(best), title=f"отрезки P=[{p1};{p2}], Q=[{q1};{q2}]")


# ---------------------------------------------------------------- №16
def gen_16(rng):
    kind = rng.choice(["upward", "factorial", "evenodd"])
    if kind == "upward":
        N = rng.choice([2024, 2025, 2026, 3000, 5000])
        c = rng.randint(1, 5)
        st = rng.choice([1, 2, 3])
        a = N - rng.randint(3, 12) * st
        b = a + st * rng.randint(1, 3)
        if b >= N:
            return None
        memo = {}
        def F(n):
            vals = {}
            for m in range(N + st + 5, n - 1, -1):
                vals[m] = m if m >= N else m + c + vals[m + st]
            return vals[n]
        ans = F(a) - F(b)
        statement = (f"<p>Алгоритм вычисления значения функции F(n), где n — натуральное число, задан следующими соотношениями:</p>"
                     f"<p class=formula>F(n) = n при n ≥ {N};<br>F(n) = n + {c} + F(n + {st}) при n &lt; {N}.</p>"
                     f"<p>Чему равно значение выражения F({a}) − F({b})?</p>")
        code = ("from functools import lru_cache\n\n\n@lru_cache(None)\ndef F(n):\n"
                f"    if n >= {N}:\n        return n\n    return n + {c} + F(n + {st})\n\n\n"
                f"print(F({a}) - F({b}))\n")
        steps = [
            f"Здесь рекурсия идёт вверх, к {N}, поэтому глубина маленькая: от {a} до {N} всего {(N - a) // st + 1} шагов. Стандартного лимита рекурсии хватает.",
            "<code>lru_cache</code> тут не обязателен, но привычка полезная: в задачах с двумя рекурсивными вызовами без него программа не досчитает.",
            f"F({a}) − F({b}) — это сумма слагаемых n + {c} для n = {a}, {a + st}, … до {b - st}: всё остальное сокращается. Можно проверить руками.",
            f"Ответ: <b>{ans}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=f"F({a}) − F({b}), граница {N}")
    if kind == "factorial":
        N = rng.choice([2023, 2024, 2025, 2026])
        k = rng.randint(2, 6)
        f = [1] * (N + 1)
        for i in range(2, N + 1):
            f[i] = i * f[i - 1]
        ans = (f[N] + k * f[N - 1]) // f[N - 2]
        assert (f[N] + k * f[N - 1]) % f[N - 2] == 0
        statement = ("<p>Алгоритм вычисления значения функции F(n), где n — натуральное число, задан следующими соотношениями:</p>"
                     "<p class=formula>F(n) = 1 при n = 1;<br>F(n) = n · F(n − 1), если n &gt; 1.</p>"
                     f"<p>Чему равно значение выражения (F({N}) + {k} · F({N - 1})) / F({N - 2})?</p>")
        code = ("import sys\nfrom functools import lru_cache\n\nsys.setrecursionlimit(10000)\n\n\n"
                "@lru_cache(None)\ndef F(n):\n    if n == 1:\n        return 1\n    return n * F(n - 1)\n\n\n"
                f"print((F({N}) + {k} * F({N - 1})) // F({N - 2}))\n")
        steps = [
            f"F(n) — это n!. Глубина рекурсии около {N}, а стандартный лимит в Python — 1000, поэтому поднимаем его через <code>sys.setrecursionlimit</code>. Без этого будет RecursionError.",
            "Делим целочисленно (<code>//</code>): обычное деление переведёт гигантские числа во float, получится OverflowError или потеря точности.",
            f"Руками: F({N}) = {N}·{N - 1}·F({N - 2}), F({N - 1}) = {N - 1}·F({N - 2}). Делим на F({N - 2}): {N}·{N - 1} + {k}·{N - 1} = {N - 1}·{N + k} = {ans}.",
            f"Ответ: <b>{ans}</b>.",
        ]
        return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=f"факториал, F({N})")
    a = rng.randint(1, 4)
    c = rng.randint(1, 5)
    m = rng.randint(2, 3)
    n0 = rng.randint(10, 40)
    vals = {}
    for n in range(1, n0 + 1):
        if n <= 2:
            vals[n] = a
        elif n % 2 == 0:
            vals[n] = vals[n - 1] + c * n
        else:
            vals[n] = m * vals[n - 2] - n
    ans = vals[n0]
    statement = ("<p>Алгоритм вычисления значения функции F(n), где n — натуральное число, задан следующими соотношениями:</p>"
                 f"<p class=formula>F(n) = {a} при n ≤ 2;<br>F(n) = F(n − 1) + {c}·n, если n &gt; 2 и n чётно;<br>"
                 f"F(n) = {m}·F(n − 2) − n, если n &gt; 2 и n нечётно.</p>"
                 f"<p>Чему равно значение функции F({n0})?</p>")
    code = ("def F(n):\n"
            f"    if n <= 2:\n        return {a}\n"
            f"    if n % 2 == 0:\n        return F(n - 1) + {c} * n\n"
            f"    return {m} * F(n - 2) - n\n\n\nprint(F({n0}))\n")
    steps = [
        "Переписываем определение в функцию один в один. Порядок проверок важен: сначала база n ≤ 2, потом чётность.",
        f"Глубина рекурсии маленькая (до {n0}), и каждый вызов порождает только один рекурсивный, так что кэш не нужен.",
        "Частая ошибка — перепутать условия «чётно/нечётно» местами или забыть, что база проверяется раньше.",
        f"Ответ: <b>{ans}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=f"F({n0}), чётные и нечётные")


# ---------------------------------------------------------------- №23
def gen_23(rng):
    add = rng.choice([1, 2])
    mul = rng.choice([2, 3])
    third = rng.choice([None, "add", "sq"])
    add2 = rng.choice([3, 4, 5]) if third == "add" else None
    cmds = [("Прибавить %d" % add, lambda x: x + add), ("Умножить на %d" % mul, lambda x: x * mul)]
    if third == "add":
        cmds.insert(1, ("Прибавить %d" % add2, lambda x: x + add2))
    elif third == "sq":
        cmds.append(("Возвести в квадрат", lambda x: x * x))
    s = rng.randint(1, 4)
    t = rng.randint(20, 45) if third != "sq" else rng.randint(30, 80)
    inter = [x for x in range(s + 2, t - 2)]
    c = rng.choice(inter)
    d = rng.choice([x for x in inter if x != c] + [None])
    if third == "sq" and s == 1:
        return None

    def count(x0, y):
        # прямой ДП по возрастанию: все команды строго увеличивают число
        ways = [0] * (y + 1)
        ways[x0] = 1
        for x in range(x0, y + 1):
            if x == d:
                ways[x] = 0
                continue
            if ways[x] == 0:
                continue
            for _, f in cmds:
                nx = f(x)
                if nx <= y:
                    ways[nx] += ways[x]
        return ways[y]
    ans = count(s, c) * count(c, t)
    if ans == 0 or ans > 10**9:
        return None
    letters = "ABC"
    lst = "".join(f"<li>{letters[i]}. {name}</li>" for i, (name, _) in enumerate(cmds))
    statement = (f"<p>Исполнитель преобразует число на экране. У исполнителя есть {len(cmds)} команды:</p><ul class=cmds>{lst}</ul>"
                 "<p>Программа для исполнителя — это последовательность команд. Траектория вычислений программы — это последовательность "
                 "результатов выполнения всех команд программы.</p>"
                 f"<p>Сколько существует программ, для которых при исходном числе {s} результатом является число {t}, и при этом траектория вычислений "
                 f"содержит число {c}" + (f" и не содержит числа {d}" if d else "") + "?</p>")
    ops = []
    if True:
        ops.append(f"f(x + {add}, y)")
        if third == "add":
            ops.append(f"f(x + {add2}, y)")
        ops.append(f"f(x * {mul}, y)")
        if third == "sq":
            ops.append("f(x * x, y)")
    bad = f" or x == {d}" if d else ""
    code = ("from functools import lru_cache\n\n\n@lru_cache(None)\ndef f(x, y):\n"
            f"    if x > y{bad}:\n        return 0\n    if x == y:\n        return 1\n"
            f"    return {' + '.join(ops)}\n\n\nprint(f({s}, {c}) * f({c}, {t}))\n")
    sq_note = (" Возведение в квадрат для x = 1 даёт снова 1 — но тогда рекурсия зациклится. "
               "Здесь стартовое число и все промежуточные больше 1, поэтому квадрат строго увеличивает число." if third == "sq" else "")
    if third == "sq" and s == 1:
        return None
    steps = [
        "f(x, y) — число программ, переводящих x в y. Все команды только увеличивают число, поэтому если x > y, путей нет, а x = y даёт ровно одну (пустую) программу." + sq_note,
        f"«Траектория содержит {c}» — значит, путь распадается на два независимых куска: {s} → {c} и {c} → {t}. Число программ — произведение.",
        (f"«Не содержит {d}» — просто считаем, что из {d} путей нет: <code>x == {d}</code> возвращает 0." if d else
         "Запрещённых чисел нет, так что дополнительных проверок не нужно."),
        f"Считаем: f({s}, {c}) · f({c}, {t}) = {ans}.",
        f"Ответ: <b>{ans}</b>.",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=str(ans), title=f"из {s} в {t} через {c}" + (f", без {d}" if d else ""))


# ---------------------------------------------------------------- №25
def expand_mask(mask, maxlen):
    out = set()

    def rec(i, cur):
        if len(cur) > maxlen:
            return
        if i == len(mask):
            if cur and cur[0] != "0":
                out.add(int(cur))
            return
        ch = mask[i]
        if ch == "?":
            for dch in "0123456789":
                rec(i + 1, cur + dch)
        elif ch == "*":
            fixed = sum(1 for c in mask[i + 1:] if c != "*")
            for L in range(0, maxlen - len(cur) - fixed + 1):
                for tail in itertools.product("0123456789", repeat=L):
                    rec(i + 1, cur + "".join(tail))
        else:
            rec(i + 1, cur + ch)
    rec(0, "")
    return out


def gen_25(rng):
    limit_pow = 9
    digits = "0123456789"
    for _ in range(50):
        parts = []
        L = rng.randint(4, 7)
        star_used = False
        for i in range(L):
            r = rng.random()
            if r < 0.2 and not star_used and i > 0:
                parts.append("*")
                star_used = True
            elif r < 0.45:
                parts.append("?")
            else:
                parts.append(rng.choice(digits[1:] if i == 0 else digits))
        mask = "".join(parts)
        if "*" not in mask and "?" not in mask:
            continue
        if mask[0] in "0":
            continue
        fixed = sum(1 for c in mask if c != "*")
        if fixed > limit_pow:
            continue
        D = rng.randint(2000, 60000)
        rx = re.compile(mask.replace("?", "[0-9]").replace("*", "[0-9]*"))
        found = [x for x in range(D, 10**limit_pow + 1, D) if rx.fullmatch(str(x))]
        if 1 <= len(found) <= 8:
            break
    else:
        return None
    statement = ("<p>Назовём маской числа последовательность цифр, в которой также могут встречаться следующие символы:</p>"
                 "<ul><li>символ «?» означает ровно одну произвольную цифру;</li>"
                 "<li>символ «*» означает любую последовательность цифр произвольной длины; в том числе «*» может задавать и пустую последовательность.</li></ul>"
                 f"<p>Среди натуральных чисел, не превышающих 10<sup>{limit_pow}</sup>, найдите все числа, соответствующие маске <b>{mask}</b>, "
                 f"делящиеся на {D} без остатка.</p>"
                 "<p>В ответе запишите все найденные числа в порядке возрастания, справа от каждого числа — результат его деления на "
                 f"{D}.</p>")
    code = ("from fnmatch import fnmatch\n\n"
            f"for x in range({D}, 10**{limit_pow} + 1, {D}):\n"
            f"    if fnmatch(str(x), '{mask}'):\n        print(x, x // {D})\n")
    ans = "\n".join(f"{x} {x // D}" for x in found)
    steps = [
        f"Перебирать все числа до 10<sup>{limit_pow}</sup> слишком долго. Перебираем только кратные {D}: шагаем по <code>range({D}, 10**{limit_pow} + 1, {D})</code>, это примерно {10**limit_pow // D:,} итераций.".replace(",", " "),
        "Маску проверяет <code>fnmatch</code> из стандартной библиотеки: в ней «?» и «*» значат ровно то же, что в условии. Число переводим в строку.",
        "Числа идут по возрастанию сами, сортировать не нужно.",
        "Если хочется быстрее: можно перебирать подстановки в маску (каждый «?» — 10 вариантов, «*» — строки разной длины) и проверять делимость. Это быстрее, когда маска почти вся из фиксированных цифр.",
        "Ответ:<br><pre class=answer>" + ans + "</pre>",
    ]
    return dict(statement=statement, steps=steps, code=code, answer=ans, title=f"маска {mask}, делится на {D}")


GENERATORS = {
    5: (gen_5, "Анализ алгоритма: двоичная запись"),
    7: (gen_7, "Кодирование изображений и звука"),
    8: (gen_8, "Комбинаторика: перебор слов"),
    11: (gen_11, "Объём информации: пароли"),
    12: (gen_12, "Исполнитель Редактор"),
    13: (gen_13, "IP-адреса и маски"),
    14: (gen_14, "Системы счисления"),
    15: (gen_15, "Логические выражения: ДЕЛ и отрезки"),
    16: (gen_16, "Рекурсивные функции"),
    23: (gen_23, "Количество программ исполнителя"),
    25: (gen_25, "Маски чисел и делимость"),
}
