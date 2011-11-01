" Vim indent file
" Language:	Enaml
" Maintainer:	Robert Kern <rkern@enthought.com>
" URL:		http://github.com/enthought/enaml
" Last Change:	2011 Nov 1

" Only load this indent file when no other was loaded.
if exists("b:did_indent")
  finish
endif

" Use Python formatting rules
runtime! indent/python.vim
