[ -z "$PS1" ] && return

if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

CLASSPATH=$HOME/lib/java

alias jump='ssh jump.adnxs.net'
alias jumpto="ssh -o 'ProxyCommand ssh jump.adnxs.net nc -w86400 \\\`mfind %h\\\` %p'"

alias schemaSpy='java -jar $HOME/lib/java/schemaSpy.jar -pfp'

alias drt='psql -h jazzhands-db jazzhands'
alias sm='ssh 10.0.72.7'
alias sp='ssh 10.3.72.87'

# Fetch the introductory text of a Wikipedia page.
# Uses a customized DNS server hosted at <page>.wp.dg.cx.
#
function wiki () {
    COLUMNS=`tput cols`
    dig +short +tcp txt "`echo $@`".wp.dg.cx | sed -e 's/” “//g' -e 's/^”//g' -e 's/”$//g' -e 's/ http:/\n\nhttp:/' | fmt -w $COLUMNS
} 2>/dev/null


# Generalized extraction routine.
function e () {
    [ -z $1 ] && echo "Usage: e [file]" && return
        
    if [ -f $1 ]; then
        case $1 in 
            *.tar.bz2)  tar xfvj $1   ;;
            *.tbz2)     tar xfvj $1   ;;
            *.tar.gz)   tar xfvz $1   ;;
            *.tgz)      tar xfvz $1   ;;
            *.tar)      tar xfv $1    ;;
            *.bz2)      bunzip2 $1    ;;
            *.gz)       gzip -d $1    ;;
            *.zip)      unzip $1      ;;
            *.Z)        uncompress $1 ;;
            *)          echo "'$1' is not in a recognized compression format."
        esac
    else
        echo "'$1' is not a regular file."
    fi
}

# Go to the user's git playground.
function pg () {
    base=$HOME/workspace/user/$USER/playground
    if [ -d "$base/$1" ]; then
	cd "$base/$1"
    fi
}

__pwdln() {
    pwdmod="${PWD}/"
    itr=0
    until [[ -z "$pwdmod" ]];do
        itr=$(($itr+1))
        pwdmod="${pwdmod#*/}"
    done
    echo -n $(($itr-1))
}

__vagrantinvestigate() {
    if [[ -f "${PWD}/.vagrant" ]];then
        echo "${PWD}/.vagrant"
        return 0
    else
        pwdmod2="${PWD}"
        for (( i=2; i<=$(__pwdln); i++ )); do
            pwdmod2="${pwdmod2%/*}"          
            if [[ -f "${pwdmod2}/.vagrant" ]]; then
                echo "${pwdmod2}/.vagrant"
                return 0
            fi
         done
    fi
    return 1
}

_vagrant()
{
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="box destroy halt help init package provision reload resume ssh ssh_config status suspend up version"

    if [ $COMP_CWORD == 1 ]
    then
        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
        return 0
    fi

    if [ $COMP_CWORD == 2 ]
    then
        case "$prev" in
            "init")
                local box_list=$(find $HOME/.vagrant.d/boxes -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
                COMPREPLY=($(compgen -W "${box_list}" -- ${cur}))
                return 0
                ;;
            "ssh")
                vagrant_state_file=$(__vagrantinvestigate) || return 1
                running_vm_list=$(grep 'active' $vagrant_state_file | sed -e 's/"active"://' | tr ',' '\n' | cut -d '"' -f 2 | tr '\n' ' ')
                COMPREPLY=($(compgen -W "${running_vm_list}" -- ${cur}))
                return 0
                ;;
            "box")
                box_commands="add help list remove repackage"
                COMPREPLY=($(compgen -W "${box_commands}" -- ${cur}))
                return 0
                ;;
            "help")
                COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
                return 0
                ;;
            *)
            ;;
        esac
    fi

    if [ $COMP_CWORD == 3 ]
    then
        action="${COMP_WORDS[COMP_CWORD-2]}"
        if [ $action == 'box' ]
        then
            case "$prev" in "remove"|"repackage")
                local box_list=$(find $HOME/.vagrant.d/boxes -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
                COMPREPLY=($(compgen -W "${box_list}" -- ${cur}))
                return 0
                ;;
            *)
                ;;
            esac
        fi
    fi
}

complete -F _vagrant vagrant

alias h2d="perl -e 'print hex(\$ARGV[0]),\"\n\" if @ARGV'"
alias go="ssh adonahue.devnxs.net"
