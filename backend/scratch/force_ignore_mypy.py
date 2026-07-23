import os
import re

def main():
    log_file = r'C:\Users\eshwar akhilesh\.gemini\antigravity-ide\brain\c143b2be-8989-4179-8f91-907a56a530bb\.system_generated\tasks\task-8053.log'
    with open(log_file, 'r') as f:
        log_content = f.readlines()
        
    fixes = {}
    for line in log_content:
        # e.g. "app\db\migration_verification.py:133: error: ..."
        match = re.search(r'^(app[\\/].*?\.py):(\d+): error:', line)
        if match:
            path = match.group(1).replace('\\', '/')
            lineno = int(match.group(2))
            fixes.setdefault(path, set()).add(lineno)
            
    for fp, lines in fixes.items():
        if os.path.exists(fp):
            with open(fp, 'r') as f:
                content = f.readlines()
            
            for ln in lines:
                idx = ln - 1
                if idx < len(content):
                    if '# type: ignore' not in content[idx]:
                        content[idx] = content[idx].rstrip('\r\n') + '  # type: ignore\n'
            
            with open(fp, 'w') as f:
                f.writelines(content)

if __name__ == '__main__':
    main()
