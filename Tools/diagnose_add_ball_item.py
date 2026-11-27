import unreal


def log(message):
    unreal.log(f"ITEM_DIAG {message}")


def dump_graphs(asset_path, wanted=None):
    bp = unreal.load_asset(asset_path)
    log(f"ASSET {asset_path} STATUS={bp.status}")
    for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
        log(f"GRAPH_NAME {asset_path} {graph.get_name()}")
        if wanted and graph.get_name() not in wanted:
            continue
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        log(f"GRAPH {asset_path} {graph.get_name()}")
        for node in editor.list_all_nodes():
            log(
                f"NODE CLASS={node.get_class().get_name()} TITLE={node.get_node_title()} "
                f"POS={node.get_node_pos()}"
            )
            for pin in node.list_all_pins():
                linked = list(pin.list_connected_pins())
                linked_desc = ",".join(
                    f"{p.get_pin_name()}:{p.get_pin_type_display_string()}" for p in linked
                )
                log(
                    f"PIN NODE={node.get_node_title()} NAME={pin.get_pin_name()} "
                    f"DIR={pin.get_pin_direction()} TYPE={pin.get_pin_type_display_string()} "
                    f"VALUE={pin.get_pin_value()} LINKS=[{linked_desc}]"
                )


def dump_actor(actor, label):
    log(
        f"ACTOR {label} NAME={actor.get_name()} CLASS={actor.get_class().get_name()} "
        f"LOCATION={actor.get_actor_location()} SCALE={actor.get_actor_scale3d()}"
    )
    for component in actor.get_components_by_class(unreal.PrimitiveComponent):
        parts = [f"COMP={component.get_name()}", f"CLASS={component.get_class().get_name()}"]
        try:
            parts.append(f"component_tags={list(component.get_editor_property('component_tags'))}")
        except Exception as exc:
            parts.append(f"component_tags=ERROR({exc})")
        for prop in ("collision_profile_name", "collision_enabled", "generate_overlap_events", "simulate_physics"):
            try:
                parts.append(f"{prop}={component.get_editor_property(prop)}")
            except Exception as exc:
                parts.append(f"{prop}=ERROR({exc})")
        for channel_name in ("ECC_PAWN", "ECC_WORLD_DYNAMIC", "ECC_PHYSICS_BODY"):
            try:
                channel = getattr(unreal.CollisionChannel, channel_name)
                parts.append(f"{channel_name}={component.get_collision_response_to_channel(channel)}")
            except Exception as exc:
                parts.append(f"{channel_name}=ERROR({exc})")
        log(" ".join(parts))


dump_graphs("/Game/AddBallItem")
dump_graphs("/Game/GameManager", {"GenerateBall", "AddBall", "EventGraph"})
dump_graphs("/Game/Paddle", {"EventGraph"})

for asset_path in ("/Game/AddBallItem", "/Game/Paddle", "/Game/Ball"):
    bp = unreal.load_asset(asset_path)
    cdo = unreal.get_default_object(bp.generated_class())
    dump_actor(cdo, f"CDO {asset_path}")

unreal.EditorLevelLibrary.load_level("/Game/Level1")
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    class_name = actor.get_class().get_name()
    if class_name in ("AddBallItem_C", "Paddle_C", "GameManager_C", "Ball_C"):
        dump_actor(actor, "LEVEL1")
