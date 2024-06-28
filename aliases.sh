#!/bin/bash

# Script to set up Docker Compose and SQLite aliases

# Docker Compose aliases
alias up='docker compose up'
alias down='docker compose down'
alias upd='docker compose up -d'

# SQLite alias
alias s='sqlite3 data/data.db'

echo "Aliases have been set up for the current session:"
echo "  up    => docker compose up"
echo "  down  => docker compose down"
echo "  upd   => docker compose up -d"
echo "  s     => sqlite3 data/data.db"

