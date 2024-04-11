package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
@AllArgsConstructor
public class WorkPlan implements IId<UUID> {
    private UUID workPlanId;
    private String description;
    private Duration duration;

    public WorkPlan() {
        this.workPlanId = UUID.randomUUID();
        this.description = "";
    }

    public UUID getId() {
        return workPlanId;
    }

    public void setId(UUID id) {
        this.workPlanId = id;
    }
}
