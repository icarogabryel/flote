from .component import Component, BitBus
from .ast import *
from typing import Optional


NOT_ASSIGNED = False
IS_ASSIGNED = True


class SemanticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Semantical Error: {self.message}'


class BusSymbol:
    """Class that represents a bus symbol in the symbol table."""

    def __init__(self, type, assigned):
        self.type: Optional[str] = type
        self.is_assigned = assigned

    def __repr__(self):
        return f'({self.type}, {self.is_assigned})'  #todo Improve


class Builder:
    """Class that builds the component from the AST."""

    def __init__(self, ast) -> None:  #todo Add signal list to error handling
        self.ast = ast
        self.bus_symbol_table: dict[str, dict[str, BusSymbol]] = {}  # component: bus: (type, is_assigned)

    def get_component(self, name = None) -> Component:  #todo Make return specific component, if not, main or unique file component
        return self.vst_mod(self.ast)

    def get_sensitivity_list(self, expr_elem: ExprElem) -> list[str]:
        """Get a list of identifiers that influence the value of a bit signal."""
        sensitivity_list = []

        if isinstance(expr_elem, Identifier):
            sensitivity_list.append(expr_elem.id)

        elif isinstance(expr_elem, Binary):  # Constant value don't need to be in the sensitivity list
            pass

        elif isinstance(expr_elem, UnaryOp):
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.expr))

        elif isinstance(expr_elem, BinaryOp):
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.l_expr))
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.r_expr))

        else:
            raise SemanticalError(f'Invalid expression element: {expr_elem}')

        return sensitivity_list

    def get_components_bus_table(self, comp: Comp) -> dict[str, BusSymbol]:
        """Get the component's bus symbol table."""

        components_bus_table: dict[str, BusSymbol] = {}

        for stmt in comp.stmts:
            if isinstance(stmt, Decl):
                decl = stmt  # Name change for better readability

                if decl.id in components_bus_table:
                    raise SemanticalError(f'Identifier {decl.id} has already been declared.')

                elif decl.assign is not None:
                    if decl.conn == INPUT:
                        raise SemanticalError(f'Input identifier {decl.id} cannot be assigned.')

                    else:
                        components_bus_table[decl.id] = BusSymbol(decl.type, IS_ASSIGNED)

                else:
                    components_bus_table[decl.id] = BusSymbol(decl.type, NOT_ASSIGNED)

        return components_bus_table

    # def validate_symbol_table(self):
    #     for id, bus in self.bus_symbol_table.items():
    #         if not bus.assigned:
    #             raise SemanticalError(f'Bus {id} has not been assigned.')

    def vst_mod(self, mod: Mod):
        if len(mod.comps) == 1:
            return self.vst_comp(mod.comps[0])

        else:
            is_main_comp_found = False
            component: Optional[Component] = None

            for comp in mod.comps:  # Search for the main component
                if comp.is_main:
                    if is_main_comp_found:
                        raise SemanticalError('Only one main component is allowed.')
                    else:
                        is_main_comp_found = True
                        component = self.vst_comp(comp)

            if not is_main_comp_found:
                raise SemanticalError('Main component not found.')

        return component

    def vst_comp(self, comp: Comp) -> Component:
        if comp.id in self.bus_symbol_table:
            raise SemanticalError(f'Component {comp.id} has already been declared.')

        component = Component(comp.id)
        self.bus_symbol_table[comp.id] = self.get_components_bus_table(comp)

        for stmt in comp.stmts:
            if isinstance(stmt, Assign):
                self.vst_assign(component, stmt)

            elif isinstance(stmt, Decl):
                self.vst_decl(component, stmt)

            else:
                raise SemanticalError(f'Invalid statement in a component: {stmt}')

        component.make_influence_list()

        return component

    def vst_decl(self, component: Component, decl: Decl) -> None:
        bit_bus = BitBus()

        if decl.conn == INPUT:
            component.inputs.append(decl.id)

        if decl.assign is not None:
            bit_bus.assignment = self.vst_expr(component, decl.assign)
            bit_bus.sensitivity_list = self.get_sensitivity_list(decl.assign)

        component.bus_dict[decl.id] = bit_bus

    def vst_assign(self, component: Component, assign: Assign) -> None:
        if assign.dt.id not in self.bus_symbol_table[component.id]:
            raise SemanticalError(f'Identifier {assign.dt.id} has not been declared.')  # All destiny signals must be declared previously

        elif self.bus_symbol_table[component.id][assign.dt.id].is_assigned:
            raise SemanticalError(f'Identifier {assign.dt.id} has already been assigned.')  # Destiny signal cannot be assigned more than once

        else:
            self.bus_symbol_table[component.id][assign.dt.id].is_assigned = IS_ASSIGNED
            component.bus_dict[assign.dt.id].assignment = self.vst_expr(component, assign.expr)

    def vst_expr(self, component, expr) -> callable:
        assignment = self.vst_expr_elem(component, expr)

        return assignment

    def vst_expr_elem(self, component: Component, expr_elem: ExprElem) -> callable:
        """Visit an expression element, validate it, and return a callable for evaluation."""

        if isinstance(expr_elem, Identifier):
            if expr_elem.id not in self.bus_symbol_table[component.id]:
                raise SemanticalError(f'Identifier {expr_elem.id} has not been declared.')

            return lambda: component.bus_dict[expr_elem.id].value

        elif isinstance(expr_elem, Binary):
            if not isinstance(expr_elem.value, bool):
                raise SemanticalError(f'Binary value {expr_elem.value} is not a valid bit.')

            return lambda: bool(expr_elem.value)

        elif isinstance(expr_elem, Not):
            self.vst_expr_elem(component, expr_elem.expr)

            return lambda: not self.vst_expr_elem(component, expr_elem.expr)()
    
        elif isinstance(expr_elem, And):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: self.vst_expr_elem(component, expr_elem.l_expr)() and self.vst_expr_elem(component, expr_elem.r_expr)()

        elif isinstance(expr_elem, Or):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: self.vst_expr_elem(component, expr_elem.l_expr)() or self.vst_expr_elem(component, expr_elem.r_expr)()

        elif isinstance(expr_elem, Xor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: self.vst_expr_elem(component, expr_elem.l_expr)() ^ self.vst_expr_elem(component, expr_elem.r_expr)()

        elif isinstance(expr_elem, Nand):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (self.vst_expr_elem(component, expr_elem.l_expr)() and self.vst_expr_elem(component, expr_elem.r_expr)())

        elif isinstance(expr_elem, Nor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (self.vst_expr_elem(component, expr_elem.l_expr)() or self.vst_expr_elem(component, expr_elem.r_expr)())
    
        elif isinstance(expr_elem, Xnor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (self.vst_expr_elem(component, expr_elem.l_expr)() ^ self.vst_expr_elem(component, expr_elem.r_expr)())

        else:
            raise SemanticalError(f'Invalid expression element: {expr_elem}')
