# Isolated environment and external builds

The Python environment is `.venv`, with system-site packages disabled. The existing required dependency remains NumPy; visualization stays optional. This phase adds optional groups only:

```bash
uv sync --extra viz --extra milp --extra matching --extra tesb
```

`milp` installs PySCIPOpt; `matching` installs NetworkX/SciPy; `tesb` installs pandas/SciPy. A plain `uv sync` still supports basic exhaustive/BM/tabu/BLS/annealing/local bifurcation methods. Missing optional packages return an explicit unavailable result for their requested backend. Default small LNS enumeration requires no MILP package; releasing more than 20 nodes requires it. `uv.lock` pins the resolved environment. Measured versions and tool paths are in the verification artifacts.

## Source identity and ownership

[`external/sources.json`](../../external/sources.json) records exact Git commits and the official BiqCrunch archive SHA. Downloaded source/build/prefix directories are ignored; project-owned adapters, build script, compiler wrapper, manifest and collected notices are retained. The BiqCrunch release archive is preserved unchanged. Reconstruct ignored checkouts using the commands below before expecting native availability on another machine. `--list` checks current installation, not an aspirational source list.

Original tracked upstream sources are unchanged. SMS's old nested MQLib/TLX headers relied on transitive `<cstdint>` inclusion; [`external/toolchain/gxx-compat`](../../external/toolchain/gxx-compat) calls `/usr/bin/g++-12 -include cstdint`. The separately preserved `external/patches/scientific-stdint.patch` documents an **abandoned, reverted** source-patching attempt and is **not applied**. Successful builds use the wrapper. Notices are copied where an upstream license file was found; the manifest's empty license list means no top-level license file was found, not a claim that all source is unrestricted. Check each upstream's terms before redistribution.

Compilers/tools used: GCC/G++ 12, gfortran, make, CMake, OpenMPI (`mpicc`, `mpirun`) and Poppler. BLAS/LAPACK SONAME flags below were tested on this Linux host. Other platforms may need equivalent linker flags.

## Optional native dependency prefix

SCIP 8.0.4, SuiteSparse and OpenBLAS were installed into **`external/native`**, with a separate package cache. The base Conda environment was not modified. Installation log: `evidence/portfolio/native_dependencies.log`; exact platform package URLs: `evidence/portfolio/native_environment_explicit.txt`.

To reconstruct the tested Linux prefix (with Conda available):

```bash
CONDA_PKGS_DIRS=/tmp/maxcut-conda-cache conda create -y \
  --prefix "$PWD/external/native" \
  --file evidence/portfolio/native_environment_explicit.txt
```

The original higher-level solve was `conda create --prefix ... --override-channels -c conda-forge scip=8.0.4 suitesparse openblas`. PySCIPOpt's installed Python solver can use a different bundled SCIP version; do not confuse it with SMS's native SCIP 8.0.4 build.

## Reproduce one backend at a time

From the repository root, use the checked-in helper; `--fetch` obtains only the pinned revision or hash-verified official release. Existing mismatched/modified tracked sources are refused rather than overwritten.

```bash
uv run python scripts/build_portfolio_backends.py --backend mqlib --fetch
uv run python scripts/build_portfolio_backends.py --backend scientific --fetch
uv run python scripts/build_portfolio_backends.py --backend biqbin --fetch
uv run python scripts/build_portfolio_backends.py --backend madam --fetch
uv run python scripts/build_portfolio_backends.py --backend biqcrunch --fetch
uv run python scripts/build_portfolio_backends.py --backend tesb --fetch
uv run python scripts/build_portfolio_backends.py --backend toroidal --fetch
```

The script prints checked argv arrays. SMS recursively obtains its pinned submodules. TESB/toroidal entries obtain source but need no compilation. The general Python SB repository is preserved as a reference pin; the local CPU dynamics do not import it or require PyTorch.

| Backend | Actual successful build | Evidence |
|---|---|---|
| MQLib | `make -j2` | `mqlib_build.log`, actual `mqlib_heuristics.txt` |
| SMS | CMake `build-compat`, TESTS=OFF, compiler wrapper, SCIP_DIR/prefix native; `LIBRARY_PATH=.../native/lib cmake --build ... --target sms -j2` | `scientific_link_paths_build.log` and earlier attempts |
| BiqBin | `make -j2 'LINALG=-l:liblapack.so.3 -l:libblas.so.3 -lm'` | `biqbin_reference_blas_build.log` |
| MADAM | SuiteSparse include/link flags, native OpenBLAS and absolute rpath | `madam_rpath_build.log` |
| BiqCrunch 2.0 | from release `src`, `make -j2 'LINALG=-l:liblapack.so.3 -l:libblas.so.3'` | `biqcrunch_build.log` |

All build evidence lives under [`evidence/portfolio`](../../evidence/portfolio). Initial failures are retained: missing SuiteSparse/SCIP, old-header incompatibility, unversioned LAPACK, and a consumed rpath variable. Those logs describe historical attempts, not current availability. The official BiqCrunch archive SHA is `b302a0d3562ae9081e5ac8791d9dc9eeb365b51d1613c9c376a150702db5ac9e`.

## Runtime limitations

BiqBin and MADAM need two MPI ranks and **seed 2020**; neither exposes a warm-start flag through this inspected interface. The source hardcodes the RNG seed, so another requested seed is rejected. BiqCrunch and MQLib also reject supplied warm labels. SMS injects a complete native partition incumbent; generic MILP injects its own complete XOR incumbent. Discovery reports these distinctions.

The native SDP implementations allocate dense matrices. BiqBin/MADAM default guard is 1024 original vertices; BiqCrunch guard is 5000. MQLib/SMS guard is 100000, without a claim that every native method fits that size. Toroidal blossom matching defaults to 4096 expanded vertices: it can inspect medium tori, but is deliberately guarded against a 100000-node expanded matching job. Guards, unsupported topology, numerical range and precision can reject an otherwise syntactically valid graph.

Every invocation uses a new native artifact directory, short relative graph filenames, command/parameter/conversion records and actual raw logs. Integer scaling is exact for supported finite-decimal graph values. Parent and adapter timeouts use owned process sessions, PID start ticks and atomic active registrations; they never kill a broad name-matched process list. Local MPI sockets are restricted in the sandbox, so native validation was run with the authorized execution escalation; ordinary user shell runs use the same public CLI.

## QuBowl: source not obtained

The full Rehfeldt–Koch–Shinano paper is retained. In the [author's official SCIP mailing-list response](https://listserv.zib.de/pipermail/scip/2024-March/004869.html) dated March 6, 2024, the code was described as unavailable publicly and separate from SCIP. The October 20, 2026 availability investigation found no obtainable official release. That historical statement alone does not prove it can never become available. The current factual blocker is **no obtained source/executable/API**. `--solver qubowl` returns unavailable, with no assignment/bound. No other backend is relabeled as QuBowl.
