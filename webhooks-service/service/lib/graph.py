"""
Visualizes the status mappings.
"""
import graphviz


def _node_key(status_type, status_key):
    return f"{status_type}.{status_key}"


def render_mappings(status_mapping):
    g = graphviz.Digraph("status-mappings", format="png")
    g.attr("node", shape="box")
    g.attr("graph", rankdir="LR")

    with g.subgraph(name="cluster_shots") as c:
        c.attr(style="filled", color="lightgrey", label="Shot Statuses")
        for shot_status in status_mapping.shot_statuses:
            c.node(_node_key("shot", shot_status.key), shot_status.label)

            task_statuses = status_mapping.map_shot_status(shot_status.key)
            for i, task_status in enumerate(task_statuses):
                g.edge(
                    _node_key("shot", shot_status.key),
                    _node_key("task", task_status),
                    style="dashed" if i > 0 else "solid",
                )

    with g.subgraph(name="cluster_tasks") as c:
        c.attr(style="filled", color="lightgrey", label="Task Statuses")
        for task_status in status_mapping.task_statuses:
            c.node(_node_key("task", task_status.key), task_status.label)

            shot_statuses = status_mapping.map_task_status(task_status.key)
            for i, shot_status in enumerate(shot_statuses):
                g.edge(
                    _node_key("task", task_status.key),
                    _node_key("shot", shot_status),
                    style="dashed" if i > 0 else "solid",
                )

    g.render()


if __name__ == "__main__":
    from .config import load_status_mapping

    render_mappings(load_status_mapping())
