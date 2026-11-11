#!/usr/bin/env python3
"""Download and verify the curated thesis literature corpus.

The manifest is intentionally code-local so the download remains reproducible.
Run: python3 download_literature.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path(__file__).resolve().parent / "literature_manifest.json"
INDEX = ROOT / "00_文献清单.md"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

ENTRIES = [
    # 01 surveys and foundations
    dict(cat="01_综述与基础", slug="2402.16968_survey-llm-cybersecurity",
         title="A Survey of Large Language Models in Cybersecurity", year=2024,
         venue="arXiv", kind="arxiv", aid="2402.16968",
         note="LLM 在网络安全中的应用全景与挑战。"),
    dict(cat="01_综述与基础", slug="2507.13629_llm-cybersecurity-applications",
         title="Large Language Models in Cybersecurity: Applications, Vulnerabilities, and Defense Techniques", year=2025,
         venue="arXiv / MDPI AI", kind="arxiv", aid="2507.13629",
         note="应用、漏洞与防御技术的系统梳理。"),
    dict(cat="01_综述与基础", slug="2512.06659_evolution-agentic-ai",
         title="The Evolution of Agentic AI in Cybersecurity: From Single LLM Reasoners to Multi-Agent Systems and Autonomous Pipelines", year=2025,
         venue="arXiv", kind="arxiv", aid="2512.06659",
         note="单智能体到多智能体/自治流水线的演进脉络。"),
    dict(cat="01_综述与基础", slug="2601.05293_survey-agentic-ai-cybersecurity",
         title="A Survey of Agentic AI and Cybersecurity: Challenges, Opportunities and Use-case Prototypes", year=2026,
         venue="arXiv", kind="arxiv", aid="2601.05293",
         note="agentic AI 与网络安全的挑战、机会与原型。"),
    dict(cat="01_综述与基础", slug="2505.12786_forewarned-forearmed",
         title="Forewarned is Forearmed: A Survey on Large Language Model-based Agents in Autonomous Cyberattacks", year=2025,
         venue="arXiv", kind="arxiv", aid="2505.12786",
         note="攻击侧 LLM agent 综述，用于威胁建模与风险边界。"),
    dict(cat="01_综述与基础", slug="2510.23883_agentic-ai-security",
         title="Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges", year=2025,
         venue="arXiv", kind="arxiv", aid="2510.23883",
         note="智能体自身安全：prompt injection、工具/记忆投毒与评测。"),
    dict(cat="01_综述与基础", slug="2303.04926_automated-cyber-defence-review",
         title="Automated Cyber Defence: A Review", year=2023,
         venue="arXiv", kind="arxiv", aid="2303.04926",
         note="自主网络防御的早期系统综述。"),
    dict(cat="01_综述与基础", slug="2405.04760_llm-cybersecurity-slr",
         title="Large Language Models for Cyber Security: A Systematic Literature Review", year=2024,
         venue="arXiv / ACM TOSEM", kind="arxiv", aid="2405.04760",
         note="185 篇文献的系统综述；覆盖面与分类框架主参考。"),
    dict(cat="01_综述与基础", slug="2608.28490_llm-agents-security-slr",
         title="LLM-Based Agents for Software and Systems Security: Approaches, Applications, and Assessment", year=2026,
         venue="arXiv", kind="arxiv", aid="2608.28490",
         note="关键结论：agent 能行动但尚缺 bounded authority 与可审计性。"),
    dict(cat="01_综述与基础", slug="jcp-2026-llm-agents-cybersecurity-review",
         title="LLM-Based Agents for Cybersecurity: A Systematic Review of Architectures, Applications, and Open Challenges", year=2026,
         venue="Journal of Cybersecurity and Privacy 6(5):159", kind="url",
         url="https://mdpi-res.com/d_attachment/jcp/jcp-06-00159/article_deploy/jcp-06-00159.pdf",
         doi="10.3390/jcp6050159",
         note="PRISMA 综述：59 项研究；渗透测试 50.8%；单智能体 30.5%；集中式多智能体 18.6% 但性能增益最高；无 E4 生产级评测。"),
    dict(cat="01_综述与基础", slug="2210.03629_react",
         title="ReAct: Synergizing Reasoning and Acting in Language Models", year=2022,
         venue="ICLR 2023 / arXiv", kind="arxiv", aid="2210.03629",
         note="推理-行动循环的 agent 基础范式。"),
    dict(cat="01_综述与基础", slug="2307.16789_toolllm",
         title="ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs", year=2023,
         venue="ICLR 2024 / arXiv", kind="arxiv", aid="2307.16789",
         note="大规模工具调用与 API 编排基础。"),
    dict(cat="01_综述与基础", slug="2308.08155_autogen",
         title="AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation", year=2023,
         venue="arXiv", kind="arxiv", aid="2308.08155",
         note="多智能体对话编排框架参考。"),
    dict(cat="01_综述与基础", slug="2303.11366_reflexion",
         title="Reflexion: Language Agents with Verbal Reinforcement Learning", year=2023,
         venue="NeurIPS 2023 / arXiv", kind="arxiv", aid="2303.11366",
         note="语言化反思与自我改进机制。"),
    dict(cat="01_综述与基础", slug="2308.03688_agentbench",
         title="AgentBench: Evaluating LLMs as Agents", year=2023,
         venue="ICLR 2024 / arXiv", kind="arxiv", aid="2308.03688",
         note="agent 能力评测框架基础。"),

    # 02 LLM agents and security operations
    dict(cat="02_LLM智能体与安全运营", slug="2412.00652_multi-agent-incident-response",
         title="Multi-Agent Collaboration in Incident Response with Large Language Models", year=2024,
         venue="arXiv", kind="arxiv", aid="2412.00652",
         note="AutoBnB：多智能体协作的网络安全事件响应。"),
    dict(cat="02_LLM智能体与安全运营", slug="2512.14846_malcdf",
         title="MALCDF: A Distributed Multi-Agent LLM Framework for Real-Time Cyber", year=2025,
         venue="arXiv", kind="arxiv", aid="2512.14846",
         note="实时网络防御的分布式多智能体 LLM 框架。"),
    dict(cat="02_LLM智能体与安全运营", slug="2505.04843_llm-autonomous-cyber-defenders",
         title="Large Language Models are Autonomous Cyber Defenders", year=2025,
         venue="arXiv", kind="arxiv", aid="2505.04843",
         note="LLM 作为自治防御者的可行性证据。"),
    dict(cat="02_LLM智能体与安全运营", slug="chatsoc-2025",
         title="ChatSOC: A Large Language Model Powered Autonomous Agent for Security Operations Center", year=2025,
         venue="PoS ISGC2025 488,009", kind="url",
         url="https://pos.sissa.it/488/009/pdf",
         doi="10.22323/1.488.0009",
         note="IHEP 实际部署的 LLM 事件响应系统，含人机协同与评测。"),
    dict(cat="02_LLM智能体与安全运营", slug="info-2025-soar-agentic-ai",
         title="Toward Robust Security Orchestration and Automated Response in Security Operations Centers with a Hyper-Automation Approach Using Agentic Artificial Intelligence", year=2025,
         venue="Information 16(5):365", kind="url",
         url="https://mdpi-res.com/d_attachment/information/information-16-00365/article_deploy/information-16-00365.pdf",
         doi="10.3390/info16050365",
         note="SOAR + agentic AI 的可信集成框架（IVAM）。"),

    # 03 autonomous cyber defence
    dict(cat="03_自主网络防御", slug="2410.09114_3cb",
         title="Catastrophic Cyber Capabilities Benchmark (3CB): Robustly Evaluating LLM Agent Cyber Offense Capabilities", year=2024,
         venue="arXiv", kind="arxiv", aid="2410.09114",
         note="攻击能力上限评测，用于风险与伦理边界。"),
    dict(cat="03_自主网络防御", slug="2509.14589_atlantis",
         title="ATLANTIS: AI-driven Threat Localization, Analysis, and Triage Intelligence System", year=2025,
         venue="arXiv", kind="arxiv", aid="2509.14589",
         note="AI 驱动的威胁定位、分析与研判系统。"),
    dict(cat="03_自主网络防御", slug="2504.21039_foundation-sec-8b",
         title="Llama-3.1-FoundationAI-SecurityLLM-Base-8B Technical Report", year=2025,
         venue="arXiv", kind="arxiv", aid="2504.21039",
         note="安全领域基础模型；可作为本地推理底座。"),
    dict(cat="03_自主网络防御", slug="2508.01059_foundation-sec-8b-instruct",
         title="Llama-3.1-FoundationAI-SecurityLLM-8B-Instruct Technical Report", year=2025,
         venue="arXiv", kind="arxiv", aid="2508.01059",
         note="安全领域指令微调模型。"),
    dict(cat="03_自主网络防御", slug="2602.07666_sok-aixcc",
         title="SoK: DARPA's AI Cyber Challenge (AIxCC): Competition Design, Architectures, and Lessons Learned", year=2026,
         venue="arXiv", kind="arxiv", aid="2602.07666",
         note="AIxCC 系统架构与工程经验，含自治修复管线。"),
    dict(cat="03_自主网络防御", slug="2408.08926_cybench",
         title="Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models", year=2024,
         venue="arXiv", kind="arxiv", aid="2408.08926",
         note="攻防任务基准，作为替代方向对照。"),

    # 04 evaluation and benchmarks
    dict(cat="04_评测与基准", slug="2506.00739_defenderbench",
         title="DefenderBench: A Toolkit for Evaluating Language Agents in Cybersecurity Environments", year=2025,
         venue="arXiv", kind="arxiv", aid="2506.00739",
         note="防御侧 agent 工具包与评测环境。"),
    dict(cat="04_评测与基准", slug="2506.02548_cybergym",
         title="CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale", year=2025,
         venue="arXiv", kind="arxiv", aid="2506.02548",
         note="大规模真实漏洞场景 agent 评测。"),
    dict(cat="04_评测与基准", slug="2510.24317_caibench",
         title="Cybersecurity AI Benchmark (CAIBench): A Meta-Benchmark for Evaluating Cybersecurity AI Agents", year=2025,
         venue="arXiv", kind="arxiv", aid="2510.24317",
         note="网络安全 AI agent 元基准。"),
    dict(cat="04_评测与基准", slug="2507.14201_excytin-bench",
         title="ExCyTIn-Bench: Evaluating LLM agents on Cyber Threat Investigation", year=2025,
         venue="arXiv", kind="arxiv", aid="2507.14201",
         note="威胁调查评测；最佳约 0.606 reward，说明开放调查仍难。"),
    dict(cat="04_评测与基准", slug="2604.12040_sir-bench",
         title="SIR-Bench: Evaluating Investigation Depth in Security Incident Response Agents", year=2026,
         venue="arXiv", kind="arxiv", aid="2604.12040",
         note="事件响应调查深度；指出 alert parroting 问题。"),
    dict(cat="04_评测与基准", slug="2606.10281_auditbench",
         title="Benchmarking and Exploring the Capabilities of LLMs for Attack Investigations", year=2026,
         venue="arXiv", kind="arxiv", aid="2606.10281",
         note="攻击调查能力基准。"),
    dict(cat="04_评测与基准", slug="2604.19533_cyber-defense-benchmark",
         title="Cyber Defense Benchmark: Agentic Threat Hunting Evaluation for LLMs in SecOps", year=2026,
         venue="arXiv", kind="arxiv", aid="2604.19533",
         note="开放威胁狩猎极难：报告约 3.8% recall。"),
    dict(cat="04_评测与基准", slug="2604.24184_dynamic-cyber-ranges",
         title="Dynamic Cyber Ranges", year=2026,
         venue="arXiv", kind="arxiv", aid="2604.24184",
         note="动态网络靶场，用于可复现实验环境设计。"),

    # 06 Chinese literature
    dict(cat="06_中文文献", slug="cn-2025-alert-triage-agent",
         title="告警研判智能体系统研究", year=2025,
         venue="信息安全研究 11(E2):39", kind="url",
         url="http://www.sicris.cn/CN/article/downloadArticleFile.do?attachType=PDF&id=2088",
         referer="http://www.sicris.cn/CN/abstract/abstract2088.shtml",
         note="中文核心：ReAct + 代码提示 + 自一致性，告警研判智能体。"),
    dict(cat="06_中文文献", slug="cn-2024-genai-soc-noise-reduction",
         title="生成式人工智能赋能网络安全运营降噪能力研究", year=2024,
         venue="信息通信技术与政策 50(8):24-31", kind="url",
         url="http://ictp.caict.ac.cn/CN/article/downloadArticleFile.do?attachType=PDF&id=1271",
         referer="http://ictp.caict.ac.cn/CN/Y2024/V50/I8/24",
         doi="10.12267/j.issn.2096-5931.2024.08.004",
         note="中文核心：生成式 AI 用于安全运营告警降噪。"),
]


def pdf_url(entry: dict) -> str:
    if entry["kind"] == "arxiv":
        return f"https://arxiv.org/pdf/{entry['aid']}"
    return entry["url"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 20_000:
        return False
    with path.open("rb") as f:
        return f.read(5) == b"%PDF-"


def load_manifest() -> dict:
    if MANIFEST.exists():
        try:
            data = json.loads(MANIFEST.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "entries" in data:
                return data
        except json.JSONDecodeError:
            pass
    return {"generated_at": None, "entries": []}


def upsert(manifest: dict, item: dict) -> None:
    entries = manifest["entries"]
    for i, old in enumerate(entries):
        if old.get("slug") == item["slug"]:
            entries[i] = item
            break
    else:
        entries.append(item)


def safe_write_json(manifest: dict) -> None:
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    tmp = MANIFEST.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(MANIFEST)


def write_index(manifest: dict) -> None:
    rows = sorted(manifest["entries"], key=lambda x: (x.get("cat", ""), x.get("year", 0), x.get("title", "")))
    lines = [
        "# 文献清单",
        "",
        f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}；以 `90_元数据与笔记/literature_manifest.json` 为准。",
        "",
        "| # | 分类 | 标题 | 年份 | 来源 | 状态 | 大小 | 文件 | 备注 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, e in enumerate(rows, 1):
        title = str(e.get("title", "")).replace("|", "\\|")
        venue = str(e.get("venue", "")).replace("|", "\\|")
        note = str(e.get("note", "")).replace("|", "\\|")
        size = e.get("bytes", 0)
        size_s = f"{size/1024/1024:.1f} MB" if size else "-"
        status = e.get("status", "pending")
        file_s = f"`{e.get('path', '')}`" if e.get("path") else "-"
        lines.append(
            f"| {i} | {e.get('cat','')} | {title} | {e.get('year','')} | {venue} | {status} | {size_s} | {file_s} | {note} |"
        )
    lines += ["", "## 说明", "", "- `ok`：已下载并通过 `%PDF-` 头与大小校验。", "- `failed`：下载失败，元数据保留，可后续人工补齐。", "- `metadata-only`：付费/受限，仅保留题录。"]

    # preserve any manually written notes below the auto block
    old = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    marker = "\n## 人工笔记\n"
    manual = old.split(marker, 1)[1] if marker in old else ""
    text = "\n".join(lines) + ("\n## 人工笔记\n" + manual if manual else "\n")
    INDEX.write_text(text, encoding="utf-8")


def main() -> int:
    session = requests.Session()
    manifest = load_manifest()
    ok = failed = skipped = 0

    for n, entry in enumerate(ENTRIES, 1):
        cat = entry["cat"]
        dest = ROOT / cat / f"{entry['slug']}.pdf"
        rel = str(dest.relative_to(ROOT))
        item = {
            "slug": entry["slug"],
            "title": entry["title"],
            "year": entry["year"],
            "venue": entry.get("venue", ""),
            "cat": cat,
            "kind": entry["kind"],
            "doi": entry.get("doi", ""),
            "arxiv": entry.get("aid", ""),
            "source_url": pdf_url(entry),
            "path": rel,
            "note": entry.get("note", ""),
        }

        if valid_pdf(dest):
            item.update(status="ok", bytes=dest.stat().st_size, sha256=sha256(dest))
            upsert(manifest, item)
            skipped += 1
            print(f"[{n:02d}/{len(ENTRIES)}] SKIP {rel}", flush=True)
            continue

        headers = {"User-Agent": UA, "Accept": "application/pdf,*/*"}
        if entry.get("referer"):
            headers["Referer"] = entry["referer"]
        tmp = dest.with_suffix(".pdf.part")
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with session.get(pdf_url(entry), headers=headers, stream=True, timeout=90, allow_redirects=True) as r:
                item["http_status"] = r.status_code
                item["final_url"] = r.url
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                ctype = r.headers.get("content-type", "")
                with tmp.open("wb") as f:
                    for chunk in r.iter_content(1024 * 256):
                        if chunk:
                            f.write(chunk)
            if not valid_pdf(tmp):
                head = tmp.read_bytes()[:200].decode("utf-8", "replace")
                tmp.unlink(missing_ok=True)
                raise RuntimeError(f"not a PDF (ctype={ctype!r}, head={head[:100]!r})")
            tmp.replace(dest)
            item.update(status="ok", bytes=dest.stat().st_size, sha256=sha256(dest),
                        content_type=ctype,
                        downloaded_at=datetime.now(timezone.utc).isoformat())
            ok += 1
            print(f"[{n:02d}/{len(ENTRIES)}] OK   {rel} ({dest.stat().st_size/1024/1024:.1f} MB)", flush=True)
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            item.update(status="failed", error=str(exc)[:500],
                        attempted_at=datetime.now(timezone.utc).isoformat())
            failed += 1
            print(f"[{n:02d}/{len(ENTRIES)}] FAIL {rel}: {exc}", flush=True)
        upsert(manifest, item)
        safe_write_json(manifest)
        time.sleep(0.3)

    safe_write_json(manifest)
    write_index(manifest)
    print(f"\nDONE ok={ok} skipped={skipped} failed={failed} total={len(ENTRIES)}", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
