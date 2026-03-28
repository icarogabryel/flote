from copy import deepcopy
from json import dumps
from typing import Optional, Tuple
from warnings import warn

from flote.elaboration import ast_nodes
from flote.elaboration.ir import expr_nodes
from flote.elaboration.ir.buses import BitBusDto
from flote.elaboration.ir.component import ComponentDto
from flote.elaboration.symbol_table import BusSymbol, ComponentTable, SymbolTable


class SemanticalError(Exception):
    def __init__(self, message: str, line_number: Optional[int] = None):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return (
            f"Semantical error at line {self.line_number}: {self.message}"
            if self.line_number is not None
            else f"Semantical error: {self.message}"
        )


class Builder:
    """Class that builds the component from the AST."""

    def __init__(
        self,
        ast,
    ) -> None:
        self.ast: ast_nodes.Module = ast
        self.symbol_table: SymbolTable = SymbolTable()
        self.components: dict[str, ComponentDto] = {}
        self.comp_nodes: dict[str, ast_nodes.Component] = {}

        self.netlist: str = self.get_netlist()

    def get_netlist(self) -> str:
        component = self.vst_mod(self.ast)
        component.make_netlist()

        return dumps(component.to_json())

    def init_component_table(
        self, comp: ast_nodes.Component, component: ComponentDto
    ) -> ComponentTable:
        """Get the component's bus symbol table."""
        comp_table: ComponentTable = ComponentTable()

        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Declaration):
                decl = stmt  # Name change for better readability
                is_assigned = False
                size = 1

                assert decl.id_ is not None, "Declaration id cannot be None."
                if decl.id_.full_id in comp_table.bus_symbols.keys():
                    raise SemanticalError(
                        f'Bus "{decl.id_}" has already been declared.', decl.line_number
                    )

                if decl.assignment_expression is not None:
                    if decl.conn == ast_nodes.Connection.INPUT:
                        raise SemanticalError(
                            f"Input Buses like {decl.id_} cannot be assigned.",
                            decl.line_number,
                        )

                    # Mark the bus as assigned in the symbol table
                    is_assigned = True

                bit_bus = BitBusDto()
                bit_bus.id_ = decl.id_.full_id

                msb_descending = False
                if decl.dimension:
                    size = decl.dimension.size
                    msb_descending = decl.dimension.msb == ast_nodes.Msb.DESCENDING
                    bit_bus.set_dimension(decl.dimension.size)

                bit_bus.msb_descending = msb_descending

                comp_table.bus_symbols[decl.id_.full_id] = BusSymbol(
                    decl.type,
                    is_assigned,
                    decl.conn,
                    size,
                    bit_bus,
                    msb_descending,
                )
            elif isinstance(stmt, ast_nodes.Instance):
                assert comp.id_ is not None, "Instance component cannot be None."
                self.vst_inst(stmt, comp.id_.value, component, comp_table)

        return comp_table

    def validate_bus_symbol_table(self):
        """Validate the bus symbol table to ensure all buses are assigned and read."""
        for bus_table in self.symbol_table.components.values():
            for bus_id, bus in bus_table.bus_symbols.items():
                if (bus.connection_type != ast_nodes.Connection.INPUT) and (
                    not bus.is_assigned
                ):
                    warn(f'Bus "{bus_id}" has not been assigned.', UserWarning)

                if (bus.connection_type != ast_nodes.Connection.OUTPUT) and (
                    not bus.is_read
                ):
                    warn(f'Bus "{bus_id}" is never read', UserWarning)

    def vst_mod(self, mod: ast_nodes.Module) -> ComponentDto:
        if not mod.comps:
            raise SemanticalError("Module is empty.")

        # Fill the comp_nodes dictionary
        for comp in mod.comps:
            assert comp.id_ is not None, "Component id cannot be None."
            self.comp_nodes[comp.id_.value] = comp

        if len(mod.comps) == 1:
            component = self.vst_comp(mod.comps[0])

            assert mod.comps[0].id_ is not None, "Component id cannot be None."
            self.components[mod.comps[0].id_.value] = component

            return component
        else:  # If there are multiple components, its assumed one of them is the main
            is_main_comp_found = False
            main_component: Optional[ComponentDto] = None

            for comp in mod.comps:  # Search for the main component
                if comp.id_ in self.components:
                    # Skip if component already processed in a previous instantiation
                    continue
                # Add component to the components dict
                component = self.vst_comp(comp)
                assert comp.id_ is not None, "Component id cannot be None."
                self.components[comp.id_.value] = component

                if comp.is_main:
                    if is_main_comp_found:
                        raise SemanticalError(
                            (
                                f"{comp.id_.full_id} can't be main. Only one main "
                                "component is allowed."
                            ),
                            comp.line_number,
                        )

                    is_main_comp_found = True
                    main_component = component

            if not is_main_comp_found:
                raise SemanticalError(
                    "Main component not found in a multiple component module."
                )

        assert main_component is not None, "Main component should not be None."

        self.validate_bus_symbol_table()

        return main_component

    def vst_comp(self, comp: ast_nodes.Component) -> ComponentDto:
        if comp.id_ in self.symbol_table.components.keys():
            raise SemanticalError(
                f'Component "{comp.id_}" has already been declared.', comp.line_number
            )

        component_id = comp.id_
        assert component_id is not None, "Component id cannot be None."

        component = ComponentDto(component_id.value)
        self.symbol_table.components[component_id.value] = self.init_component_table(
            comp, component
        )
        self.symbol_table.components[component_id.value].object = component
        for stmt in comp.stmts:
            if isinstance(stmt, ast_nodes.Declaration):
                self.vst_decl(stmt, component_id.value, component)
            elif isinstance(stmt, ast_nodes.Assignment):
                self.vst_assign(stmt, component_id.value, component)
            elif isinstance(stmt, ast_nodes.Instance):
                pass
            else:
                assert False, f"Invalid statement: {stmt}"

        return component

    def vst_decl(
        self, decl: ast_nodes.Declaration, component_id: str, component: ComponentDto
    ) -> None:
        assert decl.id_ is not None, "Declaration id cannot be None."
        assert (
            decl.id_.full_id
            in self.symbol_table.components[component_id].bus_symbols.keys()
        ), f'Bus "{decl.id_}" has not been declared.'

        bus_symbol = self.symbol_table.components[component_id].bus_symbols[
            decl.id_.full_id
        ]

        if decl.assignment_expression:
            # Create the bus assignment
            assignment, size = self.vst_expr(
                decl.assignment_expression, component_id, component
            )
            bus_symbol.object.assignment = assignment

            if size != bus_symbol.size:
                raise SemanticalError(
                    (
                        f"Assignment size ({size}) does not match bus size "
                        f'({bus_symbol.size}) for "{decl.id_.full_id}".'
                    ),
                    decl.line_number,
                )

        component.busses.append(bus_symbol.object)

    def vst_assign(
        self, assign: ast_nodes.Assignment, component_id: str, component: ComponentDto
    ) -> None:
        if (
            assign.destiny.full_id
            not in self.symbol_table.components[component_id].bus_symbols.keys()
        ):
            raise SemanticalError(
                f'Identifier "{assign.destiny.full_id}" has not been declared.',
                assign.destiny.line_number,
            )

        bus_symbol = self.symbol_table.components[component_id].bus_symbols[
            assign.destiny.full_id
        ]
        if (bus_symbol.connection_type == ast_nodes.Connection.INPUT) and (
            not bus_symbol.is_lower_lvl
        ):
            raise SemanticalError(
                (
                    f'Input Buses of top level like "{assign.destiny.full_id}" cannot '
                    "be assigned."
                ),
                assign.destiny.line_number,
            )

        if (bus_symbol.connection_type != ast_nodes.Connection.INPUT) and (
            bus_symbol.is_lower_lvl is True
        ):
            raise SemanticalError(
                (
                    f"Internal/out Buses of subcomponents like "
                    f'"{assign.destiny.full_id}" cannot be assigned.'
                ),
                assign.destiny.line_number,
            )

        if bus_symbol.is_assigned is True:
            # Destiny signal cannot be assigned more than once
            raise SemanticalError(
                f'Identifier "{assign.destiny.full_id}" already assigned.',
                assign.destiny.line_number,
            )

        # Mark the bus as assigned in the symbol table
        bus_symbol.is_assigned = True

        assignment, size = self.vst_expr(assign.expr, component_id, component)

        if size != bus_symbol.size:
            raise SemanticalError(
                (
                    f"Assignment size ({size}) does not match target bus range ("
                    f'{bus_symbol.size}") for "{assign.destiny.full_id}".'
                ),
                assign.destiny.line_number,
            )

        bus = (
            self.symbol_table.components[component_id]
            .bus_symbols[assign.destiny.full_id]
            .object
        )
        assert (
            bus is not None
        ), f'Bus object for "{assign.destiny.full_id}" cannot be None.'
        bus.assignment = assignment

    def vst_expr(
        self, expr, component_id: str, component: ComponentDto
    ) -> Tuple[expr_nodes.ExprNode, int]:
        assignment = self.vst_expr_elem(expr, component_id, component)

        return assignment

    def vst_expr_elem(
        self, expr_elem: ast_nodes.ExprElem, component_id: str, component: ComponentDto
    ) -> Tuple[expr_nodes.ExprNode, int]:
        """
        Visit an expression element, validate it, and return a callable for evaluation.
        """
        if expr_elem is None:
            raise SemanticalError("Expression element cannot be None.")

        if isinstance(expr_elem, ast_nodes.Reference):
            ref = expr_elem

            if (ref_id := ref.id_.full_id) not in self.symbol_table.components[
                component_id
            ].bus_symbols.keys():
                raise SemanticalError(
                    f'Bus reference "{ref_id}" has not been declared.',
                    ref.id_.line_number,
                )

            bus_symbol = self.symbol_table.components[component_id].bus_symbols[
                expr_elem.id_.full_id
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
            if ref.range_begin is not None:
                if ref.range_begin >= (size := bus_symbol.size):
                    raise SemanticalError(
                        f'Index [{ref.range_begin}:] out of bounds for "{ref_id}".',
                        ref.id_.line_number,
                    )

                if ref.range_end is not None:
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

            bus = (
                self.symbol_table.components[component_id]
                .bus_symbols[expr_elem.id_.full_id]
                .object
            )
            assert bus is not None, f'Bus object for "{ref_id}" cannot be None.'

            bus_ref = expr_nodes.Ref(
                bus,
                slice_begin,
                slice_end,
            )

            return bus_ref, slice_size
        elif isinstance(expr_elem, ast_nodes.BitField):
            bit_field = expr_elem
            const = expr_nodes.Const(bit_field.value)

            return const, bit_field.size
        elif isinstance(expr_elem, ast_nodes.NotOp):
            assert expr_elem.expr is not None, "Expression cannot be None."

            expr, size = self.vst_expr_elem(expr_elem.expr, component_id, component)

            return expr_nodes.Not(expr), size
        elif isinstance(expr_elem, ast_nodes.Concatenation):
            conc = expr_elem
            exprs: list[expr_nodes.ExprNode] = []
            total_size = 0

            for sub_expr in conc.exprs:
                expr, size = self.vst_expr_elem(sub_expr, component_id, component)
                exprs.append(expr)
                total_size += size

            return expr_nodes.Conc(exprs), total_size
        elif isinstance(expr_elem, ast_nodes.BinaryOp):
            match expr_elem:
                case ast_nodes.AndOp():
                    op_node = expr_nodes.And
                case ast_nodes.OrOp():
                    op_node = expr_nodes.Or
                case ast_nodes.XorOp():
                    op_node = expr_nodes.Xor
                case ast_nodes.NandOp():
                    op_node = expr_nodes.Nand
                case ast_nodes.NorOp():
                    op_node = expr_nodes.Nor
                case ast_nodes.XnorOp():
                    op_node = expr_nodes.Xnor
                case _:
                    assert False, f"Unhandled binary operation: {expr_elem}"

            assert (
                expr_elem.l_expr is not None
            ), "Left expression of operation cannot be None."
            assert (
                expr_elem.r_expr is not None
            ), "Right expression of operation cannot be None."
            l_expr, l_size = self.vst_expr_elem(
                expr_elem.l_expr, component_id, component
            )
            r_expr, r_size = self.vst_expr_elem(
                expr_elem.r_expr, component_id, component
            )

            if l_size != r_size:
                raise SemanticalError(
                    (
                        f"Left ({l_expr}) and right ({r_expr}) expressions of operation"
                        " must be the same size."
                    ),
                    expr_elem.line_number,
                )

            return op_node(l_expr, r_expr), l_size
        else:
            assert False, f"Invalid expression element: {expr_elem}"

    def vst_inst(
        self,
        inst: ast_nodes.Instance,
        component_id: str,
        component: ComponentDto,
        comp_table: ComponentTable,
    ) -> None:
        assert inst.comp_id is not None, "Instance component cannot be None."

        # Check if the subcomponent was already processed
        if inst.comp_id not in self.components.keys():
            try:
                self.components[inst.comp_id] = self.vst_comp(
                    self.comp_nodes[inst.comp_id]
                )
            except KeyError:
                raise SemanticalError(
                    f"Component '{inst.comp_id}' not found.", inst.line_number
                )

        alias = inst.comp_id if inst.sub_alias is None else inst.sub_alias
        subcomponent = deepcopy(self.components[inst.comp_id])

        bottom_busses = deepcopy(self.symbol_table.components[inst.comp_id].bus_symbols)

        for bus in bottom_busses.values():
            bus.is_lower_lvl = True

        # Add the subcomponent's buses to the top component's symbol table
        comp_table.bus_symbols |= {
            f"{alias}.{bus_id}": bus for bus_id, bus in bottom_busses.items()
        }

        # Link the new subcomponent's bus objects to the top component's symbol table
        # because deepcopy still makes references to the old objects.
        for bus in subcomponent.busses:
            comp_table.bus_symbols[f"{alias}.{bus.id_}"].object = bus

        component.add_subcomponent(subcomponent, alias)
