#!/usr/bin/env bash

set -e

BRANCH="main"
TEMP_BRANCH="temp_sem_historico"
MESSAGE="Commit inicial sem historico antigo"

if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "Configure seu nome e email do Git antes de limpar o historico:"
  echo "git config --global user.name \"Seu Nome\""
  echo "git config --global user.email \"seu-email@example.com\""
  exit 1
fi

echo "ATENCAO: este script apaga o historico local da branch $BRANCH."
echo "Ele mantem os arquivos atuais, mas substitui todos os commits por um unico commit novo."
echo ""
read -p "Digite LIMPAR para continuar: " CONFIRM

if [ "$CONFIRM" != "LIMPAR" ]; then
  echo "Operacao cancelada."
  exit 1
fi

git checkout "$BRANCH"
git branch -D "$TEMP_BRANCH" 2>/dev/null || true
git checkout --orphan "$TEMP_BRANCH"
git add -A
git commit -m "$MESSAGE"
git branch -D "$BRANCH"
git branch -m "$BRANCH"
git reflog expire --expire=now --all
git gc --prune=now

echo ""
echo "Historico local limpo."
echo "Para substituir tambem o historico no GitHub/remoto, rode:"
echo "git push --force-with-lease origin $BRANCH"
