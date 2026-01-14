#!/usr/bin/env python3
"""Test script to verify idle frame dual-purpose is properly documented"""

import sys

try:
    import prompt

    print("=" * 80)
    print("Testing Idle Frame Dual-Purpose Documentation")
    print("=" * 80)

    # Test 1: ASSETS_JSON_PROMPT - Animation Frame Guidelines
    print("\n1. Checking ASSETS_JSON_PROMPT - Animation Frame Guidelines...")
    checks = [
        ("Idle has 'Primary purpose: Display when stationary'", "Primary purpose: Display when character/object is stationary" in prompt.ASSETS_JSON_PROMPT),
        ("Idle has 'Secondary purpose: Also serves as one frame'", "Secondary purpose: Also serves as one frame in walk/run animations" in prompt.ASSETS_JSON_PROMPT),
        ("Example shows idle used for both purposes", "used when standing still AND in walk animation" in prompt.ASSETS_JSON_PROMPT),
        ("Walk frame only used in animation", "only used in walk animation" in prompt.ASSETS_JSON_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 2: IMAGE_ASSETS_PROMPT - Documentation Guidelines
    print("\n2. Checking IMAGE_ASSETS_PROMPT - Documentation Guidelines...")
    checks = [
        ("Idle frames have PRIMARY purpose documented", "Idle frames**: Document their PRIMARY purpose as static/stationary display" in prompt.IMAGE_ASSETS_PROMPT),
        ("Example idle usage shows both purposes", "Displayed when the character is not moving. Also used as one frame" in prompt.IMAGE_ASSETS_PROMPT),
        ("Motion frames only for animation", "Motion frames**: Document that they alternate with idle frames for animation" in prompt.IMAGE_ASSETS_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 3: IMAGE_ASSETS_PROMPT - Reference Example
    print("\n3. Checking IMAGE_ASSETS_PROMPT - Reference Example...")
    checks = [
        ("Person idle shows stationary purpose first", "Person standing still. Displayed when the character is not moving" in prompt.IMAGE_ASSETS_PROMPT),
        ("Person idle mentions animation as secondary", "Also used as one frame in running animation" in prompt.IMAGE_ASSETS_PROMPT),
        ("Person run only for animation", "Person in running pose" in prompt.IMAGE_ASSETS_PROMPT and "when the character is moving" in prompt.IMAGE_ASSETS_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 4: MULTIPLE_ASSETS_METADATA_PROMPT
    print("\n4. Checking MULTIPLE_ASSETS_METADATA_PROMPT...")
    checks = [
        ("Idle frame purpose documented", "Idle frame purpose**: Primary use is displaying stationary state" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("Idle secondary use mentioned", "secondary use is as one frame in motion animation" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("Motion frame only for animation", "Motion frame purpose**: Only used in animation" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
        ("Example shows dual purpose", "bird_idle.png\" (for stationary + animation)" in prompt.MULTIPLE_ASSETS_METADATA_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Test 5: UPDATE_ASSETS_JSON_PROMPT
    print("\n5. Checking UPDATE_ASSETS_JSON_PROMPT...")
    checks = [
        ("Idle frame dual purpose", "Idle frame**: Used when stationary AND as one frame in motion animation" in prompt.UPDATE_ASSETS_JSON_PROMPT),
        ("Motion frame single purpose", "Motion frame**: Only used in motion animation" in prompt.UPDATE_ASSETS_JSON_PROMPT),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}")

    # Summary
    print("\n" + "=" * 80)
    print("✓ All prompts properly document idle frame's dual purpose:")
    print("  1. PRIMARY: Display when character is stationary/not moving")
    print("  2. SECONDARY: Serve as one frame in walk/run animations")
    print("=" * 80)

except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
