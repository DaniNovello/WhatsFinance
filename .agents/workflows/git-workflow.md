---
description: Git branching and PR workflow for WhatsFinance
---

# Git Workflow — WhatsFinance

## Regra Principal
**NUNCA** faça push direto na `main`. Toda alteração deve passar por feature branch + Pull Request.

## Fluxo

1. Crie uma branch a partir da `main`:
   ```
   git checkout main && git pull origin main
   git checkout -b <tipo>/<nome-curto>
   ```
   Tipos: `feature/`, `fix/`, `refactor/`, `chore/`

2. Faça commits seguindo **Conventional Commits**:
   - `feat: adiciona transcrição de áudio`
   - `fix: corrige cálculo de fatura`
   - `refactor: simplifica handler de mensagens`

3. Push da branch e crie um **Pull Request** via GitHub:
   - Base: `main`
   - Título descritivo
   - Descreva o que mudou no body

4. Após aprovação/review, **merge** o PR (squash ou merge commit).

5. O merge na `main` dispara **deploy automático** no Render.

## Exceções
Nenhuma. Hotfixes também usam branch (`fix/nome`) + PR.

## Rollback
Se um deploy quebrar, reverta o PR no GitHub (botão "Revert") que cria um PR inverso automaticamente.
