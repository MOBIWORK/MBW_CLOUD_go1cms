export default {
  icon(
    icon_name,
    size = "sm",
    icon_class = "",
    icon_style = "",
    svg_class = ""
  ) {
    let size_class = "";
    let is_espresso = icon_name.startsWith("es-");

    icon_name = is_espresso ? `${"#" + icon_name}` : `${"#icon-" + icon_name}`;
    if (typeof size == "object") {
      icon_style += ` width: ${size.width}; height: ${size.height}`;
    } else {
      size_class = `icon-${size}`;
    }
    return `<svg class="${
      is_espresso
        ? icon_name.startsWith("es-solid")
          ? "es-icon es-solid"
          : "es-icon es-line"
        : "icon"
    } ${svg_class} ${size_class}" style="${icon_style}" aria-hidden="true">
			<use class="${icon_class}" href="${icon_name}"></use>
		</svg>`;
  },
};
