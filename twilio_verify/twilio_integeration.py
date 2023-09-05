# Import necessary modules
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from frappe import _
import frappe

def update_phone_verified_status(user, status):
    try:
        # Get the last document for the current user
        doc = frappe.get_last_doc("Customer Profile", filters={"user": user})

        if doc:
            # Update the "phone_verified" field to the specified status
            doc.phone_verified = status
            doc.save()
    except Exception as e:
        frappe.log_error(_("Error updating phone_verified status: {0}").format(str(e)))

@frappe.whitelist()
def send_verification_code():
    try:
        # Get the phone number from the request
        to = frappe.form_dict.get("to")

        # Fetch Twilio settings from the "Twilio Settings" doctype
        twilio_settings = frappe.get_single("Twilio Settings")  # Replace "Twilio Settings Docname" with the actual document name

        # Initialize the Twilio client with settings from the document
        client = Client(twilio_settings.account_sid, twilio_settings.auth_token)

        # Create a verification service
        verify = client.verify.services(twilio_settings.service_sid)

        # Send verification
        verify.verifications.create(to=to, channel='sms')

        # Update the "phone_verified" field to False for the current user
        update_phone_verified_status(frappe.session.user, False)

        return frappe.response.json({"status": "success", "message": _("Verification code sent successfully.")})
    except TwilioRestException as e:
        return frappe.response.json({"status": "error", "message": _("Error sending verification code: {0}").format(str(e))}, status=500)



@frappe.whitelist()
def verify_verification_code():
    try:
        # Get the phone number and code from the request
        to = frappe.form_dict.get("to")
        code = frappe.form_dict.get("code")

        # Fetch Twilio settings from the "Twilio Settings" doctype
        twilio_settings = frappe.get_single("Twilio Settings")   # Replace "Twilio Settings Docname" with the actual document name

        # Initialize the Twilio client with settings from the document
        client = Client(twilio_settings.account_sid, twilio_settings.auth_token)

        # Create a verification service
        verify = client.verify.services(twilio_settings.service_sid)

        # Check verification
        result = verify.verification_checks.create(to=to, code=code)

        if result.status == 'approved':
            # Update the "phone_verified" field to True for the current user
            update_phone_verified_status(frappe.session.user, True)

            return frappe.response.json({"status": "success", "message": _("Verification code approved.")})
        else:
            return frappe.response.json({"status": "error", "message": _("Verification code not approved.")})
    except TwilioRestException as e:
        return frappe.response.json({"status": "error", "message": _("Error checking verification code: {0}").format(str(e))}, status=500)