"""Reconfiguration policies for benchmark and ablation evaluation."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple, Any
import time
import numpy as np

from ..grid_engine.ieee_feeder_loader import DistributionGrid
from ..verification.fast_flow import FastFeeder
from ..qubo_engine.qubo_builder import ThermodynamicQUBOBuilder, QUBOModel
from ..qubo_engine.entropy_calculator import mesh_branch_currents, EntropyCalculator
from ..solvers.numpy_annealer import NumpyAnnealer


@dataclass
class DecisionContext:
    grid: DistributionGrid
    fast: FastFeeder
    injections: Dict[int, Tuple[float, float]]
    temps_k: np.ndarray
    prev_active: Tuple[int, ...]
    step: int
    p_pu: np.ndarray
    q_pu: np.ndarray
    resistances: np.ndarray


class Policy:
    name: str = "base_policy"

    def reset(self, grid: DistributionGrid, fast: FastFeeder, timeline: List[Dict[int, Tuple[float, float]]]):
        pass

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        """Returns (active_edges_tuple, decision_latency_ms)."""
        raise NotImplementedError


class StandardStaticPolicy(Policy):
    """Textbook IEEE 33-bus baseline: branches 0..31 closed, 5 tie lines open (no reconfiguration)."""
    name = "standard_static"

    def reset(self, grid, fast, timeline):
        self.standard = tuple(range(fast.n - 1))

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        active = self.standard
        latency_ms = (time.perf_counter() - t0) * 1e3
        return active, latency_ms


class StaticLossOptimalPolicy(Policy):
    """Optimal single static topology: the best single tree chosen offline under mean load."""
    name = "static_loss_optimal"

    def __init__(self, candidate_trees: Optional[List[Tuple[int, ...]]] = None):
        self.candidate_trees = candidate_trees
        self.best_tree: Optional[Tuple[int, ...]] = None

    def reset(self, grid, fast, timeline):
        if self.best_tree is not None:
            return
        trees = self.candidate_trees or fast.enumerate_radial_configs()
        # Compute mean loads
        mean_inj = {}
        for b in grid.graph.nodes:
            p_mean = float(np.mean([inj.get(b, (0.0, 0.0))[0] for inj in timeline]))
            q_mean = float(np.mean([inj.get(b, (0.0, 0.0))[1] for inj in timeline]))
            mean_inj[b] = (p_mean, q_mean)

        p_pu, q_pu = fast.vectors(mean_inj)
        r0 = fast.resistances()

        best_loss = 1e12
        best_t = tuple(range(fast.n - 1))
        for t in trees:
            ok, _, _, loss_kw, _ = fast.evaluate(t, p_pu, q_pu, r0)
            if ok and loss_kw < best_loss:
                best_loss = loss_kw
                best_t = t
        self.best_tree = best_t

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        active = self.best_tree or ctx.fast.standard_edges
        latency_ms = (time.perf_counter() - t0) * 1e3
        return active, latency_ms


class ExactDynamicOraclePolicy(Policy):
    """Exact loss-minimizing dynamic reconfiguration oracle with optional switching hysteresis."""

    def __init__(
        self,
        candidate_trees: Optional[List[Tuple[int, ...]]] = None,
        pool_size: int = 400,
        hysteresis_kw: float = 0.0,
        name: Optional[str] = None,
    ):
        self.candidate_trees = candidate_trees
        self.pool_size = pool_size
        self.hysteresis_kw = hysteresis_kw
        self.active_pool: List[Tuple[int, ...]] = []
        if name:
            self.name = name
        elif hysteresis_kw > 0.0:
            self.name = "exact_oracle_hysteresis"
        else:
            self.name = "exact_dynamic_oracle"

    def reset(self, grid, fast, timeline):
        if not self.active_pool:
            trees = self.candidate_trees or fast.enumerate_radial_configs()
            mean_inj = {
                b: (
                    float(np.mean([inj.get(b, (0.0, 0.0))[0] for inj in timeline])),
                    float(np.mean([inj.get(b, (0.0, 0.0))[1] for inj in timeline])),
                )
                for b in grid.graph.nodes
            }
            p_pu, q_pu = fast.vectors(mean_inj)
            r0 = fast.resistances()

            scored = []
            for t in trees:
                ok, _, _, loss, _ = fast.evaluate(t, p_pu, q_pu, r0)
                if ok:
                    scored.append((loss, t))
            scored.sort(key=lambda x: x[0])
            self.active_pool = [t for _, t in scored[: self.pool_size]]

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        best_t = ctx.prev_active
        ok_prev, _, _, prev_loss, _ = ctx.fast.evaluate(ctx.prev_active, ctx.p_pu, ctx.q_pu, ctx.resistances)
        best_loss = prev_loss if ok_prev else 1e12

        for t in self.active_pool:
            ok, _, _, loss, _ = ctx.fast.evaluate(t, ctx.p_pu, ctx.q_pu, ctx.resistances)
            if ok:
                threshold = self.hysteresis_kw if t != ctx.prev_active else 0.0
                if loss + threshold < best_loss:
                    best_loss = loss
                    best_t = t

        latency_ms = (time.perf_counter() - t0) * 1e3
        return best_t, latency_ms


class BaranWuBranchExchangePolicy(Policy):
    """Classic Baran & Wu (1989) branch exchange network reconfiguration heuristic.
    
    Starting from current operating topology (or standard baseline at t=0),
    evaluates all fundamental loop exchanges formed by closing an open tie line
    and opening a branch in the resulting cycle. Greedily selects the exchange
    yielding maximum loss reduction until local convergence.
    """
    name = "baran_wu_branch_exchange"

    def __init__(self, max_iterations: int = 10, tol_kw: float = 1e-3):
        self.max_iterations = max_iterations
        self.tol_kw = tol_kw

    def reset(self, grid, fast, timeline):
        pass

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        curr_t = ctx.prev_active
        ok, _, _, curr_loss, _ = ctx.fast.evaluate(curr_t, ctx.p_pu, ctx.q_pu, ctx.resistances)
        if not ok:
            curr_t = ctx.fast.standard_edges
            _, _, _, curr_loss, _ = ctx.fast.evaluate(curr_t, ctx.p_pu, ctx.q_pu, ctx.resistances)

        for _ in range(self.max_iterations):
            tree_info = ctx.fast._get_tree_order(curr_t)
            if tree_info is None:
                break
            order, parent, p_edge = tree_info
            open_edges = [e for e in range(ctx.fast.m) if e not in curr_t]

            best_cand = None
            best_loss = curr_loss

            for tie in open_edges:
                u, v = ctx.fast.eu[tie], ctx.fast.ev[tie]
                anc_u = {}
                curr = u
                while curr != -1:
                    anc_u[curr] = len(anc_u)
                    curr = parent[curr]
                curr = v
                while curr != -1 and curr not in anc_u:
                    curr = parent[curr]
                lca = curr

                cycle_edges = []
                curr = u
                while curr != lca:
                    cycle_edges.append(p_edge[curr])
                    curr = parent[curr]
                curr = v
                while curr != lca:
                    cycle_edges.append(p_edge[curr])
                    curr = parent[curr]

                for b in cycle_edges:
                    cand = tuple(sorted([e for e in curr_t if e != b] + [tie]))
                    ok_c, _, _, loss_c, v_min_c = ctx.fast.evaluate(cand, ctx.p_pu, ctx.q_pu, ctx.resistances)
                    if ok_c and v_min_c >= 0.90 and (loss_c < best_loss - self.tol_kw):
                        best_loss = loss_c
                        best_cand = cand

            if best_cand is not None:
                curr_t = best_cand
                curr_loss = best_loss
            else:
                break

        latency_ms = (time.perf_counter() - t0) * 1e3
        return curr_t, latency_ms


class DirectTreeSimulatedAnnealingPolicy(Policy):
    """Direct classical simulated annealing over the spanning tree manifold without QUBO.
    
    Generates neighbor trees via fundamental loop exchange and accepts moves
    using the Metropolis-Hastings criterion on power flow loss.
    """
    name = "tree_simulated_annealing"

    def __init__(self, steps: int = 60, t_init: float = 20.0, cooling: float = 0.92, seed: int = 42):
        self.steps = steps
        self.t_init = t_init
        self.cooling = cooling
        self.rng = np.random.default_rng(seed)

    def reset(self, grid, fast, timeline):
        pass

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        curr_t = ctx.prev_active
        ok, _, _, curr_loss, _ = ctx.fast.evaluate(curr_t, ctx.p_pu, ctx.q_pu, ctx.resistances)
        if not ok:
            curr_t = ctx.fast.standard_edges
            _, _, _, curr_loss, _ = ctx.fast.evaluate(curr_t, ctx.p_pu, ctx.q_pu, ctx.resistances)

        best_t = curr_t
        best_loss = curr_loss
        temp = self.t_init

        for _ in range(self.steps):
            tree_info = ctx.fast._get_tree_order(curr_t)
            if tree_info is None:
                break
            order, parent, p_edge = tree_info
            open_edges = [e for e in range(ctx.fast.m) if e not in curr_t]
            if not open_edges:
                break

            tie = self.rng.choice(open_edges)
            u, v = ctx.fast.eu[tie], ctx.fast.ev[tie]

            anc_u = {}
            curr = u
            while curr != -1:
                anc_u[curr] = len(anc_u)
                curr = parent[curr]
            curr = v
            while curr != -1 and curr not in anc_u:
                curr = parent[curr]
            lca = curr

            cycle_edges = []
            curr = u
            while curr != lca:
                cycle_edges.append(p_edge[curr])
                curr = parent[curr]
            curr = v
            while curr != lca:
                cycle_edges.append(p_edge[curr])
                curr = parent[curr]

            if not cycle_edges:
                continue

            b = self.rng.choice(cycle_edges)
            cand = tuple(sorted([e for e in curr_t if e != b] + [tie]))
            ok_c, _, _, loss_c, v_min_c = ctx.fast.evaluate(cand, ctx.p_pu, ctx.q_pu, ctx.resistances)

            if ok_c and v_min_c >= 0.90:
                delta = loss_c - curr_loss
                if delta < 0.0 or self.rng.random() < np.exp(-delta / max(temp, 1e-4)):
                    curr_t = cand
                    curr_loss = loss_c
                    if curr_loss < best_loss:
                        best_loss = curr_loss
                        best_t = cand

            temp *= self.cooling

        latency_ms = (time.perf_counter() - t0) * 1e3
        return best_t, latency_ms


class RandomTreePolicy(Policy):
    """Ablation: generates K random spanning trees.
    In 'raw' mode, picks a random tree.
    In 'filtered' mode, picks the tree with minimum power-flow loss among the K candidates.
    """

    def __init__(self, k_samples: int = 100, mode: str = "filtered", seed: int = 42):
        self.k_samples = k_samples
        self.mode = mode
        self.name = f"random_trees_{mode}"
        self.rng = np.random.default_rng(seed)
        self.all_trees: List[Tuple[int, ...]] = []

    def reset(self, grid, fast, timeline):
        self.all_trees = fast.enumerate_radial_configs()

    def _repair_to_tree(self, active_edges: Set[int], fast: FastFeeder, weights: Dict[int, float]) -> Tuple[int, ...]:
        """Greedy repair if random sample is not connected tree."""
        if fast.is_tree(tuple(active_edges)):
            return tuple(sorted(active_edges))
        all_edges = list(range(fast.m))
        all_edges.sort(key=lambda e: (0 if e in active_edges else 1, weights.get(e, 0.0)))
        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from(range(fast.n))
        chosen = []
        for e in all_edges:
            u, v = fast.eu[e], fast.ev[e]
            if not nx.has_path(G, u, v):
                G.add_edge(u, v)
                chosen.append(e)
            if len(chosen) == fast.n - 1:
                break
        return tuple(sorted(chosen))

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        if self.mode == "repair_ranked":
            # Generate K random candidate bitstrings with n-1 lines, repair each, rank by power flow
            candidates = []
            weights = {i: ctx.resistances[i] for i in range(ctx.fast.m)}
            for _ in range(self.k_samples):
                random_subset = set(self.rng.choice(ctx.fast.m, size=ctx.fast.n - 1, replace=False))
                tree = self._repair_to_tree(random_subset, ctx.fast, weights)
                candidates.append(tree)
        else:
            indices = self.rng.choice(len(self.all_trees), size=min(self.k_samples, len(self.all_trees)), replace=False)
            candidates = [self.all_trees[i] for i in indices]

        if self.mode == "raw":
            chosen = candidates[0]
        else:
            # Filtered: evaluate power flow on all K candidate trees
            best_loss = 1e12
            chosen = candidates[0]
            for t in candidates:
                ok, _, _, loss, _ = ctx.fast.evaluate(t, ctx.p_pu, ctx.q_pu, ctx.resistances)
                if ok and loss < best_loss:
                    best_loss = loss
                    chosen = t

        latency_ms = (time.perf_counter() - t0) * 1e3
        return chosen, latency_ms


class QUBOPolicy(Policy):
    """Thermodynamic QUBO Policy with Simulated Annealing.
    Modes:
      - selection:
          'raw': pure raw ground state bitstring from QUBO Hamiltonian without repair
          'marginal_mst': quantum marginal spin probability ensemble (MST of edge frequencies)
          'repair_only': raw ground state with MST repair if invalid, but NO power-flow ranking
          'filtered': candidates from annealer reads evaluated and ranked by LinDistFlow loss
      - ablation: 'no_thermo', 'no_cycle', 'no_rad', 'no_cap', 'no_sw'
      - weights: 'mesh_current' vs 'flow_preserving'
    """

    def __init__(
        self,
        sampler: Optional[Any] = None,
        num_reads: int = 25,
        selection: str = "filtered",
        weight_mode: str = "mesh_current",
        voltage_aware: bool = False,
        dynamic_thermal_weights: bool = True,
        ablation: Optional[str] = None,
        name: Optional[str] = None,
        seed: int = 42,
    ):
        self.sampler = sampler or NumpyAnnealer(sweeps=40, seed=seed)
        self.num_reads = num_reads
        self.selection = selection
        self.weight_mode = weight_mode
        self.voltage_aware = voltage_aware
        self.dynamic_thermal_weights = dynamic_thermal_weights
        self.ablation = ablation
        if name:
            self.name = name
        elif ablation:
            self.name = f"qubo_ablation_{ablation}"
        elif not dynamic_thermal_weights:
            self.name = f"qubo_{weight_mode}_{selection}_no_thermal_weights"
        elif voltage_aware:
            self.name = f"qubo_{weight_mode}_{selection}_vaware"
        else:
            self.name = f"qubo_{weight_mode}_{selection}"
        self.builder: Optional[ThermodynamicQUBOBuilder] = None
        self.calculator = EntropyCalculator()
        self.all_trees: List[Tuple[int, ...]] = []
        self.last_valid_tree_rate: float = 0.0
        self.last_ground_state_valid: bool = False

    def reset(self, grid, fast, timeline):
        edges = [(grid.lines[e].u, grid.lines[e].v) for e in fast.edge_ids]

        l_thermo = 0.0 if self.ablation == "no_thermo" else 1.0
        l_cycle = 0.0 if self.ablation == "no_cycle" else 4.0
        l_rad = 0.0 if self.ablation == "no_rad" else 4.0
        l_cap = 0.0 if self.ablation == "no_cap" else 5.0
        l_sw = 0.0 if self.ablation == "no_sw" else 0.2

        self.builder = ThermodynamicQUBOBuilder(
            num_buses=fast.n,
            edges=edges,
            substations=grid.substations,
            graph=grid.graph,
            lambda_thermo=l_thermo,
            lambda_cycle=l_cycle,
            lambda_rad=l_rad,
            lambda_cap=l_cap,
            lambda_sw=l_sw,
            cycle_mode="elementary",
            weight_mode=self.weight_mode,
        )

    def _repair_to_tree(self, active_edges: Set[int], fast: FastFeeder, weights: Dict[int, float]) -> Tuple[int, ...]:
        """Greedy repair if raw sample is not connected tree: sort by weight and keep acyclic edges."""
        if fast.is_tree(tuple(active_edges)):
            return tuple(sorted(active_edges))

        # Build minimum-weight spanning tree guided by the QUBO sample
        all_edges = list(range(fast.m))
        all_edges.sort(key=lambda e: (0 if e in active_edges else 1, weights.get(e, 0.0)))

        import networkx as nx
        G = nx.Graph()
        G.add_nodes_from(range(fast.n))
        chosen = []
        for e in all_edges:
            u, v = fast.eu[e], fast.ev[e]
            if not nx.has_path(G, u, v):
                G.add_edge(u, v)
                chosen.append(e)
            if len(chosen) == fast.n - 1:
                break
        return tuple(sorted(chosen))

    def decide(self, ctx: DecisionContext) -> Tuple[Tuple[int, ...], float]:
        t0 = time.perf_counter()
        # Compute mesh currents for non-zero weights on all lines
        temps_dict = {e: (ctx.temps_k[i] if self.dynamic_thermal_weights else 298.15) for i, e in enumerate(ctx.fast.edge_ids)}
        i_mesh = mesh_branch_currents(ctx.grid, ctx.injections, temps_dict)

        weights = {}
        for i, e in enumerate(ctx.fast.edge_ids):
            line = ctx.grid.lines[e]
            i_val = i_mesh.get(e, 30.0)
            r_val = ctx.resistances[i] if self.dynamic_thermal_weights else ctx.fast.r0[i]
            t_val = ctx.temps_k[i] if self.dynamic_thermal_weights else 298.15
            if self.weight_mode == "flow_preserving":
                weights[i] = (i_val ** 2) * r_val / max(t_val, 273.15)
            else:
                p_loss = 3.0 * (i_val ** 2) * r_val
                weights[i] = p_loss / max(t_val, 273.15)

        prev_map = {i: (1 if i in ctx.prev_active else 0) for i in range(ctx.fast.m)}
        qubo_model = self.builder.build_model(
            entropy_weights=weights,
            line_currents={i: i_mesh.get(e, 30.0) for i, e in enumerate(ctx.fast.edge_ids)},
            line_i_max={i: ctx.grid.lines[e].i_max for i, e in enumerate(ctx.fast.edge_ids)},
            prev_switch_states=prev_map,
        )

        X, E, sample_ms = self.sampler.sample(qubo_model.Q, num_reads=self.num_reads, offset=qubo_model.offset)

        # Track valid tree rate among raw reads
        raw_trees_valid = [ctx.fast.is_tree(tuple(sorted(np.nonzero(X[r, :ctx.fast.m])[0]))) for r in range(len(X))]
        self.last_valid_tree_rate = float(np.mean(raw_trees_valid))
        self.last_ground_state_valid = bool(raw_trees_valid[0])

        best_sample = X[0, :ctx.fast.m]
        active_set = set(np.nonzero(best_sample)[0])

        if self.selection == "raw":
            # Strictly return raw top read (without repair)
            chosen = tuple(sorted(active_set))
        elif self.selection == "marginal_mst":
            # Quantum marginal spin probability ensemble (MST on empirical edge probabilities)
            edge_probs = np.mean(X[:, :ctx.fast.m], axis=0)
            import networkx as nx
            G = nx.Graph()
            G.add_nodes_from(range(ctx.fast.n))
            for e_idx in range(ctx.fast.m):
                u, v = ctx.fast.eu[e_idx], ctx.fast.ev[e_idx]
                w = float(edge_probs[e_idx]) - 1e-5 * float(ctx.resistances[e_idx])
                G.add_edge(u, v, weight=w, edge_id=e_idx)
            mst = nx.maximum_spanning_tree(G, weight="weight")
            mst_edges = sorted([d["edge_id"] for _, _, d in mst.edges(data=True)])
            chosen = tuple(mst_edges)
        elif self.selection == "repair_only":
            if ctx.fast.is_tree(tuple(active_set)):
                chosen = tuple(sorted(active_set))
            else:
                chosen = self._repair_to_tree(active_set, ctx.fast, weights)
        else:
            # Filtered mode: check feasible trees among reads, repaired reads, and annealer-guided loop exchanges
            candidate_set = set()
            for r in range(len(X)):
                act = tuple(sorted(np.nonzero(X[r, :ctx.fast.m])[0]))
                if ctx.fast.is_tree(act):
                    candidate_set.add(act)

            if not candidate_set:
                candidate_set.add(self._repair_to_tree(active_set, ctx.fast, weights))

            # Annealer-guided loop branch exchange:
            # Check tie lines active in top reads and evaluate their fundamental cycle exchanges
            tie_active = set()
            for r in range(min(15, len(X))):
                for e in range(ctx.fast.m):
                    if X[r, e] == 1 and e not in ctx.prev_active:
                        tie_active.add(e)

            if tie_active:
                tree_info = ctx.fast._get_tree_order(ctx.prev_active)
                if tree_info:
                    order, parent, p_edge = tree_info
                    for tie in tie_active:
                        u, v = ctx.fast.eu[tie], ctx.fast.ev[tie]
                        anc_u = {}
                        curr = u
                        while curr != -1:
                            anc_u[curr] = len(anc_u)
                            curr = parent[curr]
                        curr = v
                        while curr != -1 and curr not in anc_u:
                            curr = parent[curr]
                        lca = curr
                        cycle_edges = []
                        curr = u
                        while curr != lca:
                            cycle_edges.append(p_edge[curr])
                            curr = parent[curr]
                        curr = v
                        while curr != lca:
                            cycle_edges.append(p_edge[curr])
                            curr = parent[curr]
                        for b in cycle_edges:
                            candidate_set.add(tuple(sorted([e for e in ctx.prev_active if e != b] + [tie])))

            # Include current operating topology so optimizer never switches to an inferior configuration
            ok_prev, _, _, prev_loss, _ = ctx.fast.evaluate(ctx.prev_active, ctx.p_pu, ctx.q_pu, ctx.resistances)
            best_t = ctx.prev_active
            best_loss = prev_loss if ok_prev else 1e12

            for t in candidate_set:
                ok, _, _, loss, v_min = ctx.fast.evaluate(t, ctx.p_pu, ctx.q_pu, ctx.resistances)
                if self.voltage_aware and v_min < 0.95:
                    continue
                if ok and v_min >= 0.90 and loss < best_loss:
                    best_loss = loss
                    best_t = t
            chosen = best_t

        latency_ms = (time.perf_counter() - t0) * 1e3
        return chosen, latency_ms
