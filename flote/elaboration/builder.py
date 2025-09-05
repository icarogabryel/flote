from enum import Enum
from typing import Optional
from warnings import warn

from ..simulation.busses import BitBus, BusValue
from ..simulation.component import Component
from ..simulation.expr_nodes import (And, BusRef, Const, Nand, Nor, Not, Or,
                                     Xnor, Xor)
from . import ast_nodes
from .symbol_table import BusSymbol, CompTable, SymbolTable


class Assigned(Enum):
    """Enum to represent if a bus is assigned."""
    ASSIGNED = 0
    NOT_ASSIGNED = 1


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


class Builder:
    """Class that builds the component from the AST."""
    def __init__(self, ast) -> None:
        self.ast: ast_nodes.Mod = ast
        self.symbol_table: SymbolTable = SymbolTable()
        self.model: Component = self.vst_mod(self.ast)

    def get_model(self) -> Component:
        return self.model

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

    def init_component_table(
        self, comp: ast_nodes.Comp, component: Component
    ) -> CompTable:
        """Get the component's bus symbol table."""
        comp_table: CompTable = CompTable()

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                decl = stmt  # Name change for better readability

                if decl.id in comp_table.buses.keys():
                    raise SemanticalError(
                        f'Bus "{decl.id}" has already been declared.',
                        decl.line_number
                    )

                if (decl.conn == ast_nodes.Connection.INPUT) and \
                        (decl.assign is not None):
                    raise SemanticalError(
                        f'Input Buses like {decl.id} cannot be assigned.',
                        decl.line_number
                    )

                comp_table.buses[decl.id] = BusSymbol(
                    decl.type,
                    Assigned.NOT_ASSIGNED,
                    decl.conn
                )

        return comp_table

    def validate_bus_symbol_table(self):
        """
        Validate the bus symbol table to ensure all buses are assigned and
        read.
        """
        for _, bus_table in self.symbol_table.components.items():
            for bus_id, bus in bus_table.buses.items():
                if (bus.connection_type != ast_nodes.Connection.INPUT) and \
                        (not bus.is_assigned):
                    warn(
                        f'Bus "{bus_id}" has not been assigned.',
                        UserWarning
                    )

                if (bus.connection_type != ast_nodes.Connection.OUTPUT) and \
                        (not bus.is_read):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    def vst_mod(self, mod: ast_nodes.Mod) -> Component:
        if not mod.comps:
            raise SemanticalError('Module is empty.')

        if len(mod.comps) == 1:
            return self.vst_comp(mod.comps[0])

        # If there are multiple components, we assume one of them is the main
        else:
            is_main_comp_found = False
            main_component: Optional[Component] = None

            for comp in mod.comps:  # Search for the main component
                if comp.is_main:
                    if is_main_comp_found:
                        raise SemanticalError(
                            (
                                f'{comp.id} can\'t be main. Only one main '
                                'component is allowed.'
                            ),
                            comp.line_number
                        )

                    is_main_comp_found = True
                    main_component = self.vst_comp(comp)

            if not is_main_comp_found:
                raise SemanticalError(
                    'Main component not found in a multiple component module.'
                )

        assert main_component is not None, (
            'Main component should not be None.'
        )

        self.validate_bus_symbol_table()

        return main_component

    def vst_comp(self, comp: ast_nodes.Comp) -> Component:
        if comp.id in self.symbol_table.components.keys():
            raise SemanticalError(
                f'Component "{comp.id}" has already been declared.',
                comp.line_number
            )

        component = Component(comp.id)
        self.symbol_table.components[comp.id] = self.init_component_table(
            comp,
            component
        )

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

        if decl.conn == ast_nodes.Connection.INPUT:
            component.inputs.append(decl.id)

        if decl.dimension is not None:
            assert decl.dimension.size is not None

            bit_bus.set_dimension(decl.dimension.size)

        if decl.assign is not None:
            # Mark the bus as assigned in the symbol table
            bus_symbol = (
                self.symbol_table.components[component.id].buses[decl.id]
            )
            bus_symbol.is_assigned = Assigned.ASSIGNED

            # Create the bus assignment
            bit_bus.assignment = self.vst_expr(component, decl.assign)
            bit_bus.sensitivity_list = self.get_sensitivity_list(decl.assign)

        component.bus_dict[decl.id] = bit_bus

    def vst_assign(
            self, component: Component, assign: ast_nodes.Assign
    ) -> None:
        if assign.destiny.id not in \
                self.symbol_table.components[component.id].buses.keys():
            # All destiny signals must be declared previously
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" has not been declared.',
                assign.destiny.line_number
            )

        bus = (
            self.symbol_table.components[component.id].buses[assign.destiny.id]
        )

        if bus.is_assigned == Assigned.ASSIGNED:
            # Destiny signal cannot be assigned more than once
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" already assigned.',
                assign.destiny.line_number
            )

        if bus.connection_type == ast_nodes.Connection.INPUT:
            # Input buses cannot be assigned
            raise SemanticalError(
                f'Input Buses like "{assign.destiny.id}" cannot be assigned.',
                assign.destiny.line_number
            )

        # Mark the bus as assigned in the symbol table
        bus.is_assigned = Assigned.ASSIGNED
        # Create the assignment callable and put in the assignment field
        if component.bus_dict.get(assign.destiny.id) is None:
            raise SemanticalError(
                (
                    f'Identifier "{assign.destiny.id}" has not been declared '
                    'before.'
                ),
                assign.destiny.line_number
            )

        component.bus_dict[assign.destiny.id].assignment = self.vst_expr(
            component,
            assign.expr
        )
        # Get the sensitivity list for the assignment expression
        component.bus_dict[assign.destiny.id].sensitivity_list = (
            self.get_sensitivity_list(assign.expr)
        )

    def vst_expr(self, component, expr):
        assignment = self.vst_expr_elem(component, expr)

        return assignment

    def vst_expr_elem(
        self, component: Component, expr_elem: ast_nodes.ExprElem
    ):
        """
        Visit an expression element, validate it, and return a callable for
        evaluation.
        """
        if expr_elem is None:
            raise SemanticalError(
                'Expression element cannot be None.'
            )

        if isinstance(expr_elem, ast_nodes.Identifier):
            if expr_elem.id not in \
                    self.symbol_table.components[component.id].buses.keys():
                raise SemanticalError(
                    f'Identifier "{expr_elem.id}" has not been declared.',
                    expr_elem.line_number
                )

            bus_symbol = (
                self.symbol_table.components[component.id].buses[expr_elem.id]
            )
            bus_symbol.is_read = True

            bus_id = BusRef(component, expr_elem.id)

            return bus_id
        elif isinstance(expr_elem, ast_nodes.BitField):
            if not isinstance(expr_elem.value, BusValue):
                assert False, f'Invalid bus value: {expr_elem.value}'

            bus_value = Const(expr_elem.value)  # change name for better readability

            return bus_value
        elif isinstance(expr_elem, ast_nodes.NotOp):
            assert expr_elem.expr is not None, 'Expression cannot be None.'

            expr = self.vst_expr_elem(component, expr_elem.expr)

            return Not(expr)
        elif isinstance(expr_elem, ast_nodes.AndOp):
            #TODO put a function for those asserts
            assert expr_elem.l_expr is not None, (
                'Left expression of And operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of And operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return And(l_expr, r_expr)
        elif isinstance(expr_elem, ast_nodes.OrOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Or operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Or operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return Or(l_expr, r_expr)
        elif isinstance(expr_elem, ast_nodes.XorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Xor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Xor operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return Xor(l_expr, r_expr)
        elif isinstance(expr_elem, ast_nodes.NandOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Nand operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Nand operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return Nand(l_expr, r_expr)
        elif isinstance(expr_elem, ast_nodes.NorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Nor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Nor operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return Nor(l_expr, r_expr)
        elif isinstance(expr_elem, ast_nodes.XnorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Xnor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Xnor operation cannot be None.'
            )

            l_expr = self.vst_expr_elem(component, expr_elem.l_expr)
            r_expr = self.vst_expr_elem(component, expr_elem.r_expr)

            return Xnor(l_expr, r_expr)
        else:
            assert False, f'Invalid expression element: {expr_elem}'
