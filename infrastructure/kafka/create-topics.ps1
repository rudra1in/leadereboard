$topics = @(
    "score_events",
    "match_status",
    "athlete_profile_updates",
    "bracket_updates",
    "gate_sync",
    "notification_push",
    "notification_email",
    "notification_sms",
    "ai_inference_results"
)

foreach ($topic in $topics) {
    Write-Host "Creating Kafka topic: $topic"

    docker exec gamex-kafka kafka-topics `
        --bootstrap-server localhost:9092 `
        --create `
        --if-not-exists `
        --topic $topic `
        --partitions 3 `
        --replication-factor 1
}

Write-Host ""
Write-Host "GameX Kafka topics:"

docker exec gamex-kafka kafka-topics `
    --bootstrap-server localhost:9092 `
    --list