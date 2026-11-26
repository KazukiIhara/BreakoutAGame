import unreal


def log(message):
    unreal.log(f"PADDLE_DIAG {message}")


bp = unreal.load_asset("/Game/Paddle")
log(f"STATUS {bp.status}")

logged_pin_api = False
for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
    if graph.get_name() not in (
        "EventGraph",
        "UserConstructionScript",
        "DrawDebugTopSurfaceNormals",
        "DrawDebugArrow",
        "GetTopNormal",
    ):
        continue
    editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
    log(f"GRAPH {graph.get_name()}")
    if graph.get_name() in ("DrawDebugArrow", "DrawDebugTopSurfaceNormals"):
        log(f"LOCAL_API {[name for name in dir(editor) if 'local' in name.lower() or 'default' in name.lower()]}")
        for method_name in ("list_local_variable_names", "list_local_variables"):
            method = getattr(editor, method_name, None)
            if method:
                try:
                    log(f"{method_name}={method()}")
                except Exception as exc:
                    log(f"{method_name}_ERROR={exc}")
        try:
            for local_name in editor.list_local_variable_names():
                log(
                    f"LOCAL_DEFAULT {graph.get_name()}.{local_name}="
                    f"{editor.get_local_variable_default_value(local_name)}"
                )
        except Exception as exc:
            log(f"LOCAL_DEFAULT_ERROR={exc}")
    node_pins = []
    for node in editor.list_all_nodes():
        log(
            f"NODE CLASS={node.get_class().get_name()} TITLE={node.get_node_title()} "
            f"POS={node.get_node_pos()}"
        )
        for pin in node.list_all_pins():
            node_pins.append((node, pin))
            if not logged_pin_api:
                log(f"PIN_API {[name for name in dir(pin) if 'link' in name.lower() or 'connect' in name.lower()]}")
                log(f"PIN_LIB_API {[name for name in dir(unreal.BlueprintGraphPinLibrary) if 'link' in name.lower() or 'connect' in name.lower()]}")
                logged_pin_api = True
            log(
                f"PIN NODE={node.get_node_title()} NAME={pin.get_pin_name()} "
                f"DIR={pin.get_pin_direction()} TYPE={pin.get_pin_type_display_string()} "
                f"VALUE={pin.get_pin_value()}"
            )
    for node, pin in node_pins:
        for linked in pin.list_connected_pins():
            linked_node = None
            for candidate_node, candidate_pin in node_pins:
                if candidate_pin == linked:
                    linked_node = candidate_node
                    break
            log(
                f"LINK {node.get_node_title()}.{pin.get_pin_name()} -> "
                f"{linked_node.get_node_title() if linked_node else '?'}"
                f".{linked.get_pin_name()}"
            )

cdo = unreal.get_default_object(bp.generated_class())
log(f"CDO TRANSFORM LOCATION={cdo.get_actor_location()} ROTATION={cdo.get_actor_rotation()} SCALE={cdo.get_actor_scale3d()}")
for variable_name in unreal.BlueprintEditorLibrary.list_member_variable_names(bp, False):
    try:
        value = cdo.get_editor_property(str(variable_name))
        log(f"DEFAULT {variable_name}={value}")
    except Exception:
        pass
for component in cdo.get_components_by_class(unreal.SceneComponent):
    log(
        f"COMP NAME={component.get_name()} CLASS={component.get_class().get_name()} "
        f"REL_LOCATION={component.get_editor_property('relative_location')} "
        f"REL_ROTATION={component.get_editor_property('relative_rotation')} "
        f"REL_SCALE={component.get_editor_property('relative_scale3d')}"
    )
