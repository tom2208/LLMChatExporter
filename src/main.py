from bs4 import BeautifulSoup, NavigableString, Tag

code_lang = ""


def escape_md(text):
    return text.replace("`", "\\`")


def process_br():
    return "\n"


def process_bold(node, list_stack):
    return "**" + "".join(node_to_md(c, list_stack) for c in node.children) + "**"


def node_to_md(node, list_stack=None):
    global code_lang

    if list_stack is None:
        list_stack = []

    if isinstance(node, NavigableString):
        return escape_md(str(node))

    if not isinstance(node, Tag):
        return ""

    tag = node.name.lower()
    tag_class = node.get("class")

    if tag == "span" and tag_class is not None:
        if any(c.startswith("ng-tns") for c in tag_class):
            code_lang = node.get_text(strip=True)
            return ""

    if tag in ("p", "div"):
        inner = "".join(node_to_md(c, list_stack) for c in node.children).strip()
        return inner + "\n\n" if inner else ""

    if tag in ("br",):
        return process_br()

    if tag in ("strong", "b"):
        return process_bold(node, list_stack)

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        text = "".join(node_to_md(c, list_stack) for c in node.children).strip()
        return "#" * level + " " + text + "\n\n"

    if tag in ("ul", "ol"):
        out = ""
        list_stack.append(tag)
        for i, li in enumerate(
            [c for c in node.children if isinstance(c, Tag) and c.name == "li"]
        ):
            out += node_to_md(li, list_stack)
        list_stack.pop()
        return out + "\n"

    if tag == "li":
        indent = "  " * (len(list_stack) - 1)
        parent = list_stack[-1] if list_stack else "ul"
        if parent == "ol":
            prefix = "1. "
        else:
            prefix = "- "
        content = "".join(node_to_md(c, list_stack) for c in node.children).strip()
        content = content.replace("\n", "\n" + indent + "  ")
        return indent + prefix + content + "\n"

    if tag == "a":
        href = node.get("href", "")
        text = "".join(node_to_md(c, list_stack) for c in node.children).strip() or href
        return f"[{text}]({href})"

    if tag == "img":
        alt = node.get("alt", "")
        src = node.get("src", "")
        return f"![{alt}]({src})"

    if tag == "hr":
        return "---\n\n"

    if tag == "table-block":
        return "".join(node_to_md(c, list_stack) for c in node.children) + "\n\n"

    if tag == "table":
        out = []
        rows = node.find_all("tr")
        if not rows:
            print("Warning: table with no rows")
            return ""

        column_numbers = len(rows[0].find_all("td"))

        if column_numbers == 0:
            print("Warning: table with no columns")
            return ""

        for r in rows:
            cols = r.find_all(["td"])
            if len(cols) != column_numbers:
                print("Warning: inconsistent number of columns in table")
                return ""
            out.append(
                "| "
                + " | ".join(node_to_md(c, list_stack).strip() for c in cols)
                + " |\n"
            )
        out.insert(1, "| " + " | ".join(["---"] * column_numbers) + " |\n")
        return "".join(out) + "\n"

    if tag == "code":
        if tag_class is None:
            code = "".join(node_to_md(c, list_stack) for c in node.children).strip()
            return f"`{code}`"
        elif "code-container" in tag_class:
            code = "".join(node_to_md(c, list_stack) for c in node.children).strip()
            result = f"```{code_lang}\n{code}\n```\n\n"
            code_lang = ""
            return result

    # fallback: render children
    return "".join(node_to_md(c, list_stack) for c in node.children)


def div_to_markdown(div_tag):
    return node_to_md(div_tag).strip() + "\n"


def generate_lines(lines: str) -> str:
    return "".join(["> " + line + "\n" for line in lines.splitlines()]) + "\n\n"


def generate_chat():
    with open("/home/tom/Downloads/Google Gemini.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")

    divs_answer = soup.select(
        "div.markdown.markdown-main-panel.enable-updated-hr-color"
    )
    divs_query = soup.select("div.query-text.gds-body-l")

    md_answers = [div_to_markdown(d) for d in divs_answer]
    md_query = [div_to_markdown(d) for d in divs_query]

    chat = ""
    for i in range(0, len(md_query)):
        exchange = ""
        exchange = exchange + "**Query:**\n"
        exchange = exchange + generate_lines(md_query[i])
        if i < len(md_answers):
            exchange = exchange + "**Answer:**\n"
            exchange = exchange + generate_lines(md_answers[i])
        chat = chat + exchange

    return chat


with open("./tar/chat.md", "w", encoding="utf-8") as f:
    f.write(generate_chat())
