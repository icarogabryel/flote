from copy import deepcopy
from json import dumps
from typing import Optional, Tuple
from warnings import warn

from . import ast_nodes
from .ir import expr_nodes
from .ir.busses import BitBusDto, BitBusValueDto
from .ir.component import ComponentDto
from .symbol_table import BusSymbol, CompTable, SymbolTable


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
        self.components: dict[str, ComponentDto] = {}
        self.comp_nodes: dict[str, ast_nodes.Comp] = {}
        self.ir: str = self.get_ir()

    def get_ir(self) -> str:
        component = self.vst_mod(self.ast)
        component.make_influence_lists()

        return dumps(component.to_json())

    def init_component_table(self, comp: ast_nodes.Comp) -> CompTable:
        """Get the component's bus symbol table."""
        comp_table: CompTable = CompTable()

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                decl = stmt  # Name change for better readability
                is_assigned = False
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
                    is_assigned = True

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
        """Validate the bus symbol table to ensure all buses are assigned and read."""
        for bus_table in self.symbol_table.components.values():
            for bus_id, bus in bus_table.busses.items():
                if (bus.connection_type != ast_nodes.Connection.INPUT) and (not bus.is_assigned):
                    warn(
                        f'Bus "{bus_id}" has not been assigned.',
                        UserWarning
                    )

                if (bus.connection_type != ast_nodes.Connection.OUTPUT) and (not bus.is_read):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    #TODO change to return a module of components
    def vst_mod(self, mod: ast_nodes.Mod) -> ComponentDto:
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
            main_component: Optional[ComponentDto] = None

            for comp in mod.comps:  # Search for the main component
                if comp.id in self.components:
                    continue  # Skip if component already processed in a previous instantiation
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

    def vst_comp(self, comp: ast_nodes.Comp) -> ComponentDto:
        if comp.id in self.symbol_table.components.keys():
            raise SemanticalError(
                f'Component "{comp.id}" has already been declared.',
                comp.line_number
            )

        component_id = comp.id
        component = ComponentDto(component_id)
        self.symbol_table.components[component_id] = self.init_component_table(
            comp,
        )
        self.symbol_table.components[component_id].object = component

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Decl):
                self.vst_decl(stmt, component_id, component)
            elif isinstance(stmt, ast_nodes.Assign):
                self.vst_assign(stmt, component_id, component)
            # elif isinstance(stmt, ast_nodes.Inst):
            #     self.vst_inst(stmt, component_id, component)
            else:
                assert False, f'Invalid statement: {stmt}'

        return component

    def vst_decl(self, decl: ast_nodes.Decl, component_id: str, component: ComponentDto) -> None:
        assert decl.id in self.symbol_table.components[component_id].busses.keys(), (
            f'Bus "{decl.id}" has not been declared in the symbol table.'
        )

        bus_symbol = self.symbol_table.components[component_id].busses[decl.id]
        bit_bus = BitBusDto()
        bit_bus.id_ = decl.id
        bus_symbol.object = bit_bus

        # if decl.conn == ast_nodes.Connection.INPUT:
        #     component.interface.append(decl.id)

        if decl.dimension is not None:
            assert decl.dimension.size is not None

            bit_bus.set_dimension(decl.dimension.size)

        if decl.assign is not None:
            # Create the bus assignment
            assignment, size = self.vst_expr(decl.assign, component_id, component)
            bit_bus.assignment = assignment

            #TODO improve using symbol table
            if size != bus_symbol.size:
                raise SemanticalError(
                    (
                        f'Assignment size ({size}) does not match bus size '
                        f'({bus_symbol.size}) for "{decl.id}".'
                    ),
                    decl.line_number
                )

        component.busses.append(bit_bus)

    def vst_assign(self, assign: ast_nodes.Assign, component_id: str, component: ComponentDto) -> None:
        if assign.destiny.id not in self.symbol_table.components[component_id].busses.keys():
            # All destiny signals must be declared previously
            raise SemanticalError(
                f'Identifier "{assign.destiny.id}" has not been declared.',
                assign.destiny.line_number
            )

        bus_symbol = self.symbol_table.components[component_id].busses[assign.destiny.id]

        if bus_symbol.is_assigned == True:
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
        bus_symbol.is_assigned = True

        # Create the assignment and put in the assignment field
        # TODO change to make run if declaration is after assignment
        if self.symbol_table.components[component_id].busses.get(assign.destiny.id) is None:
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

        #TODO improve picking an object from symbol table
        self.symbol_table.components[component_id].busses[assign.destiny.id].object.assignment = assignment

    def vst_expr(self, expr, component_id: str, component: ComponentDto) -> Tuple[expr_nodes.ExprNode, int]:
        assignment = self.vst_expr_elem(expr, component_id, component)

        return assignment

    def vst_expr_elem(
        self, expr_elem: ast_nodes.ExprElem, component_id: str, component: ComponentDto
    ) -> Tuple[expr_nodes.ExprNode, int]:
        """
        Visit an expression element, validate it, and return a callable for evaluation."""
        if expr_elem is None:
            raise SemanticalError(
                'Expression element cannot be None.'
            )

        if isinstance(expr_elem, ast_nodes.Ref):
            ref = expr_elem

            if (ref_id := ref.id_.id) not in self.symbol_table.components[component_id].busses.keys():
                raise SemanticalError(
                    f'Bus reference "{ref_id}" has not been declared.',
                   ref.id_.line_number
                )

            bus_symbol = self.symbol_table.components[component_id].busses[expr_elem.id_.id]

            if ref.slice is not None:
                if (size := bus_symbol.size) <= ref.slice:
                    raise SemanticalError(
                        f'Index [{ref.slice}] out of bounds for "{ref_id}".',
                        ref.id_.line_number
                    )

                size = 1  #TODO change when slice implemented
            else:
                size = bus_symbol.size

            bus_symbol.is_read = True

            #TODO fix type checking
            bus_ref = expr_nodes.Ref(
                self.symbol_table.components[component_id].busses[expr_elem.id_.id].object,
                ref.slice
            )

            return bus_ref, size
        elif isinstance(expr_elem, ast_nodes.BitField):
            bit_field = expr_elem
            bit_value = BitBusValueDto(bit_field.value)
            const = expr_nodes.Const(bit_value)

            return const, bit_field.size
        elif isinstance(expr_elem, ast_nodes.NotOp):
            assert expr_elem.expr is not None, 'Expression cannot be None.'

            expr, size = self.vst_expr_elem(expr_elem.expr, component_id, component)

            return expr_nodes.Not(expr), size
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

            return expr_nodes.And(l_expr, r_expr), l_size
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

            return expr_nodes.Or(l_expr, r_expr), l_size
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

            return expr_nodes.Xor(l_expr, r_expr), l_size
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

            return expr_nodes.Nand(l_expr, r_expr), l_size
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

            return expr_nodes.Nor(l_expr, r_expr), l_size
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

            return expr_nodes.Xnor(l_expr, r_expr), l_size
        else:
            assert False, f'Invalid expression element: {expr_elem}'

    def vst_inst(self, inst: ast_nodes.Inst, component_id: str, component: ComponentDto) -> None:
        assert inst.comp_id is not None, 'Instance component cannot be None.'

        # Check if the subcomponent was already processed
        if inst.comp_id not in self.components.keys():
            self.components[inst.comp_id] = self.vst_comp(self.comp_nodes[inst.comp_id])

        alias = inst.comp_id if inst.sub_alias is None else inst.sub_alias
        subcomponent = deepcopy(self.components[inst.comp_id])

        top_busses = self.symbol_table.components[component_id].busses
        bottom_busses = deepcopy(self.symbol_table.components[inst.comp_id].busses)

        # Add the subcomponent's buses to the top component's symbol table
        top_busses |= {
            f'{alias}.{bus_id}': bus for bus_id, bus in bottom_busses.items()
        }

        # Link the new subcomponent's bus objects to the top component's symbol table because
        # deepcopy still makes references to the old objects.
        for bus in subcomponent.busses:
            self.symbol_table.components[component_id].busses[f'{alias}.{bus.id_}'].object = bus

        component.add_subcomponent(subcomponent, alias)
