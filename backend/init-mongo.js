// MongoDB initialization script
db = db.getSiblingDB('ai_call_summarization');

// Create collections with validation
db.createCollection('calls', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["session_id", "start_time", "status"],
            properties: {
                session_id: {
                    bsonType: "string",
                    description: "Unique session identifier"
                },
                start_time: {
                    bsonType: "date",
                    description: "Call start timestamp"
                },
                status: {
                    enum: ["active", "ended", "processing"],
                    description: "Call status"
                },
                dialog_turns: {
                    bsonType: "array",
                    description: "Array of dialog turns"
                }
            }
        }
    }
});

db.createCollection('summaries', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["call_session_id", "summary_text", "created_at"],
            properties: {
                call_session_id: {
                    bsonType: "string",
                    description: "Reference to call session"
                },
                summary_text: {
                    bsonType: "string",
                    description: "Summary content"
                },
                is_final: {
                    bsonType: "bool",
                    description: "Whether this is the final summary"
                }
            }
        }
    }
});

db.createCollection('analytics', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["call_session_id", "total_duration", "created_at"],
            properties: {
                call_session_id: {
                    bsonType: "string",
                    description: "Reference to call session"
                },
                total_duration: {
                    bsonType: "number",
                    description: "Total call duration in seconds"
                }
            }
        }
    }
});

// Create indexes for better performance
db.calls.createIndex({ "session_id": 1 }, { unique: true });
db.calls.createIndex({ "start_time": 1 });
db.calls.createIndex({ "status": 1 });

db.summaries.createIndex({ "call_session_id": 1 });
db.summaries.createIndex({ "created_at": 1 });
db.summaries.createIndex({ "is_final": 1 });

db.analytics.createIndex({ "call_session_id": 1 }, { unique: true });
db.analytics.createIndex({ "created_at": 1 });

print("MongoDB initialization completed successfully");
