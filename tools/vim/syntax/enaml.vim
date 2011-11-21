" Vim syntax file
" Language:     Enaml
" Maintainer:   Robert Kern <rkern@enthought.com>
" URL:          http://github.com/enthought/enaml
" Last Change:  2011 November 1

" For version 5.x: Clear all syntax items
" For version 6.x: Quit when a syntax file was already loaded
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

" Read the Python syntax to start with
if version < 600
  so <sfile>:p:h/python.vim
else
  runtime! syntax/python.vim
  unlet b:current_syntax
endif

" Enaml extensions
syn keyword enamlStatement      defn
syn match enamlSeparator        ":: \w\+ ::"
" FIXME: This captures the predefined operators, not any extensions that may be
" added.
syn match enamlOperator         "\%(\w\|\s\)\(->\|<<\|>>\|=\|:=\)\%(\w\|\s\)"
if exists("python_highlight_builtins") || exists("enaml_highlight_builtins")
    syn keyword enamlBuiltin    horizontal vertical hbox vbox align align_left align_right
    syn keyword enamlBuiltin    align_top align_bottom align_v_center align_h_center _space_
endif

" Default highlighting
if version >= 508 || !exists("did_enaml_syntax_inits")
  if version < 508
    let did_enaml_syntax_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif
  HiLink enamlStatement         Statement
  HiLink enamlSeparator         Statement
  HiLink enamlOperator          Operator
  if exists("python_highlight_builtins") || exists("enaml_highlight_builtins")
      HiLink enamlBuiltin       Function
  endif

  delcommand HiLink
endif


let b:current_syntax = "enaml"
