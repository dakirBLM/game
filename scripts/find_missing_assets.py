import os, re
root = 'MagicForest'
project_root = os.path.abspath('.')
magic_root = os.path.join(project_root, root)
missing = []
found = []
for dirpath, dirs, files in os.walk(root):
    for fname in files:
        if not fname.endswith('.py'): continue
        path = os.path.join(dirpath, fname)
        try:
            with open(path, 'r', errors='ignore') as f:
                s = f.read()
        except Exception:
            continue
        # find SPRITESHEET_PATH + "..."
        for m in re.finditer(r"SPRITESHEET_PATH\s*\+\s*[\"']([^\"']+\.(?:png|bmp|jpg|jpeg))", s):
            rel = m.group(1)
            cfgpath = os.path.join(dirpath, 'Config.py')
            sp = ''
            if os.path.exists(cfgpath):
                try:
                    # Execute the Config.py in an isolated namespace so dynamic
                    # path expressions (os.path.join, __file__, etc.) are evaluated.
                    cfg_ns = {'__file__': cfgpath, '__name__': '__config__'}
                    with open(cfgpath, 'r', errors='ignore') as cf:
                        exec(cf.read(), cfg_ns)
                    sp = cfg_ns.get('SPRITESHEET_PATH', '') or ''
                    # If SPRITESHEET_PATH is absolute, keep as-is; otherwise make it
                    # relative to the MagicForest root so resolution below works.
                    if sp and not os.path.isabs(sp):
                        sp = os.path.normpath(sp)
                except Exception:
                    sp = ''
            # resolve SPRITESHEET_PATH relative to the MagicForest root
            candidate = os.path.normpath(os.path.join(magic_root, sp, rel))
            found.append(candidate)
            if not os.path.exists(candidate):
                missing.append(candidate)
        # also find direct 'Assets/...png' references
        for m in re.finditer(r"[\"']([^\"']*Assets/[^\"']+\.(?:png|bmp|jpg|jpeg))[\"']", s):
            candidate = os.path.normpath(m.group(1))
            if not os.path.isabs(candidate):
                candidate = os.path.normpath(os.path.join(project_root, candidate))
            found.append(candidate)
            if not os.path.exists(candidate):
                missing.append(candidate)

missing = sorted(set(missing))
print('Found', len(found), 'references; missing', len(missing))
for m in missing:
    print(m)
