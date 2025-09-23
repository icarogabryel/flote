import copy
from enum import Enum
from typing import Optional, Tuple
from warnings import warn

from ..backend.backend.python.busses import BitBus, BitBusValue, Evaluator
from ..backend.backend.python.component import Component
from ..backend.backend.python.expr_nodes import (And, BusRef, Const, Nand,
                                                    Nor, Not, Or, Xnor, Xor)
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
        self.components: dict[str, Component] = {}
        self.comp_nodes: dict[str, ast_nodes.Comp] = {}
        self.main_component: Component = self.vst_mod(self.ast)

    def get_component(self) -> Component:
        return self.main_component

    def init_component_table(self, comp: ast_nodes.Comp) -> CompTable:
        """Get the component's bus symbol table."""
        comp_table: CompTable = CompTable()

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                decl = stmt  # Name change for better readability
                is_assigned = Assigned.NOT_ASSIGNED
                size = 1

                if decl.id in comp_table.busses.keys():
                    raise SemanticalError(
                        f'Bus "{decl.id}" has already been declared.',
                        decl.line_number
                    )

                if decl.assign is not None:
                    if (decl.conn == ast_nodes.Connection.INPUT):
                        raise SemanticalError(
                            f'Input Buses like {decl.id} cannot be assigned.',
                            decl.line_number
                        )

                    # Mark the bus as assigned in the symbol table
                    is_assigned = Assigned.ASSIGNED

                if decl.dimension is not None:
                    size = decl.dimension.size

                comp_table.busses[decl.id] = BusSymbol(
                    decl.type,
                    is_assigned,
                    decl.conn,
                    size
                )

        return comp_table

    def validate_bus_symbol_table(self):
        """
        Validate the bus symbol table to ensure all buses are assigned and
        read.
        """
        for _, bus_table in self.symbol_table.components.items():
            for bus_id, bus in bus_table.busses.items():
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

        # Fill the comp_nodes dictionary
        for comp in mod.comps:
            self.comp_nodes[comp.id] = comp

        if len(mod.comps) == 1:
            component = self.vst_comp(mod.comps[0])
            self.components[mod.comps[0].id] = component

            return component
        else:  # If there are multiple components, we assume one of them is the main
            is_main_comp_found = False
            main_component: Optional[Component] = None

            for comp in mod.comps:  # Search for the main component
                if comp.id in self.components:
                    continue  # Skip if component already processed
                # Add component to the components dict
                component = self.vst_comp(comp)
                self.components[comp.id] = component

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
                    main_component = component

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

        component_id = comp.id
        component = Component()
        self.symbol_table.components[component_id] = self.init_component_table(
            comp,
        )

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                self.vst_decl(stmt, component_id, component)
            elif isinstance(stmt, ast_nodes.Assign):
                self.vst_assign(stmt, component_id, component)
            elif isinstance(stmt, ast_nodes.Inst):
                self.vst_inst(stmt, component_id, component)
            else:
                assert False, f'Invalid statement: {stmt}'

        return component

    def vst_decl(self, decl: ast_nodes.Decl, component_id: str, component: Component) -> None:
        assert decl.id in self.symbol_table.components[component_id].busses.keys(), (
            f'Bus "{decl.id}" has not been declared in the symbol table.'
        )

        bus_symbol = self.symbol_table.components[component_id].busses[decl.id]
        bit_bus = BitBus()
        bit_bus.id = decl.id

        # if decl.conn == ast_nodes.Connection.INPUT:
        #     component.interface.append(decl.id)

        if decl.dimension is not None:
            assert decl.dimension.size is not None

            bit_bus.set_dimension(decl.dimension.size)

        if decl.assign is not None:
            # Create the bus assignment
            assignment, size = self.vst_expr(decl.assign, component_id, component)
            bit_bus.set_assignment(assignment)

            if size != bus_symbol.size:
                raise SemanticalError(
                    (
                        f'Assignment size ({size}) does not match bus size '
                        f'({bus_symbol.size}) for "{decl.id}".'
                    ),
                    decl.line_number
                )

        component.busses[decl.id] = bit_bus

    def vst_assign(self, assign: ast_nodes.Assign, component_id: str, component: Component) -> None:
        if assign.destiny.id not in self.symbol_table.components[component_id].busses.keys():
            # All destiny signals must be declared previously
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" has not been declared.',
                assign.destiny.line_number
            )

        bus_symbol = self.symbol_table.components[component_id].busses[assign.destiny.id]

        if bus_symbol.is_assigned == Assigned.ASSIGNED:
            # Destiny signal cannot be assigned more than once
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" already assigned.',
                assign.destiny.line_number
            )

        #TODO change to accept in subcomponents
        # if bus_symbol.connection_type == ast_nodes.Connection.INPUT:
        #     # Input buses cannot be assigned
        #     raise SemanticalError(
        #         f'Input Buses like "{assign.destiny.id}" cannot be assigned.',
        #         assign.destiny.line_number
        #     )

        # Mark the bus as assigned in the symbol table
        bus_symbol.is_assigned = Assigned.ASSIGNED

        # Create the assignment and put in the assignment field
        # TODO change to make run if declaration is after assignment
        if component.busses.get(assign.destiny.id) is None:
            raise SemanticalError(
                (
                    f'Identifier "{assign.destiny.id}" has not been declared '
                    'before.'
                ),
                assign.destiny.line_number
            )

        assignment, size = self.vst_expr(
            assign.expr,
            component_id,
            component
        )

        if size != bus_symbol.size:
            raise SemanticalError(
                (
                    f'Assignment size ({size}) does not match bus size '
                    f'({bus_symbol.size}) for "{assign.destiny.id}".'
                ),
                assign.destiny.line_number
            )

        component.busses[assign.destiny.id].assignment = assignment

    def vst_expr(self, expr, component_id: str, component: Component) -> Tuple[Evaluator, int]:
        assignment = self.vst_expr_elem(expr, component_id, component)

        return assignment

    def vst_expr_elem(
        self, expr_elem: ast_nodes.ExprElem, component_id: str, component: Component
    ) -> Tuple[Evaluator, int]:
        """
        Visit an expression element, validate it, and return a callable for evaluation."""
        if expr_elem is None:
            raise SemanticalError(
                'Expression element cannot be None.'
            )

        if isinstance(expr_elem, ast_nodes.Identifier):
            if expr_elem.id not in \
                    self.symbol_table.components[component_id].busses.keys():
                raise SemanticalError(
                    f'Identifier "{expr_elem.id}" has not been declared.',
                    expr_elem.line_number
                )

            bus_symbol = self.symbol_table.components[component_id].busses[expr_elem.id]
            bus_symbol.is_read = True
            size = bus_symbol.size

            bus_ref = BusRef(component.busses[expr_elem.id])

            return bus_ref, size
        elif isinstance(expr_elem, ast_nodes.BitField):
            bit_field = expr_elem
            bit_value = BitBusValue([bool(int(bit)) for bit in bit_field.value])
            const = Const(bit_value)

            return const, bit_field.size
        elif isinstance(expr_elem, ast_nodes.NotOp):
            assert expr_elem.expr is not None, 'Expression cannot be None.'

            expr, size = self.vst_expr_elem(expr_elem.expr, component_id, component)

            return Not(expr), size
        elif isinstance(expr_elem, ast_nodes.AndOp):
            #TODO put a function for those asserts
            assert expr_elem.l_expr is not None, (
                'Left expression of And operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of And operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return And(l_expr, r_expr), l_size
        elif isinstance(expr_elem, ast_nodes.OrOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Or operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Or operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return Or(l_expr, r_expr), l_size
        elif isinstance(expr_elem, ast_nodes.XorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Xor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Xor operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return Xor(l_expr, r_expr), l_size
        elif isinstance(expr_elem, ast_nodes.NandOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Nand operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Nand operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return Nand(l_expr, r_expr), l_size
        elif isinstance(expr_elem, ast_nodes.NorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Nor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Nor operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return Nor(l_expr, r_expr), l_size
        elif isinstance(expr_elem, ast_nodes.XnorOp):
            assert expr_elem.l_expr is not None, (
                'Left expression of Xnor operation cannot be None.'
            )
            assert expr_elem.r_expr is not None, (
                'Right expression of Xnor operation cannot be None.'
            )

            l_expr, l_size = self.vst_expr_elem(expr_elem.l_expr, component_id, component)
            r_expr, r_size = self.vst_expr_elem(expr_elem.r_expr, component_id, component)

            if l_size != r_size:
                raise SemanticalError(
                    'Left and right expressions of And operation must be the same size.',
                    expr_elem.line_number
                )

            return Xnor(l_expr, r_expr), l_size
        else:
            assert False, f'Invalid expression element: {expr_elem}'

    def vst_inst(self, inst: ast_nodes.Inst, component_id: str, component: Component) -> None:
        assert inst.comp_id is not None, 'Instance component cannot be None.'

        if inst.comp_id not in self.components.keys():
            self.components[inst.comp_id] = self.vst_comp(self.comp_nodes[inst.comp_id])

        alias = inst.comp_id if inst.sub_alias is None else inst.sub_alias


        top_busses = self.symbol_table.components[component_id].busses
        bottom_busses = copy.deepcopy(self.symbol_table.components[inst.comp_id].busses)

        top_busses |= {
            f'{alias}.{bus_id}': bus for bus_id, bus in bottom_busses.items()
        }

        component.add_component(
            alias,
            copy.deepcopy(self.components[inst.comp_id])
        )
