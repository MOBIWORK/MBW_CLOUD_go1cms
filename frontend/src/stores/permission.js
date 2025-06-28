import { defineStore } from "pinia";
import { ref } from "vue";
import { call } from "frappe-ui";

export const usePermissionStore = defineStore("permission", () => {
	const permissionsMap = ref({});
	const roles = ref([]);

	async function loadPermissions(currentRoles) {
		roles.value = currentRoles;

		const res = await call("go1_cms.api.roles.get_all_docperms_for_roles", {
			roles: currentRoles,
		});

		console.log(">>>>=====res",res)

		let map = {};
		for (const p of res) {
			if (!map[p.doctype]) map[p.doctype] = {};
			for (const key of ["read", "create", "write", "delete", "submit"]) {
				if (p[key]) map[p.doctype][key] = true;
			}
		}
		permissionsMap.value = map;
		console.log(permissionsMap.value);
	}

	const can = (doctype, action) => {
		if (roles.value.includes("Administrator") || roles.value.includes("System Manager")) {
			return true;
		}
		return permissionsMap.value?.[doctype]?.[action] || false;
	};

	return {
		permissionsMap,
		loadPermissions,
		can,
		roles,
	};
});
