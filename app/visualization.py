import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import re


def should_show_diagram(question: str, subject: str) -> bool:
    """Return True only when the question explicitly asks for a visual/graph/geometry construction.

    Policy:
    - Require an explicit drawing intent for algebra/calculus/trig (draw/plot/graph/sketch/construct/diagram/illustrate/visualize)
    - Always allow geometry constructions when common geometry terms appear
    - Keep other subjects conservative
    """
    q = question.lower()

    # 1) Strong drawing intent verbs
    intent = any(w in q for w in [
        'draw', 'sketch', 'plot', 'graph', 'construct', 'diagram', 'figure',
        'illustrate', 'visualize'
    ])

    # 2) Geometry keywords that justify a diagram regardless of verb
    geometry_terms = [
        'triangle', ' abc', 'abc ', 'perpendicular bisector', 'angle bisector',
        'median', 'altitude', 'parallel', 'perpendicular', 'circumcircle',
        'incenter', 'circumcenter', 'square', 'rectangle', 'circle',
        'semicircle', 'polygon', 'pentagon', 'hexagon', 'heptagon', 'octagon',
        'geometry', 'tangent', 'tangents', 'degree'
    ]
    if any(t in q for t in geometry_terms):
        return True

    # 3) Mathematics graphs: require intent + an equation/function pattern
    if subject == 'Mathematics':
        if intent and (
            re.search(r'\by\s*=\s*', q) or  # y = ...
            re.search(r'\bf\(x\)\s*=\s*', q) or  # f(x) = ...
            'parabola' in q or  # often implies graphing when paired with intent
            'sin' in q or 'cos' in q or 'tan' in q  # trig plots when intent present
        ):
            return True
        return False

    # 4) Physics: show only for waves/trajectories when intent present
    if subject == 'Physics':
        if intent and any(k in q for k in ['wave', 'trajectory', 'motion', 'circuit']):
            return True
        return False

    # 5) Economics: show only when intent present with supply/demand
    if subject == 'Economics':
        if intent and any(k in q for k in ['supply', 'demand', 'equilibrium', 'curve']):
            return True
        return False

    # Default: require explicit intent
    return intent


def create_smart_visualization(question: str, subject: str):
    """Create simple, clean visualizations.

    Adds a basic geometry renderer for triangle construction tasks with
    given side lengths and the perpendicular bisector of BC.
    """
    question_lower = question.lower()

    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)  # Much smaller size to prevent full screen domination
        fig.patch.set_facecolor('white')

        if subject == "Mathematics":
            # Lightweight geometry engine (shapes + graphs)
            if any(k in question_lower for k in [
                'triangle', 'abc', 'perpendicular bisector', 'bisector', 'median', 'altitude',
                'angle bisector', 'parallel', 'perpendicular', 'circle', 'circumcircle', 'incenter', 'circumcenter',
                'square', 'rectangle', 'polygon', 'semicircle', 'pentagon', 'hexagon', 'heptagon', 'octagon'
            ]):
                # ---------- Helpers ----------
                def find_len(name: str):
                    pattern = rf"{name}\s*=?\s*(\d+(?:\.\d+)?)\s*cm"
                    m = re.search(pattern, question, flags=re.IGNORECASE)
                    return float(m.group(1)) if m else None

                def midpoint(p, q):
                    return ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)

                def draw_line(p, q, **kw):
                    ax.plot([p[0], q[0]], [p[1], q[1]], **kw)

                def draw_infinite_line_through(p, direction, length=20, **kw):
                    d = np.array(direction, dtype=float)
                    if np.linalg.norm(d) == 0:
                        return
                    d = d / np.linalg.norm(d)
                    p = np.array(p, dtype=float)
                    p1 = p - d * length
                    p2 = p + d * length
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], **kw)

                def perp(v):
                    return (-v[1], v[0])

                # ---------- Build baseline triangle if ABC mentioned or side lengths provided ----------
                ab = find_len('AB')
                bc = find_len('BC')
                ac = find_len('AC')

                need_triangle = any(k in question_lower for k in ['triangle', ' abc', 'abc ', '△abc', '△ abc']) or any(v is not None for v in [ab, bc, ac])

                points = {}
                if need_triangle:
                    if bc is None and ab is None and ac is None:
                        ab, bc, ac = 5.0, 6.0, 4.0
                    else:
                        bc = 6.0 if bc is None else bc
                        ab = 5.0 if ab is None else ab
                        ac = 4.0 if ac is None else ac

                    B = (0.0, 0.0)
                    C = (bc, 0.0)
                    # circle-circle intersection to get A (choose upper solution)
                    x_a = (ab**2 - ac**2 + bc**2) / (2 * bc if bc != 0 else 1e-6)
                    y_sq = max(ab**2 - x_a**2, 0.0)
                    y_a = float(np.sqrt(y_sq))
                    A = (x_a, y_a)
                    points.update({'A': A, 'B': B, 'C': C})

                    # Draw triangle with black outlines for white background
                    stroke = '#000000'
                    draw_line(B, C, color=stroke, linewidth=2)
                    draw_line(C, A, color=stroke, linewidth=2)
                    draw_line(A, B, color=stroke, linewidth=2)
                    ax.scatter([A[0], B[0], C[0]], [A[1], B[1], C[1]], color='#000000', zorder=3)
                    ax.text(B[0], B[1] - 0.2, 'B', ha='center', va='top', color=stroke)
                    ax.text(C[0], C[1] - 0.2, 'C', ha='center', va='top', color=stroke)
                    ax.text(A[0], A[1] + 0.2, 'A', ha='center', va='bottom', color=stroke)

                    # Side length labels
                    def put_len(p, q, label):
                        mx, my = (p[0]+q[0])/2.0, (p[1]+q[1])/2.0
                        ax.text(mx, my + 0.15, label, color=stroke, ha='center', va='bottom')
                    put_len(B, C, f'{bc} cm')
                    put_len(A, B, f'{ab} cm')
                    put_len(A, C, f'{ac} cm')

                # ---------- Constructions ----------
                # Perpendicular bisector of a segment XY (e.g., BC)
                seg_match = re.search(r'perpendicular\s+bisector\s+of\s+([A-Z])([A-Z])', question, flags=re.IGNORECASE)
                if seg_match:
                    x, y = seg_match.group(1).upper(), seg_match.group(2).upper()
                    if x in points and y in points:
                        P = points[x]; Q = points[y]
                    else:
                        # default segment on x-axis if points unknown
                        P, Q = (0.0, 0.0), (6.0, 0.0)
                    M = midpoint(P, Q)
                    dir_vec = (Q[0] - P[0], Q[1] - P[1])
                    draw_infinite_line_through(M, perp(dir_vec), linestyle='--', color='#4CAF50', linewidth=2, label=f'Perpendicular bisector of {x}{y}')

                # Angle bisector at a vertex (e.g., angle ABC)
                ang_match = re.search(r'(angle\s*)?bisector\s*(at|of)?\s*(angle\s*)?([A-Z])([A-Z])([A-Z])', question, flags=re.IGNORECASE)
                if ang_match:
                    a, b, c = ang_match.group(4).upper(), ang_match.group(5).upper(), ang_match.group(6).upper()
                    if a in points and b in points and c in points:
                        A, B, C = points[a], points[b], points[c]
                        v1 = np.array([A[0] - B[0], A[1] - B[1]], dtype=float)
                        v2 = np.array([C[0] - B[0], C[1] - B[1]], dtype=float)
                        if np.linalg.norm(v1) and np.linalg.norm(v2):
                            v1 /= np.linalg.norm(v1)
                            v2 /= np.linalg.norm(v2)
                            bis = v1 + v2
                            if np.linalg.norm(bis) == 0:
                                bis = perp(v1)
                            draw_infinite_line_through(B, bis, linestyle='--', color='#00E5FF', linewidth=2, label=f'Angle bisector at {b}')

                # Median from a vertex (e.g., median from A)
                med_match = re.search(r'median\s+(from|of)\s+([A-Z])', question, flags=re.IGNORECASE)
                if med_match and all(k in points for k in ['A', 'B', 'C']):
                    v = med_match.group(2).upper()
                    if v == 'A':
                        m = midpoint(points['B'], points['C'])
                        draw_line(points['A'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from A')
                    elif v == 'B':
                        m = midpoint(points['A'], points['C'])
                        draw_line(points['B'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from B')
                    elif v == 'C':
                        m = midpoint(points['A'], points['B'])
                        draw_line(points['C'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from C')

                # Altitude from a vertex (e.g., altitude from A to BC)
                alt_match = re.search(r'altitude\s+(from)\s+([A-Z])', question, flags=re.IGNORECASE)
                if alt_match and all(k in points for k in ['A', 'B', 'C']):
                    v = alt_match.group(2).upper()
                    if v == 'A':
                        dir_bc = (points['C'][0] - points['B'][0], points['C'][1] - points['B'][1])
                        draw_infinite_line_through(points['A'], perp(dir_bc), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from A')
                    elif v == 'B':
                        dir_ac = (points['C'][0] - points['A'][0], points['C'][1] - points['A'][1])
                        draw_infinite_line_through(points['B'], perp(dir_ac), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from B')
                    elif v == 'C':
                        dir_ab = (points['B'][0] - points['A'][0], points['B'][1] - points['A'][1])
                        draw_infinite_line_through(points['C'], perp(dir_ab), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from C')

                # Perpendicular/Parallel to a line through a given point (e.g., perpendicular to BC through A)
                through_match = re.search(r'(perpendicular|parallel)\s+to\s+([A-Z])([A-Z])\s+(through|from)\s+([A-Z])', question, flags=re.IGNORECASE)
                if through_match:
                    kind = through_match.group(1).lower()
                    x, y, p = through_match.group(2).upper(), through_match.group(3).upper(), through_match.group(5).upper()
                    if x in points and y in points and p in points:
                        base = (points[y][0] - points[x][0], points[y][1] - points[x][1])
                        direction = perp(base) if kind == 'perpendicular' else base
                        draw_infinite_line_through(points[p], direction, linestyle='--', color='#4CAF50' if kind=='perpendicular' else '#90CAF9', linewidth=2, label=f'{kind.title()} to {x}{y} through {p}')

                # Enhanced Circle Generation with degree support (NEW FEATURE)
                # Check for degree-based circle requests first (like "60 degree circle")
                degree_circle_match = re.search(r'(\d+(?:\.\d+)?)\s*degree\s*circle', question_lower)
                if degree_circle_match:
                    angle_degrees = float(degree_circle_match.group(1))
                    radius = 4.0  # default radius
                    
                    # Create circle with highlighted sector
                    stroke = '#000000'
                    center = (0, 0)
                    circle = plt.Circle(center, radius, fill=False, edgecolor=stroke, linewidth=2)
                    ax.add_patch(circle)
                    
                    # Center point
                    ax.scatter([center[0]], [center[1]], color=stroke, s=30, zorder=3)
                    ax.text(center[0], center[1] + 0.3, 'O', ha='center', va='bottom', color=stroke, fontweight='bold')
                    
                    # Draw the sector (highlighted)
                    start_angle = 0  # Start from positive x-axis
                    end_angle = np.radians(angle_degrees)
                    
                    # Draw sector boundary lines
                    start_x = center[0] + radius * np.cos(start_angle)
                    start_y = center[1] + radius * np.sin(start_angle)
                    end_x = center[0] + radius * np.cos(end_angle)
                    end_y = center[1] + radius * np.sin(end_angle)
                    
                    # Draw radius lines
                    ax.plot([center[0], start_x], [center[1], start_y], color='red', linewidth=2, label=f'Start radius (0°)')
                    ax.plot([center[0], end_x], [center[1], end_y], color='red', linewidth=2, label=f'End radius ({angle_degrees}°)')
                    
                    # Draw arc
                    theta = np.linspace(start_angle, end_angle, 100)
                    arc_x = center[0] + radius * np.cos(theta)
                    arc_y = center[1] + radius * np.sin(theta)
                    ax.plot(arc_x, arc_y, color='red', linewidth=3, label=f'{angle_degrees}° arc')
                    
                    # Mark the angle
                    ax.text(center[0] + 0.5*radius*np.cos(end_angle/2), 
                           center[1] + 0.5*radius*np.sin(end_angle/2), 
                           f'{angle_degrees}°', color='red', ha='center', va='center', 
                           fontweight='bold', fontsize=12)
                    
                    # Radius line for reference
                    ax.plot([center[0], radius], [center[1], 0], color=stroke, linestyle='--', linewidth=1.5)
                    ax.text(radius/2, 0.2, f'r = {radius}', ha='center', va='bottom', color=stroke)
                    
                    # Set bounds
                    ax.set_xlim(-radius-1, radius+1)
                    ax.set_ylim(-radius-1, radius+1)
                    ax.set_aspect('equal')
                    ax.set_title(f'Circle with {angle_degrees}° Sector Highlighted')

                # Simple Circle Generation (like triangle approach) - FALLBACK
                elif 'circle' in question_lower:
                    circle_match = re.search(r'circle.*?radius\s*(\d+(?:\.\d+)?)|radius\s*(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)
                    if circle_match or 'circle' in question_lower:
                        # Extract radius simply
                        radius = 4.0  # good default size
                        if circle_match:
                            radius = float(circle_match.group(1) or circle_match.group(2))
                        
                        # Simple circle at origin
                        stroke = '#000000'
                        circle = plt.Circle((0, 0), radius, fill=False, edgecolor=stroke, linewidth=2)
                        ax.add_patch(circle)
                        
                        # Center point
                        ax.scatter([0], [0], color=stroke, s=30, zorder=3)
                        ax.text(0, 0.3, 'O', ha='center', va='bottom', color=stroke, fontweight='bold')
                        
                        # Radius line
                        ax.plot([0, radius], [0, 0], color=stroke, linestyle='--', linewidth=1.5)
                        ax.text(radius/2, 0.2, f'r = {radius}', ha='center', va='bottom', color=stroke)
                        
                        # Simple bounds like triangle
                        ax.set_xlim(-radius-1, radius+1)
                        ax.set_ylim(-radius-1, radius+1)
                        ax.set_aspect('equal')

                # Improved pair of tangents to a circle with given angle between them
                tan_match = re.search(r'tangents?\s+to\s+a?\s*circle.*?(?:inclined.*?at|angle.*?of)\s*(\d+(?:\.\d+)?)\s*degrees?', question, flags=re.IGNORECASE)
                if tan_match:
                    tangent_angle = float(tan_match.group(1))  # degrees between tangents
                    
                    # Get radius from existing circle or default
                    r = 3.0
                    center = (0.0, 0.0)
                    existing_circle = next((p for p in ax.patches if isinstance(p, plt.Circle)), None)
                    if existing_circle:
                        center = existing_circle.get_center()
                        r = existing_circle.get_radius()
                    else:
                        # Create circle if none exists
                        circle = plt.Circle(center, r, fill=False, edgecolor='#000000', linewidth=2)
                        ax.add_patch(circle)
                        ax.scatter([center[0]], [center[1]], color='#000000')
                        ax.text(center[0], center[1]+0.2, 'O', color='#000000', ha='center')
                    
                    # Calculate central angle (supplementary to tangent angle)
                    central_angle = 180 - tangent_angle
                    A_angle = np.radians(central_angle / 2)
                    B_angle = -A_angle
                    
                    # Points of tangency A and B
                    A = (center[0] + r * np.cos(A_angle), center[1] + r * np.sin(A_angle))
                    B = (center[0] + r * np.cos(B_angle), center[1] + r * np.sin(B_angle))
                    
                    # Draw radii to points of tangency
                    ax.plot([center[0], A[0]], [center[1], A[1]], 'k--', linewidth=1, alpha=0.7, label='Radii')
                    ax.plot([center[0], B[0]], [center[1], B[1]], 'k--', linewidth=1, alpha=0.7)
                    
                    # Mark points of tangency
                    ax.scatter([A[0], B[0]], [A[1], B[1]], color='red', s=30, zorder=5)
                    ax.text(A[0], A[1]+0.2, 'A', color='red', ha='center', fontweight='bold')
                    ax.text(B[0], B[1]-0.2, 'B', color='red', ha='center', fontweight='bold')
                    
                    # Draw tangent lines (perpendicular to radii at A and B)
                    line_length = r * 3
                    for point, angle in [(A, A_angle), (B, B_angle)]:
                        # Tangent slope is perpendicular to radius
                        if np.abs(np.cos(angle)) < 1e-10:  # vertical radius
                            # Horizontal tangent
                            x_vals = np.array([point[0] - line_length, point[0] + line_length])
                            y_vals = np.array([point[1], point[1]])
                        else:
                            slope = -1 / np.tan(angle)
                            x_vals = np.array([point[0] - line_length, point[0] + line_length])
                            y_vals = slope * (x_vals - point[0]) + point[1]
                        ax.plot(x_vals, y_vals, 'red', linewidth=2, label='Tangents' if point == A else '')
                    
                    # Mark the angle between tangents
                    ax.text(center[0], center[1]-r-0.5, f'Angle between tangents: {int(tangent_angle)}°', 
                           color='#000000', ha='center', fontweight='bold')

                # Regular shapes when requested without triangle context
                if not points and any(k in question_lower for k in ['square', 'rectangle', 'polygon', 'circle', 'semicircle']):
                    stroke = '#000000'
                    if 'square' in question_lower:
                        s = 4.0
                        X = np.array([0, s, s, 0, 0]); Y = np.array([0, 0, s, s, 0])
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        # mark vertices and lengths
                        V = [(0,0), (s,0), (s,s), (0,s)]
                        labels = ['A','B','C','D']
                        ax.scatter([p[0] for p in V], [p[1] for p in V], color=stroke)
                        for (px,py),lab in zip(V,labels):
                            ax.text(px, py-0.2 if py==0 else py+0.2, lab, color=stroke, ha='center', va='center')
                        ax.text(s/2, -0.3, f'{s} cm', color=stroke, ha='center')
                        ax.text(s+0.3, s/2, f'{s} cm', color=stroke, va='center')
                        ax.set_title('Square')
                    elif 'rectangle' in question_lower:
                        a, b = 6.0, 4.0
                        X = np.array([0, a, a, 0, 0]); Y = np.array([0, 0, b, b, 0])
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        V = [(0,0), (a,0), (a,b), (0,b)]
                        labels = ['A','B','C','D']
                        ax.scatter([p[0] for p in V], [p[1] for p in V], color=stroke)
                        for (px,py),lab in zip(V,labels):
                            ax.text(px, py-0.2 if py==0 else py+0.2, lab, color=stroke, ha='center', va='center')
                        ax.text(a/2, -0.3, f'{a} cm', color=stroke, ha='center')
                        ax.text(a+0.3, b/2, f'{b} cm', color=stroke, va='center')
                        ax.set_title('Rectangle')
                    elif 'semicircle' in question_lower:
                        r = 3.0
                        t = np.linspace(0, np.pi, 200)
                        ax.plot(r*np.cos(t), r*np.sin(t), color=stroke, linewidth=2)
                        ax.plot([-r, r], [0, 0], color=stroke, linewidth=2)
                        # points and labels
                        A = (-r,0); B = (r,0); O = (0,0)
                        ax.scatter([A[0],B[0],O[0]],[A[1],B[1],O[1]], color=stroke)
                        ax.text(A[0], A[1]-0.2, 'A', color=stroke, ha='center')
                        ax.text(B[0], B[1]-0.2, 'B', color=stroke, ha='center')
                        ax.text(O[0], O[1]+0.2, 'O', color=stroke, ha='center')
                        ax.text(0, -0.3, f'{2*r} cm', color=stroke, ha='center')
                        ax.set_aspect('equal')
                        ax.set_title('Semicircle')
                    elif 'circle' in question_lower:
                        # Simple circle like triangle approach
                        r = 4.0  # default radius
                        radius_match = re.search(r'radius\s*(\d+(?:\.\d+)?)', question_lower)
                        if radius_match:
                            r = float(radius_match.group(1))
                        
                        # Simple circle
                        circle = plt.Circle((0, 0), r, fill=False, edgecolor=stroke, linewidth=2)
                        ax.add_patch(circle)
                        ax.scatter([0], [0], color=stroke, s=30, zorder=3)
                        ax.text(0, 0.3, 'O', ha='center', va='bottom', color=stroke, fontweight='bold')
                        ax.plot([0, r], [0, 0], color=stroke, linestyle='--', linewidth=1.5)
                        ax.text(r/2, 0.2, f'r = {r}', ha='center', va='bottom', color=stroke)
                        ax.set_xlim(-r-1, r+1)
                        ax.set_ylim(-r-1, r+1)
                        ax.set_aspect('equal')
                    elif 'polygon' in question_lower:
                        # default to regular hexagon
                        n = 6
                        t = np.linspace(0, 2*np.pi, n+1)
                        X = np.cos(t); Y = np.sin(t)
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        # label vertices
                        verts = list(zip(X[:-1], Y[:-1]))
                        labels = ['A','B','C','D','E','F','G','H']
                        for i,(px,py) in enumerate(verts):
                            ax.scatter([px],[py], color=stroke)
                            ax.text(px, py+0.15, labels[i], color=stroke, ha='center')
                        ax.set_aspect('equal')
                        ax.set_title('Regular Polygon (hexagon)')

                # Final styling and bounds
                ax.set_aspect('equal', adjustable='datalim')

                # PRIORITIZE CIRCLE-FRIENDLY BOUNDS
                # If a circle exists, frame the view around it so it is always clearly visible.
                circ = next((p for p in ax.patches if isinstance(p, plt.Circle)), None)
                if circ is not None:
                    c = circ.get_center(); r = circ.get_radius()
                    pad = max(0.4 * r, 1.0)
                    ax.set_xlim(c[0] - r - pad, c[0] + r + pad)
                    ax.set_ylim(c[1] - r - pad, c[1] + r + pad)
                else:
                    # Generic autoscaling when no circle is present
                    x_all, y_all = [], []
                    # Lines
                    for line in ax.get_lines():
                        xdata = line.get_xdata(); ydata = line.get_ydata()
                        x_all.extend(list(xdata)); y_all.extend(list(ydata))
                    # Patches
                    for patch in ax.patches:
                        try:
                            verts = patch.get_path().transformed(patch.get_transform()).vertices
                            if verts is not None and len(verts) > 0:
                                x_all.extend(list(verts[:,0])); y_all.extend(list(verts[:,1]))
                        except Exception:
                            pass
                    # Collections
                    for coll in ax.collections:
                        try:
                            offs = coll.get_offsets()
                            if offs is not None and len(offs) > 0:
                                arr = np.array(offs)
                                if arr.ndim == 2 and arr.shape[1] == 2:
                                    x_all.extend(list(arr[:,0])); y_all.extend(list(arr[:,1]))
                        except Exception:
                            pass
                    if x_all and y_all:
                        x_min, x_max = min(x_all), max(x_all)
                        y_min, y_max = min(y_all), max(y_all)
                        pad_x = max((x_max - x_min) * 0.15, 1.0)
                        pad_y = max((y_max - y_min) * 0.15, 1.0)
                        ax.set_xlim(x_min - pad_x, x_max + pad_x)
                        ax.set_ylim(y_min - pad_y, y_max + pad_y)
                    else:
                        # Safe default frame
                        ax.set_xlim(-5, 5)
                        ax.set_ylim(-5, 5)
                ax.axis('off')
                ax.legend(loc='upper right')
            else:
                # Existing math plots
                if any(term in question_lower for term in ['quadratic', 'parabola', 'x²', 'x^2']):
                    x = np.linspace(-5, 5, 100)
                    y = x**2
                    ax.plot(x, y, 'b-', linewidth=2, label='y = x²')
                    ax.set_title('Quadratic Function')
                elif any(term in question_lower for term in ['linear', 'y=', 'slope']):
                    x = np.linspace(-5, 5, 100)
                    y = 2*x + 1
                    ax.plot(x, y, 'r-', linewidth=2, label='Linear Function')
                    ax.set_title('Linear Function')
                elif any(term in question_lower for term in ['sin', 'cos']):
                    x = np.linspace(-2*np.pi, 2*np.pi, 100)
                    ax.plot(x, np.sin(x), 'b-', linewidth=2, label='sin(x)')
                    ax.plot(x, np.cos(x), 'r-', linewidth=2, label='cos(x)')
                    ax.set_title('Trigonometric Functions')

                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.axvline(x=0, color='k', linewidth=0.5)
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.legend()

        elif subject == "Physics":
            t = np.linspace(0, 4*np.pi, 100)
            y = np.sin(t)
            ax.plot(t, y, 'b-', linewidth=2, label='Wave')
            ax.set_title('Wave Function')
            ax.set_xlabel('Time/Position')
            ax.set_ylabel('Amplitude')
            ax.grid(True, alpha=0.3)
            ax.legend()

        elif subject == "Economics":
            x = np.linspace(0, 10, 100)
            supply = 2 * x
            demand = 20 - x
            ax.plot(x, supply, 'b-', linewidth=2, label='Supply')
            ax.plot(x, demand, 'r-', linewidth=2, label='Demand')
            ax.set_title('Supply and Demand')
            ax.set_xlabel('Quantity')
            ax.set_ylabel('Price')
            ax.grid(True, alpha=0.3)
            ax.legend()

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=180, facecolor='white', bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        plt.close(fig)
        return buf

    except Exception:
        plt.close('all')
        return None


