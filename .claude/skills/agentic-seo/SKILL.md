---
name: agentic-seo
description: "Agentic SEO / Agentic Engine Optimization tools. Audit SEO, identify issues, generate action plans."
---

# agentic-seo

[![npm version](https://img.shields.io/npm/v/agentic-seo.svg)](https://www.npmjs.com/package/agentic-seo)
[![npm downloads](https://img.shields.io/npm/dm/agentic-seo.svg)](https://www.npmjs.com/package/agentic-seo)
[![license](https://img.shields.io/npm/l/agentic-seo.svg)](https://github.com/addyosmani/agentic-seo/blob/main/LICENSE)
[![node](https://img.shields.io/node/v/agentic-seo.svg)](https://nodejs.org)
[![GitHub stars](https://img.shields.io/github/stars/addyosmani/agentic-seo.svg?style=social)](https://github.com/addyosmani/agentic-seo)

Audit your documentation and website for **Agentic Engine Optimization (AEO)**: ensure your content is discoverable, parseable, and useful to AI coding agents.

AI coding agents like Claude Code, Cursor, Cline, and Aider consume documentation fundamentally differently from humans. They issue single HTTP requests, strip HTML, count tokens, and either use your content as context or silently discard it. `agentic-seo` checks whether your documentation is ready for this new reality.

## Quick Start

```bash
# Audit current directory (auto-detects framework)
npx agentic-seo

# Audit a specific directory
npx agentic-seo ./my-docs-site

# Audit a live URL
npx agentic-seo --url https://docs.example.com

# Scaffold missing AEO files
npx agentic-seo init
```

## Règles d'utilisation pour Claude Code
- Quand l'utilisateur demande un audit SEO ou AEO, exécute `npx agentic-seo` dans le répertoire du projet.
- Quand l'utilisateur demande de scaffold les fichiers AEO, exécute `npx agentic-seo init`.
- Quand l'utilisateur demande d'auditer une URL live, exécute `npx agentic-seo --url <URL>`.
- Signale toujours le score final et les checks en échec.

## What It Checks

`agentic-seo` runs 10 checks across 5 categories, scoring your site out of 100:

### Discovery (25 points)
| Check | Points | What it looks for |
|---|---|---|
| `robots-txt` | 10 | AI crawlers not blocked, explicit allow rules |
| `llms-txt` | 10 | Structured index with descriptions and token counts |
| `agents-md` | 5 | AGENTS.md/CLAUDE.md with project context |

### Content Structure (25 points)
| Check | Points | What it looks for |
|---|---|---|
| `content-structure` | 15 | Heading hierarchy, semantic HTML, code examples, tables |
| `markdown-availability` | 10 | Markdown source available, low HTML noise, no JS dependency |

### Token Economics (25 points)
| Check | Points | What it looks for |
|---|---|---|
| `token-budget` | 15 | Per-page token counts, no oversized pages |
| `meta-tags` | 10 | AI-friendly meta tags, descriptions, token count metadata |

### Capability Signaling (15 points)
| Check | Points | What it looks for |
|---|---|---|
| `skill-md` | 10 | Capability descriptions, inputs, constraints |
| `agent-permissions` | 5 | Agent access rules and rate limits |

### UX Bridge (10 points)
| Check | Points | What it looks for |
|---|---|---|
| `copy-for-ai` | 10 | Copy-for-AI buttons, copy-to-clipboard, raw view links |

## Grading

| Grade | Score | Meaning |
|---|---|---|
| **A** | 90-100% | Excellent agent readiness |
| **B** | 75-89% | Good with minor improvements needed |
| **C** | 60-74% | Functional but missing key signals |
| **D** | 40-59% | Significant gaps in agent readiness |
| **F** | 0-39% | Not optimized for AI agents |

## Installation

```bash
# Global install
npm install -g agentic-seo

# Or use npx (no install needed)
npx agentic-seo
```

## Usage

### Audit a Local Directory

```bash
# Auto-detects framework (Next.js, Docusaurus, 11ty, Astro, Hugo, etc.)
agentic-seo ./my-project

# Explicitly specify build output directory
agentic-seo --output-dir ./my-project/build
```

Supported frameworks: Next.js, Docusaurus, Eleventy, Astro, Hugo, Jekyll, Gatsby, VitePress, MkDocs, Sphinx, Vite.

### Audit with Local Server

```bash
# Spin up a server and run HTTP-based checks
agentic-seo --serve ./build
```

### Audit a Live URL

```bash
agentic-seo --url https://docs.example.com
```

### CI Mode

```bash
# Exit with code 1 if score below threshold
agentic-seo --json --threshold 60

# Just the score
agentic-seo score --json
```

### Scaffold AEO Files

```bash
# Create missing llms.txt, AGENTS.md, skill.md, agent-permissions.json
agentic-seo init
```

### Run Specific Checks

```bash
agentic-seo --checks robots-txt,llms-txt,token-budget
```

## Configuration

Create `.aeorc.json` in your project root, or add an `"aeo"` key to `package.json`:

```json
{
  "outputDir": "_site",
  "checks": {
    "token-budget": { "maxTokensPerPage": 25000 },
    "robots-txt": { "requiredAgents": ["ClaudeBot", "GPTBot"] }
  },
  "ignore": ["**/node_modules/**", "**/vendor/**"],
  "threshold": 60
}
```

## Programmatic API

```js
import { audit, auditWithServer } from 'agentic-seo';

// Audit a directory
const report = await audit('./my-site');
console.log(report.grade);      // 'B'
console.log(report.percentage);  // 78
console.log(report.findings.errors); // [{ severity: 'error', message: '...' }]

// Audit with a local server
const report2 = await auditWithServer('./build');

// Access individual checkers
import { checkers } from 'agentic-seo';
```

## How It Works

`agentic-seo` does not require an API key. All checks are structural and heuristic:

1. **Framework Detection**: Auto-detects your build tool and locates the output directory
2. **File Analysis**: Checks for `robots.txt`, `llms.txt`, `AGENTS.md`, `skill.md`, and `agent-permissions.json`
3. **Content Analysis**: Parses HTML with Cheerio and Markdown with Remark to evaluate structure
4. **Token Counting**: Uses `gpt-tokenizer` to measure real token counts per page
5. **Agent Simulation**: Evaluates what AI agents would actually see when fetching your pages

## CLI Options

```
Options:
  --url, -u         Audit a live URL
  --serve, -s       Start local server and audit via HTTP
  --json            Output results as JSON
  --verbose, -v     Show all findings including info messages
  --threshold, -t   Minimum score percentage (exit 1 if below)
  --checks          Comma-separated checker IDs to run
  --output-dir      Explicitly specify build output directory
  --help            Show help
  --version         Show version
```

## Where to Start

If you're new to AEO, here's the recommended priority order:

1. **Audit robots.txt**: Prevents silent agent lockout (10 min)
2. **Add llms.txt**: Immediate discoverability gains (a few hours)
3. **Measure token counts**: High-leverage insight into page sizes (weekend project)
4. **Write skill.md**: Start with your most-used APIs
5. **Add "Copy for AI" buttons**: Low effort, high signal for human+agent workflows
6. **Set up AI traffic monitoring**: Gives you data to justify further investment

## Disclaimer

This is not an official Google project and is not endorsed by Google or Google Search. The concepts, checks, and recommendations in this tool are a best-effort community offering based on publicly available research and emerging practices around AI agent documentation consumption. Scores and recommendations should be taken as directional guidance, not as guarantees of any particular outcome.

## License

MIT
