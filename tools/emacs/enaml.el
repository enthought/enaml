;; enaml.el --- Major mode for editing Enaml files

;; define keywords unique to enaml
;; (python keywords will automatically be highlighted as well)
(defvar enaml-font-lock-keywords
  `(;; highlight these as keywords
    (,(regexp-opt '("defn" "id" "constraints") 'words)
     1 font-lock-keyword-face)
    ;; highlight these as builtins
    (,(regexp-opt '("horizontal" "vertical" "hbox" "vbox"
		    "align" "align_left" "align_right"
		    "align_top" "align_bottom" "align_v_center"
		    "align_h_center" "_space_") 'words)
     1 font-lock-builtin-face)
    ;; highlight these as types
    (,(regexp-opt '("attr") 'words)
     1 font-lock-builtin-face))
  "Additional font lock keywords for Enaml mode.")

(define-derived-mode
  enaml-mode python-mode "Enaml"
  "Major mode for editing Enaml files"
  (setcar font-lock-defaults
          (append py-font-lock-keywords enaml-font-lock-keywords)))
(provide 'enaml)
