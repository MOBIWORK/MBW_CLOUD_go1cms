import frappe
from frappe import _
from frappe.model.document import get_controller
from frappe.model import no_value_fields
from pypika import Criterion

from go1_cms.api.views import get_views
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def sort_options(doctype: str):
    fields = frappe.get_meta(doctype).fields
    fields = [field for field in fields if field.fieldtype not in no_value_fields]
    fields = [
        {
            "label": field.label,
            "value": field.fieldname,
            "fieldname": field.fieldname,
        }
        for field in fields
        if field.label and field.fieldname
    ]

    standard_fields = [
        {"label": "Name", "fieldname": "name"},
        {"label": "Created On", "fieldname": "creation"},
        {"label": "Last Modified", "fieldname": "modified"},
        {"label": "Modified By", "fieldname": "modified_by"},
        {"label": "Owner", "fieldname": "owner"},
    ]

    for field in standard_fields:
        field["label"] = field["label"]
        field["value"] = field["fieldname"]
        fields.append(field)

    return fields


@frappe.whitelist()
@check_user_admin
def get_filterable_fields(doctype: str):
    allowed_fieldtypes = [
        "Check",
        "Data",
        "Float",
        "Int",
        "Currency",
        "Dynamic Link",
        "Link",
        "Long Text",
        "Select",
        "Small Text",
        "Text Editor",
        "Text",
        "Duration",
        "Date",
        "Datetime",
    ]

    if doctype == "Mbw Blog Post":
        allowed_fieldtypes.append('Table')

    c = get_controller(doctype)
    restricted_fields = []
    if hasattr(c, "get_non_filterable_fields"):
        restricted_fields = c.get_non_filterable_fields()

    res = []

    # append DocFields
    DocField = frappe.qb.DocType("DocField")
    doc_fields = get_fields_meta(
        DocField, doctype, allowed_fieldtypes, restricted_fields)
    for i in doc_fields:
        if i.get('fieldtype') == 'Table':
            i['fieldtype'] = "Data"
    res.extend(doc_fields)

    # append Custom Fields
    CustomField = frappe.qb.DocType("Custom Field")
    custom_fields = get_fields_meta(
        CustomField, doctype, allowed_fieldtypes, restricted_fields)
    res.extend(custom_fields)

    if doctype in ["Menu", "MBW Form"]:
        res = [r for r in res if r.fieldname not in [
            'id_client_website', 'id_parent_copy']]

    # append standard fields (getting error when using frappe.model.std_fields)
    standard_fields = [
        # {"fieldname": "name", "fieldtype": "Link",
        #     "label": "ID", "options": doctype},
        # {
        #     "fieldname": "owner",
        #     "fieldtype": "Link",
        #     "label": "Created By",
        #     "options": "User"
        # },
        # {
        #     "fieldname": "modified_by",
        #     "fieldtype": "Link",
        #     "label": "Last Updated By",
        #     "options": "User",
        # },
        # {"fieldname": "_user_tags", "fieldtype": "Data", "label": "Tags"},
        # {"fieldname": "_liked_by", "fieldtype": "Data", "label": "Liked By"},
        # {"fieldname": "_comments", "fieldtype": "Text", "label": "Comments"},
        # {"fieldname": "_assign", "fieldtype": "Text", "label": "Assigned To"},
        {"fieldname": "creation", "fieldtype": "Datetime", "label": "Created On"},
        {"fieldname": "modified", "fieldtype": "Datetime", "label": "Last Modified"},
    ]
    for field in standard_fields:
        if (
                field.get("fieldname") not in restricted_fields and
                field.get("fieldtype") in allowed_fieldtypes
        ):
            field["name"] = field.get("fieldname")
            res.append(field)

    for field in res:
        field["label"] = field.get("label")
        field["value"] = field.get("fieldname")

    return res


@frappe.whitelist()
@check_user_admin
def get_group_by_fields(doctype: str):
    allowed_fieldtypes = [
        "Check",
        "Data",
        "Float",
        "Int",
        "Currency",
        "Dynamic Link",
        "Link",
        "Select",
        "Duration",
        "Date",
        "Datetime",
    ]

    fields = frappe.get_meta(doctype).fields
    fields = [field for field in fields if field.fieldtype not in no_value_fields and field.fieldtype in allowed_fieldtypes]
    fields = [
        {
            "label": _(field.label),
            "value": field.fieldname,
        }
        for field in fields
        if field.label and field.fieldname
    ]

    standard_fields = [
        {"label": "Name", "value": "name"},
        {"label": "Created On", "value": "creation"},
        {"label": "Last Modified", "value": "modified"},
        {"label": "Modified By", "value": "modified_by"},
        {"label": "Owner", "value": "owner"},
        {"label": "Liked By", "value": "_liked_by"},
        {"label": "Assigned To", "value": "_assign"},
        {"label": "Comments", "value": "_comments"},
    ]

    for field in standard_fields:
        field["label"] = _(field["label"])
        fields.append(field)

    return fields


def get_fields_meta(DocField, doctype, allowed_fieldtypes, restricted_fields):
    parent = "parent" if DocField._table_name == "tabDocField" else "dt"
    return (
        frappe.qb.from_(DocField)
        .select(
            DocField.fieldname,
            DocField.fieldtype,
            DocField.label,
            DocField.name,
            DocField.options,
        )
        .where(DocField[parent] == doctype)
        .where(DocField.hidden == False)
        .where(Criterion.any([DocField.fieldtype == i for i in allowed_fieldtypes]))
        .where(Criterion.all([DocField.fieldname != i for i in restricted_fields]))
        .run(as_dict=True)
    )


@frappe.whitelist()
@check_user_admin
def get_quick_filters(doctype: str):
    meta = frappe.get_meta(doctype)
    fields = [field for field in meta.fields if field.in_standard_filter]
    quick_filters = []

    for field in fields:
        if field.fieldtype == "Select":
            field.options = field.options.split("\n")
            field.options = [{"label": option, "value": option}
                             for option in field.options]
            field.options.insert(0, {"label": "", "value": ""})
        quick_filters.append({
            "label": field.label,
            "name": field.fieldname,
            "type": field.fieldtype,
            "options": field.options,
        })
    return quick_filters


@frappe.whitelist()
@check_user_admin
def get_list_data(
        doctype: str,
        filters: dict,
        order_by: str,
        page_length=20,
        page_length_count=20,
        columns=None,
        rows=None,
        view=None,
        default_filters=None,
):
    custom_view = False
    filters = frappe._dict(filters)

    if doctype in ["Menu", "MBW Form"]:
        web_edit = frappe.get_last_doc(
            'MBW Client Website', filters={"edit": 1})
        if web_edit:
            filters['id_client_website'] = web_edit.name
            filters['is_template'] = 0
        # if doctype == "MBW Form":
        #     filters['form_type'] = ['not in', ['Contact form']]

    custom_view_name = view.get('custom_view_name') if view else None
    view_type = view.get('view_type') if view else None
    group_by_field = view.get('group_by_field') if view else None

    for key in filters:
        value = filters[key]
        if isinstance(value, list):
            if "@me" in value:
                value[value.index("@me")] = frappe.session.user
            elif "%@me%" in value:
                index = [i for i, v in enumerate(value) if v == "%@me%"]
                for i in index:
                    value[i] = "%" + frappe.session.user + "%"
        elif value == "@me":
            filters[key] = frappe.session.user

    if default_filters:
        default_filters = frappe.parse_json(default_filters)
        filters.update(default_filters)

    is_default = True
    if columns or rows:
        custom_view = True
        is_default = False
        columns = frappe.parse_json(columns)
        rows = frappe.parse_json(rows)

    if not columns:
        columns = [
            {"label": "Name", "type": "Data", "key": "name", "width": "16rem"},
            {"label": "Last Modified", "type": "Datetime",
                "key": "modified", "width": "8rem"},
        ]

    if not rows:
        rows = ["name"]

    default_view_filters = {
        "dt": doctype,
        "type": view_type or 'list',
        "is_default": 1,
        "user": frappe.session.user,
    }

    if not custom_view and frappe.db.exists("CMS View Settings", default_view_filters):
        list_view_settings = frappe.get_doc(
            "CMS View Settings", default_view_filters)
        columns = frappe.parse_json(list_view_settings.columns)
        rows = frappe.parse_json(list_view_settings.rows)
        is_default = False
    elif not custom_view or is_default:
        _list = get_controller(doctype)

        if hasattr(_list, "default_list_data"):
            columns = _list.default_list_data().get("columns")
            rows = _list.default_list_data().get("rows")

    # check if rows has all keys from columns if not add them
    for column in columns:
        if column.get("key") not in rows:
            rows.append(column.get("key"))
        column["label"] = _(column.get("label"))

        if column.get("key") == "_liked_by" and column.get("width") == "10rem":
            column["width"] = "50px"

    # check if rows has group_by_field if not add it
    if group_by_field and group_by_field not in rows:
        rows.append(group_by_field)

    # remove field is table
    table_fields = []
    if doctype == 'Mbw Blog Post':
        if 'tags' in rows:
            table_fields.append('tags')
            rows.remove("tags")

    new_filters = []
    # handle filter field table
    name_filter = []
    if doctype == 'Mbw Blog Post':
        # tags
        tags_filter = filters.pop("tags", None)
        if tags_filter:
            if tags_filter[0] == 'in':
                tags_filter[1] = [c.strip()
                                  for c in tags_filter[1].split(';')]
            name_filter.extend(frappe.db.get_all("MBW Blog Tag Item", filters={
                "tag": tags_filter, "parentfield": "tags"}, pluck="parent") or [])

        if tags_filter:
            filt = ['name', 'in', list(set(name_filter))]
            new_filters.append(filt)

    for x, y in filters.items():
        filt = [x]
        if type(y) == list:
            if ('in' in y[0] or 'not in' in y[0]) and type(y[1]) == str:
                y[1] = [c.strip()
                        for c in y[1].split(';')]
            filt.extend(y)
        else:
            filt.extend(['=', y])
        new_filters.append(filt)

    rows = [row for row in rows if row != 'action_button']

    data = frappe.get_list(
        doctype,
        fields=rows,
        filters=new_filters,
        order_by=order_by,
        page_length=page_length,
    ) or []

    # convert field is table and add rows field
    for f in table_fields:
        if doctype == 'Mbw Blog Post':
            if f == "tags":
                for d in data:
                    data_f = frappe.db.get_all("MBW Blog Tag Item", filters={"parent": d.name, "parentfield": "tags"}, fields=[
                        'tag'
                    ], order_by="idx")
                    d[f] = data_f
            rows.append(f)

    fields = frappe.get_meta(doctype).fields
    fields = [field for field in fields if field.fieldtype not in no_value_fields]
    fields = [
        {
            "label": _(field.label),
            "type": field.fieldtype,
            "value": field.fieldname,
            "options": field.options,
        }
        for field in fields
        if field.label and field.fieldname
    ]

    std_fields = [
        # {"label": "Name", "type": "Data", "value": "name"},
        {"label": "Created On", "type": "Datetime", "value": "creation"},
        {"label": "Last Modified", "type": "Datetime", "value": "modified"},
        # {
        #     "label": "Modified By",
        #     "type": "Link",
        #             "value": "modified_by",
        #             "options": "User",
        # },
        # {"label": "Assigned To", "type": "Text", "value": "_assign"},
        # {"label": "Owner", "type": "Link", "value": "owner", "options": "User"},
        # {"label": "Like", "type": "Data", "value": "_liked_by"},
    ]

    for field in std_fields:
        if field.get('value') not in rows:
            rows.append(field.get('value'))
        if field not in fields:
            field["label"] = _(field["label"])
            fields.append(field)

    if not is_default and custom_view_name:
        is_default = frappe.db.get_value(
            "CMS View Settings", custom_view_name, "load_default_columns")

    if group_by_field and view_type == "group_by":
        def get_options(type, options):
            if type == "Select":
                return [option for option in options.split("\n")]
            else:
                has_empty_values = any(
                    [not d.get(group_by_field) for d in data])
                options = list(set([d.get(group_by_field) for d in data]))
                options = [u for u in options if u]
                if has_empty_values:
                    options.append("")

                if order_by and group_by_field in order_by:
                    order_by_fields = order_by.split(",")
                    order_by_fields = [(field.split(" ")[0], field.split(" ")[
                                        1]) for field in order_by_fields]
                    if (group_by_field, "asc") in order_by_fields:
                        options.sort()
                    elif (group_by_field, "desc") in order_by_fields:
                        options.sort(reverse=True)
                else:
                    options.sort()
                return options

        for field in fields:
            if field.get("value") == group_by_field:
                group_by_field = {
                    "label": field.get("label"),
                    "name": field.get("value"),
                    "type": field.get("type"),
                    "options": get_options(field.get("type"), field.get("options")),
                }

    return {
        "data": data,
        "columns": columns,
        "rows": rows,
        "fields": fields,
        "group_by_field": group_by_field,
        "page_length": page_length,
        "page_length_count": page_length_count,
        "is_default": is_default,
        "views": get_views(doctype),
        "total_count": len(frappe.get_list(doctype, filters=new_filters)),
        "row_count": len(data),
    }


def get_doctype_fields(doctype, name):
    not_allowed_fieldtypes = [
        "Section Break",
        "Column Break",
    ]

    fields = frappe.get_meta(doctype).fields
    fields = [
        field for field in fields if field.fieldtype not in not_allowed_fieldtypes]

    sections = {}
    section_fields = []
    last_section = None
    doc = frappe.get_cached_doc(doctype, name)

    has_high_permlevel_fields = any(df.permlevel > 0 for df in fields)
    if has_high_permlevel_fields:
        has_read_access_to_permlevels = doc.get_permlevel_access("read")
        has_write_access_to_permlevels = doc.get_permlevel_access("write")

    for field in fields:
        if field.fieldtype == "Tab Break" and last_section:
            sections[last_section]["fields"] = section_fields
            last_section = None
            if field.read_only:
                section_fields = []
                continue
        if field.fieldtype == "Tab Break":
            if field.read_only:
                section_fields = []
                continue
            section_fields = []
            last_section = field.fieldname
            sections[field.fieldname] = {
                "label": field.label,
                "name": field.fieldname,
                "opened": True,
                "fields": [],
            }
        else:
            if field.permlevel > 0:
                field_has_write_access = field.permlevel in has_write_access_to_permlevels
                field_has_read_access = field.permlevel in has_read_access_to_permlevels
                if not field_has_write_access and field_has_read_access:
                    field.read_only = 1
                if not field_has_read_access and not field_has_write_access:
                    field.hidden = 1
            section_fields.append(get_field_obj(field))

    section_fields = []
    for section in sections:
        section_fields.append(sections[section])

    fields = [field for field in fields if field.fieldtype not in "Tab Break"]
    fields_meta = {}
    for field in fields:
        fields_meta[field.fieldname] = field

    return section_fields, fields_meta


def get_field_obj(field):
    obj = {
        "label": field.label,
        "type": get_type(field),
        "name": field.fieldname,
        "hidden": field.hidden,
        "reqd": field.reqd,
        "read_only": field.read_only,
        "all_properties": field,
    }

    obj["placeholder"] = "Add " + field.label + "..."

    if field.fieldtype == "Link":
        obj["placeholder"] = "Select " + field.label + "..."
        obj["doctype"] = field.options
    elif field.fieldtype == "Select" and field.options:
        obj["options"] = [{"label": option, "value": option}
                          for option in field.options.split("\n")]

    if field.read_only:
        obj["tooltip"] = "This field is read only and cannot be edited."

    return obj


def get_type(field):
    if field.fieldtype == "Data" and field.options == "Phone":
        return "phone"
    elif field.fieldtype == "Data" and field.options == "Email":
        return "email"
    elif field.fieldtype == "Check":
        return "checkbox"
    elif field.fieldtype == "Int":
        return "number"
    elif field.fieldtype in ["Small Text", "Text", "Long Text"]:
        return "textarea"
    elif field.read_only:
        return "read_only"
    return field.fieldtype.lower()


def get_assigned_users(doctype, name, default_assigned_to=None):
    assigned_users = frappe.get_all(
        "ToDo",
        fields=["allocated_to"],
        filters={
            "reference_type": doctype,
            "reference_name": name,
            "status": ("!=", "Cancelled"),
        },
        pluck="allocated_to",
    )

    users = list(set(assigned_users))

    # if users is empty, add default_assigned_to
    if not users and default_assigned_to:
        users = [default_assigned_to]
    return users


@frappe.whitelist()
@check_user_admin
def get_fields(doctype: str):
    not_allowed_fieldtypes = list(frappe.model.no_value_fields) + ["Read Only"]
    fields = frappe.get_meta(doctype).fields

    _fields = []

    for field in fields:
        if (
                field.fieldtype not in not_allowed_fieldtypes
                and not field.hidden
                and not field.read_only
                and not field.is_virtual
                and field.fieldname
        ):
            _fields.append({
                "label": field.label,
                "type": field.fieldtype,
                "value": field.fieldname,
                "options": field.options,
            })

    return _fields
