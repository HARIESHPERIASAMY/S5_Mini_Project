from PIL import Image, ImageDraw, ImageFont
import os

def render_root_cause_card():
    # Render dark theme UI panel matching SentinelMesh dark theme (#0B1120 / #1E293B)
    w, h = 1100, 480
    im = Image.new('RGB', (w, h), color='#0B132B')
    draw = ImageDraw.Draw(im)

    # Card background
    draw.rounded_rectangle((20, 20, w - 20, h - 20), radius=12, fill='#111C38', outline='#1E293B', width=2)

    # Header bar
    draw.rectangle((20, 20, w - 20, 75), fill='#16254A')
    draw.text((45, 36), "ROOT-CAUSE ANALYSIS & BACKWARD AST SLICER", fill='#60A5FA', font_size=16)
    draw.rounded_rectangle((w - 180, 32, w - 40, 62), radius=6, fill='#DC2626')
    draw.text((w - 170, 40), "CRITICAL DEFECT", fill='#FFFFFF', font_size=12)

    # File & Line details
    draw.text((45, 95), "Target File: demo/ecommerce/cart.py  |  Line: 52  |  Exception: ZeroDivisionError", fill='#F8FAFC', font_size=15)
    draw.text((45, 125), "Function Scope: calculate_cart_discount(cart_items, coupon_code)", fill='#94A3B8', font_size=13)

    # Causal Chain Box
    draw.rounded_rectangle((45, 155, 520, 430), radius=8, fill='#0B132B', outline='#1E293B')
    draw.text((60, 170), "Causal Fault Chain:", fill='#38BDF8', font_size=14)
    draw.text((60, 205), "1. Trigger Input: Empty cart passed with subtotal = 0.0", fill='#E2E8F0', font_size=12)
    draw.text((60, 240), "2. AST Node: BinOp(op=Div, left=discount_val, right=item_count)", fill='#E2E8F0', font_size=12)
    draw.text((60, 275), "3. Missing Guard: item_count evaluated to 0 without boundary check", fill='#F87171', font_size=12)
    draw.text((60, 310), "4. Runtime Crash: ZeroDivisionError: float division by zero", fill='#EF4444', font_size=12)
    draw.text((60, 355), "Backward Sliced Dependencies:", fill='#38BDF8', font_size=13)
    draw.text((60, 385), "• cart_items (line 46) -> subtotal (line 48) -> item_count (line 50)", fill='#94A3B8', font_size=12)

    # Code Slice Box
    draw.rounded_rectangle((545, 155, w - 45, 430), radius=8, fill='#070D1D', outline='#1E293B')
    draw.text((565, 170), "Source AST Code Slice:", fill='#38BDF8', font_size=14)
    code_lines = [
        ("48:    subtotal = sum(item.price for item in cart_items)", '#94A3B8'),
        ("49:    discount_pool = get_active_promotion(coupon_code)", '#94A3B8'),
        ("50:    item_count = len(cart_items)", '#94A3B8'),
        ("51:    # FAILING LINE: Unchecked division when item_count == 0", '#F87171'),
        ("52:    per_item_discount = discount_pool / item_count", '#EF4444'),
        ("53:    return round(subtotal - per_item_discount, 2)", '#94A3B8'),
        ("54: ", '#94A3B8'),
        ("[Recommended Guard]: if item_count == 0: return 0.0", '#4ADE80')
    ]
    y_code = 205
    for text, col in code_lines:
        draw.text((565, y_code), text, fill=col, font_size=12)
        y_code += 28

    im.save('report_images/fig_4_4_root_cause.png')
    print("Saved custom fig_4_4_root_cause.png")

def render_autofix_card():
    # Render dark theme UI panel for AutoFix Pre-flight diff
    w, h = 1100, 480
    im = Image.new('RGB', (w, h), color='#0B132B')
    draw = ImageDraw.Draw(im)

    # Card background
    draw.rounded_rectangle((20, 20, w - 20, h - 20), radius=12, fill='#111C38', outline='#1E293B', width=2)

    # Header bar
    draw.rectangle((20, 20, w - 20, 75), fill='#16254A')
    draw.text((45, 36), "AUTOFIX AGENT: PRE-FLIGHT VERIFIED PATCH", fill='#60A5FA', font_size=16)
    draw.rounded_rectangle((w - 220, 32, w - 40, 62), radius=6, fill='#16A34A')
    draw.text((w - 205, 40), "PRE-FLIGHT PASSED", fill='#FFFFFF', font_size=12)

    # Metrics row
    draw.text((45, 95), "Target: demo/ecommerce/cart.py  |  Patch Strategy: Boundary Zero-Divisor Guard", fill='#F8FAFC', font_size=15)
    draw.text((45, 125), "Sandbox Tests: 68 Passed / 0 Regressions  |  Regression Safety: 100% Certified", fill='#34D399', font_size=13)

    # Left: Unified Diff
    draw.rounded_rectangle((45, 155, 620, 430), radius=8, fill='#070D1D', outline='#1E293B')
    draw.text((60, 170), "Synthesized Unified Diff Patch:", fill='#38BDF8', font_size=14)
    diff_lines = [
        ("--- a/demo/ecommerce/cart.py", '#94A3B8'),
        ("+++ b/demo/ecommerce/cart.py", '#94A3B8'),
        ("@@ -50,5 +50,7 @@ def calculate_cart_discount(...):", '#818CF8'),
        ("     item_count = len(cart_items)", '#94A3B8'),
        ("+    if item_count == 0:", '#4ADE80'),
        ("+        return 0.0", '#4ADE80'),
        ("     per_item_discount = discount_pool / item_count", '#94A3B8'),
        ("     return round(subtotal - per_item_discount, 2)", '#94A3B8')
    ]
    y_diff = 205
    for text, col in diff_lines:
        draw.text((60, y_diff), text, fill=col, font_size=13)
        y_diff += 26

    # Right: Critic Consensus & Merge Gate
    draw.rounded_rectangle((645, 155, w - 45, 430), radius=8, fill='#0B132B', outline='#1E293B')
    draw.text((665, 170), "Critic Debate Consensus:", fill='#38BDF8', font_size=14)
    draw.text((665, 205), "Advocate Persona Score: 0.95 / 1.0", fill='#38BDF8', font_size=12)
    draw.text((665, 225), "\"Fix resolves boundary crash with zero side effects.\"", fill='#94A3B8', font_size=11)

    draw.text((665, 260), "Skeptic Persona Score: 0.90 / 1.0", fill='#FBBF24', font_size=12)
    draw.text((665, 280), "\"Preserves public contract; mathematical edge handled.\"", fill='#94A3B8', font_size=11)

    draw.text((665, 315), "Weighted Consensus Score: 0.925 (Threshold: >=0.85)", fill='#4ADE80', font_size=12)

    draw.rounded_rectangle((665, 360, w - 65, 410), radius=8, fill='#2563EB')
    draw.text((710, 375), "PROMOTE & MERGE PATCH (1-CLICK)", fill='#FFFFFF', font_size=13)

    im.save('report_images/fig_4_5_autofix.png')
    print("Saved custom fig_4_5_autofix.png")

if __name__ == '__main__':
    render_root_cause_card()
    render_autofix_card()
