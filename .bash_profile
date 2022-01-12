# git
alias add='git add .'
alias ci='git commit -m "update"'
alias br='git branch'
alias brd='git branch -d'
alias st='git status'
alias gpo='git push origin'
alias gpl='git pull'
alias gf='git fetch'
alias gba='git branch -a'
alias cob='git checkout -b'
alias co='git checkout'
alias sw='git switch'
alias sah='git stash'
alias sahp='git stash pop'
alias reset='git reset --hard HEAD^'
alias gpom='git pull origin master'
alias cpr='gh pr create -t'

# os
alias la='ls -a'
alias ll='ls -ll'

# docker
alias dc='/Users/ikeli/script/docker/dc.sh'
alias dcup='docker-compose up -d'
alias dp='docker ps'
alias dcsp='docker-compose stop'
alias dcd='docker-compose down'

# git 推送
alias up="/Users/ikeli/script/upp.sh"

# prc-commit
alias prc='pre-commit run -a'

export CLICOLOR=1
export LSCOLORS=gxfxcxdxbxegedabagacad
#export PS1='\[\e[01;33m\][\[\e[01;32m\]\u\[\e[01;33m\]@\[\e[01;35m\]\h:\[\e[01;33m\]] \[\e[01;36m\]\w \[\e[01;32m\]\$ '
