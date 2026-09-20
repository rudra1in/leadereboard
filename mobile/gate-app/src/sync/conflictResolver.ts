export type ConflictType =
  | "DUPLICATE_VALIDATION"
  | "STALE_TICKET"
  | "REVOKED_CREDENTIAL"
  | "CONFLICTING_UPDATE";

export interface SyncEvent {
  id: string;
  entityType: string;
  entityId: string;
  operation: string;
  payload: string;
  createdAt: string;
  deviceId: string;
}

export interface ConflictResult {
  hasConflict: boolean;
  conflictType?: ConflictType;
  reason?: string;
}

export function detectConflict(
  localEvent: SyncEvent,
  serverEvent: SyncEvent,
): ConflictResult {
  if (
    localEvent.entityType === "validation_event" &&
    serverEvent.entityType === "validation_event" &&
    localEvent.entityId === serverEvent.entityId
  ) {
    return {
      hasConflict: true,
      conflictType: "DUPLICATE_VALIDATION",
      reason: "The validation event already exists on the server.",
    };
  }

  if (
    localEvent.entityType === serverEvent.entityType &&
    localEvent.entityId === serverEvent.entityId &&
    localEvent.operation !== serverEvent.operation
  ) {
    return {
      hasConflict: true,
      conflictType: "CONFLICTING_UPDATE",
      reason: "The local and server operations conflict.",
    };
  }

  return {
    hasConflict: false,
  };
}