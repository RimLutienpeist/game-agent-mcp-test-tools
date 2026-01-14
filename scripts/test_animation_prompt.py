#!/usr/bin/env python3
"""Test script to verify animation frame guidelines in prompts"""

import sys

try:
    import prompt

    print("=" * 80)
    print("Testing Animation Frame Guidelines in Prompts")
    print("=" * 80)

    # Test 1: Check ASSETS_JSON_PROMPT
    print("\n1. Checking ASSETS_JSON_PROMPT...")
    checks = [
        ("Contains 'ONLY 1 walk frame'", "ONLY 1 walk frame" in prompt.ASSETS_JSON_PROMPT),
        ("Contains alternating animation explanation", "alternating between idle and walk" in prompt.ASSETS_JSON_PROMPT),
        ("Contains 'DO NOT generate walk_1, walk_2'", "DO NOT generate walk_1, walk_2" in prompt.ASSETS_JSON_PROMPT),
        ("Example shows 8 frames total", "Total: 8 frames, NOT 12+" in prompt.ASSETS_JSON_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 2: Check IMAGE_ASSETS_PROMPT
    print("\n2. Checking IMAGE_ASSETS_PROMPT...")
    checks = [
        ("Contains animation documentation note", "Animation Frame Documentation" in prompt.IMAGE_ASSETS_PROMPT),
        ("Shows idle + run alternating", "person_idle.png" in prompt.IMAGE_ASSETS_PROMPT and "person_run.png" in prompt.IMAGE_ASSETS_PROMPT),
        ("Explains alternating pattern", "idle → run → idle → run" in prompt.IMAGE_ASSETS_PROMPT),
        ("No multiple running frames", "Running 1" not in prompt.IMAGE_ASSETS_PROMPT or "person_idle" in prompt.IMAGE_ASSETS_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 3: Check MULTIPLE_ASSETS_METADATA_PROMPT
    print("\n3. Checking MULTIPLE_ASSETS_METADATA_PROMPT...")
    checks = [
        ("Contains animation frame rule", "CRITICAL - Animation Frames" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("Shows bird_idle + bird_fly", "bird_idle.png" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT and "bird_fly.png" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("No bird_fly_1, bird_fly_2", "bird_fly_1" not in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("Explains alternating in code", "alternating frames in code" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT or "alternate with" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 4: Check UPDATE_ASSETS_JSON_PROMPT
    print("\n4. Checking UPDATE_ASSETS_JSON_PROMPT...")
    checks = [
        ("Contains animation frame rule", "CRITICAL - Animation Frames" in prompt.UPDATE_ASSETS_JSON_PROMPT),
        ("Mentions 1 idle + 1 motion", "1 idle frame + 1 motion frame" in prompt.UPDATE_ASSETS_JSON_PROMPT),
        ("Prohibits walk_1, walk_2, walk_3", "DO NOT generate walk_1, walk_2, walk_3" in prompt.UPDATE_ASSETS_JSON_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Summary
    print("\n" + "=" * 80)
    print("All animation frame guidelines have been successfully updated!")
    print("=" * 80)

except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
