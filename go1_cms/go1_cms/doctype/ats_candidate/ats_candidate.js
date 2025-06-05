// Copyright (c) 2025, mbwcloud.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("ATS_Candidate", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Candidate Stages", {
    job_opening: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.job_opening) {
            frappe.call({
                method: "go1_cms.go1_cms.doctype.ats_candidate.ats_candidate.get_job_opening_rounds",
                args: { job_opening: row.job_opening },
                callback: function (r) {
                    if (r.message) {
                        let rounds = r.message.map(round => round.round_name);
                        console.log("Rounds fetched:", rounds);

                        // **Cập nhật danh sách lựa chọn cho status trong từng row**
                        frm.fields_dict["candidate_stages"].grid.update_docfield_property(
                            "status", "options", rounds.join("\n")
                        );

                        // **Gán giá trị mặc định cho status**
                        frappe.model.set_value(cdt, cdn, "status", rounds[0] || "");

                        // **Refresh field để cập nhật UI**
                        frm.refresh_field("candidate_stages");
                    }
                },
            });
        }
    }
});


frappe.ui.form.on("Candidate Stages", "status", function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    frm.fields_dict["candidate_stages"].grid.get_field("status").get_query = function () {
        return {
            filters: [
                ["round_name", "in", row.status_options || []], // Chỉ hiển thị options của vòng hiện tại
            ],
        };
    };

    frm.refresh_field("candidate_stages");
});

frappe.ui.form.on("ATS_Candidate", {
    refresh: function (frm) {
        if (frm.doc.job_opening_id) {
            // Khi mở lại form, gọi API để lấy danh sách vòng tuyển dụng
            fetchRecruitmentStages(frm);
        }
    },
    job_opening_id: function (frm) {
        // Khi thay đổi job_opening, gọi lại API
        fetchRecruitmentStages(frm);
    }
});

// Hàm gọi API lấy danh sách vòng tuyển dụng
function fetchRecruitmentStages(frm) {
    if (frm.doc.job_opening_id) {
        frappe.call({
            method: "go1_cms.go1_cms.doctype.ats_jobopening.api.get_recruitment_stages",
            args: { job_opening: frm.doc.job_opening_id },
            callback: function (r) {
                if (r.message) {
                    // Cập nhật danh sách trạng thái động
                    frm.set_df_property("status", "options", r.message);
                    // Nếu chưa có giá trị, gán mặc định là vòng đầu tiên
                    if (!frm.doc.status) {
                        frm.set_value("status", r.message[0] || "");
                    }
                }
            }
        });
    }
}
