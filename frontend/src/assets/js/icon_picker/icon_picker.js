import utils from "./utils";

class Picker {
  constructor(opts) {
    this.parent = opts.parent;
    this.width = opts.width;
    this.height = opts.height;
    this.set_icon(opts.icon);
    this.icons = opts.icons;
    this.setup_picker();
  }

  refresh() {
    this.update_icon_selected(true);
  }

  setup_picker() {
    let icon_picker_template = document.createElement("template");
    icon_picker_template.innerHTML = `
			<div class="icon-picker">
				<div class="search-icons">
					<input type="search" placeholder="${__("Search for icons...")}" class="form-control">
					<span class="search-icon">${utils.icon("search", "sm")}</span>
				</div>
				<div class="icon-section">
					<div class="icons"></div>
				</div>
			</div>
		`;
    this.icon_picker_wrapper =
      icon_picker_template.content.firstElementChild.cloneNode(true);
    this.parent.appendChild(this.icon_picker_wrapper);
    this.icon_wrapper =
      this.icon_picker_wrapper.getElementsByClassName("icons")[0];
    this.search_input = this.icon_picker_wrapper.querySelector(
      ".search-icons > input"
    );
    this.refresh();
    this.setup_icons();
  }

  setup_icons() {
    this.icons.forEach((icon) => {
      let elIcon = document.createElement("div");
      elIcon.id = icon;
      elIcon.className = "icon-wrapper";
      elIcon.innerHTML = `${utils.icon(icon, "md")}`;
      this.icon_wrapper.append(elIcon);
      const set_values = () => {
        this.set_icon(icon);
        this.update_icon_selected();
      };
      elIcon.addEventListener("click", () => {
        set_values();
      });
      elIcon.addEventListener("keydown", (e) => {
        const key_code = e.keyCode;
        if ([13, 32].includes(key_code)) {
          e.preventDefault();
          set_values();
        }
      });
    });
    this.search_input.addEventListener("keyup", (e) => {
      e.preventDefault();
      this.filter_icons();
    });

    this.search_input.addEventListener("search", () => {
      this.filter_icons();
    });
  }

  filter_icons() {
    let value = this.search_input.value;
    const allIconWrappers = this.icon_wrapper.querySelectorAll(".icon-wrapper");

    if (!value) {
      allIconWrappers.forEach((iconWrapper) => {
        iconWrapper.classList.remove("hidden");
      });
    } else {
      allIconWrappers.forEach((iconWrapper) => {
        iconWrapper.classList.add("hidden");
      });

      const filterIconWrappers = document.querySelectorAll(
        `.icon-wrapper[id*='${value}']`
      );
      filterIconWrappers.forEach((iconWrapper) => {
        iconWrapper.classList.remove("hidden");
      });
    }
  }

  update_icon_selected(silent) {
    !silent && this.on_change && this.on_change(this.get_icon());
  }

  set_icon(icon) {
    this.icon = icon || "";
  }

  get_icon() {
    return this.icon || "";
  }
}

export default Picker;
