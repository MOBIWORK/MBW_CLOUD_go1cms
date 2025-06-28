import { defineStore } from "pinia";

export const useQuickEntry = defineStore("reloadQuickEntry", {
	state: () => ({
		doctype: "", // Giá trị chiều rộng khối cha
        timestamp: null,
	}),
	actions: {
		setDoctypeQuickEntry(doctype) {
			this.doctype = doctype;
            this.timestamp = Date.now();
		},
	},
});
