// stores/filterStore.js
import { defineStore } from "pinia";

export const useFilterStore = defineStore("filterStore", {
	state: () => ({
		filterData: null, // Lưu trữ dữ liệu được truyền từ component con
		timestamp: null, // Dấu thời gian cập nhật
	}),
	actions: {
		updateFilterData(data) {
			this.filterData = data; // Lưu dữ liệu mới
			this.timestamp = new Date().getTime(); // Đánh dấu thời gian cập nhật
		},
	},
});
