frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("⬇ Factur-X PDF"), function() {
                frappe.call({
                    method: "fatora_facturx.fatora_facturx.api.get_settings",
                    callback: function(r) {
                        if (r.message.mode === "Single Format") {
                            generate_and_download(frm, r.message.default_print_format);
                        } else {
                            show_format_dialog(frm);
                        }
                    }
                });
            });
        }
    }
});

function show_format_dialog(frm) {
    let d = new frappe.ui.Dialog({
        title: __("اختر تنسيق الطباعة"),
        fields: [{
            fieldname: "print_format",
            fieldtype: "Link",
            label: __("Print Format"),
            options: "Print Format",
            reqd: 1,
            get_query: function() {
                return {
                    filters: [["Print Format", "doc_type", "=", "Sales Invoice"]]
                };
            }
        }],
        primary_action_label: __("تحميل"),
        primary_action: function(values) {
            d.hide();
            generate_and_download(frm, values.print_format);
        }
    });
    d.show();
}

function generate_and_download(frm, print_format) {
    if (!print_format) {
        frappe.throw(__("الرجاء تحديد تنسيق طباعة في إعدادات Facturx"));
        return;
    }
    
    frappe.show_progress(__("جاري إنشاء Factur-X..."), 0, 100, __("يرجى الانتظار"));
    
    frappe.call({
        method: "fatora_facturx.fatora_facturx.api.generate_facturx",
        args: {
            invoice_name: frm.doc.name,
            print_format: print_format
        },
        callback: function(r) {
            frappe.hide_progress();
            if (r.message) {
                window.open(r.message.file_url, "_blank");
                frappe.show_alert({
                    message: __("تم إنشاء Factur-X بنجاح"),
                    indicator: "green"
                });
            }
        },
        error: function() {
            frappe.hide_progress();
        }
    });
}
