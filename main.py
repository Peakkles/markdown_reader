# File: app.py
import os
import sys
import re
from flask import Flask, render_template, send_from_directory
from markdown_it import MarkdownIt

app = Flask(__name__)

MD_DIR = None

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")

def resolve_wiki_links(content: str) -> str:
    return re.sub(r'\[\[([\w\s-]+)\]\]', lambda m: f'[{m.group(1)}]({m.group(1).strip().replace(" ", "-")}.md)', content)

@app.route('/')
def index():
    return serve_markdown(None)

@app.route('/<path:filename>')
def serve_markdown(filename):
    files = sorted([f for f in os.listdir(MD_DIR) if f.endswith('.md')])
    if not filename:
        filename = files[0] if files else None

    content_html = ""
    if filename:
        full_path = os.path.join(MD_DIR, filename)
        if os.path.isfile(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            resolved = resolve_wiki_links(raw)
            content_html = md.render(resolved)
        else:
            content_html = f"<p><strong>Error:</strong> File '{filename}' not found.</p>"

    return render_template('layout.html', files=files, content=content_html)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python app.py path_to_directory")
        sys.exit(1)

    MD_DIR = os.path.abspath(sys.argv[1])
    if not os.path.isdir(MD_DIR):
        print("Provided path is not a directory.")
        sys.exit(1)

    print(f"Serving Markdown files from {MD_DIR} at http://localhost:5000")
    app.run(debug=True, use_reloader=False)
