// Copyright (c) 2025, AWOKE India and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Phase", {
    project_phase: function(frm) {
        if (frm.doc.__islocal) {
			// add missing " " arg in split method
			let parts = frm.doc.project_phase.split(" ");
			let abbr = $.map(parts, function (p) {
				return p ? p.substr(0, 1) : null;
			}).join("");
			frm.set_value("abbr", abbr);
		}
    },
    refresh(frm) {
        if (!frm.is_new()) {
            frm.doc.abbr && frm.set_df_property("abbr", "read_only", 1);
        }
	},
});
