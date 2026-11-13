"""
Everything the Admin panel needs, kept separate from the regular
user-facing app.py routes:

- System-wide stats (all users, all calls combined - not scoped to one
  uploaded_by like the regular dashboard/profile stats are)
- User management: list users, promote/demote admin, delete a user
  (cascades to delete that user's calls too)
- Call management: list/filter ALL calls across every user, delete any
  call, see which calls failed and why

This mirrors the shape of auth_service.py / pipeline.py - app.py's admin
routes stay thin HTTP handlers, all the actual logic lives here.
"""
from bson import ObjectId


# ---------- system-wide stats ----------

def get_global_stats(calls_collection, users_collection):
    calls = list(calls_collection.find({}))
    completed = [c for c in calls if c.get("status") == "completed"]
    failed = [c for c in calls if c.get("status") == "failed"]
    in_progress = [c for c in calls if c.get("status") not in ("completed", "failed")]

    confidences = [c["confidence_percent"] for c in completed if c.get("confidence_percent") is not None]
    times = [c["total_time_seconds"] for c in completed if c.get("total_time_seconds") is not None]

    category_counts = {}
    sentiment_counts = {}
    priority_counts = {}
    language_counts = {}
    for c in completed:
        if c.get("category"):
            category_counts[c["category"]] = category_counts.get(c["category"], 0) + 1
        if c.get("sentiment"):
            sentiment_counts[c["sentiment"]] = sentiment_counts.get(c["sentiment"], 0) + 1
        if c.get("priority"):
            priority_counts[c["priority"]] = priority_counts.get(c["priority"], 0) + 1
        if c.get("language"):
            language_counts[c["language"]] = language_counts.get(c["language"], 0) + 1

    # Aggregate WHY confidence isn't 100%, across every completed call that
    # has a breakdown - so admins can see systemic issues (e.g. "background
    # noise is the #1 issue across all calls, maybe agents need better mics")
    # rather than only ever seeing it one call at a time.
    reason_totals = {}
    calls_with_breakdown = 0
    for c in completed:
        breakdown = c.get("confidence_breakdown")
        if not breakdown or not breakdown.get("reasons"):
            continue
        calls_with_breakdown += 1
        for reason in breakdown["reasons"]:
            reason_totals[reason["category"]] = reason_totals.get(reason["category"], {
                "label": reason["label"], "total_percent": 0.0, "call_count": 0,
            })
            reason_totals[reason["category"]]["total_percent"] += reason["percent"]
            reason_totals[reason["category"]]["call_count"] += 1

    top_reasons = []
    for category, data in sorted(reason_totals.items(), key=lambda kv: -kv[1]["total_percent"]):
        top_reasons.append({
            "category": category,
            "label": data["label"],
            "avg_percent": round(data["total_percent"] / data["call_count"], 1),
            "call_count": data["call_count"],
        })

    return {
        "total_users": users_collection.count_documents({}),
        "total_calls": len(calls),
        "completed_calls": len(completed),
        "failed_calls": len(failed),
        "in_progress_calls": len(in_progress),
        "avg_confidence": round(sum(confidences) / len(confidences), 1) if confidences else None,
        "avg_time": round(sum(times) / len(times), 1) if times else None,
        "category_counts": category_counts,
        "sentiment_counts": sentiment_counts,
        "priority_counts": priority_counts,
        "language_counts": language_counts,
        "top_confidence_reasons": top_reasons,
        "calls_with_breakdown": calls_with_breakdown,
    }


# ---------- user management ----------

def list_users(users_collection, calls_collection):
    users = list(users_collection.find({}).sort("created_at", -1))
    for user in users:
        user["call_count"] = calls_collection.count_documents({"uploaded_by": str(user["_id"])})
    return users


def set_admin_status(users_collection, target_user_id, make_admin, actor_user_id):
    """Promotes/demotes a user. Admins can't demote themselves (guards
    against a lone admin locking themselves out)."""
    if target_user_id == actor_user_id and not make_admin:
        return False, "You can't remove your own admin access."

    try:
        oid = ObjectId(target_user_id)
    except Exception:
        return False, "Invalid user."

    result = users_collection.update_one({"_id": oid}, {"$set": {"is_admin": make_admin}})
    if result.matched_count == 0:
        return False, "User not found."
    return True, None


def delete_user_cascade(users_collection, calls_collection, target_user_id, actor_user_id):
    """Deletes a user AND every call they uploaded. Admins can't delete
    their own account from this panel (use normal account flows for that,
    keeps this destructive action unambiguous)."""
    if target_user_id == actor_user_id:
        return False, "You can't delete your own account from the admin panel."

    try:
        oid = ObjectId(target_user_id)
    except Exception:
        return False, "Invalid user."

    user = users_collection.find_one({"_id": oid})
    if not user:
        return False, "User not found."

    calls_collection.delete_many({"uploaded_by": target_user_id})
    users_collection.delete_one({"_id": oid})
    return True, None


# ---------- call management (all users) ----------

def list_all_calls(calls_collection, status=None, category=None, limit=200):
    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    return list(
        calls_collection.find(query).sort("created_at", -1).limit(limit)
    )


def delete_any_call(calls_collection, call_id):
    try:
        oid = ObjectId(call_id)
    except Exception:
        return False
    result = calls_collection.delete_one({"_id": oid})
    return result.deleted_count > 0
