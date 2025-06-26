import os
import sys
import re
from flask import Flask, render_template_string
from markdown_it import MarkdownIt

app = Flask(__name__)

MD_DIR = None

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")

TEMPLATE = """
<html>
<head>
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            background: #f8fafc;
            color: #222;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 270px;
            background: #fff;
            border-right: 1px solid #e5e7eb;
            padding: 32px 24px;
            box-shadow: 2px 0 8px rgba(0,0,0,0.03);
            display: flex;
            flex-direction: column;
        }
        .sidebar h2 {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom:  1.5rem;
            color: #2563eb;
            letter-spacing: 1px;
        }
        .sidebar ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .sidebar li {
            margin-bottom: 0.7rem;
        }
        .sidebar a {
            display: block;
            padding: 8px 14px;
            border-radius: 6px;
            color: #2563eb;
            font-weight: 500;
            transition: background 0.15s, color 0.15s;
        }
        .sidebar a:hover {
            background: #e0e7ff;
            color: #1e40af;
        }
        .content {
            flex: 1;
            padding: 40px 48px;
            overflow-y: auto;
            background: #f8fafc;
            box-shadow: -2px 0 8px rgba(0,0,0,0.02);
        }
        .content h1, .content h2, .content h3, .content h4 {
            color: #1e293b;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        .content p {
            line-height: 1.7;
            margin-bottom: 1.2em;
        }
        .content pre {
            background: #1e293b;
            color: #f1f5f9;
            padding: 1em;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 1em;
        }
        .content code {
            background: #e2e8f0;
            color: #be185d;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.97em;
        }
        .content ul, .content ol {
            margin-left: 1.5em;
            margin-bottom: 1em;
        }
        .content blockquote {
            border-left: 4px solid #60a5fa;
            background: #f1f5f9;
            color: #334155;
            padding: 0.7em 1.2em;
            margin: 1.2em 0;
            border-radius: 6px;
        }
        @media (max-width: 800px) {
            .container { flex-direction: column; }
            .sidebar { width: 100%; border-right: none; border-bottom: 1px solid #e5e7eb; box-shadow: none; }
            .content { padding: 24px 12px; }
        }
    </style>
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']]
            }
        };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <meta http-equiv="refresh" content="1">
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>Markdown Files</h2>
            <ul>
                {% for file in files %}
                    <li><a href="/{{ file }}">{{ file }}</a></li>
                {% endfor %}
            </ul>
        </div>
        <div class="content">
            {{ content|safe }}
        </div>
    </div>
</body>
</html>
"""

def resolve_wiki_links(content: str) -> str:
    # First, handle [[file|display]]
    content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', lambda m: f'[{m.group(2)}]({m.group(1).strip().replace(" ", "-")}.md)', content)
    # Then, handle [[file]]
    content = re.sub(r'\[\[([\w\s-]+)\]\]', lambda m: f'[{m.group(1)}]({m.group(1).strip().replace(" ", "-")}.md)', content)
    return content

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

    return render_template_string(TEMPLATE, files=files, content=content_html)

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