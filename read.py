import re


def preprocess(str):
    table = re.sub(r'\n\s*', '\\n', str)
    table = re.sub(r'<td class="">', '<td>', table)
    table = re.sub(r'\s*->\s*', '##', table)
    #table = re.sub(r'<(/*)ul\\n>', '', table)
    table = table.replace("<ul>", "")
    table = table.replace("</ul>", "")
    return table


def inpiece(str, left, right, endFinder, rest=False):
    start = str.find(left)
    end = endFinder(right)
    # print(f's{start},e{end}')
    if (end < 0 or start < 0):
        raise Exception(f"cant find {left}:{start} or {right}:{end} in input")
    start += len(left)
    if (end < start):
        raise Exception(f'nothing between {left}:{start} and {right}:{end} in input')
    if (rest):
        return str[start:end], str[end + len(right):]
    return str[start:end]


def piece(str, left, right, rest=False):
    return inpiece(str, left, right, str.find, rest)


def rpiece(str, left, right, rest=False):
    return inpiece(str, left, right, str.rfind, rest)


def sanitize(str):
    s = str.strip()
    occ = s.find("<")
    count = 0
    while True:
        if occ < -1 or count > 11 or len(s) == 0:
            break
        end = s.find(">")
        s = s[0:max(occ, 0)] + s[end + 1:len(s) + 1]
        occ = s.find("<")
        count += 1
    return s


def scrub(str):
    splits = str.split("\n")
    splits = [sanitize(s) for s in splits][1:len(splits) - 1]
    return len(splits),",".join(splits)


def clean_conflict(str):
    sub = "<td class=\"conflict\">"
    start = str.find(sub)
    end = str.find("</td>", start)
    x = "<td>" + str[start + len(sub):end].replace(" ", "")
    return str[:start] + x + str[end:]


def section(str, n):
    out = []
    str = clean_conflict(str)
    str = str.replace("</li>\n<li>", "!!")
    row, fields = piece(str, "<th ", "</th>", True)
    out.append(sanitize(row))
    for i in range(n - 1):
        try:
            row, fields = piece(fields, "<td>", "</td>", True)
            out.append(sanitize(row))
        except Exception as e:
            print("error:", e)
    return ",".join(out)


def extract(str):
    out = ""
    table = preprocess(str)
    fullHead, tail = piece(table, "<thead>", "</thead>", True)
    headers = piece(fullHead, "<tr>", "</tr>")

    n, scrubbed = scrub(headers)

    out = scrubbed + "\n"

    while True:
        try:
            head, tail = piece(tail, "<tr>", "</tr>", True)
            out += section(head,n) + "\n"
        except Exception:
            return out


with open("in/table2.html", "r") as f:
    table = f.read()
    f.close()

table = extract(table)

with open("out/table2.csv", "w") as f:
    f.write(table)
    f.close()
