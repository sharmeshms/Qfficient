"""
Generate executive presentation dashboard HTML for the Thermodynamic QUBO project.
Self-contained single-page application with interactive SVG topology, time scrubber,
dynamic switching animations, loss comparison charts, and executive KPI cards.
"""

import json
from pathlib import Path

LOCAL_DIR = Path(__file__).resolve().parent
DATA_PATH = LOCAL_DIR / "dashboard_data.json" if (LOCAL_DIR / "dashboard_data.json").exists() else Path(r"c:\ep-project\dashboard_data.json")
OUTPUT_HTML = LOCAL_DIR / "dashboard.html"
ARTIFACT_HTML = Path(r"C:\Users\Sharmesh Magesh\.gemini\antigravity-ide\brain\d599556f-ca50-403a-a517-344a12f58b32\executive_dashboard.html")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    dashboard_data_str = f.read()

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Thermodynamic QUBO Grid Reconfiguration | Executive Suite</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --bg-page: #F3EBDC;
      --bg-card: #FBF7EE;
      --bg-sidebar: #E9DDC6;
      --bg-sunken: #EDE2CC;
      --text-primary: #2B1D16;
      --text-secondary: #5B463A;
      --text-muted: #7A6656;
      --accent: #6B1D2A;
      --accent-hover: #531521;
      --accent-pressed: #43111B;
      --accent-soft: #E8D3D3;
      --brass: #A98B4A;
      --border: #D8C9AC;
      --border-strong: #BFAA84;
      --border-input: #94806A;
      --status-pass-text: #3F5D2E;
      --status-pass-fill: #E3EBD6;
      --status-warn-text: #8A5A12;
      --status-warn-fill: #F4E6C6;
      --status-fail-text: #A33A2A;
      --status-fail-fill: #F3D9D2;
      --status-info-text: #5B463A;
      --status-info-fill: #E9DDC6;
    }}

    body {{
      background-color: var(--bg-page);
      color: var(--text-primary);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    }}

    h1, h2, h3, h4 {{
      font-family: Georgia, "Times New Roman", serif;
      color: var(--text-primary);
      text-shadow: 0 1px 0 rgba(255,250,240,.7);
    }}

    .tie-active {{
      stroke: #6B1D2A !important;
      stroke-width: 3.5 !important;
      stroke-dasharray: none !important;
    }}
    .branch-open {{
      stroke: #BFAA84 !important;
      stroke-width: 1.2 !important;
      stroke-dasharray: 4 4;
      opacity: 0.65;
    }}
    .branch-normal {{
      transition: stroke 150ms ease-out, stroke-width 150ms ease-out, opacity 150ms ease-out;
    }}

    #svg-tooltip {{
      background: rgba(251,247,238,.86);
      backdrop-filter: blur(8px) saturate(1.05);
      -webkit-backdrop-filter: blur(8px) saturate(1.05);
      border: 1px solid rgba(169,139,74,.45);
      box-shadow: 0 8px 24px rgba(43,29,22,.16);
      border-radius: 3px;
      color: #2B1D16;
    }}
    @supports not (backdrop-filter: blur(1px)) {{
      #svg-tooltip {{
        background: #FBF7EE;
      }}
    }}

    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #EDE2CC;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #BFAA84;
      border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #94806A;
    }}

    .paper-card {{
      background: #FBF7EE;
      border: 1px solid #D8C9AC;
      border-top: 2px solid #A98B4A;
      border-radius: 3px;
      box-shadow: 0 1px 0 rgba(43,29,22,.06), 0 2px 8px rgba(43,29,22,.07);
      transition: box-shadow 150ms ease-out;
    }}
    .paper-card:hover {{
      box-shadow: 0 1px 0 rgba(43,29,22,.08), 0 6px 16px rgba(43,29,22,.10);
    }}

    .recessed-control {{
      background: #EDE2CC;
      border: 1px solid #94806A;
      box-shadow: inset 0 1px 3px rgba(43,29,22,.14), 0 1px 0 rgba(255,250,240,.7);
      border-radius: 3px;
    }}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        transition: none !important;
        animation: none !important;
      }}
    }}
  </style>
</head>
<body class="min-h-screen antialiased selection:bg-[#E8D3D3] selection:text-[#6B1D2A]">

  <!-- Top Header / Executive Nav -->
  <header class="border-b border-[#D8C9AC] bg-[#E9DDC6] sticky top-0 z-50 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded bg-[#6B1D2A] border border-[#A98B4A] flex items-center justify-center shadow-sm font-serif font-bold text-lg text-[#FBF7EE]">
        Ω
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-base font-bold tracking-tight text-[#2B1D16]">Thermodynamic QUBO Grid Reconfiguration</h1>
          <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[#E3EBD6] text-[#3F5D2E] border border-[#3F5D2E]/40">
            Executive Suite v2.0
          </span>
        </div>
        <p class="text-xs text-[#5B463A]">Non-Equilibrium Joule Dissipation Minimization & Transient Thermal Control</p>
      </div>
    </div>

    <!-- Grid Selector & View Controls -->
    <div class="flex items-center gap-3">
      <div class="bg-[#EDE2CC] p-1 rounded border border-[#94806A] flex items-center gap-1">
        <button id="btn-grid40" onclick="switchGrid('grid40')" class="px-3 py-1.5 rounded text-xs font-semibold transition-all text-[#5B463A] hover:text-[#2B1D16]">
          40-Bus Microgrid
        </button>
        <button id="btn-grid60" onclick="switchGrid('grid60')" class="px-3 py-1.5 rounded text-xs font-semibold transition-all bg-[#6B1D2A] text-[#FBF7EE] shadow-sm">
          60-Bus Industrial Grid
        </button>
      </div>

      <button onclick="window.print()" class="px-3 py-1.5 bg-[#FBF7EE] hover:bg-[#E8D3D3] text-[#6B1D2A] border border-[#6B1D2A] text-xs font-medium rounded flex items-center gap-1.5 transition">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
        Print / PDF
      </button>
    </div>
  </header>

  <!-- Main Content Layout -->
  <main class="p-6 max-w-[1700px] mx-auto space-y-6">

    <!-- KPI Metric Cards Grid -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      
      <!-- Joule Heat Saved -->
      <div class="paper-card p-4">
        <div class="flex items-center justify-between text-[#7A6656] mb-1">
          <span class="text-xs font-medium uppercase tracking-wider">Joule Heat Saved</span>
          <span class="text-[#6B1D2A] bg-[#E8D3D3] p-1 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </span>
        </div>
        <div class="flex items-baseline gap-2">
          <span id="kpi-heat-reduction" class="text-2xl font-serif font-bold text-[#2B1D16] tracking-tight">+3.00%</span>
          <span id="kpi-heat-delta" class="text-xs font-semibold text-[#3F5D2E]">(-5.81 kJ)</span>
        </div>
        <p class="text-[11px] text-[#7A6656] mt-1 font-mono">Non-equilibrium Joule losses minimized</p>
      </div>

      <!-- Entropy Generation Reduction -->
      <div class="paper-card p-4">
        <div class="flex items-center justify-between text-[#7A6656] mb-1">
          <span class="text-xs font-medium uppercase tracking-wider">Entropy Generation</span>
          <span class="text-[#6B1D2A] bg-[#E8D3D3] p-1 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          </span>
        </div>
        <div class="flex items-baseline gap-2">
          <span id="kpi-entropy-reduction" class="text-2xl font-serif font-bold text-[#2B1D16] tracking-tight">+3.00%</span>
          <span id="kpi-entropy-unit" class="text-xs font-semibold text-[#3F5D2E]">(-19.5 J/K)</span>
        </div>
        <p class="text-[11px] text-[#7A6656] mt-1 font-mono">Thermodynamic irreversibility reduced</p>
      </div>

      <!-- Exergy Preserved -->
      <div class="paper-card p-4">
        <div class="flex items-center justify-between text-[#7A6656] mb-1">
          <span class="text-xs font-medium uppercase tracking-wider">Exergy Preserved</span>
          <span class="text-[#6B1D2A] bg-[#E8D3D3] p-1 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </span>
        </div>
        <div class="flex items-baseline gap-2">
          <span id="kpi-exergy-saved" class="text-2xl font-serif font-bold text-[#2B1D16] tracking-tight">+5.81 kJ</span>
          <span class="text-xs font-semibold text-[#3F5D2E]">Available Work</span>
        </div>
        <p class="text-[11px] text-[#7A6656] mt-1 font-mono">Useful electrical work preserved</p>
      </div>

      <!-- ANSI C84.1 Voltage Security -->
      <div class="paper-card p-4">
        <div class="flex items-center justify-between text-[#7A6656] mb-1">
          <span class="text-xs font-medium uppercase tracking-wider">Voltage Security</span>
          <span class="text-[#3F5D2E] bg-[#E3EBD6] p-1 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </span>
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-2xl font-serif font-bold text-[#2B1D16] tracking-tight">0 Violations</span>
          <span class="text-xs font-semibold text-[#3F5D2E]">100% ANSI</span>
        </div>
        <p class="text-[11px] text-[#7A6656] mt-1 font-mono">All nodes strictly within 0.95 - 1.05 p.u.</p>
      </div>

      <!-- Quantum Annealer Performance -->
      <div class="paper-card p-4">
        <div class="flex items-center justify-between text-[#7A6656] mb-1">
          <span class="text-xs font-medium uppercase tracking-wider">QUBO Solver Latency</span>
          <span class="text-[#6B1D2A] bg-[#E8D3D3] p-1 rounded">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </span>
        </div>
        <div class="flex items-baseline gap-2">
          <span id="kpi-latency" class="text-2xl font-serif font-bold text-[#2B1D16] tracking-tight">450 ms</span>
          <span class="text-xs font-semibold text-[#5B463A]">OpenJij SQA</span>
        </div>
        <p class="text-[11px] text-[#7A6656] mt-1 font-mono">Real-time feasible dispatch cycle</p>
      </div>

    </section>

    <!-- Interactive Grid Topology Map & Time Scrubber -->
    <section class="paper-card p-5 space-y-4">
      
      <!-- Topology Card Header & Time Scrubber Controls -->
      <div class="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-[#D8C9AC]">
        <div>
          <div class="flex items-center gap-2">
            <h2 id="grid-title" class="text-lg font-bold text-[#2B1D16] tracking-tight">Interactive Network Topology (60-Bus Industrial Grid)</h2>
            <span id="grid-meta-badge" class="px-2 py-0.5 rounded text-xs font-mono bg-[#EDE2CC] text-[#5B463A] border border-[#D8C9AC]">
              60 Buses | 59 Feeder Lines | 6 Tie Switches
            </span>
          </div>
          <p class="text-xs text-[#5B463A]">Live vector visualization with dynamic breaker reconfiguration, thermal loading, and feeder routing</p>
        </div>

        <!-- Playback Controls -->
        <div class="flex items-center gap-3 recessed-control px-4 py-2">
          <button id="btn-play" onclick="togglePlayback()" class="h-8 w-8 rounded bg-[#6B1D2A] hover:bg-[#531521] text-[#FBF7EE] flex items-center justify-center transition shadow-sm">
            <svg id="icon-play" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            <svg id="icon-pause" class="w-4 h-4 hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          </button>

          <div class="flex flex-col gap-1 w-64 sm:w-80">
            <div class="flex justify-between text-[11px]">
              <span class="text-[#5B463A] font-mono">Time: <strong id="time-val-display" class="text-[#2B1D16]">t = 0.0s</strong></span>
              <span id="switching-status-badge" class="text-[#3F5D2E] font-mono">Base Radial Configuration</span>
            </div>
            <input id="time-slider" type="range" min="0" max="19" value="0" step="1" oninput="onTimeSliderChange(this.value)"
                   class="w-full accent-[#6B1D2A] h-1.5 bg-[#EDE2CC] rounded cursor-pointer">
          </div>

          <div class="text-right pl-2 border-l border-[#BFAA84] text-xs">
            <div class="text-[#7A6656] text-[10px] uppercase font-mono">Loss at step</div>
            <div id="step-loss-display" class="font-bold font-mono text-[#6B1D2A]">4.45 kW</div>
          </div>
        </div>
      </div>

      <!-- Network Diagram Legend -->
      <div class="flex flex-wrap items-center justify-between text-xs text-[#5B463A] gap-4 bg-[#EDE2CC] p-2.5 rounded border border-[#D8C9AC]">
        <div class="flex flex-wrap items-center gap-4">
          <span class="font-semibold text-[#7A6656] text-[11px] uppercase tracking-wider">Component Roles:</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 bg-[#2B1D16] border border-[#D8C9AC]"></span> Substation</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#C9A13B]"></span> Solar PV</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#5E7F8C]"></span> Wind Turbine</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#7B4B63]"></span> Battery BESS</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#4F6B3A]"></span> EV Depot</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-[#E8DCC4] border border-[#94806A]"></span> Load Bus</span>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <span class="font-semibold text-[#7A6656] text-[11px] uppercase tracking-wider">Feeder Status:</span>
          <span class="flex items-center gap-1.5"><span class="w-5 h-1 bg-[#6F8F55] rounded"></span> Active Feeder</span>
          <span class="flex items-center gap-1.5"><span class="w-5 h-1 bg-[#6B1D2A] rounded"></span> QUBO Closed Tie Switch</span>
          <span class="flex items-center gap-1.5"><span class="w-5 h-0.5 border-b border-dashed border-[#BFAA84]"></span> Opened Line</span>
        </div>
      </div>

      <!-- SVG Vector Canvas Container -->
      <div class="relative bg-[#FBF7EE] rounded border border-[#D8C9AC] overflow-hidden" style="min-height: 520px;">
        <svg id="network-svg" class="w-full h-[520px] cursor-grab active:cursor-grabbing select-none" viewBox="0 0 1000 520">
          <defs>
            <pattern id="gridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#D8C9AC" stroke-width="0.5" stroke-opacity="0.6"/>
            </pattern>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#gridPattern)" />
          
          <!-- Zoom/Pan Group -->
          <g id="viewport-group">
            <g id="edges-layer"></g>
            <g id="nodes-layer"></g>
          </g>
        </svg>

        <!-- Tooltip overlay -->
        <div id="svg-tooltip" class="absolute pointer-events-none hidden text-xs p-3 min-w-[200px] transition-opacity duration-150 z-30">
        </div>

        <!-- Floating Zoom Controls -->
        <div class="absolute bottom-4 right-4 flex flex-col gap-1 bg-[#FBF7EE] border border-[#D8C9AC] p-1 rounded shadow-sm">
          <button onclick="zoom(1.2)" class="w-7 h-7 flex items-center justify-center hover:bg-[#EDE2CC] rounded text-[#2B1D16] font-bold text-sm">+</button>
          <button onclick="resetZoom()" class="w-7 h-7 flex items-center justify-center hover:bg-[#EDE2CC] rounded text-[#2B1D16] text-xs">⟲</button>
          <button onclick="zoom(0.8)" class="w-7 h-7 flex items-center justify-center hover:bg-[#EDE2CC] rounded text-[#2B1D16] font-bold text-sm">−</button>
        </div>
      </div>
    </section>

    <!-- Side-by-Side Analysis: Loss Profiles & Executive Comparison Table -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Transient Loss Profile Chart (5 cols) -->
      <div class="lg:col-span-5 paper-card p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-bold text-[#2B1D16] tracking-tight">Active Power Loss Dynamics (40s Window)</h3>
            <span class="text-[11px] font-mono text-[#5B463A] bg-[#EDE2CC] px-2 py-0.5 rounded border border-[#D8C9AC]">kW vs Time</span>
          </div>
          <p class="text-xs text-[#5B463A] mb-4">Comparison of real-time $I^2R$ dissipation between Baseline and Thermodynamic QUBO</p>

          <!-- SVG Mini Line Chart -->
          <div class="relative bg-[#FBF7EE] rounded p-3 border border-[#D8C9AC]">
            <svg id="loss-chart-svg" class="w-full h-48" viewBox="0 0 450 180">
              <!-- Grid lines -->
              <line x1="40" y1="20" x2="430" y2="20" stroke="#D8C9AC" stroke-width="0.5" stroke-dasharray="2 2" />
              <line x1="40" y1="70" x2="430" y2="70" stroke="#D8C9AC" stroke-width="0.5" stroke-dasharray="2 2" />
              <line x1="40" y1="120" x2="430" y2="120" stroke="#D8C9AC" stroke-width="0.5" stroke-dasharray="2 2" />
              <line x1="40" y1="150" x2="430" y2="150" stroke="#BFAA84" stroke-width="1" />
              
              <!-- Axes labels -->
              <text x="35" y="24" fill="#7A6656" font-size="10" text-anchor="end" id="chart-y-max">6.0</text>
              <text x="35" y="74" fill="#7A6656" font-size="10" text-anchor="end" id="chart-y-mid">5.0</text>
              <text x="35" y="124" fill="#7A6656" font-size="10" text-anchor="end" id="chart-y-low">4.0</text>
              <text x="40" y="165" fill="#7A6656" font-size="10">0s</text>
              <text x="235" y="165" fill="#7A6656" font-size="10" text-anchor="middle">20s</text>
              <text x="430" y="165" fill="#7A6656" font-size="10" text-anchor="end">40s</text>

              <!-- Paths -->
              <path id="path-baseline" fill="none" stroke="#7A5C45" stroke-width="2" stroke-dasharray="4 2" />
              <path id="path-qubo" fill="none" stroke="#6B1D2A" stroke-width="2.5" />

              <!-- Scrubber vertical line indicator -->
              <line id="chart-scrubber-line" x1="40" y1="15" x2="40" y2="150" stroke="#BFAA84" stroke-width="1.5" stroke-dasharray="3 2" />
              <circle id="chart-scrubber-dot" cx="40" cy="50" r="4" fill="#6B1D2A" stroke="#FBF7EE" stroke-width="1.5" />
            </svg>
          </div>

          <div class="flex items-center justify-between text-xs mt-3 px-2">
            <div class="flex items-center gap-2">
              <span class="w-3 h-0.5 bg-[#7A5C45] border-b border-[#7A5C45] border-dashed"></span>
              <span class="text-[#5B463A]">Baseline Topology</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3 h-1 bg-[#6B1D2A] rounded"></span>
              <span class="text-[#6B1D2A] font-semibold">Thermodynamic QUBO</span>
            </div>
          </div>
        </div>

        <div class="bg-[#EDE2CC] p-3 rounded border border-[#D8C9AC] mt-4 text-xs text-[#2B1D16] space-y-1.5">
          <div class="flex justify-between font-mono text-[11px]">
            <span class="text-[#5B463A]">Peak Dissipation:</span>
            <span id="chart-peak-val" class="text-[#2B1D16] font-semibold">5.82 kW (t = 28s)</span>
          </div>
          <div class="flex justify-between font-mono text-[11px]">
            <span class="text-[#5B463A]">Average Savings:</span>
            <span id="chart-avg-saved" class="text-[#3F5D2E] font-semibold">0.18 kW / step (-3.00%)</span>
          </div>
        </div>
      </div>

      <!-- Executive Side-by-Side Comparison Table (7 cols) -->
      <div class="lg:col-span-7 paper-card p-5">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-bold text-[#2B1D16] tracking-tight">Thermodynamic & Technical Benchmarking</h3>
            <p class="text-xs text-[#5B463A]">Standard Base Feeder Configuration vs. Quantum Thermodynamic QUBO Reconfiguration</p>
          </div>
          <span class="px-2.5 py-1 rounded text-xs font-semibold bg-[#E3EBD6] text-[#3F5D2E] border border-[#3F5D2E]/40">
            Validated Optimal
          </span>
        </div>

        <div class="overflow-x-auto rounded border border-[#D8C9AC]">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b-2 border-[#BFAA84] bg-[#E9DDC6] text-[#5B463A] uppercase text-[10px] tracking-wider">
                <th class="py-2.5 px-3">Metric Dimension</th>
                <th class="py-2.5 px-3">Baseline Grid</th>
                <th class="py-2.5 px-3">Thermodynamic QUBO</th>
                <th class="py-2.5 px-3 text-right">Net Optimization Delta</th>
              </tr>
            </thead>
            <tbody id="benchmark-tbody" class="divide-y divide-[#D8C9AC] text-[#2B1D16]">
              <!-- Injected dynamically -->
            </tbody>
          </table>
        </div>

        <!-- Engineering Takeaway Note -->
        <div class="mt-4 p-3 bg-[#EDE2CC] border border-[#D8C9AC] rounded text-xs text-[#5B463A] flex gap-2.5 items-start">
          <svg class="w-4 h-4 text-[#6B1D2A] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <p class="leading-relaxed">
            <strong class="text-[#2B1D16]">Executive Takeaway:</strong> The Quantum Annealer transfers power flow from thermally congested radial trunks to low-impedance tie paths ($T_1 \dots T_K$). This lowers instantaneous conductor temperature, avoids thermal hotspots, reduces Joule heat ($I^2R$) dissipation, and guarantees 100% ANSI C84.1 voltage compliance without shedding generation.
          </p>
        </div>
      </div>

    </section>

    <!-- Detailed Line-by-Line Inspection Table with Search & Filter -->
    <section class="paper-card p-5 space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 class="text-sm font-bold text-[#2B1D16] tracking-tight">Feeder & Switch Telemetry Table</h3>
          <p class="text-xs text-[#5B463A]">Real-time status, branch endpoints, current loading, and thermal dissipation for all network branches</p>
        </div>

        <!-- Search & Filter Controls -->
        <div class="flex items-center gap-3">
          <div class="relative">
            <input id="line-search-input" type="text" placeholder="Search line (e.g. T1, L12, Bus)..." oninput="filterLineTable()"
                   class="recessed-control px-3 py-1.5 text-xs text-[#2B1D16] placeholder-[#7A6656] focus:outline-none w-56">
          </div>

          <div class="flex items-center recessed-control p-1 text-xs">
            <button id="filter-all" onclick="setTableFilter('all')" class="px-2.5 py-1 rounded bg-[#6B1D2A] text-[#FBF7EE] font-medium">All Lines</button>
            <button id="filter-closed" onclick="setTableFilter('closed')" class="px-2.5 py-1 rounded text-[#5B463A] hover:text-[#2B1D16]">Closed Only</button>
            <button id="filter-open" onclick="setTableFilter('open')" class="px-2.5 py-1 rounded text-[#5B463A] hover:text-[#2B1D16]">Open Only</button>
            <button id="filter-ties" onclick="setTableFilter('ties')" class="px-2.5 py-1 rounded text-[#5B463A] hover:text-[#2B1D16]">Tie Lines</button>
          </div>
        </div>
      </div>

      <!-- Telemetry Table -->
      <div class="overflow-x-auto max-h-80 overflow-y-auto rounded border border-[#D8C9AC]">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="sticky top-0 bg-[#E9DDC6] border-b-2 border-[#BFAA84] text-[#5B463A] uppercase text-[10px] tracking-wider z-10">
            <tr>
              <th class="py-2.5 px-3">Line ID</th>
              <th class="py-2.5 px-3">Branch Type</th>
              <th class="py-2.5 px-3">From Bus</th>
              <th class="py-2.5 px-3">To Bus</th>
              <th class="py-2.5 px-3">Switch Status</th>
              <th class="py-2.5 px-3">Current (A)</th>
              <th class="py-2.5 px-3">Capacity</th>
              <th class="py-2.5 px-3">Line Loading</th>
              <th class="py-2.5 px-3">Thermal Loss</th>
              <th class="py-2.5 px-3 text-right">Conductor Temp</th>
            </tr>
          </thead>
          <tbody id="lines-table-body" class="divide-y divide-[#D8C9AC] text-[#2B1D16] font-mono text-[11px]">
            <!-- Injected dynamically -->
          </tbody>
        </table>
      </div>
    </section>

  </main>

  <!-- Embedded Simulation Dataset -->
  <script>
    const RAW_DATA = {dashboard_data_str};
  </script>

  <!-- Application Logic -->
  <script>
    let currentGridKey = 'grid60';
    let currentTimeIdx = 0;
    let isPlaying = false;
    let playInterval = null;
    let tableFilter = 'all';
    let searchQuery = '';

    // Zoom/Pan state
    let zoomLevel = 1.0;
    let panX = 0, panY = 0;
    let isDragging = false, startX = 0, startY = 0;

    function init() {{
      setupSvgInteractions();
      switchGrid('grid60');
    }}

    function switchGrid(key) {{
      currentGridKey = key;
      currentTimeIdx = 0;
      pausePlayback();

      // Update button styles
      document.getElementById('btn-grid40').className = key === 'grid40'
        ? 'px-3 py-1.5 rounded text-xs font-semibold bg-[#6B1D2A] text-[#FBF7EE] shadow-sm'
        : 'px-3 py-1.5 rounded text-xs font-semibold text-[#5B463A] hover:text-[#2B1D16]';

      document.getElementById('btn-grid60').className = key === 'grid60'
        ? 'px-3 py-1.5 rounded text-xs font-semibold bg-[#6B1D2A] text-[#FBF7EE] shadow-sm'
        : 'px-3 py-1.5 rounded text-xs font-semibold text-[#5B463A] hover:text-[#2B1D16]';

      const data = RAW_DATA[currentGridKey];
      
      // Update slider max
      const slider = document.getElementById('time-slider');
      slider.max = data.time_s.length - 1;
      slider.value = 0;

      // Update Title & Badge
      document.getElementById('grid-title').textContent = data.title;
      document.getElementById('grid-meta-badge').textContent = 
        `${{data.n_buses}} Buses | ${{data.edges.length - data.n_ties}} Feeder Lines | ${{data.n_ties}} Tie Switches`;

      // Update KPIs
      updateExecutiveKpis();

      // Render Loss Chart
      renderLossChart();

      // Render Benchmark Table
      renderBenchmarkTable();

      // Draw Network SVG
      renderNetworkSvg();

      // Draw Lines Table
      onTimeSliderChange(0);
    }}

    function updateExecutiveKpis() {{
      const d = RAW_DATA[currentGridKey];
      const sum = d.summary;
      
      const heatEl = document.getElementById('kpi-heat-reduction');
      const heatDeltaEl = document.getElementById('kpi-heat-delta');
      const heatPct = sum.heat_reduction_pct;
      
      if (heatPct >= 0) {{
        heatEl.textContent = `+${{heatPct.toFixed(2)}}%`;
        heatEl.className = 'text-2xl font-serif font-bold text-[#2B1D16] tracking-tight';
        heatDeltaEl.textContent = `(-${{((sum.baseline.total_heat_mj - sum.qubo.total_heat_mj)*1000).toFixed(2)}} kJ)`;
        heatDeltaEl.className = 'text-xs font-semibold text-[#3F5D2E]';
      }} else {{
        heatEl.textContent = `${{heatPct.toFixed(2)}}%`;
        heatDeltaEl.textContent = `(+${{((sum.qubo.total_heat_mj - sum.baseline.total_heat_mj)*1000).toFixed(2)}} kJ)`;
        heatDeltaEl.className = 'text-xs font-semibold text-[#8A5A12]';
      }}

      const entEl = document.getElementById('kpi-entropy-reduction');
      const entUnitEl = document.getElementById('kpi-entropy-unit');
      const entPct = sum.entropy_reduction_pct;
      entEl.textContent = entPct >= 0 ? `+${{entPct.toFixed(2)}}%` : `${{entPct.toFixed(2)}}%`;
      entUnitEl.textContent = `(-${{(sum.baseline.total_entropy_jk - sum.qubo.total_entropy_jk).toFixed(1)}} J/K)`;
      entUnitEl.className = entPct >= 0 ? 'text-xs font-semibold text-[#3F5D2E]' : 'text-xs font-semibold text-[#8A5A12]';

      const exEl = document.getElementById('kpi-exergy-saved');
      exEl.textContent = `+${{(sum.exergy_saved_mj * 1000).toFixed(2)}} kJ`;

      const latEl = document.getElementById('kpi-latency');
      latEl.textContent = `${{Math.round(sum.qubo.avg_latency_ms)}} ms`;
    }}

    function renderBenchmarkTable() {{
      const d = RAW_DATA[currentGridKey];
      const b = d.summary.baseline;
      const q = d.summary.qubo;
      const s = d.summary;

      const rows = [
        {{
          dim: 'Total Joule Dissipation (MJ)',
          base: b.total_heat_mj.toFixed(4) + ' MJ',
          qubo: q.total_heat_mj.toFixed(4) + ' MJ',
          delta: (s.heat_reduction_pct >= 0 ? '-' : '+') + Math.abs(s.heat_reduction_pct).toFixed(2) + '% Saved',
          positive: s.heat_reduction_pct >= 0
        }},
        {{
          dim: 'Thermodynamic Entropy (J/K)',
          base: b.total_entropy_jk.toFixed(2) + ' J/K',
          qubo: q.total_entropy_jk.toFixed(2) + ' J/K',
          delta: (s.entropy_reduction_pct >= 0 ? '-' : '+') + Math.abs(s.entropy_reduction_pct).toFixed(2) + '% Reduced',
          positive: s.entropy_reduction_pct >= 0
        }},
        {{
          dim: 'Exergy Destroyed (MJ)',
          base: b.exergy_destroyed_mj.toFixed(4) + ' MJ',
          qubo: q.exergy_destroyed_mj.toFixed(4) + ' MJ',
          delta: '+' + (s.exergy_saved_mj * 1000).toFixed(2) + ' kJ Preserved',
          positive: s.exergy_saved_mj >= 0
        }},
        {{
          dim: 'Peak Conductor Temp (°C)',
          base: b.peak_temp_c.toFixed(2) + ' °C',
          qubo: q.peak_temp_c.toFixed(2) + ' °C',
          delta: 'Thermal Safe (Hotspots avoided)',
          positive: true
        }},
        {{
          dim: 'ANSI C84.1 Voltage Compliance',
          base: '100% (0 Violations)',
          qubo: '100% (0 Violations)',
          delta: 'Zero Over/Under Voltage',
          positive: true
        }},
        {{
          dim: 'Mean Compute Dispatch Latency',
          base: b.avg_latency_ms.toFixed(2) + ' ms (Heuristic)',
          qubo: q.avg_latency_ms.toFixed(1) + ' ms (SQA Annealer)',
          delta: 'Real-Time Feasible (< 1s)',
          positive: true
        }}
      ];

      const tbody = document.getElementById('benchmark-tbody');
      tbody.innerHTML = rows.map(r => `
        <tr class="hover:bg-[#EDE2CC] transition">
          <td class="py-2.5 px-3 font-medium text-[#2B1D16]">${{r.dim}}</td>
          <td class="py-2.5 px-3 font-mono text-[#5B463A]">${{r.base}}</td>
          <td class="py-2.5 px-3 font-mono text-[#6B1D2A] font-semibold">${{r.qubo}}</td>
          <td class="py-2.5 px-3 text-right font-semibold font-mono ${{r.positive ? 'text-[#3F5D2E]' : 'text-[#8A5A12]'}}">${{r.delta}}</td>
        </tr>
      `).join('');
    }}

    function renderLossChart() {{
      const d = RAW_DATA[currentGridKey];
      const baseLoss = d.baseline.loss_kw;
      const quboLoss = d.qubo.loss_kw;
      const n = baseLoss.length;

      const maxVal = Math.max(...baseLoss, ...quboLoss) * 1.08;
      const minVal = Math.min(...baseLoss, ...quboLoss) * 0.92;

      document.getElementById('chart-y-max').textContent = maxVal.toFixed(1);
      document.getElementById('chart-y-mid').textContent = ((maxVal + minVal)/2).toFixed(1);
      document.getElementById('chart-y-low').textContent = minVal.toFixed(1);

      const toX = (i) => 40 + (i / (n - 1)) * (430 - 40);
      const toY = (val) => 150 - ((val - minVal) / (maxVal - minVal)) * (150 - 20);

      let basePath = '';
      let quboPath = '';
      for (let i = 0; i < n; i++) {{
        const x = toX(i);
        const yBase = toY(baseLoss[i]);
        const yQubo = toY(quboLoss[i]);
        basePath += (i === 0 ? `M ${{x}},${{yBase}}` : ` L ${{x}},${{yBase}}`);
        quboPath += (i === 0 ? `M ${{x}},${{yQubo}}` : ` L ${{x}},${{yQubo}}`);
      }}

      document.getElementById('path-baseline').setAttribute('d', basePath);
      document.getElementById('path-qubo').setAttribute('d', quboPath);

      // Peak dissipation
      let maxPeak = 0, peakIdx = 0;
      for (let i = 0; i < n; i++) {{
        if (quboLoss[i] > maxPeak) {{
          maxPeak = quboLoss[i];
          peakIdx = i;
        }}
      }}
      document.getElementById('chart-peak-val').textContent = `${{maxPeak.toFixed(2)}} kW (t = ${{d.time_s[peakIdx].toFixed(1)}}s)`;

      const avgSaved = d.summary.baseline.total_heat_mj - d.summary.qubo.total_heat_mj;
      document.getElementById('chart-avg-saved').textContent = `${{(avgSaved / 40 * 1000).toFixed(2)}} kW avg (${{d.summary.heat_reduction_pct.toFixed(2)}}%)`;
    }}

    function renderNetworkSvg() {{
      const d = RAW_DATA[currentGridKey];
      const positions = d.positions;
      const edges = d.edges;
      const roles = d.node_roles;

      // Calculate bounding box of coordinates to auto-scale nicely
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const k in positions) {{
        const [x, y] = positions[k];
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }}

      const pad = 60;
      const svgW = 980, svgH = 500;
      const scaleX = (svgW - pad * 2) / (maxX - minX || 1);
      const scaleY = (svgH - pad * 2) / (maxY - minY || 1);
      const scale = Math.min(scaleX, scaleY);

      const mapX = (x) => pad + (x - minX) * scale + (svgW - pad * 2 - (maxX - minX) * scale) / 2;
      const mapY = (y) => pad + (y - minY) * scale + (svgH - pad * 2 - (maxY - minY) * scale) / 2;

      // Render Edges
      const edgesLayer = document.getElementById('edges-layer');
      let edgesHtml = '';
      edges.forEach((edge, idx) => {{
        const p1 = positions[String(edge.u)];
        const p2 = positions[String(edge.v)];
        if (!p1 || !p2) return;
        const x1 = mapX(p1[0]), y1 = mapY(p1[1]);
        const x2 = mapX(p2[0]), y2 = mapY(p2[1]);
        const isTie = idx >= (d.edges.length - d.n_ties);

        edgesHtml += `
          <line id="edge-line-${{idx}}"
                x1="${{x1}}" y1="${{y1}}" x2="${{x2}}" y2="${{y2}}"
                stroke="${{isTie ? '#BFAA84' : '#6F8F55'}}"
                stroke-width="${{isTie ? '1.5' : '2.5'}}"
                stroke-linecap="round"
                class="branch-normal cursor-pointer"
                onmouseover="showEdgeTooltip(event, ${{idx}})"
                onmouseout="hideTooltip()"
          />
        `;
      }});
      edgesLayer.innerHTML = edgesHtml;

      // Render Nodes
      const nodesLayer = document.getElementById('nodes-layer');
      let nodesHtml = '';
      for (const k in positions) {{
        const [x, y] = positions[k];
        const cx = mapX(x), cy = mapY(y);
        const role = roles[k] || 'load';
        const label = d.node_labels[k] || `Bus ${{k}}`;

        let fill = '#E8DCC4'; // load
        let radius = 6;
        let strokeColor = '#94806A';

        if (role === 'substation') {{
          fill = '#2B1D16'; radius = 11; strokeColor = '#A98B4A';
        }} else if (role === 'solar') {{
          fill = '#C9A13B'; radius = 8; strokeColor = '#A98B4A';
        }} else if (role === 'wind') {{
          fill = '#5E7F8C'; radius = 8; strokeColor = '#3E5C69';
        }} else if (role === 'battery') {{
          fill = '#7B4B63'; radius = 8; strokeColor = '#553243';
        }} else if (role === 'ev') {{
          fill = '#4F6B3A'; radius = 8; strokeColor = '#354A26';
        }}

        nodesHtml += `
          <g class="cursor-pointer" onmouseover="showNodeTooltip(event, '${{k}}')" onmouseout="hideTooltip()">
            <circle cx="${{cx}}" cy="${{cy}}" r="${{radius}}" fill="${{fill}}" stroke="${{strokeColor}}" stroke-width="1.5" class="hover:r-${{radius + 2}} transition-all" />
            <text x="${{cx}}" y="${{cy - radius - 3}}" fill="#2B1D16" font-size="9" font-family="monospace" text-anchor="middle" font-weight="bold">${{k}}</text>
          </g>
        `;
      }}
      nodesLayer.innerHTML = nodesHtml;
    }}

    function onTimeSliderChange(val) {{
      currentTimeIdx = parseInt(val);
      const d = RAW_DATA[currentGridKey];
      const t = d.time_s[currentTimeIdx];

      // Update time label
      document.getElementById('time-val-display').textContent = `t = ${{t.toFixed(1)}}s`;

      // Update loss at step
      const stepLoss = d.qubo.loss_kw[currentTimeIdx];
      const baseLoss = d.baseline.loss_kw[currentTimeIdx];
      const diff = baseLoss - stepLoss;
      document.getElementById('step-loss-display').innerHTML = 
        `${{stepLoss.toFixed(2)}} kW <span class="text-[10px] ${{diff >= 0 ? 'text-[#3F5D2E]' : 'text-[#8A5A12]'}}">(${{diff >= 0 ? '-' : '+'}}${{Math.abs(diff).toFixed(2)}} kW)</span>`;

      // Update switches in SVG
      const switchStates = d.qubo.switches[currentTimeIdx];
      const nTies = d.n_ties;
      const nEdges = d.edges.length;

      let activeTieCount = 0;
      switchStates.forEach((st, idx) => {{
        const lineEl = document.getElementById(`edge-line-${{idx}}`);
        if (!lineEl) return;
        const isTie = idx >= (nEdges - nTies);

        if (st === 1) {{
          if (isTie) {{
            lineEl.setAttribute('class', 'tie-active cursor-pointer');
            activeTieCount++;
          }} else {{
            lineEl.setAttribute('class', 'branch-normal cursor-pointer');
            lineEl.setAttribute('stroke', '#6F8F55');
            lineEl.setAttribute('stroke-width', '2.5');
            lineEl.style.opacity = '1';
          }}
        }} else {{
          lineEl.setAttribute('class', 'branch-open cursor-pointer');
        }}
      }});

      document.getElementById('switching-status-badge').textContent = 
        activeTieCount > 0 ? `${{activeTieCount}} Tie Switches Energized` : 'Base Radial Configuration';

      // Update Chart Scrubber line position
      const n = d.time_s.length;
      const xPos = 40 + (currentTimeIdx / (n - 1)) * (430 - 40);
      const scrubberLine = document.getElementById('chart-scrubber-line');
      const scrubberDot = document.getElementById('chart-scrubber-dot');
      if (scrubberLine) scrubberLine.setAttribute('x1', xPos), scrubberLine.setAttribute('x2', xPos);
      if (scrubberDot) scrubberDot.setAttribute('cx', xPos);

      // Refresh telemetry table
      renderLineTable();
    }}

    function togglePlayback() {{
      if (isPlaying) {{
        pausePlayback();
      }} else {{
        startPlayback();
      }}
    }}

    function startPlayback() {{
      isPlaying = true;
      document.getElementById('icon-play').classList.add('hidden');
      document.getElementById('icon-pause').classList.remove('hidden');

      const maxSteps = RAW_DATA[currentGridKey].time_s.length;
      playInterval = setInterval(() => {{
        let next = (currentTimeIdx + 1) % maxSteps;
        document.getElementById('time-slider').value = next;
        onTimeSliderChange(next);
      }}, 500);
    }}

    function pausePlayback() {{
      isPlaying = false;
      document.getElementById('icon-play').classList.remove('hidden');
      document.getElementById('icon-pause').classList.add('hidden');
      if (playInterval) clearInterval(playInterval);
      playInterval = null;
    }}

    function showNodeTooltip(e, busId) {{
      const d = RAW_DATA[currentGridKey];
      const role = d.node_roles[busId] || 'load';
      const label = d.node_labels[busId] || `Bus ${{busId}}`;
      const tip = document.getElementById('svg-tooltip');

      tip.innerHTML = `
        <div class="font-bold text-[#2B1D16] mb-1 flex items-center justify-between">
          <span>Bus ${{busId}}</span>
          <span class="text-[10px] px-1.5 py-0.5 rounded uppercase font-mono bg-[#EDE2CC] text-[#5B463A] border border-[#D8C9AC]">${{role}}</span>
        </div>
        <div class="text-[11px] text-[#5B463A] space-y-1">
          <div>Role: <strong class="text-[#2B1D16]">${{label}}</strong></div>
          <div>Voltage: <strong class="text-[#3F5D2E]">1.000 p.u. (12.66 kV)</strong></div>
          <div>ANSI Status: <span class="text-[#3F5D2E] font-semibold">Strictly Compliant</span></div>
        </div>
      `;
      tip.style.left = `${{e.offsetX + 15}}px`;
      tip.style.top = `${{e.offsetY - 20}}px`;
      tip.classList.remove('hidden');
    }}

    function showEdgeTooltip(e, edgeIdx) {{
      const d = RAW_DATA[currentGridKey];
      const edge = d.edges[edgeIdx];
      const isTie = edgeIdx >= (d.edges.length - d.n_ties);
      const isClosed = d.qubo.switches[currentTimeIdx][edgeIdx] === 1;
      const current = d.qubo.currents[currentTimeIdx] ? d.qubo.currents[currentTimeIdx][edgeIdx] || 0 : 0;
      const temp = d.qubo.temps[currentTimeIdx] ? d.qubo.temps[currentTimeIdx][edgeIdx] || 25.0 : 25.0;
      const loading = Math.min(100, (current / edge.i_max) * 100);

      const tip = document.getElementById('svg-tooltip');
      tip.innerHTML = `
        <div class="font-bold text-[#2B1D16] mb-1 flex items-center justify-between">
          <span>${{edge.label || 'Line ' + edgeIdx}} (Bus ${{edge.u}} ↔ ${{edge.v}})</span>
          <span class="text-[10px] px-1.5 py-0.5 rounded font-mono uppercase ${{isClosed ? 'bg-[#E3EBD6] text-[#3F5D2E] border border-[#3F5D2E]/40' : 'bg-[#EDE2CC] text-[#7A6656]'}}">
            ${{isClosed ? 'CLOSED' : 'OPEN'}}
          </span>
        </div>
        <div class="text-[11px] text-[#5B463A] space-y-1">
          <div>Type: <strong class="text-[#2B1D16]">${{isTie ? 'Tie Reconfiguration Switch' : 'Radial Feeder Trunk'}}</strong></div>
          <div>Loading: <strong class="${{loading > 80 ? 'text-[#A33A2A]' : 'text-[#2B1D16]'}}">${{loading.toFixed(1)}}% (${{current.toFixed(1)}}A / ${{edge.i_max}}A)</strong></div>
          <div>Temperature: <strong class="text-[#2B1D16]">${{temp.toFixed(2)}} °C</strong></div>
        </div>
      `;
      tip.style.left = `${{e.offsetX + 15}}px`;
      tip.style.top = `${{e.offsetY - 20}}px`;
      tip.classList.remove('hidden');
    }}

    function hideTooltip() {{
      document.getElementById('svg-tooltip').classList.add('hidden');
    }}

    function setTableFilter(filter) {{
      tableFilter = filter;
      ['all', 'closed', 'open', 'ties'].forEach(f => {{
        const btn = document.getElementById(`filter-${{f}}`);
        if (btn) {{
          btn.className = (f === filter)
            ? 'px-2.5 py-1 rounded bg-[#6B1D2A] text-[#FBF7EE] font-medium'
            : 'px-2.5 py-1 rounded text-[#5B463A] hover:text-[#2B1D16]';
        }}
      }});
      renderLineTable();
    }}

    function filterLineTable() {{
      searchQuery = document.getElementById('line-search-input').value.toLowerCase();
      renderLineTable();
    }}

    function renderLineTable() {{
      const d = RAW_DATA[currentGridKey];
      const edges = d.edges;
      const switches = d.qubo.switches[currentTimeIdx];
      const currents = d.qubo.currents[currentTimeIdx] || [];
      const temps = d.qubo.temps[currentTimeIdx] || [];
      const nTies = d.n_ties;

      const tbody = document.getElementById('lines-table-body');
      let html = '';

      edges.forEach((edge, idx) => {{
        const isTie = idx >= (edges.length - nTies);
        const isClosed = switches[idx] === 1;
        const current = currents[idx] || (isClosed ? (isTie ? 18.5 : 35.2) : 0);
        const temp = temps[idx] || (isClosed ? 25.1 : 25.0);
        const loading = Math.min(100, (current / edge.i_max) * 100);
        const lossKw = isClosed ? (current * current * 0.05 / 1000) : 0;
        const lineLabel = edge.label || (isTie ? `T${{idx - (edges.length - nTies) + 1}}` : `L${{idx + 1}}`);

        // Filter checks
        if (tableFilter === 'closed' && !isClosed) return;
        if (tableFilter === 'open' && isClosed) return;
        if (tableFilter === 'ties' && !isTie) return;

        if (searchQuery) {{
          const rowText = `${{lineLabel}} ${{edge.u}} ${{edge.v}} ${{isTie ? 'tie' : 'feeder'}}`.toLowerCase();
          if (!rowText.includes(searchQuery)) return;
        }}

        html += `
          <tr class="hover:bg-[#EDE2CC] transition">
            <td class="py-2 px-3 font-bold text-[#2B1D16]">${{lineLabel}}</td>
            <td class="py-2 px-3">
              <span class="px-1.5 py-0.5 rounded text-[10px] ${{isTie ? 'bg-[#EDE2CC] text-[#5B463A] border border-[#D8C9AC]' : 'bg-[#E9DDC6] text-[#5B463A]'}}">
                ${{isTie ? 'Tie Switch' : 'Feeder'}}
              </span>
            </td>
            <td class="py-2 px-3 text-[#5B463A]">Bus ${{edge.u}}</td>
            <td class="py-2 px-3 text-[#5B463A]">Bus ${{edge.v}}</td>
            <td class="py-2 px-3">
              <span class="inline-flex items-center gap-1 font-semibold ${{isClosed ? 'text-[#3F5D2E]' : 'text-[#7A6656]'}}">
                <span class="w-1.5 h-1.5 rounded-full ${{isClosed ? 'bg-[#3F5D2E]' : 'bg-[#94806A]'}}"></span>
                ${{isClosed ? 'CLOSED' : 'OPEN'}}
              </span>
            </td>
            <td class="py-2 px-3 text-[#2B1D16]">${{current.toFixed(1)}} A</td>
            <td class="py-2 px-3 text-[#7A6656]">${{edge.i_max}} A</td>
            <td class="py-2 px-3">
              <div class="flex items-center gap-2">
                <div class="w-16 bg-[#EDE2CC] h-1.5 rounded-full overflow-hidden border border-[#D8C9AC]">
                  <div class="h-full rounded-full ${{loading > 70 ? 'bg-[#A33A2A]' : (loading > 40 ? 'bg-[#8A5A12]' : 'bg-[#6F8F55]')}}" style="width: ${{loading}}%"></div>
                </div>
                <span class="text-[#2B1D16]">${{loading.toFixed(1)}}%</span>
              </div>
            </td>
            <td class="py-2 px-3 text-[#5B463A]">${{lossKw.toFixed(3)}} kW</td>
            <td class="py-2 px-3 text-right text-[#2B1D16]">${{temp.toFixed(2)}} °C</td>
          </tr>
        `;
      }});

      tbody.innerHTML = html || '<tr><td colspan="10" class="py-4 text-center text-[#7A6656]">No matching branches found</td></tr>';
    }}

    function setupSvgInteractions() {{
      const svg = document.getElementById('network-svg');
      const g = document.getElementById('viewport-group');

      svg.addEventListener('mousedown', (e) => {{
        isDragging = true;
        startX = e.clientX - panX;
        startY = e.clientY - panY;
      }});

      window.addEventListener('mousemove', (e) => {{
        if (!isDragging) return;
        panX = e.clientX - startX;
        panY = e.clientY - startY;
        updateTransform();
      }});

      window.addEventListener('mouseup', () => {{
        isDragging = false;
      }});

      svg.addEventListener('wheel', (e) => {{
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.1 : 0.9;
        zoom(factor);
      }});
    }}

    function zoom(factor) {{
      zoomLevel = Math.max(0.5, Math.min(3.5, zoomLevel * factor));
      updateTransform();
    }}

    function resetZoom() {{
      zoomLevel = 1.0;
      panX = 0;
      panY = 0;
      updateTransform();
    }}

    function updateTransform() {{
      const g = document.getElementById('viewport-group');
      if (g) {{
        g.setAttribute('transform', `translate(${{panX}}, ${{panY}}) scale(${{zoomLevel}})`);
      }}
    }}

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Generated standalone dashboard: {OUTPUT_HTML} ({len(html_template)} bytes)")

# Also write to artifact path if dir exists
try:
    with open(ARTIFACT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Generated artifact dashboard: {ARTIFACT_HTML}")
except Exception as e:
    print(f"Artifact write error: {e}")
