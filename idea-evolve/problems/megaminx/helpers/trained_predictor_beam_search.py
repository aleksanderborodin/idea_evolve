"""Trained MLP predictor-guided beam search for Megaminx.

Packages the full pipeline: generate random walks, train MLP, run guided beam search.
Solves the int64/float32 dtype mismatch that blocked previous agents.

Usage:
    from helpers.trained_predictor_beam_search import trained_predictor_beam_search

    path_str, result = trained_predictor_beam_search(
        state, beam_width=4096, max_steps=60
    )
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

import torch
import torch.nn as nn


def trained_predictor_beam_search(
    state,
    graph=None,
    n_walks: int = 50000,
    walk_length: int = 20,
    beam_width: int = 4096,
    max_steps: int = 80,
    hidden_dims: tuple = (256, 128),
    epochs: int = 10,
    learning_rate: float = 1e-3,
    batch_size: int = 4096,
    device=None,
    verbose: bool = False,
) -> Tuple[Optional[str], object]:
    """Train a tiny MLP on random walks and run predictor-guided beam search.

    Args:
        state: Starting state as tuple/list of 120 ints.
        graph: Optional pre-built CayleyGraph. If None, creates one.
        n_walks: Number of random walks for training data.
        walk_length: Random walk depth for training data.
        beam_width: Beam search width.
        max_steps: Max beam search depth.
        hidden_dims: MLP hidden layer sizes.
        epochs: Training epochs.
        learning_rate: Adam learning rate.
        batch_size: Mini-batch size for training.
        device: Torch device. Auto-detects CUDA if None.
        verbose: Print training progress.

    Returns:
        (path_str, result_object)
        - path_str: dot-joined move string if solved, else None
        - result_object: the raw beam_search result for diagnostics

    Raises:
        RuntimeError: If state encoding or beam search fails.
    """
    import cayleypy

    t_total = time.time()

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if graph is None:
        gdef = cayleypy.Puzzles.megaminx()
        graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
    else:
        gdef = graph.definition

    t0 = time.time()
    X, y = graph.random_walks(width=n_walks, length=walk_length, mode="bfs")
    if verbose:
        print(
            f"[trained_predictor] Walks: X={X.shape} y={y.shape} "
            f"y_max={y.max().item()} in {time.time()-t0:.1f}s"
        )

    model = _build_mlp(120, hidden_dims, device)
    _train_mlp(model, X, y, epochs, learning_rate, batch_size, verbose)

    predictor = cayleypy.Predictor(graph, model)

    if verbose:
        print(f"[trained_predictor] Training+walk took {time.time()-t_total:.1f}s")

    path_str, result = _run_beam(graph, gdef, state, predictor, beam_width, max_steps)

    if verbose:
        print(
            f"[trained_predictor] Total: {time.time()-t_total:.1f}s, "
            f"solved={path_str is not None}"
        )

    return path_str, result


def build_graph(device=None):
    """Build a CayleyGraph for Megaminx. Returns (graph, gdef)."""
    import cayleypy

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
    return graph, gdef


def train_predictor(
    graph,
    n_walks: int = 50000,
    walk_length: int = 20,
    hidden_dims: tuple = (256, 128),
    epochs: int = 10,
    learning_rate: float = 1e-3,
    batch_size: int = 4096,
    verbose: bool = False,
):
    """Train an MLP predictor on random walks. Returns a cayleypy.Predictor."""
    import cayleypy

    t0 = time.time()
    X, y = graph.random_walks(width=n_walks, length=walk_length, mode="bfs")
    if verbose:
        print(
            f"[train_predictor] Walks: X={X.shape} y_max={y.max().item()} "
            f"in {time.time()-t0:.1f}s"
        )

    model = _build_mlp(120, hidden_dims, graph.device)
    _train_mlp(model, X, y, epochs, learning_rate, batch_size, verbose)

    return cayleypy.Predictor(graph, model)


def guided_beam_search(
    state,
    graph,
    predictor,
    beam_width: int = 4096,
    max_steps: int = 80,
) -> Tuple[Optional[str], object]:
    """Run beam search with a pre-built predictor. Returns (path_str, result)."""
    return _run_beam(graph, graph.definition, state, predictor, beam_width, max_steps)


class _PredictorMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: tuple):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        if x.dtype != torch.float32:
            x = x.float()
        return self.net(x).squeeze(-1)


def _build_mlp(input_dim, hidden_dims, device):
    model = _PredictorMLP(input_dim, hidden_dims).to(device)
    return model


def _train_mlp(model, X, y, epochs, lr, batch_size, verbose):
    Xf = X.float()
    yf = y.float()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        perm = torch.randperm(Xf.shape[0], device=Xf.device)
        total_loss = 0.0
        n_batches = 0
        for i in range(0, Xf.shape[0], batch_size):
            idx = perm[i : i + batch_size]
            pred = model(Xf[idx])
            loss = loss_fn(pred, yf[idx])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1
        if verbose and (epoch % 5 == 0 or epoch == epochs - 1):
            print(
                f"  Epoch {epoch}/{epochs}: loss={total_loss/n_batches:.4f}"
            )


def _to_kaggle_name(cname: str) -> str:
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


def _run_beam(graph, gdef, state, predictor, beam_width, max_steps):
    try:
        result = graph.beam_search(
            start_state=list(state),
            beam_width=beam_width,
            max_steps=max_steps,
            return_path=True,
            predictor=predictor,
            beam_mode="simple",
        )
    except Exception as e:
        raise RuntimeError(f"Beam search failed: {e}") from e

    if not getattr(result, "path_found", False):
        return None, result

    if result.path is None:
        return None, result

    moves = [_to_kaggle_name(gdef.generator_names[idx]) for idx in result.path]
    return ".".join(moves), result
