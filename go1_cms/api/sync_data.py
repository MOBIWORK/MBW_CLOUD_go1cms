import frappe

def check_sync_flags(doc, method):
    """
    Helper function to prevent two-way sync loops.
    Used in before_save and before_delete hooks for synchronized doctypes.
    """
    # Check if this is a sync operation (being triggered by the sync system)
    if hasattr(doc, 'flags') and getattr(doc.flags, 'ignore_sync', False):
        # If it is, we don't want to trigger any further sync operations
        return
        
    # If a document is being synced from the source system, don't sync back
    if hasattr(doc, 'sync_source') and doc.sync_source:
        # Reset the flag for future updates but don't trigger sync
        frappe.db.set_value(doc.doctype, doc.name, 'sync_source', 0)
        # Set the ignore_sync flag to prevent any sync operations during this save
        doc.flags.ignore_sync = True