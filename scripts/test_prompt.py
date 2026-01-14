#!/usr/bin/env python3
import sys
try:
    import prompt
    print('✓ Import successful!')
    print(f'✓ ASSETS_JSON_PROMPT length: {len(prompt.ASSETS_JSON_PROMPT)} chars')
    print(f'✓ Contains "1920x1080": {"1920x1080" in prompt.ASSETS_JSON_PROMPT}')
    print(f'✓ Contains size guidelines: {"Screen Resolution Considerations" in prompt.ASSETS_JSON_PROMPT}')
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
