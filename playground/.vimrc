let python_highlight_all=1

filetype indent on
filetype plugin on

syntax on

set autoindent

au BufRead,BufNewFile *.sql,*.py,*.xsd,*.json set tabstop=4	" Existing tabs.
au BufRead,BufNewFile *.sql,*.py,*.xsd,*.json set shiftwidth=4	" New tabs.
au BufRead,BufNewFile *.rb,*.pp set tabstop=2
au BufRead,BufNewFile *.rb,*.pp set shiftwidth=2
au BufRead,BufNewFile *.js set tabstop=2
au BufRead,BufNewFile *.js set shiftwidth=2
au BufRead,BufNewFile *.html set tabstop=2
au BufRead,BufNewFile *.html set shiftwidth=2

au BufRead,BufNewFile *.js,*.rb,*.pp,*.sql,*.py,*.json,*.html set expandtab	" Convert tabs to spaces.

highlight BadWhitespace ctermbg=red guibg=red	

au BufRead,BufNewFile *.py,*.json match BadWhitespace /^\t\+/
au BufRead,BufNewFile *.py,*.json match BadWhitespace /\s+$/

au BufNewFile *.py set fileformat=unix
au BufRead,BufNewFile *.rb,*.pp set fileformat=unix
au BufRead,BufNewFile *.js set fileformat=unix
au BufRead,BufNewFile *.html set fileformat=unix

au BufWinLeave * mkview
au BufWinEnter * silent loadview
