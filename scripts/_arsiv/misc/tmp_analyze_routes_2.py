import ast

class RouteAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.routes = []

    def visit_FunctionDef(self, node):
        is_route = False
        route_path = "<unknown>"
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute) and getattr(decorator.func, 'attr', '') == 'route':
                    is_route = True
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        route_path = str(decorator.args[0].value)
        
        if is_route:
            body_lines = node.end_lineno - node.lineno
            self.routes.append({
                'name': str(node.name),
                'path': route_path.replace('\n', ' '),
                'lines': body_lines,
                'start': node.lineno,
                'end': node.end_lineno
            })
        self.generic_visit(node)

with open(r'c:\kokpitim\api\routes.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)
analyzer = RouteAnalyzer()
analyzer.visit(tree)

# Sort by lines descending
analyzer.routes.sort(key=lambda x: x['lines'], reverse=True)

with open(r'c:\kokpitim\tmp_routes_report.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total Routes found: {len(analyzer.routes)}\n")
    out.write(f"{'Method Name':<40} {'Lines':<8} {'Location':<15} {'Path'}\n")
    out.write("-" * 90 + "\n")
    for r in analyzer.routes[:30]:  # Top 30 largest routes
        out.write(f"{r['name']:<40} {r['lines']:<8} {r['start']}-{r['end']:<15} {r['path']}\n")
