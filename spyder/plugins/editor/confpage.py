# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Editor config page."""

import os
import sys
from itertools import combinations

from qtpy.QtWidgets import (QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                            QVBoxLayout, QDialog, QDialogButtonBox, QWidget,
                            QCheckBox, QSizePolicy)
from qtpy.QtCore import Qt, Signal

from spyder.api.config.decorators import on_conf_change
from spyder.api.config.mixins import SpyderConfigurationObserver
from spyder.api.preferences import PluginConfigPage
from spyder.config.base import _
from spyder.config.manager import CONF
from spyder.utils.icon_manager import ima
from spyder.widgets.helperwidgets import TipWidget


NUMPYDOC = "https://numpydoc.readthedocs.io/en/latest/format.html"
GOOGLEDOC = (
    "https://sphinxcontrib-napoleon.readthedocs.io/en/latest/"
    "example_google.html"
)
SPHINXDOC = (
    "https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html"
)
DOCSTRING_SHORTCUT = CONF.get('shortcuts', 'editor/docstring')


class EditorConfigPage(PluginConfigPage, SpyderConfigurationObserver):
    def __init__(self, plugin, parent):
        PluginConfigPage.__init__(self, plugin, parent)
        SpyderConfigurationObserver.__init__(self)

        self.removetrail_box = None
        self.add_newline_box = None
        self.remove_trail_newline_box = None

        # *********************** IMPORTANT NOTES *****************************
        # * This value needs to be ajusted if we add new options to the
        #   "Advanced settings" tab.
        # * We need to do this so that the text of some options is not clipped.
        if os.name == "nt":
            min_height = 620
        elif sys.platform == "darwin":
            min_height = 760
        else:
            min_height = 670

        self.setMinimumHeight(min_height)

    def get_name(self):
        return _("Editor")

    def get_icon(self):
        return ima.icon('edit')

    def setup_page(self):
        newcb = self.create_checkbox

        # ---- Display tab
        showtabbar_box = newcb(_("Show tab bar"), 'show_tab_bar')
        showclassfuncdropdown_box = newcb(
                _("Show selector for classes and functions"),
                'show_class_func_dropdown')
        showindentguides_box = newcb(_("Show indent guides"),
                                     'indent_guides')
        showcodefolding_box = newcb(_("Show code folding"), 'code_folding')
        linenumbers_box = newcb(_("Show line numbers"), 'line_numbers')
        breakpoints_box = newcb(_("Show breakpoints"), 'editor_debugger_panel',
                                section='debugger')
        blanks_box = newcb(_("Show blank spaces"), 'blank_spaces')
        currentline_box = newcb(_("Highlight current line"),
                                'highlight_current_line')
        currentcell_box = newcb(_("Highlight current cell"),
                                'highlight_current_cell')
        wrap_mode_box = newcb(_("Wrap lines"), 'wrap')
        scroll_past_end_box = newcb(_("Scroll past the end"),
                                    'scroll_past_end')

        occurrence_box = newcb(_("Highlight occurrences after"),
                               'occurrence_highlighting')
        occurrence_spin = self.create_spinbox(
            "", _(" ms"),
            'occurrence_highlighting/timeout',
            min_=100, max_=1000000, step=100)
        occurrence_box.checkbox.toggled.connect(
            occurrence_spin.spinbox.setEnabled)
        occurrence_box.checkbox.toggled.connect(
            occurrence_spin.slabel.setEnabled)
        occurrence_spin.spinbox.setEnabled(
                self.get_option('occurrence_highlighting'))
        occurrence_spin.slabel.setEnabled(
                self.get_option('occurrence_highlighting'))

        occurrence_glayout = QGridLayout()
        occurrence_glayout.addWidget(occurrence_box, 0, 0)
        occurrence_glayout.addWidget(occurrence_spin.spinbox, 0, 1)
        occurrence_glayout.addWidget(occurrence_spin.slabel, 0, 2)

        occurrence_layout = QHBoxLayout()
        occurrence_layout.addLayout(occurrence_glayout)
        occurrence_layout.addStretch(1)

        display_group = QGroupBox(_("Display"))
        display_layout = QVBoxLayout()
        display_layout.addWidget(showtabbar_box)
        display_layout.addWidget(showclassfuncdropdown_box)
        display_layout.addWidget(showindentguides_box)
        display_layout.addWidget(showcodefolding_box)
        display_layout.addWidget(linenumbers_box)
        display_layout.addWidget(breakpoints_box)
        display_layout.addWidget(blanks_box)
        display_group.setLayout(display_layout)

        highlight_group = QGroupBox(_("Highlight"))
        highlight_layout = QVBoxLayout()
        highlight_layout.addWidget(currentline_box)
        highlight_layout.addWidget(currentcell_box)
        highlight_layout.addLayout(occurrence_layout)
        highlight_group.setLayout(highlight_layout)

        other_group = QGroupBox(_("Other"))
        other_layout = QVBoxLayout()
        other_layout.addWidget(wrap_mode_box)
        other_layout.addWidget(scroll_past_end_box)
        other_group.setLayout(other_layout)

        # ---- Source code tab
        closepar_box = newcb(
            _("Automatic insertion of parentheses, braces and brackets"),
            'close_parentheses')
        close_quotes_box = newcb(
            _("Automatic insertion of closing quotes"),
            'close_quotes')
        add_colons_box = newcb(
            _("Automatic insertion of colons after 'for', 'if', 'def', etc"),
            'add_colons')
        autounindent_box = newcb(
            _("Automatic indentation after 'else', 'elif', etc."),
            'auto_unindent')
        tab_mode_box = newcb(
            _("Tab always indent"),
            'tab_always_indent', default=False,
            tip=_("If enabled, pressing Tab will always indent,\n"
                  "even when the cursor is not at the beginning\n"
                  "of a line (when this option is enabled, code\n"
                  "completion may be triggered using the alternate\n"
                  "shortcut: Ctrl+Space)"))
        strip_mode_box = newcb(
            _("Automatic stripping of trailing spaces on changed lines"),
            'strip_trailing_spaces_on_modify', default=True,
            tip=_("If enabled, modified lines of code (excluding strings)\n"
                  "will have their trailing whitespace stripped when leaving them.\n"
                  "If disabled, only whitespace added by Spyder will be stripped."))
        ibackspace_box = newcb(
            _("Intelligent backspace"),
            'intelligent_backspace',
            tip=_("Make the backspace key automatically remove the amount of "
                  "indentation characters set above."),
            default=True)
        self.removetrail_box = newcb(
            _("Automatic removal of trailing spaces when saving files"),
            'always_remove_trailing_spaces',
            default=False)
        self.add_newline_box = newcb(
            _("Insert a newline at the end if one does not exist when saving "
              "a file"),
            'add_newline',
            default=False)
        self.remove_trail_newline_box = newcb(
            _("Trim all newlines after the final one when saving a file"),
            'always_remove_trailing_newlines',
            default=False)

        indent_chars_box = self.create_combobox(
            _("Indentation characters: "),
            ((_("2 spaces"), '*  *'),
             (_("3 spaces"), '*   *'),
             (_("4 spaces"), '*    *'),
             (_("5 spaces"), '*     *'),
             (_("6 spaces"), '*      *'),
             (_("7 spaces"), '*       *'),
             (_("8 spaces"), '*        *'),
             (_("Tabulations"), '*\t*')),
            'indent_chars')
        tabwidth_spin = self.create_spinbox(
            _("Tab stop width:"),
            _("spaces"),
            'tab_stop_width_spaces',
            default=4, min_=1, max_=8, step=1)

        format_on_save = CONF.get(
            'completions',
            ('provider_configuration', 'lsp', 'values', 'format_on_save'),
            False
        )
        self.on_format_save_state(format_on_save)

        def enable_tabwidth_spin(index):
            if index == 7:  # Tabulations
                tabwidth_spin.plabel.setEnabled(True)
                tabwidth_spin.spinbox.setEnabled(True)
            else:
                tabwidth_spin.plabel.setEnabled(False)
                tabwidth_spin.spinbox.setEnabled(False)

        indent_chars_box.combobox.currentIndexChanged.connect(
            enable_tabwidth_spin)

        indent_tab_grid_layout = QGridLayout()
        indent_tab_grid_layout.addWidget(indent_chars_box.label, 0, 0)
        indent_tab_grid_layout.addWidget(indent_chars_box.combobox, 0, 1)
        indent_tab_grid_layout.addWidget(tabwidth_spin.plabel, 1, 0)
        indent_tab_grid_layout.addWidget(tabwidth_spin.spinbox, 1, 1)
        indent_tab_grid_layout.addWidget(tabwidth_spin.slabel, 1, 2)

        indent_tab_layout = QHBoxLayout()
        indent_tab_layout.addLayout(indent_tab_grid_layout)
        indent_tab_layout.addStretch(1)

        automatic_group = QGroupBox(_("Automatic changes"))
        automatic_layout = QVBoxLayout()
        automatic_layout.addWidget(closepar_box)
        automatic_layout.addWidget(autounindent_box)
        automatic_layout.addWidget(add_colons_box)
        automatic_layout.addWidget(close_quotes_box)
        automatic_layout.addWidget(self.removetrail_box)
        automatic_layout.addWidget(strip_mode_box)
        automatic_layout.addWidget(self.add_newline_box)
        automatic_layout.addWidget(self.remove_trail_newline_box)
        automatic_group.setLayout(automatic_layout)

        indentation_group = QGroupBox(_("Indentation"))
        indentation_layout = QVBoxLayout()
        indentation_layout.addLayout(indent_tab_layout)
        indentation_layout.addWidget(ibackspace_box)
        indentation_layout.addWidget(tab_mode_box)
        indentation_group.setLayout(indentation_layout)

        # ---- Advanced tab
        # -- Templates
        templates_group = QGroupBox(_('Templates'))
        template_btn = self.create_button(
            text=_("Edit template for new files"),
            callback=self.plugin.edit_template,
            set_modified_on_click=True
        )

        templates_layout = QVBoxLayout()
        templates_layout.addSpacing(3)
        templates_layout.addWidget(template_btn)
        templates_group.setLayout(templates_layout)

        # -- Autosave
        autosave_group = QGroupBox(_('Autosave'))
        autosave_checkbox = newcb(
            _('Automatically save a copy of files with unsaved changes'),
            'autosave_enabled')
        autosave_spinbox = self.create_spinbox(
            _('Autosave interval: '),
            _('seconds'),
            'autosave_interval',
            min_=1, max_=3600)
        autosave_checkbox.checkbox.toggled.connect(autosave_spinbox.setEnabled)

        autosave_layout = QVBoxLayout()
        autosave_layout.addWidget(autosave_checkbox)
        autosave_layout.addWidget(autosave_spinbox)
        autosave_group.setLayout(autosave_layout)

        # -- Docstring
        docstring_group = QGroupBox(_('Docstring type'))

        numpy_url = "<a href='{}'>Numpy</a>".format(NUMPYDOC)
        googledoc_url = "<a href='{}'>Google</a>".format(GOOGLEDOC)
        sphinx_url = "<a href='{}'>Sphinx</a>".format(SPHINXDOC)
        docstring_label = QLabel(
            _("Here you can select the type of docstrings ({}, {} or {}) you "
              "want the editor to automatically introduce when pressing "
              "<tt>{}</tt> after a function, method or class "
              "declaration.").format(
                  numpy_url, googledoc_url, sphinx_url, DOCSTRING_SHORTCUT)
        )
        docstring_label.setOpenExternalLinks(True)
        docstring_label.setWordWrap(True)

        docstring_combo_choices = ((_("Numpy"), 'Numpydoc'),
                                   (_("Google"), 'Googledoc'),
                                   (_("Sphinx"), 'Sphinxdoc'),)
        docstring_combo = self.create_combobox(
            _("Type:"),
            docstring_combo_choices,
            'docstring_type'
        )

        docstring_layout = QVBoxLayout()
        docstring_layout.addWidget(docstring_label)
        docstring_layout.addWidget(docstring_combo)
        docstring_group.setLayout(docstring_layout)

        # -- Annotations
        annotations_group = QGroupBox(_("Annotations"))
        annotations_label = QLabel(
            _("Display a marker to the left of line numbers when the "
              "following annotations appear at the beginning of a comment: "
              "<tt>TODO, FIXME, XXX, HINT, TIP, @todo, HACK, BUG, OPTIMIZE, "
              "!!!, ???</tt>"))
        annotations_label.setWordWrap(True)
        todolist_box = newcb(
            _("Display code annotations"),
            'todo_list')

        annotations_layout = QVBoxLayout()
        annotations_layout.addWidget(annotations_label)
        annotations_layout.addWidget(todolist_box)
        annotations_group.setLayout(annotations_layout)

        # -- EOL
        eol_group = QGroupBox(_("End-of-line characters"))
        eol_label = QLabel(_("When opening a text file containing "
                             "mixed end-of-line characters (this may "
                             "raise syntax errors in the consoles "
                             "on Windows platforms), Spyder may fix the "
                             "file automatically."))
        eol_label.setWordWrap(True)
        check_eol_box = newcb(_("Fix automatically and show warning "
                                "message box"),
                              'check_eol_chars', default=True)
        convert_eol_on_save_box = newcb(
            _("Convert end-of-line characters to the following on save:"),
            'convert_eol_on_save',
            default=False
        )
        eol_combo_choices = (
            (_("LF (Unix)"), 'LF'),
            (_("CRLF (Windows)"), 'CRLF'),
            (_("CR (macOS)"), 'CR'),
        )
        convert_eol_on_save_combo = self.create_combobox(
            "",
            eol_combo_choices,
            'convert_eol_on_save_to',
        )
        convert_eol_on_save_box.checkbox.toggled.connect(
                convert_eol_on_save_combo.setEnabled)
        convert_eol_on_save_combo.setEnabled(
                self.get_option('convert_eol_on_save'))

        eol_on_save_layout = QHBoxLayout()
        eol_on_save_layout.addWidget(convert_eol_on_save_box)
        eol_on_save_layout.addWidget(convert_eol_on_save_combo)

        eol_layout = QVBoxLayout()
        eol_layout.addWidget(eol_label)
        eol_layout.addWidget(check_eol_box)
        eol_layout.addLayout(eol_on_save_layout)
        eol_group.setLayout(eol_layout)

        # -- Multi-cursor
        multicursor_group = QGroupBox(_("Multi-Cursor"))
        multicursor_label = QLabel(
            _("Enable adding multiple cursors for simultaneous editing. "
              "Additional cursors are added and removed using the Ctrl-Alt "
              "click shortcut. A column of cursors can be added using the "
              "Ctrl-Alt-Shift click shortcut."))
        multicursor_label.setWordWrap(True)
        multicursor_box = newcb(
            _("Enable Multi-Cursor "),
            'multicursor_support')

        multicursor_layout = QVBoxLayout()
        multicursor_layout.addWidget(multicursor_label)
        multicursor_layout.addWidget(multicursor_box)
        multicursor_group.setLayout(multicursor_layout)

        # -- Mouse Shortcuts
        mouse_shortcuts_group = QGroupBox(_("Mouse Shortcuts"))
        mouse_shortcuts_button = self.create_button(
            lambda: MouseShortcutEditor(self).exec_(),
            _("Edit Mouse Shortcut Modifiers")
        )

        mouse_shortcuts_layout = QVBoxLayout()
        mouse_shortcuts_layout.addWidget(mouse_shortcuts_button)
        mouse_shortcuts_group.setLayout(mouse_shortcuts_layout)

        # --- Tabs ---
        self.create_tab(
            _("Interface"),
            [display_group, highlight_group, other_group]
        )

        self.create_tab(_("Source code"), [automatic_group, indentation_group])

        self.create_tab(
            _("Advanced settings"),
            [templates_group, autosave_group, docstring_group,
             annotations_group, eol_group, multicursor_group,
             mouse_shortcuts_group]
        )

    @on_conf_change(
        option=('provider_configuration', 'lsp', 'values', 'format_on_save'),
        section='completions'
    )
    def on_format_save_state(self, value):
        """
        Change options following the `format_on_save` completion option.

        Parameters
        ----------
        value : bool
            If the completion `format_on_save` option is enabled or disabled.

        Returns
        -------
        None.

        """
        options = [
            self.removetrail_box,
            self.add_newline_box,
            self.remove_trail_newline_box]
        for option in options:
            if option:
                if value:
                    option.setToolTip(
                        _("This option is disabled since the "
                          "<i>Autoformat files on save</i> option is active.")
                    )
                else:
                    option.setToolTip("")
                option.setDisabled(value)


class MouseShortcutEditor(QDialog):
    """A dialog to edit the modifier keys for CodeEditor mouse interactions."""

    def __init__(self, parent):
        super().__init__(parent)
        self.editor_config_page = parent
        mouse_shortcuts = CONF.get('editor', 'mouse_shortcuts')
        self.setWindowFlags(self.windowFlags() &
                            ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        self.scrollflag_shortcut = ShortcutSelector(
            self,
            _("Jump Within Document"),
            mouse_shortcuts['jump_to_position']
        )
        self.scrollflag_shortcut.sig_changed.connect(self.validate)
        layout.addWidget(self.scrollflag_shortcut)

        self.goto_def_shortcut = ShortcutSelector(
            self,
            _("Goto Definition"),
            mouse_shortcuts['goto_definition']
        )
        self.goto_def_shortcut.sig_changed.connect(self.validate)
        layout.addWidget(self.goto_def_shortcut)

        self.add_cursor_shortcut = ShortcutSelector(
            self,
            _("Add / Remove Cursor"),
            mouse_shortcuts['add_remove_cursor']
        )
        self.add_cursor_shortcut.sig_changed.connect(self.validate)
        layout.addWidget(self.add_cursor_shortcut)

        self.column_cursor_shortcut = ShortcutSelector(
            self,
            _("Add Column Cursor"),
            mouse_shortcuts['column_cursor']
        )
        self.column_cursor_shortcut.sig_changed.connect(self.validate)
        layout.addWidget(self.column_cursor_shortcut)

        button_box = QDialogButtonBox(self)
        apply_b = button_box.addButton(QDialogButtonBox.StandardButton.Apply)
        apply_b.clicked.connect(self.apply_mouse_shortcuts)
        apply_b.setEnabled(False)
        self.apply_button = apply_b
        ok_b = button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        ok_b.clicked.connect(self.accept)
        self.ok_button = ok_b
        cancel_b = button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        cancel_b.clicked.connect(self.reject)
        layout.addWidget(button_box)

    def apply_mouse_shortcuts(self):
        """Set new config to CONF"""

        self.editor_config_page.set_option('mouse_shortcuts',
                                           self.mouse_shortcuts)
        self.scrollflag_shortcut.apply_modifiers()
        self.goto_def_shortcut.apply_modifiers()
        self.add_cursor_shortcut.apply_modifiers()
        self.column_cursor_shortcut.apply_modifiers()
        self.apply_button.setEnabled(False)

    def accept(self):
        """Apply new settings and close dialog."""

        self.apply_mouse_shortcuts()
        super().accept()

    def validate(self):
        """
        Detect conflicts between shortcuts, and detect if current selection is
        different from current config. Set Ok and Apply buttons enabled or
        disabled accordingly, as well as set visibility of the warning for
        shortcut conflict.
        """
        shortcut_selectors = (
            self.scrollflag_shortcut,
            self.goto_def_shortcut,
            self.add_cursor_shortcut,
            self.column_cursor_shortcut
        )

        for selector in shortcut_selectors:
            selector.warning.setVisible(False)

        conflict = False
        for a, b in combinations(shortcut_selectors, 2):
            if a.modifiers() and a.modifiers() == b.modifiers():
                conflict = True
                a.warning.setVisible(True)
                b.warning.setVisible(True)

        self.ok_button.setEnabled(not conflict)

        self.apply_button.setEnabled(
            not conflict and (
                self.scrollflag_shortcut.is_changed() or
                self.goto_def_shortcut.is_changed() or
                self.add_cursor_shortcut.is_changed() or
                self.column_cursor_shortcut.is_changed()
            )
        )

    @property
    def mouse_shortcuts(self):
        """Format shortcuts dict for CONF."""

        return {'jump_to_position': self.scrollflag_shortcut.modifiers(),
                'goto_definition': self.goto_def_shortcut.modifiers(),
                'add_remove_cursor': self.add_cursor_shortcut.modifiers(),
                'column_cursor': self.column_cursor_shortcut.modifiers()}


class ShortcutSelector(QWidget):
    """Line representing an editor for a single mouse shortcut."""

    sig_changed = Signal()

    def __init__(self, parent, label, modifiers):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        label = QLabel(label)
        layout.addWidget(label)

        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Preferred)
        layout.addWidget(spacer)

        # TODO _() translate these checkboxes?
        # TODO rename based on OS? (CONF strings should stay the same)
        self.ctrl_check = QCheckBox("Ctrl")
        self.ctrl_check.setChecked("ctrl" in modifiers.lower())
        self.ctrl_check.toggled.connect(self.validate)
        layout.addWidget(self.ctrl_check)

        self.alt_check = QCheckBox("Alt")
        self.alt_check.setChecked("alt" in modifiers.lower())
        self.alt_check.toggled.connect(self.validate)
        layout.addWidget(self.alt_check)

        self.meta_check = QCheckBox("Meta")
        self.meta_check.setChecked("meta" in modifiers.lower())
        self.meta_check.toggled.connect(self.validate)
        layout.addWidget(self.meta_check)

        self.shift_check = QCheckBox("Shift")
        self.shift_check.setChecked("shift" in modifiers.lower())
        self.shift_check.toggled.connect(self.validate)
        layout.addWidget(self.shift_check)

        warning_icon = ima.icon("MessageBoxWarning")
        self.warning = TipWidget(
            _("Shortcut Conflicts With Another"),
            warning_icon,
            warning_icon
        )
        # Thanks to https://stackoverflow.com/a/34663079/3220135
        sp_retain = self.warning.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.warning.setSizePolicy(sp_retain)
        self.warning.setVisible(False)
        layout.addWidget(self.warning)

        self.setLayout(layout)

        self.apply_modifiers()

    def validate(self):
        """
        Cannot have shortcut of Shift alone as that conflicts with setting the
        cursor position without moving the anchor. Enable/Disable the Shift
        checkbox accordingly. (Re)Emit a signal to MouseShortcutEditor which
        will perform other validation.
        """

        if (
            self.ctrl_check.isChecked() or
            self.alt_check.isChecked() or
            self.meta_check.isChecked()
        ):
            self.shift_check.setEnabled(True)

        else:
            self.shift_check.setEnabled(False)
            self.shift_check.setChecked(False)

        self.sig_changed.emit()

    def modifiers(self):
        """Get the current modifiers string."""

        modifiers = []
        if self.ctrl_check.isChecked():
            modifiers.append("Ctrl")
        if self.alt_check.isChecked():
            modifiers.append("Alt")
        if self.meta_check.isChecked():
            modifiers.append("Meta")
        if self.shift_check.isChecked():
            modifiers.append("Shift")
        return "+".join(modifiers)

    def is_changed(self):
        """Is the current selection different from when last applied?"""
        return self.current_modifiers != self.modifiers()

    def apply_modifiers(self):
        """Informs ShortcutSelector that settings have been applied."""
        self.current_modifiers = self.modifiers()
