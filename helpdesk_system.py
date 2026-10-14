
"""Manage helpdesk tickets and their status."""

import json
import os
from datetime import datetime
from itertools import count

tickets = {}
TICKET_IDS = count(101)
ADMIN_PASSWORD = os.environ.get("HELPDESK_ADMIN_PASSWORD")


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a ticket with a validated priority."""
    if audit_trail is None:
        audit_trail = []

    try:
        priority = int(urgency)
    except (TypeError, ValueError) as error:
        raise ValueError("Urgency must be an integer from 1 to 5.") from error

    if not 1 <= priority <= 5:
        raise ValueError("Urgency must be between 1 and 5.")

    ticket_id = next(TICKET_IDS)
    tickets[ticket_id] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": [],
    }
    audit_trail.append(
        f"{user} raised #{ticket_id} at {datetime.now().isoformat()}"
    )
    return ticket_id


def assign_ticket(ticket_id, technician):
    """Assign an existing ticket to a technician."""
    if ticket_id not in tickets:
        return False
    tickets[ticket_id]["tech"] = technician
    return True


def add_note(ticket_id, note):
    """Add a note to an existing ticket."""
    if ticket_id not in tickets:
        return False
    tickets[ticket_id]["notes"].append(note)
    return True


def close_ticket(ticket_id, password):
    """Close a ticket if the configured admin password is valid."""
    if ticket_id not in tickets:
        return False
    if not ADMIN_PASSWORD or password != ADMIN_PASSWORD:
        return False
    del tickets[ticket_id]
    return True


def unresolved_high_priority():
    """Return unassigned tickets with priority 4 or 5."""
    return [
        ticket_id
        for ticket_id, ticket in tickets.items()
        if ticket["priority"] >= 4 and ticket["tech"] is None
    ]


def save_tickets(file="tickets.json"):
    """Save all tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(tickets, output_file, indent=2)


def main():
    """Run a small interactive helpdesk demonstration."""
    first_ticket = raise_ticket("anil", "printer", "5")
    raise_ticket("meera", "wifi", "4")
    third_ticket = raise_ticket("joe", "vpn", "3")

    assign_ticket(first_ticket, "Tech-Kiran")
    add_note(first_ticket, "Called user")
    add_note(999, "This ticket does not exist")

    print("Unassigned high priority:", unresolved_high_priority())

    while True:
        level = input(
            "Urgency for a new laptop ticket (1-5, Enter for 3): "
        ).strip() or "3"
        try:
            raise_ticket("sana", "laptop", level)
            break
        except ValueError as error:
            print(error)

    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD", "")
    close_ticket(third_ticket, admin_password)
    save_tickets()
    print("Open tickets:", list(tickets.keys()))


if __name__ == "__main__":
    main()
