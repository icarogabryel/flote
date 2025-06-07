from .component import Component, BitBus
from .ast import (
    Mod, Comp, Decl, Assign, ExprElem,
    Identifier, BitField, UnaryOp, BinaryOp,
    Not, And, Or, Xor, Nand, Nor, Xnor,
    INPUT, OUTPUT
)
from typing import Optional, Union
from warnings import warn


NOT_ASSIGNED = False
IS_ASSIGNED = True


class SemanticalError(Exception):
    def __init__(self, line_number: Union[None, int, str], message):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f'Semantical error at line {self.line_number}: {self.message}'


class BusSymbol:
    """Class that represents a bus symbol in the symbol table."""
    def __init__(self, type, is_assigned, conn):
        self.type: Optional[str] = type
        self.is_assigned = is_assigned
        self.conn = conn
        self.is_read = False

    def __repr__(self):
        return f'({self.type}, {self.is_assigned})'  # todo Improve


class Builder:
    """Class that builds the component from the AST."""
    def __init__(self, ast) -> None:  # todo Add signal list to error handling
        self.ast = ast
        # component: bus: (type, is_assigned)
        self.bus_symbol_table: dict[str, dict[str, BusSymbol]] = {}

    # todo Make return specific component, if not, main or unique file
    # todo component.
    def get_component(self, name=None) -> Component:
        return self.vst_mod(self.ast)

    def get_sensitivity_list(self, expr_elem: ExprElem) -> list[str]:
        """
        Get a list of identifiers that influence the value of a bit signal.
        """
        sensitivity_list = []

        if isinstance(expr_elem, Identifier):
            sensitivity_list.append(expr_elem.id)
        # Constant value don't need to be in the sensitivity list
        elif isinstance(expr_elem, BitField):
            pass
        elif isinstance(expr_elem, UnaryOp):
            sensitivity_list.extend(self.get_sensitivity_list(expr_elem.expr))
        elif isinstance(expr_elem, BinaryOp):
            sensitivity_list.extend(
                self.get_sensitivity_list(expr_elem.l_expr)
            )
            sensitivity_list.extend(
                self.get_sensitivity_list(expr_elem.r_expr)
            )
        else:
            # todo check if this makes sense
            assert False, f'Invalid expression element: {expr_elem}'

        return sensitivity_list

    def get_components_bus_table(self, comp: Comp) -> dict[str, BusSymbol]:
        """Get the component's bus symbol table."""
        components_bus_table: dict[str, BusSymbol] = {}

        for stmt in comp.stmts:
            if isinstance(stmt, Decl):
                decl = stmt  # Name change for better readability

                if decl.id in components_bus_table:
                    raise SemanticalError(
                        decl.line_number,
                        f'Bus "{decl.id}" has already been declared.'
                    )

                if decl.conn == INPUT:
                    if decl.assign is not None:
                        raise SemanticalError(
                            decl.line_number,
                            f'Input Buses like {decl.id} cannot be assigned.'
                        )
                    else:
                        components_bus_table[decl.id] = BusSymbol(
                            decl.type,
                            # Is considered assigned if it has an input
                            # connection
                            # todo Improve this logic
                            IS_ASSIGNED,
                            decl.conn
                        )
                else:
                    components_bus_table[decl.id] = BusSymbol(
                        decl.type,
                        NOT_ASSIGNED,
                        decl.conn
                    )

        return components_bus_table

    def validate_bus_symbol_table(self):
        """
        Validate the bus symbol table to ensure all buses are assigned and
        read.
        """
        for comp_id, comp_bus_list in self.bus_symbol_table.items():
            for bus_id, bus in comp_bus_list.items():
                if (bus.conn != INPUT) and (not bus.is_assigned):
                    warn(
                        f'Bus "{bus_id}" has not been assigned.',
                        UserWarning
                    )

                if (bus.conn != OUTPUT) and (not bus.is_read):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    def vst_mod(self, mod: Mod):
        if len(mod.comps) == 1:
            return self.vst_comp(mod.comps[0])

        else:
            is_main_comp_found = False
            main_component: Optional[Component] = None

            for comp in mod.comps:  # Search for the main component
                if comp.is_main:
                    if is_main_comp_found:
                        raise SemanticalError(
                            comp.line_number,
                            (
                                f'{comp.id} can\'t be main. Only one main'
                                'component is allowed.'
                            )
                        )
                    else:
                        is_main_comp_found = True
                        main_component = self.vst_comp(comp)
                else:
                    self.vst_comp(comp)

            if not is_main_comp_found:
                raise SemanticalError(
                    '_',  # todo Check if this logic is correct
                    'Main component not found in a multiple component module.'
                )

        self.validate_bus_symbol_table()

        return main_component

    def vst_comp(self, comp: Comp) -> Component:
        if comp.id in self.bus_symbol_table.keys():
            raise SemanticalError(
                comp.line_number,
                f'Component "{comp.id}" has already been declared.'
            )

        component = Component(comp.id)
        self.bus_symbol_table[comp.id] = self.get_components_bus_table(comp)

        for stmt in comp.stmts:
            if isinstance(stmt, Assign):
                self.vst_assign(component, stmt)
            elif isinstance(stmt, Decl):
                self.vst_decl(component, stmt)
            else:
                assert False, f'Invalid statement: {stmt}'

        component.make_influence_list()

        return component

    def vst_decl(self, component: Component, decl: Decl) -> None:
        bit_bus = BitBus()

        if decl.conn == INPUT:
            component.inputs.append(decl.id)

        if decl.assign is not None:
            self.bus_symbol_table[component.id][decl.id].is_assigned = (
                IS_ASSIGNED
            )

            bit_bus.assignment = self.vst_expr(component, decl.assign)
            bit_bus.sensitivity_list = self.get_sensitivity_list(decl.assign)

        component.bus_dict[decl.id] = bit_bus

    def vst_assign(self, component: Component, assign: Assign) -> None:
        if assign.dt.id not in self.bus_symbol_table[component.id]:
            # All destiny signals must be declared previously
            raise SemanticalError(
                assign.dt.line_number,
                f'Identifier "{assign.dt.id}" has not been declared.'
            )
        elif self.bus_symbol_table[component.id][assign.dt.id].is_assigned:
            # Destiny signal cannot be assigned more than once
            raise SemanticalError(
                assign.dt.line_number,
                f'Identifier "{assign.dt.id}" has already been assigned.'
            )
        elif self.bus_symbol_table[component.id][assign.dt.id].conn == INPUT:
            # Input buses cannot be assigned
            raise SemanticalError(
                assign.dt.line_number,
                f'Input Buses like "{assign.dt.id}" cannot be assigned.'
            )
        else:
            # Mark the bus as assigned in the symbol table
            self.bus_symbol_table[component.id][assign.dt.id].is_assigned = (
                IS_ASSIGNED
            )
            # Create the assignment callable and put in the assignment field
            component.bus_dict[assign.dt.id].assignment = self.vst_expr(
                component,
                assign.expr
            )
            # Get the sensitivity list for the assignment expression
            component.bus_dict[assign.dt.id].sensitivity_list = (
                self.get_sensitivity_list(assign.expr)
            )

    def vst_expr(self, component, expr) -> callable:
        assignment = self.vst_expr_elem(component, expr)

        return assignment

    def vst_expr_elem(
        self,
        component: Component,
        expr_elem: ExprElem
    ) -> callable:
        """
        Visit an expression element, validate it, and return a callable for
        evaluation.
        """
        if isinstance(expr_elem, Identifier):
            if expr_elem.id not in self.bus_symbol_table[component.id]:
                raise SemanticalError(
                    expr_elem.line_number,
                    f'Identifier "{expr_elem.id}" has not been declared.'
                )

            self.bus_symbol_table[component.id][expr_elem.id].is_read = True

            return lambda: component.bus_dict[expr_elem.id].value
        elif isinstance(expr_elem, BitField):
            # todo change here for vectorial format
            if not isinstance(expr_elem.value, bool):
                assert False, f'Invalid bit field value: {expr_elem.value}'

            return lambda: bool(expr_elem.value)
        elif isinstance(expr_elem, Not):
            self.vst_expr_elem(component, expr_elem.expr)

            return lambda: not self.vst_expr_elem(component, expr_elem.expr)()
        elif isinstance(expr_elem, And):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                and
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )
        elif isinstance(expr_elem, Or):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                or
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )
        elif isinstance(expr_elem, Xor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                ^
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )
        elif isinstance(expr_elem, Nand):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                and
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )
        elif isinstance(expr_elem, Nor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                or
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )
        elif isinstance(expr_elem, Xnor):
            self.vst_expr_elem(component, expr_elem.l_expr)
            self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: not (
                self.vst_expr_elem(component, expr_elem.l_expr)()
                ^
                self.vst_expr_elem(component, expr_elem.r_expr)()
            )

        assert False, f'Invalid expression element: {expr_elem}'
