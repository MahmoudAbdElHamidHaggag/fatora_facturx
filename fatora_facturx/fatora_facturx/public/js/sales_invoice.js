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
    let dialog = new frappe.ui.Dialog({
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
        primary_action: function() {
            let fmt = dialog.fields_dict.print_format.get_value();
            if (!fmt) {
                frappe.msgprint(__("الرجاء اختيار تنسيق طباعة"));
                return;
            }
            dialog.hide();
            generate_and_download(frm, fmt);
        }
    });
    dialog.show();
}

function generate_and_download(frm, print_format) {
    frappe.call({
        method: "fatora_facturx.fatora_facturx.api.generate_facturx",
        args: {
            invoice_name: frm.doc.name,
            print_format: print_format
        },
        freeze: true,
        freeze_message: __("جاري إنشاء Factur-X PDF..."),
        callback: function(r) {
            if (r.message) {
                // أضف timestamp عشان المتصفح ميعملش cache
                let url = r.message.file_url + "?t=" + new Date().getTime();
                window.open(url, "_blank");
                frappe.show_alert({
                    message: __("تم إنشاء Factur-X بنجاح ✅"),
                    indicator: "green"
                });
            }
        }
    });
}
