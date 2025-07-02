import IndicatorIcon from "@/components//Icons/IndicatorIcon.vue";
import { capture } from "@/telemetry";
import { defineStore } from "pinia";
import { createListResource } from "frappe-ui";
import { reactive, h } from "vue";

export const statusesStore = defineStore("ats-statuses", () => {
	let joStatusesByName = reactive({});

	const JOStatuses = createListResource({
		doctype: "JO Status",
		fields: ["name", "color", "position"],
		orderBy: "position asc",
		cache: "jo-statuses",
		initialData: [],
		auto: true,
		transform(statuses) {
			for (let status of statuses) {
				status.colorClass = colorClasses(status.color);
				status.iconColorClass = colorClasses(status.color, true);
				joStatusesByName[status.name] = status;
			}
			return statuses;
		},
	});

	function colorClasses(color, onlyIcon = false) {
		let textColor = `!text-${color}-600`;
		if (color == "black") {
			textColor = "!text-gray-900";
		} else if (["gray", "green"].includes(color)) {
			textColor = `!text-${color}-700`;
		}

		let bgColor = `bg-${color}-100 hover:bg-${color}-200 active:bg-${color}-300`;
		let theme = `${color}`;

		return [textColor, onlyIcon ? "" : bgColor, theme];
	}

	function getJOStatus(name) {
		if (!name) {
			name = "Public";
		}
		return joStatusesByName[name];
	}

	function statusOptions(doctype, action, statuses = []) {
		let statusesByName;
		if (doctype == "CMS_JobOpening") {
			statusesByName = joStatusesByName;
		} else {
			statusesByName = null;
		}
		if (statuses.length) {
			statusesByName = statuses.reduce((acc, status) => {
				acc[status] = statusesByName[status];
				return acc;
			}, {});
		}
		let options = [];
		for (const status in statusesByName) {
			options.push({
				label: statusesByName[status].name,
				value: statusesByName[status].name,
				icon: () =>
					h(IndicatorIcon, {
						class: statusesByName[status].iconColorClass[0],
					}),
				onClick: () => {
					capture("status_changed", { doctype, status });
					action && action("status", statusesByName[status].name);
				},
			});
		}
		return options;
	}

	return {
		JOStatuses,
		getJOStatus,
		statusOptions,
	};
});
