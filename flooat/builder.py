
from .component import Component, Bit
from .ast import *


def match_class_name(obj, class_name):  #! delete this
    return obj.__class__.__name__ == class_name


class SemanticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Semantical Error: {self.message}'


class Builder:
    def __init__(self, ast) -> None:
        self.ast = ast

    def get_component(self, name = None) -> Component:  #todo Make return specific component, if not, main or unique file component
        return self.vst_mod(self.ast)

    def get_sensitivity_list(self, expr_elem: ExprElem) -> list[str]:
        sensitivity_list = []

        if match_class_name(expr_elem, 'Identifier'):
            sensitivity_list.append(expr_elem.id)
        
        elif match_class_name(expr_elem, 'Binary'):
            pass

        elif isinstance(expr_elem, UnaryOp):
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.expr))

        elif isinstance(expr_elem, BinaryOp):
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.l_expr))
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.r_expr))

        else:
            raise SemanticalError(f'Invalid expression element: {expr_elem}')

        return sensitivity_list

    def vst_mod(self, mod: Mod):
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
    
    def vst_comp(self, comp_node: Comp) -> Component:
        component = Component(comp_node.id)

        for stmt in comp_node.stmts:
            if match_class_name(stmt, 'Assign'):
                self.vst_assign(component, stmt)

            elif match_class_name(stmt, 'Decl'):
                self.vst_decl(component, stmt)

            else:
                raise SemanticalError(f'Invalid statement in a component: {stmt}')

        return component

    def vst_assign(self, comp_inst: Component, assign: Assign) -> None:
        comp_inst.bits_dict[assign.dt.id] = self.visit_expr(comp_inst, assign.expr)

    def visit_expr(self, comp_inst, expr) -> Bit:
        bit = Bit()
        bit.assignment = self.vst_expr(comp_inst, expr)
        bit.sensitivity_list = self.get_sensitivity_list(expr)

        return bit

    def vst_decl(self, comp_inst: Component, bit: Decl) -> None:
        comp_inst.bits_dict[bit.id] = Bit()

    def vst_expr(self, comp_inst: Component, expr_elem: ExprElem) -> str:
        if match_class_name(expr_elem, 'Identifier'):
            return lambda: comp_inst.bits_dict[expr_elem.id]
        
        elif match_class_name(expr_elem, 'Binary'):
            return lambda: expr_elem.value

        elif match_class_name(expr_elem, 'Not'):
            return lambda: not self.vst_expr(expr_elem.expr)()

        elif match_class_name(expr_elem, 'and'):
            return lambda: self.vst_expr(expr_elem.l_expr)() and self.vst_expr(expr_elem.r_expr)()
        
        elif match_class_name(expr_elem, 'or'):
            return lambda: self.vst_expr(expr_elem.l_expr)() or self.vst_expr(expr_elem.r_expr)()
        
        elif match_class_name(expr_elem, 'xor'):
            return lambda: self.vst_expr(expr_elem.l_expr)() ^ self.vst_expr(expr_elem.r_expr)()
        
        elif match_class_name(expr_elem, 'nand'):
            return lambda: not (self.vst_expr(expr_elem.l_expr)() and self.vst_expr(expr_elem.r_expr)())
        
        elif match_class_name(expr_elem, 'nor'):
            return lambda: not (self.vst_expr(expr_elem.l_expr)() or self.vst_expr(expr_elem.r_expr)())
        
        elif match_class_name(expr_elem, 'xnor'):
            return lambda: not (self.vst_expr(expr_elem.l_expr)() ^ self.vst_expr(expr_elem.r_expr)())
