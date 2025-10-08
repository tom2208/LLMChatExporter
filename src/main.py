from bs4 import BeautifulSoup, NavigableString, Tag


def escape_md(text):
    return text.replace("`", "\\`")


def node_to_md(node, list_stack=None):
    if list_stack is None:
        list_stack = []

    if isinstance(node, NavigableString):
        return escape_md(str(node))

    if not isinstance(node, Tag):
        return ""

    tag = node.name.lower()

    if tag in ("p", "div"):
        inner = "".join(node_to_md(c, list_stack) for c in node.children).strip()
        return inner + "\n\n" if inner else ""

    if tag in ("br",):
        return "  \n"

    if tag in ("strong", "b"):
        return "**" + "".join(node_to_md(c, list_stack) for c in node.children) + "**"

    if tag in ("em", "i"):
        return "_" + "".join(node_to_md(c, list_stack) for c in node.children) + "_"

    if tag == "code" and node.parent.name == "pre":
        return ""
    if tag == "code":
        return "`" + "".join(node_to_md(c, list_stack) for c in node.children) + "`"

    if tag == "pre":
        # try to get language from child <code class="language-...">
        code_tag = node.find("code")
        code_text = code_tag.get_text() if code_tag else node.get_text()
        return "```\n" + code_text.rstrip() + "\n```\n\n"

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
            # find index among siblings
            # caller preserves order so we can approximate with placeholder number
            prefix = "1. "
        else:
            prefix = "- "
        content = "".join(node_to_md(c, list_stack) for c in node.children).strip()
        # allow nested lists inside li; ensure inner lines are indented
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

    if tag == "blockquote":
        inner = (
            "".join(node_to_md(c, list_stack) for c in node.children)
            .strip()
            .splitlines()
        )
        return "\n".join(["> " + line for line in inner]) + "\n\n"

    if tag == "hr":
        return "---\n\n"

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


with open("/home/tom/Downloads/output.md", "w", encoding="utf-8") as f:
    f.write(generate_chat())
