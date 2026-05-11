import os

def fix_file(filepath, depth):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        prefix = '../' * depth
        
        content = content.replace('src="/assets/', f'src="{prefix}assets/')
        content = content.replace('href="/assets/', f'href="{prefix}assets/')
        content = content.replace('src="/components/', f'src="{prefix}components/')
        content = content.replace('href="/components/', f'href="{prefix}components/')
        content = content.replace('href="/pages/', f'href="{prefix}pages/')
        content = content.replace('href="/index.html', f'href="{prefix}index.html')
        content = content.replace("href='/index.html", f"href='{prefix}index.html")
        content = content.replace("window.location.href = '/index.html'", f"window.location.href = '{prefix}index.html'")
        content = content.replace('window.location.href = "/index.html"', f'window.location.href = "{prefix}index.html"')
        content = content.replace("href: '/pages/", f"href: '{prefix}pages/")
        content = content.replace('href: "/pages/', f'href: "{prefix}pages/')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'OK: {filepath}')
    except Exception as e:
        print(f'XATO {filepath}: {e}')

# index.html - depth 0
fix_file('index.html', 0)

# Admin sahifalari - depth 2
for fn in os.listdir('pages/admin'):
    if fn.endswith('.html'):
        fix_file(f'pages/admin/{fn}', 2)

# Teacher sahifalari - depth 2
for fn in os.listdir('pages/teacher'):
    if fn.endswith('.html'):
        fix_file(f'pages/teacher/{fn}', 2)

# Student sahifalari - depth 2
for fn in os.listdir('pages/student'):
    if fn.endswith('.html'):
        fix_file(f'pages/student/{fn}', 2)

print('Hammasi tayyor!')