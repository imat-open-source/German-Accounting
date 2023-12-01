from . import __version__ as app_version

app_name = "german_accounting"
app_title = "German Accounting"
app_publisher = "phamos.eu"
app_description = "ERPNext Enhancement for IMAT"
app_email = "furqan.asghar@phamos.eu"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/german_accounting/css/german_accounting.css"
# app_include_js = "/assets/german_accounting/js/german_accounting.js"

# include js, css files in header of web template
# web_include_css = "/assets/german_accounting/css/german_accounting.css"
# web_include_js = "/assets/german_accounting/js/german_accounting.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "german_accounting/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doc_events = {
    "Quotation": {
        "validate": "german_accounting.events.extended_tax_category.validate_tax_category_fields"
	},
    "Sales Order": {
        "validate": "german_accounting.events.extended_tax_category.validate_tax_category_fields"
	},
    "Sales Invoice": {
        "validate": "german_accounting.events.extended_tax_category.validate_tax_category_fields"
	},
    "Address": {
        "validate": "german_accounting.events.address.set_tax_category"
    }
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "german_accounting.utils.jinja_methods",
#	"filters": "german_accounting.utils.jinja_filters"
# }

# Installation
# ------------

after_migrate = "german_accounting.setup.install.after_migrate"
after_install = "german_accounting.setup.install.after_migrate"

# Uninstallation
# ------------

before_uninstall = "german_accounting.setup.install.before_uninstall"
# after_uninstall = "german_accounting.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "german_accounting.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"german_accounting.tasks.all"
#	],
#	"daily": [
#		"german_accounting.tasks.daily"
#	],
#	"hourly": [
#		"german_accounting.tasks.hourly"
#	],
#	"weekly": [
#		"german_accounting.tasks.weekly"
#	],
#	"monthly": [
#		"german_accounting.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "german_accounting.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "german_accounting.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "german_accounting.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["german_accounting.utils.before_request"]
# after_request = ["german_accounting.utils.after_request"]

# Job Events
# ----------
# before_job = ["german_accounting.utils.before_job"]
# after_job = ["german_accounting.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"german_accounting.auth.validate"
# ]
