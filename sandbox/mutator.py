"""
AST Mutation Testing Engine for SentinelMesh.
Generates code mutants and calculates mutation kill score to measure test quality.
"""

import ast
import copy
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sandbox.runner import SandboxRunner, default_runner


class MutationPoint:
    def __init__(self, lineno: int, col_offset: int, mut_type: str, orig_str: str, new_str: str, ast_modifier):
        self.lineno = lineno
        self.col_offset = col_offset
        self.mut_type = mut_type
        self.orig_str = orig_str
        self.new_str = new_str
        self.ast_modifier = ast_modifier


class ASTMutationFinder(ast.NodeVisitor):
    def __init__(self):
        self.mutations: List[MutationPoint] = []

    def visit_Compare(self, node: ast.Compare):
        cmp_swaps = {
            ast.Eq: (ast.NotEq, "==", "!="),
            ast.NotEq: (ast.Eq, "!=", "=="),
            ast.Lt: (ast.GtE, "<", ">="),
            ast.LtE: (ast.Gt, "<=", ">"),
            ast.Gt: (ast.LtE, ">", "<="),
            ast.GtE: (ast.Lt, ">=", "<"),
            ast.In: (ast.NotIn, "in", "not in"),
            ast.NotIn: (ast.In, "not in", "in"),
        }
        for idx, op in enumerate(node.ops):
            op_cls = type(op)
            if op_cls in cmp_swaps:
                new_cls, orig_str, new_str = cmp_swaps[op_cls]
                def modifier(n=node, i=idx, nc=new_cls):
                    n.ops[i] = nc()

                self.mutations.append(MutationPoint(
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    mut_type="COMPARE_OP",
                    orig_str=orig_str,
                    new_str=new_str,
                    ast_modifier=modifier
                ))
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        bin_swaps = {
            ast.Add: (ast.Sub, "+", "-"),
            ast.Sub: (ast.Add, "-", "+"),
            ast.Mult: (ast.Div, "*", "/"),
            ast.Div: (ast.Mult, "/", "*"),
        }
        op_cls = type(node.op)
        if op_cls in bin_swaps:
            new_cls, orig_str, new_str = bin_swaps[op_cls]
            def modifier(n=node, nc=new_cls):
                n.op = nc()

            self.mutations.append(MutationPoint(
                lineno=node.lineno,
                col_offset=node.col_offset,
                mut_type="ARITHMETIC_OP",
                orig_str=orig_str,
                new_str=new_str,
                ast_modifier=modifier
            ))
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, bool):
            orig_str = str(node.value)
            new_val = not node.value
            new_str = str(new_val)
            def modifier(n=node, nv=new_val):
                n.value = nv

            self.mutations.append(MutationPoint(
                lineno=node.lineno,
                col_offset=node.col_offset,
                mut_type="BOOLEAN_FLIP",
                orig_str=orig_str,
                new_str=new_str,
                ast_modifier=modifier
            ))
        self.generic_visit(node)


class MutationEngine:
    def __init__(self, runner: SandboxRunner = default_runner):
        self.runner = runner

    def discover_mutants(self, source_code: str) -> List[Tuple[MutationPoint, str]]:
        """
        Parses code and creates AST mutant code strings.
        Returns list of (MutationPoint, mutated_source_code).
        """
        try:
            tree = ast.parse(source_code)
        except Exception:
            return []

        finder = ASTMutationFinder()
        finder.visit(tree)

        mutant_variants = []
        for mut in finder.mutations[:20]:  # Limit to 20 highest-impact mutants per file
            try:
                # Re-parse cleanly to apply single modification
                fresh_tree = ast.parse(source_code)
                # Find matching node in fresh tree by line and col
                fresh_finder = ASTMutationFinder()
                fresh_finder.visit(fresh_tree)
                matching = [m for m in fresh_finder.mutations if m.lineno == mut.lineno and m.mut_type == mut.mut_type and m.orig_str == mut.orig_str]
                if matching:
                    matching[0].ast_modifier()
                    ast.fix_missing_locations(fresh_tree)
                    mutated_code = ast.unparse(fresh_tree)
                    mutant_variants.append((mut, mutated_code))
            except Exception:
                continue

        return mutant_variants

    async def run_mutation_analysis(
        self,
        workspace_dir: str,
        target_file_rel: str,
        test_file_rel: str
    ) -> Dict[str, Any]:
        """
        Injects mutants into target file one by one, runs test suite,
        and determines if mutants are KILLED or SURVIVED.
        """
        target_path = Path(workspace_dir) / target_file_rel
        if not target_path.exists():
            return {"score": 0.0, "total": 0, "killed": 0, "survived": 0, "records": []}

        original_code = target_path.read_text(encoding="utf-8", errors="replace")
        mutants = self.discover_mutants(original_code)

        if not mutants:
            return {"score": 100.0, "total": 0, "killed": 0, "survived": 0, "records": []}

        killed_count = 0
        survived_count = 0
        records = []

        try:
            for mut_point, mutated_code in mutants:
                # Write mutated code
                target_path.write_text(mutated_code, encoding="utf-8")

                # Run pytest against test file
                cmd = [sys.executable, "-m", "pytest", test_file_rel, "-q"]
                result = await self.runner.run_command(cmd, cwd=workspace_dir, timeout=8.0)

                # If test failed or timed out -> mutant was KILLED
                if not result.success or result.timed_out:
                    status = "KILLED"
                    killed_count += 1
                else:
                    status = "SURVIVED"
                    survived_count += 1

                records.append({
                    "file_path": target_file_rel,
                    "line_number": mut_point.lineno,
                    "mutation_type": mut_point.mut_type,
                    "original_op": mut_point.orig_str,
                    "mutated_op": mut_point.new_str,
                    "status": status
                })
        finally:
            # Restore original code
            target_path.write_text(original_code, encoding="utf-8")

        total = killed_count + survived_count
        score = round((killed_count / total * 100.0), 1) if total > 0 else 0.0

        return {
            "score": score,
            "total": total,
            "killed": killed_count,
            "survived": survived_count,
            "records": records
        }
