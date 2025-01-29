from .parser import Parser, Assign
from .component import Component, Bit


def match_class_name(obj, class_name):
    return obj.__class__.__name__ == class_name


class SemanticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Semantical Error: {self.message}'


class Visitor:
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def get_component(self):
        return self.vst_mod(self.parser.ast)
    
    def get_sensitivity_list(self, expr) -> list[str]:  #todo make it recursive
        sensitivity_list = []

        if expr.l_expr:
            sensitivity_list.append(expr.l_expr)
        if expr.r_expr:
            if expr.r_expr != 'place': #! take off!
                sensitivity_list.append(expr.r_expr)

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

            elif match_class_name(stmt, 'Signal'):
                self.vst_signal(component, stmt)

        return component

    def vst_assign(self, comp, assign: Assign) -> None:
                comp.bits_dict[assign.dt] = self.visit_expr(assign.expr)

    def visit_expr(self, expr) -> Bit:
        bit = Bit()
        bit.assignment = expr
        bit.sensitivity_list = self.get_sensitivity_list(expr)

        return bit

    def vst_signal(self, comp, signal) -> None:
        comp.bits_dict[signal.id] = Bit()
