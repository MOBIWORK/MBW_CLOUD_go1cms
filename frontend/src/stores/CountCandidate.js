import { defineStore } from "pinia";

export const useCountCandidateStore = defineStore("CountCandidate", {
	state: () => ({
		countCandidate: [],
		ProcessRecruitment: [],
	}),
	actions: {
		setCountCandidate(count) {
			this.countCandidate = count;
		},
		getCountCandidate() {
			return this.countCandidate;
		},
		setRecruitmentProcess(process) {
			this.ProcessRecruitment = process;
		},
	},
});
