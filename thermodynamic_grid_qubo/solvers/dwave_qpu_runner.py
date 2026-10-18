"""
D-Wave QPU and Leap Hybrid Solver Interface.

Provides a unified interface for submitting Thermodynamic QUBO instances to:
1. Direct Physical Quantum Processing Unit (DWaveSampler with EmbeddingComposite)
2. Leap Hybrid Sampler (LeapHybridSampler)
3. Local classical Simulated Annealing fallback (neal) when credentials or hardware are unavailable.

Reports the TRUE execution backend in `solver_backend` ('qpu', 'hybrid', or 'local_fallback').
Captures hardware embedding metrics (logical variables, physical qubits, maximum chain length,
chain strength, chain-break fraction, annealing time, reads, wall-clock time).
"""
import os
import time
from typing import Dict, Tuple, Any, Optional
import numpy as np
import dimod


class DWaveQPURunner:
    """
    Submits Thermodynamic QUBO instances to D-Wave Advantage QPU or Leap Hybrid Sampler
    using the D-Wave Ocean SDK, with strict reporting of physical backend execution.
    """
    def __init__(
        self,
        token: Optional[str] = None,
        backend: str = "auto",
        qpu_profile: Optional[str] = None,
    ):
        """
        Parameters:
            token: D-Wave Leap API token (defaults to DWAVE_API_TOKEN environment variable).
            backend: 'qpu' for direct hardware, 'hybrid' for Leap Hybrid, 'auto' for QPU-first,
                     or 'local_fallback' for classical Neal.
            qpu_profile: Optional specific solver name (e.g. 'Advantage_system4.1').
        """
        self.token = token or os.environ.get("DWAVE_API_TOKEN", "")
        self.backend = backend
        self.qpu_profile = qpu_profile
        self.solver_backend: str = "local_fallback"
        self.last_qpu_metrics: Dict[str, Any] = {}

    def solve(
        self,
        bqm: dimod.BinaryQuadraticModel,
        num_reads: int = 500,
        chain_strength: Optional[float] = None,
        annealing_time_us: int = 20,
    ) -> Tuple[Dict[int, int], float, float, Any]:
        """
        Executes sampling on D-Wave QPU, Leap Hybrid, or local fallback.

        Returns:
            parsed_sample: Dict[int, int] mapping edge_idx -> switch state (0 or 1)
            best_energy: float (lowest Hamiltonian energy)
            elapsed_ms: float (wall-clock latency)
            response: dimod.SampleSet
        """
        response = None
        elapsed_ms = 0.0

        # 1. Direct Physical QPU Path
        if self.backend in ("qpu", "auto") and bool(self.token):
            try:
                from dwave.system import DWaveSampler, EmbeddingComposite
                qpu_kwargs = {"token": self.token}
                if self.qpu_profile:
                    qpu_kwargs["solver"] = self.qpu_profile
                
                qpu = DWaveSampler(**qpu_kwargs)
                sampler = EmbeddingComposite(qpu)

                if chain_strength is None:
                    max_q = max(abs(v) for v in bqm.quadratic.values()) if bqm.quadratic else 1.0
                    chain_strength = float(max_q * 1.5)

                t0 = time.perf_counter()
                response = sampler.sample(
                    bqm,
                    num_reads=num_reads,
                    chain_strength=chain_strength,
                    annealing_time=annealing_time_us,
                )
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                self.solver_backend = "qpu"

                embedding = getattr(sampler, "embedding", {})
                chain_lens = [len(physical_qubits) for physical_qubits in embedding.values()] if embedding else []
                physical_qubits = sum(chain_lens)
                max_chain = max(chain_lens) if chain_lens else 0

                cb_frac = 0.0
                if hasattr(response, "data_vectors") and "chain_break_fraction" in response.data_vectors:
                    cb_frac = float(np.mean(response.data_vectors["chain_break_fraction"]))
                elif hasattr(response, "chain_break_fraction"):
                    cb_frac = float(np.mean(response.chain_break_fraction))
                elif hasattr(response, "record") and hasattr(response.record, "dtype") and response.record.dtype.names and "chain_break_fraction" in response.record.dtype.names:
                    cb_frac = float(np.mean(response.record["chain_break_fraction"]))

                self.last_qpu_metrics = {
                    "logical_variables": len(bqm.variables),
                    "physical_qubits": physical_qubits,
                    "max_chain_length": max_chain,
                    "chain_strength": float(chain_strength),
                    "chain_break_fraction": float(cb_frac),
                    "annealing_time_us": annealing_time_us,
                    "num_reads": num_reads,
                    "wall_clock_ms": elapsed_ms,
                    "timing": getattr(response, "info", {}).get("timing", {}),
                }
            except Exception as e:
                # If explicit QPU failed, note error and continue to fallback or hybrid
                self.last_qpu_metrics = {"qpu_error": str(e)}

        # 2. Leap Hybrid Path
        if response is None and (self.backend in ("hybrid", "auto")) and bool(self.token):
            try:
                from dwave.system import LeapHybridSampler
                sampler = LeapHybridSampler(token=self.token)
                t0 = time.perf_counter()
                response = sampler.sample(bqm)
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                self.solver_backend = "hybrid"
                self.last_qpu_metrics = {
                    "logical_variables": len(bqm.variables),
                    "wall_clock_ms": elapsed_ms,
                    "qpu_access_time_us": getattr(response, "info", {}).get("qpu_access_time"),
                }
            except Exception as e:
                self.last_qpu_metrics["hybrid_error"] = str(e)

        # 3. Local Classical Neal Fallback
        if response is None:
            import neal
            sampler = neal.SimulatedAnnealingSampler()
            t0 = time.perf_counter()
            response = sampler.sample(bqm, num_reads=num_reads)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self.solver_backend = "local_fallback"
            self.last_qpu_metrics = {
                "logical_variables": len(bqm.variables),
                "wall_clock_ms": elapsed_ms,
                "backend_note": "Local simulated annealing fallback (neal). No QPU hardware execution occurred.",
            }

        best_record = response.first
        raw_sample = best_record.sample
        best_energy = float(best_record.energy)

        parsed_sample = {}
        for var_name, val in raw_sample.items():
            if var_name.startswith("x_"):
                edge_idx = int(var_name.split("_")[1])
                parsed_sample[edge_idx] = int(val)

        return parsed_sample, best_energy, elapsed_ms, response
