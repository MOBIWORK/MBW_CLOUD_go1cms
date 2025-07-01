// Utility function for candidate avatar with default fallback
export const getCandidateAvatar = (avatarUrl) => {
	if (avatarUrl) {
		return avatarUrl;
	}
	// Return default avatar - a nice professional looking person icon
	return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjUwIiBjeT0iNTAiIHI9IjUwIiBmaWxsPSIjNjM2NkY4Ii8+CjxjaXJjbGUgY3g9IjUwIiBjeT0iMzgiIHI9IjE2IiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMjQgODBDMjQgNjguOTU0MyAzMi45NTQzIDYwIDQ0IDYwSDU2QzY3LjA0NTcgNjAgNzYgNjguOTU0MyA3NiA4MFY5MEgyNFY4MFoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPg==';
};

// Alternative avatar colors
export const getDefaultAvatarColors = () => [
	'#6366F8', // Indigo
	'#06B6D4', // Cyan  
	'#10B981', // Emerald
	'#F59E0B', // Amber
	'#EF4444', // Red
	'#8B5CF6', // Violet
	'#EC4899', // Pink
	'#84CC16', // Lime
];

// Generate colored avatar based on name
export const getColoredAvatar = (name, avatarUrl) => {
	if (avatarUrl) {
		return avatarUrl;
	}
	
	const colors = getDefaultAvatarColors();
	const colorIndex = name ? name.charCodeAt(0) % colors.length : 0;
	const color = colors[colorIndex];
	
	return `data:image/svg+xml;base64,${btoa(`
		<svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
			<circle cx="50" cy="50" r="50" fill="${color}"/>
			<circle cx="50" cy="38" r="16" fill="white"/>
			<path d="M24 80C24 68.9543 32.9543 60 44 60H56C67.0457 60 76 68.9543 76 80V90H24V80Z" fill="white"/>
		</svg>
	`)}`;
}; 