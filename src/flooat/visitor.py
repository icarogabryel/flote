from .parser import Assign, UnaryOp, BinaryOp, Signal
from .component import Component, Bit


def match_class_name(obj, class_name):
    return obj.__class__.__name__ == class_name


class SemanticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Semantical Error: {self.message}'


class Visitor:
    def __init__(self, ast) -> None:
        self.ast = ast

    def get_component(self):
        return self.vst_mod(self.ast)

    def get_sensitivity_list(self, expr: Assign) -> list[str]:  #todo make it recursive
        sensitivity_list = []

        if match_class_name(expr, 'Signal'):
            sensitivity_list.append(expr.id)
        
        elif match_class_name(expr, 'UnaryOp'):
            sensitivity_list.extend(self.get_sensitivity_list(expr.expr))

        elif match_class_name(expr, 'BinaryOp'):
            sensitivity_list.extend(self.get_sensitivity_list(expr.l_expr))
            sensitivity_list.extend(self.get_sensitivity_list(expr.r_expr))

        return sensitivity_list

    def vst_mod(self, mod):
        is_main_comp_found = False

        for comp in mod.comps:  # Search for the main component
            if comp.is_main:
                if is_main_comp_found:
                    raise SemanticalError('Only one main component is allowed.')
                else:
                    is_main_comp_found = True

                    component = self.vst_comp(comp)

        if not is_main_comp_found:  #todo change to 'main' be obligatory only if there is multiple components
            raise SemanticalError('Main component not found.')
        else:
            return component

    def vst_comp(self, comp):
        component = Component(comp.id)

        for stmt in comp.stmts:
            if match_class_name(stmt, 'Assign'):
                self.vst_assign(component, stmt)

            elif match_class_name(stmt, 'Decl'):
                self.vst_decl(component, stmt)

        return component

    def vst_assign(self, comp, assign: Assign) -> None:
                comp.bits_dict[assign.dt] = self.visit_expr(assign.expr)

    def visit_expr(self, expr) -> Bit:
        bit = Bit()
        bit.assignment = expr
        bit.sensitivity_list = self.get_sensitivity_list(expr)

        return bit

    def vst_decl(self, comp, signal) -> None:
        comp.bits_dict[signal.id] = Bit()
