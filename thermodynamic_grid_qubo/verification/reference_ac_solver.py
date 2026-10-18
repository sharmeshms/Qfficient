"""Independent AC power flow reference solver for radial distribution networks.

Uses an independent iterative Backward/Forward Sweep (BFS) algorithm to solve
exact AC power flow without linear approximations, providing ground-truth
validation for LinDistFlow and AC DistFlow implementations.
"""
from typing import Dict, Tuple, Optional, Sequence
import numpy as np
import networkx as nx
from thermodynamic_grid_qubo.grid_engine.ieee_feeder_loader import DistributionGrid


def reference_ac_power_flow(
    grid: DistributionGrid,
    injections: Dict[int, Tuple[float, float]],
    active_edges: Optional[Sequence[int]] = None,
    resistances_ohm: Optional[np.ndarray] = None,
    v_slack_pu: float = 1.00,
    max_iter: int = 50,
    tol: float = 1e-8,
) -> Tuple[bool, Dict[int, float], Dict[int, float], float, float]:
    """Independent reference AC power flow solver for balanced radial distribution networks.
    
    Returns:
        converged: bool
        voltages_pu: Dict[bus_id -> voltage magnitude in pu]
        currents_a: Dict[edge_id -> current magnitude in Amperes]
        total_loss_kw: float (active power loss in kW)
        v_min_pu: float (minimum voltage magnitude in pu)
    """
    buses = sorted(grid.graph.nodes)
    sub = grid.substations[0]
    all_lines = grid.lines
    edge_ids = sorted(all_lines.keys())

    if active_edges is None:
        active_edges = [e for e in edge_ids if not grid.graph[all_lines[e].u][all_lines[e].v].get("is_tie", False)]

    # Check radial tree
    if len(active_edges) != len(buses) - 1:
        return False, {}, {}, 1e9, 0.0

    g = nx.Graph()
    g.add_nodes_from(buses)
    for e in active_edges:
        line = all_lines[e]
        g.add_edge(line.u, line.v, edge_id=e)

    if not nx.is_connected(g):
        return False, {}, {}, 1e9, 0.0

    tree = nx.bfs_tree(g, source=sub)
    order = list(nx.topological_sort(tree))
    parent = {}
    parent_edge = {}
    for u in order:
        if u != sub:
            p = list(tree.predecessors(u))[0]
            parent[u] = p
            parent_edge[u] = g[p][u]["edge_id"]

    s_base_va = grid.s_base_mva * 1e6
    z_base = grid.z_base_ohm
    v_base_v = grid.v_base_kv * 1e3
    v_base_ln = v_base_v / np.sqrt(3.0)

    # Injections: P_inj_kw, Q_inj_kvar. Net load is -injection
    p_load_pu = {b: -injections.get(b, (0.0, 0.0))[0] * 1e3 / s_base_va for b in buses}
    q_load_pu = {b: -injections.get(b, (0.0, 0.0))[1] * 1e3 / s_base_va for b in buses}

    if resistances_ohm is None:
        r_pu = {e: all_lines[e].r0 / z_base for e in edge_ids}
    else:
        r_pu = {e: resistances_ohm[i] / z_base for i, e in enumerate(edge_ids)}
    x_pu = {e: all_lines[e].x0 / z_base for e in edge_ids}

    # Complex bus voltages (slack is 1.0 + 0j)
    V = {b: complex(v_slack_pu, 0.0) for b in buses}
    I_branch = {e: 0.0 + 0.0j for e in edge_ids}

    converged = False
    for it in range(max_iter):
        V_old = V.copy()

        # 1. Backward sweep: compute branch currents from bus load currents
        # Bus load current I_inj = (S_load / V)^*
        I_bus = {}
        for b in buses:
            s_complex_pu = complex(p_load_pu[b], q_load_pu[b])
            I_bus[b] = np.conj(s_complex_pu / V[b])

        # Sum currents from leaves to root
        I_branch_flow = {}
        for u in reversed(order):
            if u != sub:
                e = parent_edge[u]
                # Branch current into bus u = bus load current + sum of downstream branch currents
                i_downstream = I_bus[u]
                for child in tree.successors(u):
                    e_child = parent_edge[child]
                    i_downstream += I_branch_flow[e_child]
                I_branch_flow[e] = i_downstream

        # 2. Forward sweep: compute bus voltages from root to leaves
        # V_j = V_i - I_{ij} * Z_{ij}
        for u in order:
            if u != sub:
                p = parent[u]
                e = parent_edge[u]
                z_branch = complex(r_pu[e], x_pu[e])
                V[u] = V[p] - I_branch_flow[e] * z_branch

        # Check convergence on voltage magnitudes
        max_diff = max(abs(abs(V[b]) - abs(V_old[b])) for b in buses)
        if max_diff < tol:
            converged = True
            for e, cur in I_branch_flow.items():
                I_branch[e] = cur
            break

    # Calculate outputs
    v_pu_dict = {b: float(abs(V[b])) for b in buses}
    i_base_a = s_base_va / (np.sqrt(3.0) * v_base_v)
    i_a_dict = {e: float(abs(I_branch[e])) * i_base_a for e in edge_ids}

    # 3-phase real power loss: 3 * sum(|I_branch|^2 * R_ohm) in kW
    total_loss_kw = sum(3.0 * (i_a_dict[e] ** 2) * (r_pu[e] * z_base) / 1e3 for e in active_edges)
    v_min_pu = min(v_pu_dict.values())

    return converged, v_pu_dict, i_a_dict, float(total_loss_kw), float(v_min_pu)
