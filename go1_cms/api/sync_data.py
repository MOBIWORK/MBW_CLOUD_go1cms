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
    
    # If a document has sync_source flag, reset it for future syncs    
    if hasattr(doc, 'sync_source') and doc.sync_source:
        # Reset the flag to allow syncing on next update
        frappe.db.set_value(doc.doctype, doc.name, 'sync_source', 0)
        
    # Always mark the document as needing sync unless ignore_sync is set
    doc.flags.needs_sync = True