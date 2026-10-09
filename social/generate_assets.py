#!/usr/bin/env python3
"""Generate the editable SVG sources and optimized PNG exports for the social package."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import shutil
import subprocess
import textwrap

from PIL import Image


ROOT = Path(__file__).resolve().parent
W, H, SAFE = 1080, 1350, 72
FONT = "Arial, Helvetica, sans-serif"
BG, PANEL, PANEL_2, LINE = "#07101d", "#0d192b", "#12213a", "#29405f"
TEXT, MUTED = "#f3f7ff", "#9fb1cc"
CYAN, VIOLET, AMBER, GREEN, RED = "#53e0d0", "#8492ff", "#f4c768", "#4ad5a5", "#ff7188"


@dataclass
class Canvas:
    parts: list[str]

    @classmethod
    def create(cls) -> "Canvas":
        return cls([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            "<defs>",
            '<linearGradient id="bgGlow" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#15274a"/><stop offset=".52" stop-color="#07101d"/><stop offset="1" stop-color="#091522"/></linearGradient>',
            '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#53e0d0"/><stop offset="1" stop-color="#8492ff"/></linearGradient>',
            '<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#263954" stroke-opacity=".28"/></pattern>',
            '<filter id="glow"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
            "</defs>",
            f'<rect width="{W}" height="{H}" fill="url(#bgGlow)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>',
            '<circle cx="940" cy="90" r="210" fill="#8492ff" opacity=".06"/><circle cx="90" cy="1170" r="250" fill="#53e0d0" opacity=".04"/>',
        ])

    def add(self, raw: str) -> None:
        self.parts.append(raw)

    def rect(self, x: float, y: float, w: float, h: float, *, fill=PANEL, stroke=LINE, radius=18,
             sw=2, opacity=1.0) -> None:
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, color=LINE, sw=3, dash="") -> None:
        dash_attr=f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{dash_attr}/>' )

    def circle(self, x: float, y: float, r: float, *, fill=CYAN, stroke="none", sw=0, opacity=1.0) -> None:
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d: str, *, stroke=CYAN, sw=4, fill="none", opacity=1.0, dash="") -> None:
        dash_attr=f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{dash_attr}/>' )

    def text(self, x: float, y: float, value: str, *, size=38, fill=TEXT, weight=500,
             anchor="start", letter=0) -> None:
        self.add(f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{letter}">{escape(value)}</text>')

    def multiline(self, x: float, y: float, lines: list[str] | tuple[str, ...], *, size=40, fill=TEXT,
                  weight=500, line_height=1.22, anchor="start") -> float:
        spans=[]
        for index, line in enumerate(lines):
            dy="0" if index == 0 else f"{size*line_height:.1f}"
            spans.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
        self.add(f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{"".join(spans)}</text>')
        return y + (len(lines)-1)*size*line_height

    def finish(self) -> str:
        return "\n".join([*self.parts, "</svg>", ""])


def wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False)


def header(c: Canvas, series: str, index: int, total: int, headline: str, *, kicker="PERSENSEAI · SYNTHETIC RESEARCH") -> float:
    c.circle(94, 84, 22, fill="url(#accent)")
    c.text(94, 96, "P", size=34, fill=BG, weight=900, anchor="middle")
    c.text(132, 94, "PersenseAI", size=36, weight=800)
    c.text(1008, 94, f"{index:02d} / {total:02d}", size=34, fill=MUTED, weight=700, anchor="end")
    c.text(SAFE, 170, kicker, size=34, fill=CYAN, weight=800, letter=2)
    headline_lines=wrap(headline, 27)
    end=c.multiline(SAFE, 248, headline_lines, size=72 if len(headline_lines)<=2 else 62, weight=800, line_height=1.05)
    c.line(SAFE, end+42, 1008, end+42, color=LINE, sw=2)
    return end+86


def footer(c: Canvas, series: str, index: int, total: int, *, disclaimer="Synthetic · inspectable · bounded") -> None:
    c.line(SAFE, 1266, 1008, 1266, color=LINE, sw=2)
    disclaimer_lines=disclaimer.splitlines()
    if len(disclaimer_lines)>1:
        c.multiline(SAFE,1294,disclaimer_lines,size=34,fill=MUTED,weight=600,line_height=1.0)
    else:
        c.text(SAFE,1315,disclaimer,size=34,fill=MUTED,weight=600)
        c.text(1008,1315,f"{series.upper()}  ·  {index}/{total}",size=34,fill=CYAN,weight=700,anchor="end")


def card(c: Canvas, x: float, y: float, w: float, h: float, title: str, body: str = "", *,
         accent=CYAN, selected=False, title_size=38, body_size=34) -> None:
    c.rect(x,y,w,h,fill="#15253d" if selected else PANEL,stroke=accent if selected else LINE,radius=18,sw=3 if selected else 2)
    c.rect(x,y,10,h,fill=accent,stroke=accent,radius=5,sw=0)
    c.text(x+32,y+52,title,size=title_size,fill=TEXT,weight=750)
    if body:
        body_lines=[]
        for paragraph in body.splitlines():
            body_lines.extend(wrap(paragraph,max(16,int((w-60)/(body_size*.55)))))
        c.multiline(x+32,y+100,body_lines,size=body_size,fill=MUTED,weight=500,line_height=1.18)


def chip(c: Canvas, x: float, y: float, label: str, *, color=CYAN, w: float | None=None, size=34) -> float:
    width=w or max(120, 30+len(label)*19)
    c.rect(x,y,width,54,fill="#14243a",stroke=color,radius=27,sw=2)
    c.text(x+width/2,y+38,label,size=size,fill=color,weight=700,anchor="middle")
    return width


def arrow(c: Canvas, x1: float, y: float, x2: float, *, color=VIOLET) -> None:
    c.line(x1,y,x2,y,color=color,sw=4)
    c.path(f"M{x2-16} {y-12} L{x2} {y} L{x2-16} {y+12}",stroke=color,sw=4)


def pipeline_slide(index: int) -> str:
    titles=[
        "From observations to grounded reasoning",
        "1. Multimodal inputs become observations",
        "2. Visual Reward Timeline",
        "3. Evidence Graph Timeline",
        "4. Evidence Utility Timeline",
        "5. Evidence Orchestration Agent",
        "6. Answer — or stop honestly",
        "One pipeline. Four inspectable research modules.",
    ]
    c=Canvas.create(); y=header(c,"Pipeline",index,8,titles[index-1])
    if index==1:
        c.multiline(SAFE,y,wrap("A visual research pipeline for turning video, images, text, audio, and sensor signals into inspectable evidence, uncertainty, and bounded conclusions.",52),size=40,fill=MUTED,line_height=1.28)
        labels=[("VIDEO",CYAN),("IMAGE",VIOLET),("TEXT",AMBER),("AUDIO",GREEN),("SENSOR",RED)]
        base_y=700
        for i,(label,color) in enumerate(labels):
            yy=base_y+i*88;c.rect(SAFE,yy,218,62,fill=PANEL_2,stroke=color,radius=14,sw=2);c.text(181,yy+43,label,size=34,fill=color,weight=750,anchor="middle")
            c.path(f"M290 {yy+31} C430 {yy+31} 480 930 600 930",stroke=color,sw=4,opacity=.85)
        c.rect(600,820,408,240,fill=PANEL,stroke=VIOLET,radius=26,sw=3)
        c.text(804,876,"UNIFIED TIMELINE",size=34,fill=CYAN,weight=800,anchor="middle")
        c.line(650,944,960,944,color=LINE,sw=5)
        for x,color in [(680,CYAN),(750,VIOLET),(820,AMBER),(890,GREEN),(950,RED)]:c.circle(x,944,14,fill=color)
        c.multiline(804,1002,["observations", "→ evidence"],size=34,fill=TEXT,weight=700,line_height=1.08,anchor="middle")
    elif index==2:
        c.multiline(SAFE,y,wrap("Five distinct streams become structured evidence cards with entities, events, time, confidence, and provenance.",50),size=40,fill=MUTED)
        modalities=[("VIDEO","entity · 1.0s",CYAN),("IMAGE","event · 1.4s",VIOLET),("TEXT","claim · 2.0s",AMBER),("AUDIO","event · 2.4s",GREEN),("SENSOR","state · 2.8s",RED)]
        for i,(name,meta,color) in enumerate(modalities):
            yy=630+i*104
            c.rect(SAFE,yy,936,82,fill=PANEL,stroke=color,radius=18,sw=2)
            c.rect(SAFE,yy,10,82,fill=color,stroke=color,radius=5,sw=0)
            c.text(104,yy+54,name,size=34,weight=750)
            c.text(976,yy+54,meta,size=34,fill=MUTED,weight=650,anchor="end")
        c.text(540,1192,"confidence  ·  provenance  ·  timestamp",size=36,fill=CYAN,weight=700,anchor="middle")
    elif index==3:
        c.text(SAFE,y,"RESEARCH QUESTION",size=34,fill=CYAN,weight=800);c.text(SAFE,y+56,"What changed over time?",size=46,weight=750)
        c.multiline(SAFE,y+128,wrap("Dense progress and failure signals keep temporal behavior visible instead of reducing a sequence to one final score.",49),size=38,fill=MUTED)
        for i in range(5):
            x=SAFE+i*188;c.rect(x,720,168,160,fill=["#16344a","#1a314a","#233049","#37293a","#183a3a"][i],stroke=LINE,radius=14)
            c.text(x+84,816,f"t{i+1}",size=34,fill=MUTED,weight=700,anchor="middle")
        c.line(SAFE,1000,1008,1000,color=LINE,sw=3)
        c.path("M72 1090 C180 1070 240 990 340 1018 S500 1110 610 950 S790 850 1008 900",stroke=CYAN,sw=8)
        c.line(610,920,610,1130,color=RED,sw=4,dash="14 12");c.text(630,1150,"failure marker",size=34,fill=RED,weight=700)
        c.text(SAFE,960,"PROGRESS REWARD",size=34,fill=CYAN,weight=800)
    elif index==4:
        c.text(SAFE,y,"RESEARCH QUESTION",size=34,fill=CYAN,weight=800);c.multiline(SAFE,y+60,["What supports or contradicts", "the hypothesis?"],size=46,weight=750,line_height=1.08)
        c.multiline(SAFE,y+180,wrap("Observations remain connected to source IDs, frames, timestamps, events, claims, and provenance.",49),size=38,fill=MUTED)
        nodes=[(180,840,"01",GREEN),(310,1010,"A",GREEN),(540,850,"H",VIOLET),(770,1010,"B",RED),(900,820,"04",AMBER)]
        for x1,y1,x2,y2,color in [(180,840,310,1010,GREEN),(310,1010,540,850,GREEN),(540,850,770,1010,RED),(770,1010,900,820,AMBER)]:c.line(x1,y1,x2,y2,color=color,sw=5)
        for x0,y0,label,color in nodes:
            c.circle(x0,y0,54,fill=PANEL_2,stroke=color,sw=5);c.text(x0,y0+12,label,size=34,fill=color,weight=750,anchor="middle")
        chip(c,180,1130,"SUPPORT",color=GREEN,w=220);chip(c,430,1130,"UNRESOLVED",color=AMBER,w=260);chip(c,720,1130,"CONTRADICT",color=RED,w=260)
    elif index==5:
        c.text(SAFE,y,"RESEARCH QUESTION",size=34,fill=CYAN,weight=800)
        c.multiline(SAFE,y+56,["Which observation actually", "changed the conclusion?"],size=41,weight=750,line_height=1.08)
        c.multiline(SAFE,y+158,wrap("Information gain, uncertainty reduction, redundancy, counterfactual contribution, cost, and provenance stay visible.",52),size=37,fill=MUTED)
        rows=[("SNS-201","2.78",.92,GREEN,"decisive"),("VID-101","1.16",.58,CYAN,"useful"),("AUD-701","1.00",.48,VIOLET,"cross-modal"),("VID-103","0.11",.12,RED,"redundant")]
        for i,(eid,value,fraction,color,label) in enumerate(rows):
            yy=690+i*126
            c.text(SAFE,yy+38,eid,size=36,weight=750)
            c.text(SAFE,yy+78,label,size=34,fill=MUTED,weight=650)
            c.rect(300,yy+10,570,62,fill="#162238",stroke=LINE,radius=14)
            c.rect(300,yy+10,570*fraction,62,fill=color,stroke=color,radius=14,sw=0,opacity=.82)
            c.text(1008,yy+54,value,size=36,fill=color,weight=850,anchor="end")
        c.multiline(SAFE,1192,["Redundancy lowers modeled utility;", "provenance remains visible."],size=34,fill=MUTED,weight=600,line_height=1.08)
    elif index==6:
        c.text(SAFE,y,"RESEARCH QUESTION",size=34,fill=CYAN,weight=800);c.text(SAFE,y+56,"What should the system inspect next?",size=45,weight=750)
        c.multiline(SAFE,y+128,wrap("A bounded utility-driven agent selects registered tools, updates structured state, tracks budget, handles contradiction, and replans.",50),size=38,fill=MUTED)
        card(c,SAFE,700,292,190,"CANDIDATES","ranked value\n+ cost",accent=VIOLET,title_size=34)
        card(c,394,700,292,190,"SELECTED","inspect sensor\nevent",accent=CYAN,selected=True,title_size=34)
        card(c,716,700,292,190,"TOOL RESULT","available\n+ cited",accent=GREEN,title_size=34)
        arrow(c,365,792,390);arrow(c,687,792,712)
        c.rect(SAFE,940,936,190,fill=PANEL,stroke=LINE,radius=20)
        c.text(106,998,"STATE UPDATE",size=34,fill=CYAN,weight=800)
        labels=[("support","0.50 → 0.84",GREEN),("uncertainty","1.00 → 0.62",AMBER),("budget","10 → 8 steps",VIOLET)]
        for i,(label,value,color) in enumerate(labels):
            x=106+i*300;c.text(x,1060,label,size=34,fill=MUTED,weight=650);c.text(x,1110,value,size=36,fill=color,weight=800)
    elif index==7:
        c.multiline(SAFE,y,wrap("The pipeline returns a grounded answer only when citations, provenance, uncertainty, and contradiction conditions are satisfied.",50),size=39,fill=MUTED)
        card(c,SAFE,650,448,440,"GROUNDED ANSWER","Citations complete\nProvenance sufficient\nContradictions resolved",accent=GREEN,selected=True,title_size=40,body_size=36)
        card(c,560,650,448,440,"INCONCLUSIVE STOP","Required modality missing\nBudget exhausted\nConflict unresolved",accent=AMBER,selected=True,title_size=40,body_size=36)
        c.text(296,1142,"answer with citations",size=34,fill=GREEN,weight=700,anchor="middle")
        c.text(784,1142,"do not fabricate",size=34,fill=AMBER,weight=700,anchor="middle")
    else:
        modules=[("01","Visual Reward Timeline",CYAN),("02","Evidence Graph Timeline",GREEN),("03","Evidence Utility Timeline",AMBER),("04","Evidence Orchestration Agent",VIOLET)]
        for i,(num,name,color) in enumerate(modules):
            yy=550+i*128;c.rect(SAFE,yy,936,98,fill=PANEL,stroke=color,radius=18,sw=2);c.text(112,yy+64,num,size=36,fill=color,weight=850);c.text(200,yy+64,name,size=39,weight=750)
        c.multiline(SAFE,1080,["How should evidence-seeking systems", "measure progress?"],size=44,weight=800,line_height=1.08)
        c.text(SAFE,1192,"Explore the interactive demos at persenseai.com",size=36,fill=CYAN,weight=750)
    if index==7:
        footer(c,"Pipeline",index,8,disclaimer="Deterministic utility-driven policy.\nNo language model is used for planning.")
    elif index==8:
        footer(c,"Pipeline",index,8,disclaimer="Synthetic deterministic research prototypes.\nNo forensic, operational, or legal validity is claimed.")
    else:
        footer(c,"Pipeline",index,8,disclaimer="Synthetic · inspectable")
    return c.finish()


def agent_slide(index: int) -> str:
    titles=[
        "Not every agent action is progress",
        "The agent begins with a bounded goal",
        "It ranks possible next actions",
        "It selects one registered tool",
        "The result updates the investigation",
        "Positive progress reward",
        "Penalties prevent fake progress",
        "The reward-driven agent can be much more selective",
        "Continue, answer, or stop inconclusive",
    ]
    c=Canvas.create();y=header(c,"Agent Progress Reward",index,9,titles[index-1],kicker="PERSENSEAI · AGENT PROGRESS REWARD")
    if index==1:
        c.multiline(SAFE,y,wrap("More steps, more tools, and more evidence do not automatically produce a better answer.",49),size=40,fill=MUTED)
        c.text(SAFE,650,"NOISY ROUTE",size=34,fill=RED,weight=800)
        noisy=[(120,760),(260,700),(390,820),(520,720),(660,850),(800,730),(960,800)]
        for a,b in zip(noisy,noisy[1:]):c.line(*a,*b,color=RED,sw=4,dash="12 10")
        for i,(x0,y0) in enumerate(noisy):c.circle(x0,y0,28,fill=PANEL_2,stroke=RED,sw=4);c.text(x0,y0+11,str(i+1),size=34,fill=RED,weight=800,anchor="middle")
        c.text(SAFE,940,"GROUNDED ROUTE",size=34,fill=GREEN,weight=800)
        route=[(130,1060),(430,1015),(720,1070),(960,1008)]
        for a,b in zip(route,route[1:]):c.line(*a,*b,color=GREEN,sw=7)
        for i,(x0,y0) in enumerate(route):c.circle(x0,y0,34,fill=GREEN);c.text(x0,y0+12,str(i+1),size=34,fill=BG,weight=900,anchor="middle")
        c.text(540,1165,"fewer actions · grounded resolution",size=36,fill=GREEN,weight=750,anchor="middle")
    elif index==2:
        c.rect(SAFE,y,936,650,fill=PANEL,stroke=VIOLET,radius=24,sw=3);c.text(110,y+66,"STRUCTURED AGENT STATE",size=36,fill=CYAN,weight=800)
        fields=[("HYPOTHESIS","Parcel entered Zone B",CYAN),("AVAILABLE EVIDENCE","VID-A1 · VID-A2",TEXT),("UNCERTAINTY","1.00",AMBER),("CONTRADICTIONS","none",GREEN),("PROVENANCE","0.91",VIOLET),("STEP BUDGET","12",TEXT),("COST BUDGET","2.10",TEXT)]
        for i,(label,value,color) in enumerate(fields):
            yy=y+125+i*69;c.text(110,yy,label,size=34,fill=MUTED,weight=700);c.text(960,yy,value,size=34,fill=color,weight=750,anchor="end");c.line(110,yy+22,960,yy+22,color="#20344f",sw=2)
        c.multiline(SAFE,1122,["Explicit goal · finite tools", "Finite budget · inspectable memory"],size=35,fill=CYAN,weight=700,line_height=1.08)
    elif index==3:
        c.multiline(SAFE,y,wrap("Each candidate exposes expected value, cost, latency, and structured reason codes.",49),size=39,fill=MUTED)
        rows=[("inspect sensor","2.15",".20",".8s",GREEN),("inspect visual","1.96",".12",".5s",CYAN),("test contradiction","1.84",".03",".3s",RED),("run counterfactual","1.52",".05",".6s",VIOLET),("compare modes","0.75",".03",".4s",CYAN),("request evidence","0.62",".06","1.2s",AMBER),("answer","0.41",".00",".1s",GREEN),("stop","0.10",".00",".1s",MUTED)]
        for i,(name,value,cost,latency,color) in enumerate(rows):
            yy=570+i*72
            c.rect(SAFE,yy,936,60,fill=PANEL_2 if i==0 else PANEL,stroke=color if i==0 else LINE,radius=12,sw=3 if i==0 else 1)
            c.text(100,yy+42,f"{i+1}",size=34,fill=color,weight=850)
            c.text(160,yy+42,name,size=34,weight=700)
            c.text(740,yy+42,value,size=34,fill=color,weight=800,anchor="end")
            c.text(865,yy+42,f"c {cost}",size=34,fill=MUTED,weight=650,anchor="end")
            c.text(980,yy+42,f"l {latency}",size=34,fill=MUTED,weight=650,anchor="end")
        c.text(SAFE,1195,"REASON CODES  ·  EXPECTED_UTILITY  ·  NOVEL_MODALITY",size=34,fill=CYAN,weight=700)
    elif index==4:
        c.multiline(SAFE,y,wrap("No arbitrary shell access, unrestricted execution, or hidden action space.",48),size=40,fill=MUTED)
        card(c,SAFE,650,264,190,"STATE","typed\n+ bounded",accent=VIOLET,title_size=34)
        card(c,376,650,264,190,"CANDIDATES","valid tools\nonly",accent=AMBER,title_size=34)
        card(c,680,650,328,190,"SELECTED","inspect sensor\nevent",accent=CYAN,selected=True,title_size=34)
        arrow(c,340,746,370);arrow(c,644,746,674)
        c.rect(SAFE,900,936,220,fill=PANEL,stroke=GREEN,radius=22,sw=3)
        c.text(110,960,"STRUCTURED TOOL RESULT",size=36,fill=GREEN,weight=800)
        c.text(110,1028,"available: true",size=38,weight=750);c.text(540,1028,"citation: SNS-A3",size=38,weight=750)
        c.text(110,1085,"→ update graph, uncertainty, provenance, budget",size=35,fill=MUTED,weight=650)
    elif index==5:
        c.text(SAFE,y,"ONE TOOL RESULT · TWO STATES",size=34,fill=CYAN,weight=800)
        c.text(270,y+90,"BEFORE",size=38,fill=MUTED,weight=750,anchor="middle");c.text(810,y+90,"AFTER",size=38,fill=GREEN,weight=750,anchor="middle")
        for offset,color in [(0,VIOLET),(1,GREEN),(2,AMBER)]:
            c.circle(160+offset*100,750+(offset%2)*90,34,fill=PANEL_2,stroke=color,sw=4)
            c.circle(700+offset*100,735+(offset%2)*80,34,fill=PANEL_2,stroke=color,sw=4)
        c.line(160,750,260,840,color=VIOLET,sw=4);c.line(260,840,360,750,color=GREEN,sw=4)
        c.line(700,735,800,815,color=GREEN,sw=5);c.line(800,815,900,735,color=GREEN,sw=5);c.line(700,735,900,735,color=CYAN,sw=5)
        arrow(c,450,800,630,color=CYAN)
        updates=[("SUPPORT","0.50 → 0.84",GREEN),("UNCERTAINTY","1.00 → 0.62",AMBER),("CONTRADICTION","open → resolved",RED),("PROVENANCE","0.91 → 0.95",VIOLET),("BUDGET","10 → 8 steps",CYAN)]
        for i,(label,value,color) in enumerate(updates):
            yy=940+i*58
            c.text(SAFE,yy,label,size=34,fill=MUTED,weight=700)
            c.text(1008,yy,value,size=36,fill=color,weight=850,anchor="end")
    elif index==6:
        positives=[("uncertainty reduction",.84,CYAN),("information gain",.72,VIOLET),("grounded claim",.64,GREEN),("provenance",.55,AMBER),("contradiction resolved",.78,GREEN),("cross-modal",.60,CYAN),("answer coverage",.48,VIOLET),("graph connectivity",.40,AMBER),("cited answer",.88,GREEN)]
        c.text(SAFE,y,"TRANSPARENT CONTRIBUTIONS",size=34,fill=CYAN,weight=800)
        for i,(label,value,color) in enumerate(positives):
            yy=y+60+i*67;c.text(SAFE,yy+36,label,size=34,fill=TEXT,weight=650);c.rect(520,yy,420,46,fill="#16243a",stroke=LINE,radius=10,sw=1);c.rect(520,yy,420*value,46,fill=color,stroke=color,radius=10,sw=0,opacity=.82);c.text(1008,yy+36,f"+{value:.2f}",size=34,fill=color,weight=800,anchor="end")
        c.text(SAFE,1185,"Positive total rises when the state becomes better grounded.",size=34,fill=GREEN,weight=700)
    elif index==7:
        penalties=[("redundant evidence",.86),("repeated tool call",.68),("unsupported claim",.90),("collection cost",.46),("latency",.38),("wasted budget",.58),("unresolved contradiction",.82),("premature stop",.92),("failed tool",.74)]
        c.text(SAFE,y,"NEGATIVE CONTRIBUTIONS",size=34,fill=RED,weight=800)
        for i,(label,value) in enumerate(penalties):
            yy=y+60+i*67;c.text(SAFE,yy+36,label,size=34,fill=TEXT,weight=650);c.rect(520,yy,420,46,fill="#241a2a",stroke=LINE,radius=10,sw=1);c.rect(940-420*value,yy,420*value,46,fill=RED,stroke=RED,radius=10,sw=0,opacity=.78);c.text(1008,yy+36,f"−{value:.2f}",size=34,fill=RED,weight=800,anchor="end")
        c.text(SAFE,1185,"Penalties make repetition and unsupported output visible.",size=34,fill=AMBER,weight=700)
    elif index==8:
        c.text(SAFE,y,"VERIFIED REDUNDANT-FRAME SCENARIO",size=34,fill=CYAN,weight=800)
        c.rect(SAFE,y+70,448,430,fill=PANEL,stroke=MUTED,radius=24,sw=2);c.text(296,y+135,"FIXED PIPELINE",size=36,fill=MUTED,weight=800,anchor="middle");c.text(296,y+270,"12",size=112,fill=TEXT,weight=900,anchor="middle");c.text(296,y+325,"steps",size=38,fill=MUTED,weight=650,anchor="middle");c.text(296,y+420,"cost 1.44",size=44,fill=RED,weight=800,anchor="middle")
        c.rect(560,y+70,448,430,fill=PANEL_2,stroke=GREEN,radius=24,sw=4);c.text(784,y+135,"UTILITY-DRIVEN AGENT",size=34,fill=GREEN,weight=800,anchor="middle");c.text(784,y+270,"4",size=112,fill=GREEN,weight=900,anchor="middle");c.text(784,y+325,"steps",size=38,fill=MUTED,weight=650,anchor="middle");c.text(784,y+420,"cost 0.32",size=44,fill=GREEN,weight=800,anchor="middle")
        c.multiline(SAFE,y+580,wrap("Comparable supported state: one useful frame inspected instead of a burst of repeated frames.",49),size=39,fill=TEXT,weight=650)
        c.rect(SAFE,1050,936,180,fill="#281f19",stroke=AMBER,radius=16,sw=2)
        c.text(104,1094,"HONESTY NOTE",size=34,fill=AMBER,weight=800)
        c.text(104,1136,"The agent is not always cheaper.",size=34,fill=TEXT,weight=650)
        c.text(104,1178,"Contradiction resolution may require",size=34,fill=TEXT,weight=650)
        c.text(104,1220,"additional steps and tools.",size=34,fill=TEXT,weight=650)
    else:
        c.text(SAFE,y,"BOUNDED NEXT DECISION",size=34,fill=CYAN,weight=800)
        center=(540,800);c.circle(*center,112,fill=PANEL_2,stroke=VIOLET,sw=5);c.multiline(540,780,["CURRENT", "STATE"],size=36,weight=850,line_height=1.1,anchor="middle")
        options=[("INSPECT",190,650,CYAN),("VERIFY",190,950,RED),("COMPARE",540,1080,VIOLET),("REQUEST",890,950,AMBER),("ANSWER",890,650,GREEN)]
        for label,x0,y0,color in options:
            c.line(540,800,x0,y0,color=color,sw=4);c.circle(x0,y0,68,fill=PANEL,stroke=color,sw=4);c.text(x0,y0+12,label,size=34,fill=color,weight=800,anchor="middle")
        c.rect(250,1105,580,68,fill="#262218",stroke=AMBER,radius=34,sw=3);c.text(540,1151,"STOP INCONCLUSIVE",size=36,fill=AMBER,weight=850,anchor="middle")
        c.text(540,1218,"Explore the bounded agent demo at persenseai.com",size=34,fill=CYAN,weight=750,anchor="middle")
        c.multiline(SAFE,535,["Grounded resolution — not support", "for a preferred conclusion."],size=35,fill=MUTED,weight=650,line_height=1.08)
    if index==9:
        footer(c,"Agent Reward",index,9,disclaimer="Deterministic utility-driven policy.\nNo language model is used for planning.")
    else:
        footer(c,"Agent Reward",index,9,disclaimer="Deterministic · no LLM planning")
    return c.finish()


def pipeline_cheatsheet() -> str:
    c=Canvas.create();header(c,"Cheatsheet",1,1,"PersenseAI Multimodal Reasoning Pipeline",kicker="PERSENSEAI · CHEAT SHEET")
    stages=[("INPUTS",["Video · Images · Text · Audio · Sensors"],CYAN),("OBSERVATIONS",["Entities · Events · Time · Confidence · Provenance"],VIOLET),("TEMPORAL EVALUATION",["Visual Reward · Progress · Failure Signals"],AMBER),("EVIDENCE REASONING",["Evidence Graph · Support · Contradiction"],GREEN),("UTILITY",["Information Gain · Uncertainty · Redundancy","Counterfactuals"],CYAN),("AGENT",["Select Tool · Update State · Replan","Track Budget · Stop"],VIOLET),("OUTPUT",["Grounded Answer  or  Inconclusive Stop"],GREEN)]
    y=410
    for i,(title,body_lines,color) in enumerate(stages):
        box_h=120 if len(body_lines)>1 else 96
        c.rect(SAFE,y,936,box_h,fill=PANEL,stroke=color,radius=16,sw=2)
        c.text(104,y+38,title,size=34,fill=color,weight=850)
        c.multiline(104,y+76,body_lines,size=34,fill=TEXT,weight=600,line_height=1.0)
        if i<len(stages)-1:c.line(540,y+box_h,540,y+box_h+12,color=color,sw=4)
        y+=box_h+12
    footer(c,"Pipeline Cheatsheet",1,1,disclaimer="Synthetic, inspectable, bounded research prototypes\npersenseai.com")
    return c.finish()


def reward_cheatsheet() -> str:
    c=Canvas.create();header(c,"Cheatsheet",1,1,"Agent Progress Reward",kicker="PERSENSEAI · CHEAT SHEET")
    c.text(SAFE,440,"Agent action → Tool result → State change",size=35,fill=TEXT,weight=750)
    c.text(SAFE,490,"→ Progress reward → Next action or stop",size=35,fill=CYAN,weight=750)
    c.rect(SAFE,545,470,450,fill=PANEL,stroke=GREEN,radius=22,sw=3);c.text(104,600,"POSITIVE REWARD",size=36,fill=GREEN,weight=850)
    positive=["uncertainty reduction","information gain","grounded claims","provenance completeness","contradiction resolution","cross-modal corroboration","answer coverage","useful graph connectivity","cited grounded answer"]
    for i,label in enumerate(positive):c.text(108,654+i*39,"+  "+label,size=30,fill=TEXT,weight=600)
    c.rect(566,545,442,450,fill=PANEL,stroke=RED,radius=22,sw=3);c.text(598,600,"PENALTIES",size=36,fill=RED,weight=850)
    negative=["redundant evidence","repeated actions","unsupported claims","cost","latency","wasted budget","unresolved contradiction","premature stopping","failed tool calls"]
    for i,label in enumerate(negative):c.text(602,654+i*39,"−  "+label,size=30,fill=TEXT,weight=600)
    c.text(SAFE,1038,"DECIDE",size=34,fill=CYAN,weight=850)
    chip(c,80,1060,"CONTINUE",color=CYAN,w=200)
    chip(c,296,1060,"REQUEST EVIDENCE",color=AMBER,w=330,size=30)
    chip(c,642,1060,"TEST CONTRADICTION",color=RED,w=358,size=30)
    chip(c,210,1128,"ANSWER",color=GREEN,w=260)
    chip(c,494,1128,"STOP INCONCLUSIVE",color=VIOLET,w=440,size=30)
    c.multiline(SAFE,1214,wrap("Reward measures grounded resolution, not whether the agent confirms the original hypothesis.",61),size=34,fill=MUTED,weight=650)
    footer(c,"Reward Cheatsheet",1,1,disclaimer="Deterministic bounded agent · no LLM planning\nSynthetic evidence")
    return c.finish()


def write_sources() -> list[tuple[Path,Path,str]]:
    outputs=[]
    pipeline_source=ROOT/"pipeline-carousel"/"source";pipeline_png=ROOT/"pipeline-carousel"/"png"
    agent_source=ROOT/"agent-reward-carousel"/"source";agent_png=ROOT/"agent-reward-carousel"/"png"
    cheat_source=ROOT/"cheatsheets"/"source";cheat_png=ROOT/"cheatsheets"/"png"
    for directory in (pipeline_source,pipeline_png,agent_source,agent_png,cheat_source,cheat_png):directory.mkdir(parents=True,exist_ok=True)
    for index in range(1,9):
        source=pipeline_source/f"slide-{index:02d}.svg";png=pipeline_png/f"pipeline-{index:02d}.png";source.write_text(pipeline_slide(index),encoding="utf-8");outputs.append((source,png,"pipeline carousel"))
    for index in range(1,10):
        source=agent_source/f"slide-{index:02d}.svg";png=agent_png/f"agent-reward-{index:02d}.png";source.write_text(agent_slide(index),encoding="utf-8");outputs.append((source,png,"agent reward carousel"))
    for name,svg in (("persenseai-pipeline-cheatsheet",pipeline_cheatsheet()),("agent-progress-reward-cheatsheet",reward_cheatsheet())):
        source=cheat_source/f"{name}.svg";png=cheat_png/f"{name}.png";source.write_text(svg,encoding="utf-8");outputs.append((source,png,"cheatsheet"))
    return outputs


def render_png(source: Path, output: Path, chrome: str) -> None:
    output.parent.mkdir(parents=True,exist_ok=True)
    render_height=H+120
    command=[chrome,"--headless=new","--no-sandbox","--disable-gpu","--disable-background-networking","--no-first-run",
             "--hide-scrollbars","--force-device-scale-factor=1",f"--window-size={W},{render_height}",f"--screenshot={output.resolve()}",source.resolve().as_uri()]
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=30)
    if result.returncode:raise RuntimeError(result.stderr)
    with Image.open(output) as image:
        if image.size!=(W,render_height):raise ValueError(f"Unexpected render size for {output}: {image.size}")
        rgb=image.convert("RGB").crop((0,0,W,H));rgb.save(output,"PNG",optimize=True,compress_level=9)


def main() -> None:
    chrome=shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:raise SystemExit("A local Chromium-compatible browser is required for PNG export.")
    outputs=write_sources()
    for source,png,_ in outputs:render_png(source,png,chrome)
    print(f"Generated {len(outputs)} SVG sources and {len(outputs)} optimized RGB PNG exports.")


if __name__=="__main__":main()
