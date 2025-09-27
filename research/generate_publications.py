import bibtexparser
from collections import defaultdict

# ---------------------------
# Configuration
# ---------------------------
BIB_FILE = "content/research/pubs.bib"
OUTPUT_PUB_MD = "content/research/publications.md"
OUTPUT_COLLAB_MD = "content/research/collaborators.md"
SELF_NAME = "Qiong Zhang"


# ---------------------------
# Helper functions
# ---------------------------
def normalize_name(name):
    if "," in name:
        last, first = [n.strip() for n in name.split(",", 1)]
        return f"{first} {last}"
    return name.strip()


def parse_note_field(note_str):
    notes = {}
    if not note_str:
        return notes
    for part in note_str.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            notes[key.strip()] = [
                normalize_name(v.strip()) for v in value.split("|")
            ]
    return notes


def format_authors(authors_str, notes, self_name=SELF_NAME):
    authors = [
        normalize_name(a)
        for a in authors_str.replace("\n", " ").split(" and ")
    ]
    print(authors)
    formatted = []
    for a in authors:
        print(a)
        name_fmt = a
        # Bold self
        if "self" in notes and a in notes["self"]:
            name_fmt = f"**{a}**"
        # Equal contribution
        if "equalcontrib" in notes and a in notes["equalcontrib"]:
            name_fmt += "†"
        # Supervised students
        if "supervised" in notes and a in notes["supervised"]:
            name_fmt += "*"
        # Corresponding authors
        if "corresponding" in notes and a in notes["corresponding"]:
            name_fmt += "✉"
        formatted.append(name_fmt)
    return ", ".join(formatted)


def format_links(entry):
    """Generate Markdown links for paper, code, and BibTeX collapsible."""
    links = []
    if "publisherurl" in entry:
        links.append(f"[Paper]({entry['publisherurl']})")
    if "code" in entry:
        links.append(f"[Code]({entry['code']})")
    bibtex_md = ""
    if "bibtex" in entry:
        bibtex_content = entry["bibtex"].replace("\n", "  \n")
        bibtex_md = f"<details>\n<summary>BibTeX</summary>\n\n```bibtex\n{bibtex_content}\n```\n</details>"
    links_line = " | ".join(links)
    if links_line:
        links_line += "\n" + bibtex_md
    else:
        links_line = bibtex_md
    return links_line


# ---------------------------
# Load BibTeX
# ---------------------------
with open(BIB_FILE, encoding="utf-8") as f:
    bib_entries = bibtexparser.load(f).entries

# ---------------------------
# Generate publications.md
# ---------------------------
sections = ["published", "preprints", "workinprogress", "thesis"]
section_entries = {s: [] for s in sections}

for entry in bib_entries:
    keywords = entry.get("keywords", "").lower().split(",")
    section = None
    for s in sections:
        if s in keywords:
            section = s
            break
    if section is None:
        section = "published"

    notes = parse_note_field(entry.get("note", ""))
    authors_formatted = format_authors(entry.get("author", ""),
                                       notes,
                                       self_name=SELF_NAME)
    title = entry.get("title", "")
    journal = entry.get("journal", "") or entry.get("booktitle", "")
    year = entry.get("year", "")
    links = format_links(entry)

    # Markdown entry
    md_entry = f"- **{title}**  \n"
    md_entry += f"   {authors_formatted}     \n"
    md_entry += f"   {journal}, {year}     \n"
    if links:
        md_entry += f"  {links}\n"

    section_entries[section].append(md_entry)

with open(OUTPUT_PUB_MD, "w", encoding="utf-8") as f:
    f.write("# Publications\n\n")
    for sec in sections:
        f.write(f"## {sec.capitalize()}\n\n")
        for md in section_entries[sec]:
            f.write(md + "\n\n")

print(f"Generated {OUTPUT_PUB_MD}")

# ---------------------------
# Generate collaborators.md
# ---------------------------
collab_count = defaultdict(int)
for entry in bib_entries:
    notes = parse_note_field(entry.get("note", ""))
    authors = [
        normalize_name(a)
        for a in entry.get("author", "").replace("\n", " ").split(" and ")
    ]
    for a in authors:
        if a != SELF_NAME:
            collab_count[a] += 1

# Sort by number of papers descending
collabs_sorted = sorted(collab_count.items(), key=lambda x: -x[1])

with open(OUTPUT_COLLAB_MD, "w", encoding="utf-8") as f:
    f.write("# Collaborators\n\n")
    for name, count in collabs_sorted:
        f.write(f"- {name} ({count} papers)\n")

print(f"Generated {OUTPUT_COLLAB_MD}")
