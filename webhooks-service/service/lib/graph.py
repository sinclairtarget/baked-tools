"""
Visualizes the status mappings.
"""
import graphviz


def _node_key(status_type, status_key):
    return f"{status_type}.{status_key}"


def _get_statuses(status_mapping, status_type):
    if status_type == "shot":
        return status_mapping.shot_statuses
    elif status_type == "task":
        return status_mapping.task_statuses
    elif status_type == "version":
        return status_mapping.version_statuses
    else:
        raise NotImplementedError(f"Unknown status type: {status_type}.")


def _get_map_func(status_mapping, source_status_type, target_status_type):
    if source_status_type == "shot" and target_status_type == "task":
        return status_mapping.map_shot_status
    elif source_status_type == "task" and target_status_type == "shot":
        return status_mapping.map_task_status
    elif source_status_type == "version" and target_status_type == "task":
        return status_mapping.map_version_status
    else:
        raise NotImplementedError(
            f"Cannot map {source_status_type} to {target_status_type}."
        )


def render_mapping(status_mapping, source_status_type, target_status_type):
    source_statuses = _get_statuses(status_mapping, source_status_type)
    target_statuses = _get_statuses(status_mapping, target_status_type)
    map_func = _get_map_func(status_mapping, source_status_type, target_status_type)

    g = graphviz.Digraph(
        f"{source_status_type}-{target_status_type}-map",
        format="png",
    )
    g.attr("node", shape="box")
    g.attr("graph", rankdir="LR")

    with g.subgraph(name="cluster_source") as c:
        c.attr(style="filled", color="lightgrey")
        for status in source_statuses:
            c.node(_node_key(source_status_type, status.key), status.label)

            mapped_statuses = map_func(status.key)
            for i, mapped_status in enumerate(mapped_statuses):
                g.edge(
                    _node_key(source_status_type, status.key),
                    _node_key(target_status_type, mapped_status),
                    style="dashed" if i > 0 else "solid",
                )

    with g.subgraph(name="cluster_target") as c:
        c.attr(style="filled", color="lightgrey", label="Task Statuses")
        for status in target_statuses:
            c.node(_node_key(target_status_type, status.key), status.label)

    g.render()


if __name__ == "__main__":
    from .config import load_status_mapping

    m = load_status_mapping()
    render_mapping(m, "shot", "task")
    render_mapping(m, "task", "shot")
    render_mapping(m, "version", "task")
