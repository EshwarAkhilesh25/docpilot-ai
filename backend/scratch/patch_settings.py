import re

def fix_file(filepath, module_path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern: 
    #         "app.something.get_settings"
    #     ) as mock_settings:
    #         mock_settings.return_value = MagicMock(
    #             KEY="val",
    #             ...
    #         )
    
    # We can use regex to find and replace this.
    # The patch string can be on the same line or next line.
    
    # Replace get_settings with settings
    content = content.replace(f'"{module_path}.get_settings"', f'"{module_path}.settings"')
    
    # Replace mock_settings.return_value = MagicMock(\n ... ) with mock_settings.KEY = "val"
    
    def replacer(match):
        indent = match.group(1)
        args_block = match.group(2)
        
        lines = []
        for line in args_block.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                # Remove trailing comma
                if line.endswith(','):
                    line = line[:-1]
                key, val = line.split('=', 1)
                lines.append(f"{indent}mock_settings.{key.strip()} = {val.strip()}")
        return '\n'.join(lines)
        
    pattern = re.compile(r'([ \t]+)mock_settings\.return_value\s*=\s*MagicMock\((.*?)\)', re.DOTALL)
    
    # We need to make sure we don't accidentally match too much, but since it's just tests, it should be fine.
    
    new_content = pattern.sub(replacer, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

fix_file("tests/chat/test_groq_provider.py", "app.chat.providers.groq_provider")
fix_file("tests/ingestion/test_whisper_transcription_provider.py", "app.ingestion.providers.whisper_transcription_provider")
fix_file("tests/retrieval/test_hybrid_retrieval.py", "app.retrieval.services.retriever_service")

# Note: tests/retrieval/test_hybrid_retrieval.py might be patching something else? Let's check what it patches.
