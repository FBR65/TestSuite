import os
import json
import glob
from datetime import datetime
from pathlib import Path

def read_markdown_file(file_path):
    """Read and return the content of a markdown file as formatted HTML."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return convert_markdown_to_html(content)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def convert_markdown_to_html(markdown_content):
    """Convert markdown content to properly formatted HTML."""
    if not markdown_content:
        return ""
    
    lines = markdown_content.split('\n')
    html_lines = []
    in_list = False
    list_type = None
    in_table = False
    table_lines = []
    
    for line in lines:
        line = line.rstrip()
        
        # Headers
        if line.startswith('# '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h1>{line[2:].strip()}</h1>')
        elif line.startswith('## '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('### '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('#### '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h4>{line[5:].strip()}</h4>')
        elif line.startswith('##### '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h5>{line[6:].strip()}</h5>')
        elif line.startswith('###### '):
            # Close any open lists before adding header
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<h6>{line[7:].strip()}</h6>')
        # Lists
        elif line.startswith('- ') or line.startswith('* ') or line.startswith('+ '):
            if not in_list or list_type != 'ul':
                html_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_lines.append(f'<li>{line[2:].strip()}</li>')
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            if not in_list or list_type != 'ol':
                html_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            # Remove trailing dot if present
            list_content = line.split(". ", 1)[1].strip()
            if list_content.endswith('.'):
                list_content = list_content[:-1]
            html_lines.append(f'<li>{list_content}</li>')
        # Tables - collect table lines first
        elif line.startswith('|') and line.endswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
        # End of table (non-table line after table lines)
        elif in_table and not line.startswith('|'):
            in_table = False
            # Process collected table lines
            if table_lines:
                html_lines.append('<table>')
                for table_line in table_lines:
                    cells = [cell.strip() for cell in table_line.split('|')[1:-1]]
                    if table_line.strip().startswith('|---'):
                        # Header separator
                        html_lines.append('<tr>')
                        html_lines.append(''.join([f'<th>{cell}</th>' for cell in cells]))
                        html_lines.append('</tr>')
                    else:
                        # Data row
                        html_lines.append('<tr>')
                        html_lines.append(''.join([f'<td>{cell}</td>' for cell in cells]))
                        html_lines.append('</tr>')
                html_lines.append('</table>')
                table_lines = []
        # Horizontal rules
        elif line.strip() in ['---', '***', '___']:
            # Close any open lists before adding horizontal rule
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append('<hr>')
        # Blockquotes
        elif line.startswith('> '):
            # Close any open lists before adding blockquote
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<blockquote>{line[2:].strip()}</blockquote>')
        # Code blocks
        elif line.startswith('    ') or line.startswith('\t'):
            # Close any open lists before adding code block
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            html_lines.append(f'<pre><code>{line.strip()}</code></pre>')
        # Empty lines (end lists)
        elif not line.strip():
            if in_list:
                html_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            # Only add <br> if not at the end of content
            if html_lines and html_lines[-1] != '<br>':
                html_lines.append('<br>')
        # Regular paragraphs
        else:
            if line.strip():
                # Close any open lists before adding paragraph
                if in_list:
                    html_lines.append(f'</{list_type}>')
                    in_list = False
                    list_type = None
                html_lines.append(f'<p>{line.strip()}</p>')
    
    # Close any open lists
    if in_list:
        html_lines.append(f'</{list_type}>')
    
    # Handle any remaining table lines
    if in_table and table_lines:
        html_lines.append('<table>')
        for table_line in table_lines:
            cells = [cell.strip() for cell in table_line.split('|')[1:-1]]
            if table_line.strip().startswith('|---'):
                # Header separator
                html_lines.append('<tr>')
                html_lines.append(''.join([f'<th>{cell}</th>' for cell in cells]))
                html_lines.append('</tr>')
            else:
                # Data row
                html_lines.append('<tr>')
                html_lines.append(''.join([f'<td>{cell}</td>' for cell in cells]))
                html_lines.append('</tr>')
        html_lines.append('</table>')
    
    return '\n'.join(html_lines)

def read_json_file(file_path):
    """Read and return the content of a JSON file as formatted HTML."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return format_json_as_html(data)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def format_json_as_html(data, indent=0):
    """Format JSON data as HTML with proper styling."""
    html = ""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                html += f"<div style='margin-left: {indent * 20}px;'>"
                html += f"<strong>{key}:</strong>"
                html += format_json_as_html(value, indent + 1)
                html += "</div>"
            else:
                html += f"<div style='margin-left: {indent * 20}px;'>"
                html += f"<strong>{key}:</strong> {value}"
                html += "</div>"
    elif isinstance(data, list):
        for i, item in enumerate(data):
            html += f"<div style='margin-left: {indent * 20}px;'>"
            html += f"<strong>Item {i + 1}:</strong>"
            html += format_json_as_html(item, indent + 1)
            html += "</div>"
    return html

def get_test_report_files():
    """Get all test_report*.md files sorted by creation time (oldest first)."""
    pattern = "test_report_*.md"
    files = glob.glob(pattern)
    # Sort by creation time (oldest first)
    files.sort(key=lambda x: os.path.getctime(x))
    return files

def generate_html_report():
    """Generate the complete HTML report."""
    
    # HTML header
    html = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bewertung von Modellen</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 30px;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
        }
        .divider {
            border: 2px solid #bdc3c7;
            margin: 30px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .json-content {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .timestamp {
            text-align: right;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bewertung von Modellen</h1>
"""
    
    # Add DurchgeführteTests.md
    durchgefuehrte_tests = read_markdown_file("DurchgeführteTests.md")
    if durchgefuehrte_tests:
        # Remove duplicate heading from markdown content by replacing h2 with h1
        durchgefuehrte_tests = durchgefuehrte_tests.replace('<h2>Durchgeführte Tests - TestSuite System</h2>', '')
        # Remove "5. Allgemeine Testdurchführung" section completely
        durchgefuehrte_tests = durchgefuehrte_tests.replace('<h2>5. Allgemeine Testdurchführung</h2>', '')
        # Remove everything from "Testablauf" heading until the next h2 or hr
        lines = durchgefuehrte_tests.split('\n')
        filtered_lines = []
        skip_section = False
        for line in lines:
            if '<h3>Testablauf</h3>' in line:
                skip_section = True
                continue
            if skip_section:
                if line.startswith('<h2>') or line.startswith('<hr>') or line.startswith('<div class="divider">'):
                    skip_section = False
                else:
                    continue
            filtered_lines.append(line)
        durchgefuehrte_tests = '\n'.join(filtered_lines)
        html += durchgefuehrte_tests
        html += '<div class="divider"></div>'
    
    # Get test report files and add them with specific headings
    test_report_files = get_test_report_files()
    
    if len(test_report_files) >= 1:
        # First test report (oldest) gets "Detaillierte Analyse"
        first_report = read_markdown_file(test_report_files[0])
        if first_report:
            html += "<h1>Detaillierte Analyse</h1>"
            html += first_report
            html += '<div class="divider"></div>'
        
        # Second test report gets "Umfassendes Memo" if available
        if len(test_report_files) >= 2:
            second_report = read_markdown_file(test_report_files[1])
            if second_report:
                html += "<h1>Umfassendes Memo</h1>"
                html += second_report
                html += '<div class="divider"></div>'
        
        # Remaining test reports go under "Anhänge"
        if len(test_report_files) > 2:
            html += "<h2>Anhänge</h2>"
            for i, file_path in enumerate(test_report_files[2:], 2):
                report_content = read_markdown_file(file_path)
                if report_content:
                    html += f"<h3>Testbericht {i + 1}</h3>"
                    html += report_content
                    html += '<hr style="margin: 20px 0; border: 1px solid #bdc3c7;">'
    
    # Add JSON files from data/results
    html += "<h2>Anhang - Testergebnisse (JSON)</h2>"
    
    # Get all JSON files in data/results directory
    json_files = []
    for root, dirs, files in os.walk("data/results"):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    
    # Sort JSON files alphabetically
    json_files.sort()
    
    for json_file in json_files:
        json_content = read_json_file(json_file)
        if json_content:
            # Get relative path for display
            relative_path = os.path.relpath(json_file)
            html += f"<h3>{relative_path}</h3>"
            html += f'<div class="json-content">{json_content}</div>'
            html += '<hr style="margin: 20px 0; border: 1px solid #bdc3c7;">'
    
    # HTML footer
    html += f"""
        <div class="timestamp">
            Bericht erstellt am: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Main function to generate and save the HTML report."""
    print("Generiere HTML-Bericht...")
    
    html_content = generate_html_report()
    
    # Save the HTML report
    output_file = "model_evaluation_report.html"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML-Bericht erfolgreich erstellt: {output_file}")
        print(f"Datei gespeichert unter: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")

if __name__ == "__main__":
    main()