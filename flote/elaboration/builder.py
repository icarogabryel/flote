from enum import Enum
from typing import Optional, Callable
from warnings import warn

from ..model.busses import BusValue
from ..model.component import BitBus, Component
from . import ast_nodes


class AssignType(Enum):
    """Enum to represent the assignment type."""
    INPUT = 'input'
    OUTPUT = 'output'


class Assigned(Enum):
    """Enum to represent if a bus is assigned."""
    ASSIGNED = True
    NOT_ASSIGNED = False


class SemanticalError(Exception):
    def __init__(self, message: str, line_number: Optional[int] = None):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return (
            f'Semantical error at line {self.line_number}: {self.message}'
            if self.line_number is not None
            else f'Semantical error: {self.message}'
        )


class BusSymbol:
    """Class that represents a bus symbol in the symbol table."""
    def __init__(self, type, is_assigned, conn):
        self.type: Optional[str] = type
        self.is_assigned = is_assigned
        self.conn = conn
        self.is_read = False

    def __repr__(self):
        return (
            f'| {self.type} | {self.is_assigned} | {self.conn} | '
            f'{self.is_read} |'
        )


class Builder:
    """Class that builds the component from the AST."""
    def __init__(self, ast) -> None:
        self.ast = ast
        # component: bus: (type, is_assigned)
        #TODO improve
        self.bus_symbol_table: dict[str, dict[str, BusSymbol]] = {}

    def get_component(self) -> None | Component:
        return self.vst_mod(self.ast)

    def get_sensitivity_list(self, expr_elem: ast_nodes.ExprElem) -> list[str]:
        """
        Get a list of identifiers that influence the value of a bit signal.
        """

        sensitivity_list = []

        if isinstance(expr_elem, ast_nodes.Identifier):
            sensitivity_list.append(expr_elem.id)
        # Constant value don't need to be in the sensitivity list
        elif isinstance(expr_elem, ast_nodes.BitField):
            pass
        elif isinstance(expr_elem, ast_nodes.UnaryOp):
            expr = expr_elem.expr

            assert expr is not None, (
                'Unary operation expression cannot be None.'
            )

            sensitivity_list.extend(self.get_sensitivity_list(expr))
        elif isinstance(expr_elem, ast_nodes.BinaryOp):
            l_expr = expr_elem.l_expr
            r_expr = expr_elem.r_expr

            assert l_expr is not None, (
                'Binary operation left expression cannot be None.'
            )
            assert r_expr is not None, (
                'Binary operation right expression cannot be None.'
            )

            sensitivity_list.extend(
                self.get_sensitivity_list(l_expr)
            )
            sensitivity_list.extend(
                self.get_sensitivity_list(r_expr)
            )
        else:
            assert False, f'Unexpected expression element: {expr_elem}'

        return sensitivity_list

    def get_components_bus_table(
        self, comp: ast_nodes.Comp
    ) -> dict[str, BusSymbol]:
        """Get the component's bus symbol table."""
        components_bus_table: dict[str, BusSymbol] = {}

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                decl = stmt  # Name change for better readability

                if decl.id in components_bus_table:
                    raise SemanticalError(
                        f'Bus "{decl.id}" has already been declared.',
                        decl.line_number
                    )

                if decl.conn == AssignType.INPUT:
                    if decl.assign is not None:
                        raise SemanticalError(
                            f'Input Buses like {decl.id} cannot be assigned.',
                            decl.line_number
                        )
                    else:
                        components_bus_table[decl.id] = BusSymbol(
                            decl.type,
                            # Is considered assigned if it has an input
                            # connection
                            # todo Improve this logic
                            Assigned.ASSIGNED,
                            decl.conn
                        )
                else:
                    components_bus_table[decl.id] = BusSymbol(
                        decl.type,
                        Assigned.NOT_ASSIGNED,
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
                if (bus.conn != AssignType.INPUT) and (not bus.is_assigned):
                    warn(
                        f'Bus "{bus_id}" has not been assigned.',
                        UserWarning
                    )

                if (bus.conn != AssignType.OUTPUT) and (not bus.is_read):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    def vst_mod(self, mod: ast_nodes.Mod):
        if len(mod.comps) == 1:
            return self.vst_comp(mod.comps[0])

        else:
            is_main_comp_found = False
            main_component: Optional[Component] = None

            for comp in mod.comps:  # Search for the main component
                if comp.is_main:
                    if is_main_comp_found:
                        raise SemanticalError(
                            (
                                f'{comp.id} can\'t be main. Only one main'
                                'component is allowed.'
                            ),
                            comp.line_number
                        )
                    else:
                        is_main_comp_found = True
                        main_component = self.vst_comp(comp)
                else:
                    self.vst_comp(comp)

            if not is_main_comp_found:
                raise SemanticalError(
                    'Main component not found in a multiple component module.'
                )

        self.validate_bus_symbol_table()

        return main_component

    def vst_comp(self, comp: ast_nodes.Comp) -> Component:
        if comp.id in self.bus_symbol_table.keys():
            raise SemanticalError(
                f'Component "{comp.id}" has already been declared.',
                comp.line_number
            )

        component = Component(comp.id)
        self.bus_symbol_table[comp.id] = self.get_components_bus_table(comp)

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Assign):
                self.vst_assign(component, stmt)
            elif isinstance(stmt, ast_nodes.Decl):
                self.vst_decl(component, stmt)
            else:
                assert False, f'Invalid statement: {stmt}'

        component.make_influence_list()

        return component

    def vst_decl(self, component: Component, decl: ast_nodes.Decl) -> None:
        bit_bus = BitBus()

        if decl.conn == AssignType.INPUT:
            component.inputs.append(decl.id)

        if decl.dimension is not None:
            assert decl.dimension.size is not None

            bit_bus.set_dimension(decl.dimension.size)

        if decl.assign is not None:
            self.bus_symbol_table[component.id][decl.id].is_assigned = (
                Assigned.ASSIGNED
            )

            bit_bus.assignment = self.vst_expr(component, decl.assign)
            bit_bus.sensitivity_list = self.get_sensitivity_list(decl.assign)

        component.bus_dict[decl.id] = bit_bus

    def vst_assign(
            self, component: Component, assign: ast_nodes.Assign
    ) -> None:
        if assign.destiny.id not in self.bus_symbol_table[component.id]:
            # All destiny signals must be declared previously
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" has not been declared.',
                assign.destiny.line_number
            )
        elif (
            self.bus_symbol_table[component.id][assign.destiny.id].is_assigned
        ):
            # Destiny signal cannot be assigned more than once
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" has already been assigned.',
                assign.destiny.line_number
            )
        elif (
            self.bus_symbol_table[component.id][assign.destiny.id].conn
            ==
            ast_nodes.Connection.INPUT
        ):
            # Input buses cannot be assigned
            raise SemanticalError(
                f'Input Buses like "{assign.destiny.id}" cannot be assigned.',
                assign.destiny.line_number
            )
        else:
            # Mark the bus as assigned in the symbol table
            bus = self.bus_symbol_table[component.id][assign.destiny.id]
            bus.is_assigned = Assigned.ASSIGNED
            # Create the assignment callable and put in the assignment field
            component.bus_dict[assign.destiny.id].assignment = self.vst_expr(
                component,
                assign.expr
            )
            # Get the sensitivity list for the assignment expression
            component.bus_dict[assign.destiny.id].sensitivity_list = (
                self.get_sensitivity_list(assign.expr)
            )

    def vst_expr(self, component, expr) -> Callable:
        assignment = self.vst_expr_elem(component, expr)

        return assignment

    def vst_expr_elem(
        self, component: Component, expr_elem: ast_nodes.ExprElem
    ) -> Callable:
        """
        Visit an expression element, validate it, and return a callable for
        evaluation.
        """
        if expr_elem is None:
            raise SemanticalError(
                'Expression element cannot be None.'
            )

        if isinstance(expr_elem, ast_nodes.Identifier):
            if expr_elem.id not in self.bus_symbol_table[component.id]:
                raise SemanticalError(
                    f'Identifier "{expr_elem.id}" has not been declared.',
                    expr_elem.line_number
                )

            self.bus_symbol_table[component.id][expr_elem.id].is_read = True

            return lambda: component.bus_dict[expr_elem.id].value
        elif isinstance(expr_elem, ast_nodes.BitField):
            if not isinstance(expr_elem.value, BusValue):
                assert False, f'Invalid bus value: {expr_elem.value}'

            bus_value = expr_elem.value  # change name for better readability

            return lambda: bus_value
        elif isinstance(expr_elem, ast_nodes.Not):
            expr = self.vst_expr_elem(component, expr_elem.expr)

            return lambda: ~ expr()
        elif isinstance(expr_elem, ast_nodes.And):
            l_expr: BusValue = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr: BusValue = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: l_expr() & r_expr()
        elif isinstance(expr_elem, ast_nodes.Or):
            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: l_expr() | r_expr()
        elif isinstance(expr_elem, ast_nodes.Xor):
            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: l_expr() ^ r_expr()
        elif isinstance(expr_elem, ast_nodes.Nand):
            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: ~ (l_expr() & r_expr())
        elif isinstance(expr_elem, ast_nodes.Nor):
            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: ~ (l_expr() | r_expr())
        elif isinstance(expr_elem, ast_nodes.Xnor):
            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return lambda: ~ (l_expr() ^ r_expr())

        assert False, f'Invalid expression element: {expr_elem}'
