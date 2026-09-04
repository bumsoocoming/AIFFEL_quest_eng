#!/usr/bin/env python3
"""Build the compact in-conversation turn-dynamics visualization fragment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = json.loads(args.analysis.read_text(encoding="utf-8"))
    compact = {
        "meta": raw["meta"],
        "series": [
            {
                "d": row["dataset"], "r": row["run"], "t": row["turn"],
                "a": row["agent_id"], "n": row["agent_name"], "s": row["stance"],
                "c": row["confidence"], "x": row["stance_changed"],
            }
            for row in raw["series"]
        ],
        "events": [
            {
                "d": row["dataset"], "r": row["run"], "t": row["target_turn"],
                "a": row["agent_id"], "n": row["agent_name"],
                "p": row["previous_stance"], "q": row["new_stance"], "z": row["delta"],
                "k": row["primary_category_ko"], "cl": row["trigger_clause"],
                "sn": row["source_speaker"], "st": row["source_turn"],
                "rel": row["trigger_persona_relation"], "resp": row["persona_response"],
                "why": row["stance_reason"],
            }
            for row in raw["events"]
        ],
        "agents": [
            {
                "d": row["dataset"], "r": row["run"], "a": row["agent_id"], "n": row["agent_name"],
                "vol": row["total_volatility"], "rate": row["event_rate_per_speech"],
                "flex": row["stance_flexibility"], "assert": row["personality_assertiveness"],
                "agree": row["personality_agreeableness"], "skeptic": row["personality_skepticism"],
                "emotion": row["personality_emotionality"], "evidence": row["configured_evidence_demand"],
            }
            for row in raw["agent_summaries"]
        ],
    }
    data = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    local_d3 = Path(".codex_build/d3-7.9.0.min.js")
    if local_d3.exists():
        d3_tag = "<script>" + local_d3.read_text(encoding="utf-8") + "</script>"
    else:
        d3_tag = '<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'
    template = r'''<div id="turn-dynamics-viz">
  <h2>턴별 입장 변화와 반응 트리거</h2>
  <div class="viz-controls" aria-label="분석 범위 선택">
    <label class="form-label">주제 데이터
      <select id="td-dataset" class="form-select"></select>
    </label>
    <label class="form-label">반복 실행
      <select id="td-run" class="form-select"></select>
    </label>
    <label class="form-label">변화 사건
      <select id="td-event" class="form-select"></select>
    </label>
  </div>

  <div id="td-legend" class="td-legend" aria-label="에이전트 표시 전환"></div>
  <section aria-labelledby="td-step-title">
    <h3 id="td-step-title">입장지수 계단 그래프</h3>
    <div id="td-step" class="td-chart"></div>
    <div id="td-detail" class="card td-detail" aria-live="polite"></div>
  </section>

  <div class="td-facets">
    <section aria-labelledby="td-trigger-title">
      <h3 id="td-trigger-title">어떤 입력이 큰 변화를 만들었나</h3>
      <div id="td-trigger" class="td-chart"></div>
    </section>
    <section aria-labelledby="td-personality-title">
      <h3 id="td-personality-title">성격값 × 실제 변동성</h3>
      <div id="td-personality" class="td-chart"></div>
    </section>
  </div>
  <div id="td-tooltip" class="tooltip" role="tooltip" hidden></div>
</div>

<style>
#turn-dynamics-viz { position:relative; width:100%; color:var(--foreground); }
#turn-dynamics-viz h2 { margin:0 0 12px; font-weight:500; }
#turn-dynamics-viz h3 { margin:18px 0 8px; font-weight:500; }
#turn-dynamics-viz .viz-controls { align-items:end; }
#turn-dynamics-viz .form-label { min-width:180px; }
#turn-dynamics-viz .td-legend { display:flex; flex-wrap:wrap; gap:4px 14px; margin:8px 0; }
#turn-dynamics-viz .td-series-toggle { display:inline-flex; align-items:center; gap:6px; padding:4px 0; border:0; background:transparent; color:var(--foreground); }
#turn-dynamics-viz .td-series-toggle[aria-pressed="false"] { opacity:.45; }
#turn-dynamics-viz .td-swatch { width:12px; height:3px; display:inline-block; background:var(--series); }
#turn-dynamics-viz .td-chart { position:relative; width:100%; min-width:0; }
#turn-dynamics-viz .td-chart svg { display:block; width:100%; overflow:visible; }
#turn-dynamics-viz .td-chart text { fill:var(--foreground); font-size:12px; font-weight:400; }
#turn-dynamics-viz .td-chart .muted { fill:var(--muted-foreground); }
#turn-dynamics-viz .td-chart .domain, #turn-dynamics-viz .td-chart .tick line { stroke:var(--border); }
#turn-dynamics-viz .td-detail { margin-top:8px; padding:12px; }
#turn-dynamics-viz .td-detail-grid { display:grid; grid-template-columns:minmax(120px,.55fr) minmax(0,2.45fr); gap:5px 12px; }
#turn-dynamics-viz .td-detail-grid strong { font-weight:500; }
#turn-dynamics-viz .td-detail-grid span { min-width:0; overflow-wrap:anywhere; }
#turn-dynamics-viz .td-facets { display:grid; grid-template-columns:1fr 1fr; gap:24px; }
#turn-dynamics-viz .td-empty { color:var(--muted-foreground); padding:16px 0; }
#turn-dynamics-viz .tooltip { position:absolute; pointer-events:none; z-index:5; max-width:300px; }
@media (max-width:700px) {
  #turn-dynamics-viz .td-facets { grid-template-columns:1fr; gap:4px; }
  #turn-dynamics-viz .td-detail-grid { grid-template-columns:1fr; gap:2px; }
  #turn-dynamics-viz .form-label { min-width:0; width:100%; }
}
</style>

__D3_TAG__
<script>
(() => {
  const DATA = __DATA__;
  const root = document.getElementById('turn-dynamics-viz');
  const datasetSelect = root.querySelector('#td-dataset');
  const runSelect = root.querySelector('#td-run');
  const eventSelect = root.querySelector('#td-event');
  const legend = root.querySelector('#td-legend');
  const detail = root.querySelector('#td-detail');
  const tooltip = root.querySelector('#td-tooltip');
  const seriesVars = ['--viz-series-1','--viz-series-2','--viz-series-3','--viz-series-4','--viz-series-5','--viz-series-6'];
  const visible = new Set();
  let selectedEvent = null;

  const datasets = Array.from(new Set(DATA.series.map(d => d.d))).sort();
  const datasetLabels = {'elon-musk-five-runs':'일론 머스크','var-ai-referee-five-runs':'VAR·AI 심판'};
  datasets.forEach(d => datasetSelect.add(new Option(datasetLabels[d] || d.replaceAll('-', ' '), d)));

  function selectedRows() {
    return DATA.series.filter(d => d.d === datasetSelect.value && d.r === runSelect.value);
  }
  function selectedEvents() {
    return DATA.events.filter(d => d.d === datasetSelect.value && d.r === runSelect.value);
  }
  function selectedAgents() {
    return Array.from(d3.group(selectedRows(), d => d.a), ([id, rows]) => ({id, name:rows[0].n, rows}));
  }
  function updateRuns() {
    const prior = runSelect.value;
    const runs = Array.from(new Set(DATA.series.filter(d => d.d === datasetSelect.value).map(d => d.r))).sort();
    runSelect.replaceChildren(...runs.map(r => new Option(r, r)));
    runSelect.value = runs.includes(prior) ? prior : runs[0];
    visible.clear();
    selectedAgents().forEach(a => visible.add(a.id));
    updateEvents();
  }
  function updateEvents() {
    const events = selectedEvents();
    eventSelect.replaceChildren(...events.map((e, i) => new Option(`T${e.t} ${e.n} ${e.z > 0 ? '+' : ''}${e.z}점`, String(i))));
    selectedEvent = events[0] || null;
    eventSelect.disabled = !events.length;
    renderAll();
  }
  function renderLegend(agents) {
    legend.replaceChildren();
    agents.forEach((agent, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'td-series-toggle';
      button.setAttribute('aria-pressed', visible.has(agent.id) ? 'true' : 'false');
      button.style.setProperty('--series', `var(${seriesVars[index % seriesVars.length]})`);
      const swatch = document.createElement('span');
      swatch.className = 'td-swatch';
      const label = document.createElement('span');
      label.textContent = agent.name;
      button.append(swatch, label);
      button.addEventListener('click', () => {
        if (visible.has(agent.id) && visible.size > 1) visible.delete(agent.id); else visible.add(agent.id);
        renderAll();
      });
      legend.append(button);
    });
  }
  function showDetail(event) {
    if (!event) {
      detail.innerHTML = '<span class="text-muted">이 실행에서는 기록된 입장 변화가 없습니다.</span>';
      return;
    }
    detail.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'td-detail-grid';
    const rows = [
      ['변화', `T${event.t} ${event.n}: ${event.p > 0 ? '+' : ''}${event.p} → ${event.q > 0 ? '+' : ''}${event.q} (${event.z > 0 ? '+' : ''}${event.z})`],
      ['반응 구절', `“${event.cl}” — ${event.sn} T${event.st}`],
      ['분석', `${event.k} · ${event.rel} · ${event.resp}`],
      ['로그상 이유', event.why],
    ];
    rows.forEach(([label, value]) => {
      const strong = document.createElement('strong'); strong.textContent = label;
      const span = document.createElement('span'); span.textContent = value;
      grid.append(strong, span);
    });
    detail.append(grid);
  }
  function svgBase(container, height, aria) {
    container.replaceChildren();
    const width = Math.max(320, container.clientWidth || 736);
    return {width, svg:d3.select(container).append('svg').attr('viewBox', `0 0 ${width} ${height}`).attr('role','img').attr('aria-label',aria)};
  }
  function drawStep() {
    const container = root.querySelector('#td-step');
    const {width, svg} = svgBase(container, 400, '전역 턴별 네 에이전트 입장지수 계단 그래프');
    const agents = selectedAgents();
    renderLegend(agents);
    if (!agents.length) return;
    const narrow = width < 520;
    const margin = {top:14,right:narrow ? 16 : 28,bottom:54,left:64};
    const innerW = width - margin.left - margin.right;
    const innerH = 400 - margin.top - margin.bottom;
    const maxTurn = d3.max(agents.flatMap(a => a.rows), d => d.t) || 1;
    const x = d3.scaleLinear().domain([0,maxTurn]).range([margin.left, margin.left + innerW]);
    const y = d3.scaleLinear().domain([-100,100]).range([margin.top + innerH, margin.top]);
    const plot = svg.append('g');
    plot.append('rect').attr('data-chart-frame','').attr('x',margin.left).attr('y',margin.top).attr('width',innerW).attr('height',innerH).attr('fill','transparent').attr('stroke','var(--border)');
    plot.selectAll('.grid').data([-100,-50,0,50,100]).join('line').attr('x1',margin.left).attr('x2',margin.left+innerW).attr('y1',d=>y(d)).attr('y2',d=>y(d)).attr('stroke','var(--border)').attr('opacity',d=>d===0?.9:.35);
    const xTicks = narrow ? 4 : 7;
    svg.append('g').attr('transform',`translate(0,${margin.top+innerH})`).call(d3.axisBottom(x).ticks(xTicks).tickFormat(d3.format('d')));
    svg.append('g').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y).tickValues([-100,-50,0,50,100]));
    svg.append('text').attr('class','axis-title').attr('data-axis','x').attr('x',margin.left+innerW/2).attr('y',392).attr('text-anchor','middle').text('전역 대화 턴');
    svg.append('text').attr('class','axis-title').attr('data-axis','y').attr('transform',`translate(16,${margin.top+innerH/2}) rotate(-90)`).attr('text-anchor','middle').text('입장지수 (-100 반대 ↔ +100 찬성)');
    const line = d3.line().x(d=>x(d.t)).y(d=>y(d.s)).curve(d3.curveStepAfter);
    agents.forEach((agent,index) => {
      if (!visible.has(agent.id)) return;
      const color = `var(${seriesVars[index % seriesVars.length]})`;
      plot.append('path').datum(agent.rows).attr('fill','none').attr('stroke',color).attr('stroke-width',2.5).attr('d',line);
    });
    const events = selectedEvents().filter(e => visible.has(e.a));
    const agentIndex = new Map(agents.map((a,i)=>[a.id,i]));
    plot.selectAll('circle.td-event').data(events).join('circle').attr('class','td-event')
      .attr('cx',d=>x(d.t)).attr('cy',d=>y(d.q)).attr('r',d=>selectedEvent===d?7:4.5)
      .attr('fill',d=>`var(${seriesVars[(agentIndex.get(d.a)||0)%seriesVars.length]})`)
      .attr('stroke','var(--background)').attr('stroke-width',2)
      .attr('data-tooltip',d=>`T${d.t} ${d.n}: ${d.p}→${d.q} · ${d.k}`)
      .on('click',(_,d)=>{ selectedEvent=d; const idx=selectedEvents().indexOf(d); eventSelect.value=String(idx); drawStep(); showDetail(d); });

    const guide = plot.append('line').attr('data-chart-hover-guide','').attr('y1',margin.top).attr('y2',margin.top+innerH).attr('stroke','var(--foreground)').attr('opacity',0);
    const hoverLayer = plot.append('g');
    const overlay = plot.append('rect').attr('data-chart-hit','').attr('data-chart-hover-overlay','cross-series')
      .attr('x',margin.left).attr('y',margin.top).attr('width',innerW).attr('height',innerH).attr('fill','transparent');
    function pointerMoved(event) {
      const [px] = d3.pointer(event, svg.node());
      const turn = Math.max(0, Math.min(maxTurn, x.invert(px)));
      guide.attr('x1',x(turn)).attr('x2',x(turn)).attr('opacity',.45);
      hoverLayer.selectAll('*').remove();
      const rows=[];
      agents.filter(a=>visible.has(a.id)).forEach((agent,index)=>{
        const i=Math.max(0,d3.bisector(d=>d.t).right(agent.rows,turn)-1);
        const point=agent.rows[i];
        rows.push(`${agent.name} ${point.s>0?'+':''}${point.s}`);
        hoverLayer.append('circle').attr('data-chart-hover-marker','').attr('cx',x(turn)).attr('cy',y(point.s)).attr('r',4).attr('fill',`var(${seriesVars[index%seriesVars.length]})`);
      });
      tooltip.hidden=false;
      tooltip.textContent=`T${turn.toFixed(1)} · ${rows.join(' · ')}`;
      tooltip.style.left=`${Math.max(0,Math.min(width-290,px+12))}px`;
      tooltip.style.top=`${container.offsetTop+margin.top+8}px`;
    }
    function pointerLeft(){ guide.attr('opacity',0); hoverLayer.selectAll('*').remove(); tooltip.hidden=true; }
    overlay.on('pointermove',pointerMoved).on('pointerleave',pointerLeft).on('click',event=>{
      const [px]=d3.pointer(event,svg.node()); const turn=x.invert(px);
      const nearest=d3.least(events,d=>Math.abs(d.t-turn));
      if(nearest && Math.abs(nearest.t-turn)<1.2){ selectedEvent=nearest; eventSelect.value=String(selectedEvents().indexOf(nearest)); drawStep(); showDetail(nearest); }
    });
  }
  function drawTrigger() {
    const container=root.querySelector('#td-trigger');
    const events=DATA.events.filter(d=>d.d===datasetSelect.value);
    const grouped=Array.from(d3.group(events,d=>d.k),([key,vals])=>({key,n:vals.length,mean:d3.mean(vals,d=>Math.abs(d.z))||0})).sort((a,b)=>b.mean-a.mean);
    const height=Math.max(270,70+grouped.length*34);
    const {width,svg}=svgBase(container,height,'트리거 카테고리별 평균 절대 입장 변화폭');
    if(!grouped.length){container.innerHTML='<div class="td-empty">변화 사건이 없습니다.</div>';return;}
    const margin={top:12,right:28,bottom:52,left:142}; const innerW=width-margin.left-margin.right; const innerH=height-margin.top-margin.bottom;
    const x=d3.scaleLinear().domain([0,(d3.max(grouped,d=>d.mean)||1)*1.15]).nice().range([margin.left,margin.left+innerW]);
    const y=d3.scaleBand().domain(grouped.map(d=>d.key)).range([margin.top,margin.top+innerH]).padding(.32);
    svg.append('rect').attr('data-chart-frame','').attr('x',margin.left).attr('y',margin.top).attr('width',innerW).attr('height',innerH).attr('fill','transparent').attr('stroke','var(--border)');
    svg.append('g').attr('transform',`translate(0,${margin.top+innerH})`).call(d3.axisBottom(x).ticks(width<500?4:6));
    svg.append('g').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0));
    svg.selectAll('rect.td-bar').data(grouped).join('rect').attr('class','td-bar').attr('x',x(0)).attr('y',d=>y(d.key)).attr('width',d=>Math.max(1,x(d.mean)-x(0))).attr('height',y.bandwidth()).attr('fill','var(--viz-series-2)').attr('data-tooltip',d=>`${d.key}: 평균 ${d.mean.toFixed(1)}점, n=${d.n}`);
    svg.selectAll('text.td-value').data(grouped).join('text').attr('class','td-value').attr('x',d=>Math.min(width-4,x(d.mean)+6)).attr('y',d=>(y(d.key)||0)+y.bandwidth()/2+4).attr('text-anchor',d=>x(d.mean)>width-58?'end':'start').text(d=>`${d.mean.toFixed(1)} · n=${d.n}`);
    svg.append('text').attr('class','axis-title').attr('data-axis','x').attr('x',margin.left+innerW/2).attr('y',height-5).attr('text-anchor','middle').text('평균 절대 입장 변화폭 (점)');
    svg.append('text').attr('class','axis-title').attr('data-axis','y').attr('transform',`translate(14,${margin.top+innerH/2}) rotate(-90)`).attr('text-anchor','middle').text('트리거 카테고리');
  }
  function corr(xs,ys){ if(xs.length<3)return 0; const mx=d3.mean(xs),my=d3.mean(ys); const num=d3.sum(xs.map((x,i)=>(x-mx)*(ys[i]-my))); const den=Math.sqrt(d3.sum(xs.map(x=>(x-mx)**2))*d3.sum(ys.map(y=>(y-my)**2))); return den?num/den:0; }
  function drawPersonality() {
    const container=root.querySelector('#td-personality');
    const rows=DATA.agents.filter(d=>d.d===datasetSelect.value);
    const fields=[['flex','입장 유연성'],['assert','주장성'],['agree','친화성'],['skeptic','회의성'],['emotion','감정성'],['evidence','근거 요구']];
    const stats=fields.map(([key,label])=>({key,label,r:corr(rows.map(d=>+d[key]),rows.map(d=>+d.vol))})).sort((a,b)=>Math.abs(b.r)-Math.abs(a.r));
    const height=306; const {width,svg}=svgBase(container,height,'설정 성격값과 실제 총 입장 변동성의 기술적 상관계수');
    const margin={top:12,right:28,bottom:58,left:104}; const innerW=width-margin.left-margin.right; const innerH=height-margin.top-margin.bottom;
    const x=d3.scaleLinear().domain([-1,1]).range([margin.left,margin.left+innerW]); const y=d3.scaleBand().domain(stats.map(d=>d.label)).range([margin.top,margin.top+innerH]).padding(.3);
    svg.append('rect').attr('data-chart-frame','').attr('x',margin.left).attr('y',margin.top).attr('width',innerW).attr('height',innerH).attr('fill','transparent').attr('stroke','var(--border)');
    svg.append('line').attr('x1',x(0)).attr('x2',x(0)).attr('y1',margin.top).attr('y2',margin.top+innerH).attr('stroke','var(--foreground)').attr('opacity',.6);
    svg.append('g').attr('transform',`translate(0,${margin.top+innerH})`).call(d3.axisBottom(x).tickValues([-1,-.5,0,.5,1]));
    svg.append('g').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y).tickSize(0));
    svg.selectAll('rect.td-corr').data(stats).join('rect').attr('class','td-corr').attr('x',d=>Math.min(x(0),x(d.r))).attr('y',d=>y(d.label)).attr('width',d=>Math.abs(x(d.r)-x(0))).attr('height',y.bandwidth()).attr('fill',d=>d.r>=0?'var(--viz-series-3)':'var(--viz-series-4)').attr('data-tooltip',d=>`${d.label}: r=${d.r.toFixed(2)} (실행×에이전트 n=${rows.length})`);
    svg.selectAll('text.td-corr-value').data(stats).join('text').attr('class','td-corr-value').attr('x',d=>x(d.r)+(d.r>=0?6:-6)).attr('y',d=>(y(d.label)||0)+y.bandwidth()/2+4).attr('text-anchor',d=>d.r>=0?'start':'end').text(d=>d.r.toFixed(2));
    svg.append('text').attr('class','axis-title').attr('data-axis','x').attr('x',margin.left+innerW/2).attr('y',height-18).attr('text-anchor','middle').text('Pearson r · 총 입장 변동성 (기술통계)');
    svg.append('text').attr('class','axis-title').attr('data-axis','y').attr('transform',`translate(14,${margin.top+innerH/2}) rotate(-90)`).attr('text-anchor','middle').text('설정 성격·행동값');
  }
  function renderAll(){ drawStep(); drawTrigger(); drawPersonality(); showDetail(selectedEvent); }
  datasetSelect.addEventListener('change',updateRuns);
  runSelect.addEventListener('change',updateEvents);
  eventSelect.addEventListener('change',()=>{ selectedEvent=selectedEvents()[+eventSelect.value]||null; renderAll(); });
  new ResizeObserver(()=>renderAll()).observe(root);
  updateRuns();
})();
</script>
'''
    output = template.replace("__DATA__", data).replace("__D3_TAG__", d3_tag)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"bytes={args.output.stat().st_size}")
    print(args.output)


if __name__ == "__main__":
    main()
