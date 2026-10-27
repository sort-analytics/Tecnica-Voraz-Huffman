"""Árboles de expansión mínima (otra técnica voraz): Kruskal y Prim."""
import heapq


def parse_edges(text):
    edges = []
    for line in text.strip().splitlines():
        p = line.split()
        if len(p) == 3:
            edges.append((p[0], p[1], float(p[2])))
    return edges


def kruskal(edges):
    """Ordena aristas por peso; añade la menor que no forme ciclo (Union-Find)."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst, total = [], 0.0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            mst.append((u, v, w)); total += w
    return mst, total


def prim(edges, start=None):
    """Crece un árbol desde `start`, tomando siempre la arista más barata que sale de él."""
    adj = {}
    for u, v, w in edges:
        adj.setdefault(u, []).append((w, u, v))
        adj.setdefault(v, []).append((w, v, u))
    if not adj:
        return [], 0.0
    start = start if start in adj else next(iter(adj))
    seen, heap, mst, total = {start}, list(adj[start]), [], 0.0
    heapq.heapify(heap)
    while heap:
        w, u, v = heapq.heappop(heap)
        if v in seen:
            continue
        seen.add(v); mst.append((u, v, w)); total += w
        for e in adj[v]:
            if e[2] not in seen:
                heapq.heappush(heap, e)
    return mst, total
