---
name: feedback-git-commit-push-orchestrator
description: "2026-07-24: commit/push için scripts/ops/git/commit_push.ps1; main koruması; FALLBACK elle git. Kullanıcı istemeden commit yok."
metadata:
  node_type: memory
  type: feedback
  modified: 2026-07-24T02:00:00.000Z
---

Commit/push ajan sohbetinde tekrar tekrar status/diff/GCM ile token yakıyordu.
Kalıcı yol: **`scripts/ops/git/commit_push.ps1`** (KURALLAR-MASTER §8.7).

**How to apply:** Kullanıcı commit/push istediğinde önce script.
`-Onay` + `-Mesaj` zorunlu; main için `-YeniDal` veya `-MainIzin`; push için `-Push`.
Secret stage yok. Script FALLBACK basarsa elle `git` — `--no-verify` / force-push yok.
Merge ve Yayın bu scriptte değil.
