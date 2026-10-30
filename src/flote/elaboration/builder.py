from copy import deepcopy
from json import dumps
from typing import Tuple
from warnings import warn

from flote.elaboration import ast_nodes
from flote.elaboration.ir import expression_nodes
from flote.elaboration.ir.buses import BitBusDto
from flote.elaboration.ir.component import ComponentDto
from flote.elaboration.symbol_table import BusSymbol, ComponentSymbol, SymbolTable


class SemanticalError(Exception):
    def __init__(self, message: str, line_number: None | int = None) -> None:
        self.line_number = line_number
        self.message = message

    def __str__(self) -> str:
        return (
            f"Semantical error at line {self.line_number}: {self.message}"
            if self.line_number
            else f"Semantical error: {self.message}"
        )


class Builder:
    """Class that builds the component from the AST."""

    def __init__(self, ast: ast_nodes.Module) -> None:
        self.ast = ast
        self.symbol_table: SymbolTable = SymbolTable()
        self.components: dict[str, ComponentDto] = {}
        self.components_nodes: dict[str, ast_nodes.Component] = {}
        self.netlist: str = self.get_netlist()

    def get_netlist(self) -> str:
        component = self.vst_mod(self.ast)
        component.make_netlist()  # TODO see what happens when dumps with no netlist

        return dumps(component.to_json())

    def init_component_symbol(
        self, component_node: ast_nodes.Component, component_dto: ComponentDto
    ) -> ComponentSymbol:
        """Get the component symbol table."""
        component_symbol: ComponentSymbol = ComponentSymbol()

        for statement_node in component_node.statements:
            # Read all information available in declaration for the bus symbol
            if isinstance(statement_node, ast_nodes.Declaration):
                declaration_node = statement_node  # Name change for better readability

                if (
                    declaration_node.identifier.full_id
                    in component_symbol.bus_symbols.keys()
                ):
                    raise SemanticalError(
                        (
                            f'Bus "{declaration_node.identifier}" has already been '
                            "declared."
                        ),
                        declaration_node.line_number,
                    )

                if declaration_node.assignment_expression:
                    if declaration_node.connection == ast_nodes.Connection.INPUT:
                        raise SemanticalError(
                            (
                                f'Input Buses like "{declaration_node.identifier}" '
                                "cannot be assigned."
                            ),
                            declaration_node.line_number,
                        )

                    # Mark the bus as assigned in the symbol table
                    is_assigned = True
                else:
                    is_assigned = False

                if declaration_node.dimension:
                    size = declaration_node.dimension.size
                    msb_descending = (
                        declaration_node.dimension.msb == ast_nodes.Msb.DESCENDING
                    )
                else:
                    size = 1
                    msb_descending = False

                bit_bus_id = declaration_node.identifier.full_id
                bit_bus_dto = BitBusDto(bit_bus_id, size, msb_descending)

                component_symbol.bus_symbols[bit_bus_id] = BusSymbol(
                    declaration_node.type_,
                    is_assigned,
                    declaration_node.connection,
                    size,
                    msb_descending,
                    bit_bus_dto,
                )
            elif isinstance(statement_node, ast_nodes.Instance):  # TODO do it lazily?
                self.vst_inst(statement_node, component_dto, component_symbol)

        return component_symbol

    def check_bus_usage(self) -> None:
        """Check bus symbols to ensure all buses are correctly assigned and read."""
        for component_symbol in self.symbol_table.component_symbols.values():
            for bus_id, bus in component_symbol.bus_symbols.items():
                # Internal or exit without assignment
                if (bus.connection_type != ast_nodes.Connection.INPUT) and (
                    not bus.is_assigned
                ):
                    warn(f'Bus "{bus_id}" has not been assigned.', UserWarning)

                # Entry or internal was never read
                if (bus.connection_type != ast_nodes.Connection.OUTPUT) and (
                    not bus.is_read
                ):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    def vst_mod(self, mod: ast_nodes.Module) -> ComponentDto:
        # Fill the components_nodes dictionary
        for component_node in mod.components:
            self.components_nodes[component_node.identifier.full_id] = component_node

        assert len(mod.components) > 0, "Parser should block modules with no components"

        if len(mod.components) == 1:
            component_dto = self.vst_comp(mod.components[0])
            self.components[mod.components[0].identifier.full_id] = component_dto

            return component_dto
        else:  # If there are multiple components, its assumed one of them is the main
            main_component: None | ComponentDto = None

            for component_node in mod.components:  # Search for the main component
                if component_node.identifier.full_id in self.components:
                    # Skip if component already processed in a previous instantiation
                    continue  # TODO try lazy
                # Add component to the components dict
                component_dto = self.vst_comp(component_node)
                self.components[component_dto.identifier] = component_dto

                if component_node.is_main:
                    if main_component:
                        raise SemanticalError(
                            (
                                f'"{component_node.identifier.full_id}" can\'t be main.'
                                " Only one main component is allowed."
                            ),
                            component_node.line_number,
                        )

                    main_component = component_dto

            if not main_component:
                raise SemanticalError(
                    "Main component not found in a multiple component module."
                )

        self.check_bus_usage()
        return main_component

    def vst_comp(self, component_node: ast_nodes.Component) -> ComponentDto:
        if (
            component_node.identifier.full_id
            in self.symbol_table.component_symbols.keys()
        ):
            raise SemanticalError(
                f'Component "{component_node.identifier}" has already been declared.',
                component_node.line_number,
            )

        component_identifier = component_node.identifier.full_id
        component_dto = ComponentDto(component_identifier)

        self.symbol_table.component_symbols[component_identifier] = (
            self.init_component_symbol(component_node, component_dto)
        )
        self.symbol_table.component_symbols[
            component_identifier
        ].object_ = component_dto

        for stmt in component_node.statements:
            # Do nothing if the instance is Instance (subcomponent)
            if isinstance(stmt, ast_nodes.Declaration):
                self.vst_decl(stmt, component_identifier, component_dto)
            elif isinstance(stmt, ast_nodes.Assignment):
                self.vst_assign(stmt, component_identifier, component_dto)
            else:
                pass

        return component_dto

    def vst_decl(
        self,
        decl: ast_nodes.Declaration,
        component_id: str,  # TODO remove, no need
        component_dto: ComponentDto,
    ) -> None:
        assert (
            decl.identifier.full_id
            in self.symbol_table.component_symbols[component_id].bus_symbols.keys()
        ), f'Bus "{decl.identifier}" has not been declared.'
        bus_symbol = self.symbol_table.component_symbols[component_id].bus_symbols[
            decl.identifier.full_id
        ]

        if decl.assignment_expression:
            # Create the bus assignment
            assignment, size = self.vst_expr(
                decl.assignment_expression, component_id, component_dto
            )

            if size != bus_symbol.size:
                raise SemanticalError(
                    (
                        f"Assignment size ({size}) does not match bus size "
                        f'({bus_symbol.size}) for "{decl.identifier.full_id}".'
                    ),
                    decl.line_number,
                )

            bus_symbol.object_.assignment = assignment

        component_dto.buses.append(bus_symbol.object_)

    def vst_assign(
        self,
        assignment_node: ast_nodes.Assignment,
        component_id: str,  # TODO remove, no need
        component_dto: ComponentDto,
    ) -> None:
        assert (
            assignment_node.destiny.full_id
            in self.symbol_table.component_symbols[component_id].bus_symbols.keys()
        ), f'Identifier "{assignment_node.destiny.full_id}" has not been declared.'

        bus_symbol = self.symbol_table.component_symbols[component_id].bus_symbols[
            assignment_node.destiny.full_id
        ]

        if (bus_symbol.connection_type == ast_nodes.Connection.INPUT) and (
            not bus_symbol.is_lower_lvl
        ):
            raise SemanticalError(
                (
                    f'Input Buses of top level like "{assignment_node.destiny.full_id}"'
                    " cannot be assigned."
                ),
                assignment_node.destiny.line_number,
            )

        if (bus_symbol.connection_type != ast_nodes.Connection.INPUT) and (
            bus_symbol.is_lower_lvl is True
        ):
            raise SemanticalError(
                (
                    f"Internal/out Buses of subcomponents like "
                    f'"{assignment_node.destiny.full_id}" cannot be assigned.'
                ),
                assignment_node.destiny.line_number,
            )

        if bus_symbol.is_assigned:
            # Destiny signal cannot be assigned more than once in this version
            raise SemanticalError(
                f'Identifier "{assignment_node.destiny.full_id}" already assigned.',
                assignment_node.destiny.line_number,
            )

        assignment, size = self.vst_expr(
            assignment_node.expr, component_id, component_dto
        )

        if size != bus_symbol.size:
            raise SemanticalError(
                (
                    f"Assignment size ({size}) does not match target bus range ("
                    f'{bus_symbol.size}") for "{assignment_node.destiny.full_id}".'
                ),
                assignment_node.destiny.line_number,
            )

        # Mark the bus as assigned in the symbol table
        bus_symbol.is_assigned = True
        bus = (
            self.symbol_table.component_symbols[component_id]
            .bus_symbols[assignment_node.destiny.full_id]
            .object_
        )
        assert bus is not None, (
            f'Bus object for "{assignment_node.destiny.full_id}" cannot be None.'
        )
        # Update bus object
        bus.assignment = assignment

    # Just a wrapper for a better name than call vst_expr_elem() directly
    def vst_expr(
        self,
        expression_node: ast_nodes.ExpressionElement,
        component_id: str,  # TODO remove component_id
        component_dto: ComponentDto,
    ) -> Tuple[expression_nodes.ExpressionNode, int]:
        expression, size = self.vst_expr_elem(
            expression_node, component_id, component_dto
        )

        return expression, size

    def vst_expr_elem(
        self,
        expression_element_node: ast_nodes.ExpressionElement,
        component_id: str,  # TODO remove component_id
        component_dto: ComponentDto,
    ) -> Tuple[expression_nodes.ExpressionNode, int]:
        """
        Visit an expression element, validate it, and return a callable for evaluation.
        """

        if isinstance(expression_element_node, ast_nodes.Reference):
            ref = expression_element_node  # Change name for better readability

            assert (ref_id := ref.id_.full_id) in self.symbol_table.component_symbols[
                component_id
            ].bus_symbols.keys(), f'Bus reference "{ref_id}" has not been declared.'

            bus_symbol = self.symbol_table.component_symbols[component_id].bus_symbols[
                expression_element_node.id_.full_id
            ]

            # Validate subcomponents busses references
            if (bus_symbol.is_lower_lvl is True) and (
                bus_symbol.connection_type != ast_nodes.Connection.OUTPUT
            ):
                raise SemanticalError(
                    (
                        f'Input/Internal busses like "{ref_id}" of a subcomponent '
                        f"cannot be referenced from the higher level component."
                    ),
                    ref.id_.line_number,
                )

            # Validate range
            if ref.range_begin:  # TODO verify logic
                if ref.range_begin >= (size := bus_symbol.size):
                    raise SemanticalError(
                        f'Index [{ref.range_begin}:] out of bounds for "{ref_id}".',
                        ref.id_.line_number,
                    )

                if ref.range_end:
                    if ref.range_end >= size:
                        raise SemanticalError(
                            f'Index [:{ref.range_end}] out of bounds for "{ref_id}".',
                            ref.id_.line_number,
                        )

                    if bus_symbol.msb_descending:
                        if ref.range_begin < ref.range_end:
                            raise SemanticalError(
                                (
                                    f'Invalid range [:{ref.range_end}] for "{ref_id}". '
                                    "For descending buses, begin index must be equal or"
                                    " greater than the end index."
                                ),
                                ref.id_.line_number,
                            )
                    else:
                        if ref.range_begin > ref.range_end:
                            raise SemanticalError(
                                (
                                    f'Invalid range [:{ref.range_end}] for "{ref_id}". '
                                    "The end index must be equal or greater than to the"
                                    " begin index."
                                ),
                                ref.id_.line_number,
                            )

                    range_begin = ref.range_begin
                    range_end = ref.range_end
                else:
                    range_begin = ref.range_begin
                    range_end = range_begin

                slice_begin = range_begin
                slice_end = range_end
                slice_size = (abs(range_end - range_begin)) + 1
            else:
                slice_begin = None
                slice_end = None
                slice_size = bus_symbol.size

            bus_symbol.is_read = True

            bus = bus_symbol.object_
            assert bus is not None, f'Bus object for "{ref_id}" cannot be None.'

            bus_ref = expression_nodes.Ref(
                bus,
                slice_begin,
                slice_end,
            )

            return bus_ref, slice_size
        elif isinstance(expression_element_node, ast_nodes.BitField):
            bit_field = expression_element_node
            const = expression_nodes.Const(bit_field.value)

            return const, bit_field.size  # TODO check size
        elif isinstance(expression_element_node, ast_nodes.NotOp):
            expr, size = self.vst_expr_elem(
                expression_element_node.expr, component_id, component_dto
            )

            return expression_nodes.Not(expr), size
        elif isinstance(expression_element_node, ast_nodes.Concatenation):
            conc = expression_element_node
            exprs: list[expression_nodes.ExpressionNode] = []
            total_size = 0

            for sub_expr in conc.expressions:
                expr, size = self.vst_expr_elem(sub_expr, component_id, component_dto)
                exprs.append(expr)
                total_size += size

            return expression_nodes.Conc(exprs), total_size
        elif isinstance(expression_element_node, ast_nodes.BinaryOp):
            op_node: type[expression_nodes.BinaryOperation]
            match expression_element_node:
                case ast_nodes.AndOp():
                    op_node = expression_nodes.And
                case ast_nodes.OrOp():
                    op_node = expression_nodes.Or
                case ast_nodes.XorOp():
                    op_node = expression_nodes.Xor
                case ast_nodes.NandOp():
                    op_node = expression_nodes.Nand
                case ast_nodes.NorOp():
                    op_node = expression_nodes.Nor
                case ast_nodes.XnorOp():
                    op_node = expression_nodes.Xnor
                case _:
                    assert False, (
                        f"Unhandled binary operation: {expression_element_node}"
                    )

            assert expression_element_node.l_expr is not None, (
                "Left expression of operation cannot be None."
            )
            assert expression_element_node.r_expr is not None, (
                "Right expression of operation cannot be None."
            )
            l_expr, l_size = self.vst_expr_elem(
                expression_element_node.l_expr, component_id, component_dto
            )
            r_expr, r_size = self.vst_expr_elem(
                expression_element_node.r_expr, component_id, component_dto
            )

            if l_size != r_size:
                raise SemanticalError(
                    (
                        f"Left ({l_expr}) and right ({r_expr}) expressions of operation"
                        " must be the same size."
                    ),
                    expression_element_node.line_number,
                )

            return op_node(l_expr, r_expr), l_size
        else:
            assert False, f"Invalid expression element: {expression_element_node}"

    def vst_inst(
        self,
        inst: ast_nodes.Instance,
        component_dto: ComponentDto,
        component_symbol: ComponentSymbol,
    ) -> None:
        # Check if the subcomponent was already processed
        if inst.identifier not in self.components:
            assert inst.identifier in self.components_nodes, (
                f'Component "{inst.identifier}" not found.'
            )

            self.components[inst.identifier] = self.vst_comp(
                self.components_nodes[inst.identifier]
            )

        subcomponent_dto, bottom_buses_symbols = deepcopy(
            (
                self.components[inst.identifier],
                self.symbol_table.component_symbols[inst.identifier].bus_symbols,
            )
        )

        for bus_symbol in bottom_buses_symbols.values():
            bus_symbol.is_lower_lvl = True

        # Add the subcomponent's buses to the top component's symbol table
        alias = inst.identifier if inst.alias is None else inst.alias
        component_symbol.bus_symbols |= {
            f"{alias}.{bus_id}": bus_symbol
            for bus_id, bus_symbol in bottom_buses_symbols.items()
        }

        component_dto.add_subcomponent(subcomponent_dto, alias)  # TODO verify logic
